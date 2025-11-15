import streamlit as st
from app.auth import login_user, register_user, logout_user, get_current_user
from backend.rbac import UserRole




def show_login_signup_tabs():
    """Display login and signup tabs with a welcoming hero banner."""
    st.markdown(
        """
        <div class="auth-hero">
          <div class="auth-hero-icon">🎓</div>
          <div class="auth-hero-text">
            <h2>Welcome to Powerpuff College</h2>
            <p>Your personalized access to campus information and services.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )




    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])




    with tab1:
        show_login_form()




    with tab2:
        show_signup_form()




def show_login_form():
    """Display login form."""
    st.markdown("""
    <div class="auth-card">
      <div class="auth-header">
        <span class="auth-header-icon">🔐</span>
        <div>
          <h3>Welcome Back</h3>
          <p class="muted">Sign in to continue to your personalized dashboard.</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)




    with st.form("login_form"):
        col1, col2, col3 = st.columns([1, 2, 1])




        with col2:
            username = st.text_input("👤 Username", placeholder="e.g., John")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            remember_me = st.checkbox("Keep me signed in")




            login_button = st.form_submit_button("✨ Login", use_container_width=True)




            if login_button:
                login_user(username, password)




def show_signup_form():
    """Display signup form."""
    st.markdown("""
    <div class="auth-card">
      <div class="auth-header">
        <span class="auth-header-icon">📝</span>
        <div>
          <h3>Create Account</h3>
          <p class="muted">Join our college information system for tailored assistance.</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


   
    # Role selector placed OUTSIDE the form to enable live updates
    selected_role = st.selectbox(
        "🎭 Select Your Role",
        options=UserRole.get_all_roles(),
        format_func=lambda x: x.title(),
        key="signup_role",
        help="Select your role to get personalized information access"
    )


    # Role descriptions
    role_descriptions = {
        "parent": "Access college overview, placement records, courses, and fee structure",
        "student": "Access course syllabus, placement opportunities, events, and exam schedules",
        "professor": "Access academic policies, leave applications, event coordination, and exam guidelines",
        "dean": "Full access to all information including analytics and strategic planning"
    }
    st.info(f"**{selected_role.title()}:** {role_descriptions.get(selected_role, '')}")


    with st.form("signup_form"):
        col1, col2, col3 = st.columns([1, 2, 1])
       
        with col2:
            username = st.text_input("👤 Username", key="signup_username", placeholder="Choose a unique username")
            email = st.text_input("📧 Email", key="signup_email", placeholder="your.name@example.com")
           
            col_pass1, col_pass2 = st.columns(2)
            with col_pass1:
                password = st.text_input("🔑 Password", key="signup_password", type="password", placeholder="Enter a strong password")
            with col_pass2:
                confirm_password = st.text_input("✅ Confirm Password", key="signup_confirm", type="password", placeholder="Re-enter password")
           
            signup_button = st.form_submit_button("🌟 Create Account", use_container_width=True)
           
            if signup_button:
                role_to_register = st.session_state.get("signup_role", UserRole.get_all_roles()[0])
                if register_user(username, email, password, confirm_password, role_to_register):
                    # Clear fields after successful registration
                    st.session_state["signup_username"] = ""
                    st.session_state["signup_email"] = ""
                    st.session_state["signup_password"] = ""
                    st.session_state["signup_confirm"] = ""
                    st.session_state["signup_role"] = UserRole.get_all_roles()[0]
                    st.balloons()
                    st.rerun()




def show_chat_interface():
    """Display the main chat interface for authenticated users."""
    user_info = get_current_user()
   
    # Header with user info and logout
    col1, col2, col3 = st.columns([2, 1, 1])
   
    with col1:
        st.markdown(f"### 💬 Chat with AI Assistant")
        st.markdown(f"**Role:** {user_info['role'].title()} | **User:** {user_info['username']}")
   
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
   
    # Role-specific welcome message
    username = user_info['username']

    role_messages = {
    "parent": (
        "👨‍👩‍👧‍👦 Welcome, {username}! "
        "You can access information about the college overview, available courses, fees, placements, and important highlights relevant to your child’s education journey. "
 
    ),
    "student": (
        "🎓 Welcome, {username}! "
        "You have access to course syllabi, exam schedules, placement opportunities, student events, and all information needed for your academic progress. "
      
    ),
    "professor": (
        "👨‍🏫 Welcome, {username}!"
        "You can explore academic and administrative policies, event coordination, exam evaluation guidelines, leave application procedures, and details on courses and placements. "
    ),
    "dean": (
        "🏛️ Welcome, {username}! "
        "You have comprehensive access to all college documents, including analytics, performance reports, strategic planning, administrative policies, and every resource available to other roles. "
    )
}

    welcome_template = role_messages.get(user_info['role'], "Welcome to the college chatbot!")
    welcome_message = welcome_template.format(username=user_info['username'])
    st.info(welcome_message)

   
    # Chat interface
    display_chat_history()
    handle_chat_input()




def display_chat_history():
    """Display chat history with Streamlit chat components."""
    if st.session_state.chat_history:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    else:
        st.markdown("*No chat history yet. Start by asking a question!*")




def render_quick_prompts():
    """Show role-aware quick prompts to jumpstart queries."""
    from app.auth import get_current_user_role
    role = get_current_user_role()
    role_prompts = {
        "parent": ["College overview", "Placement stats", "Courses offered", "Fees details"],
        "student": ["Exam schedule", "Placement opportunities", "Student events", "Course syllabus"],
        "professor": ["Academic policies", "Leave application process", "Event coordination", "Exam evaluation"],
        "dean": ["Administrative policies", "Strategic planning", "Performance analytics", "Department overview"],
    }
    prompts = role_prompts.get(role, [])
    if not prompts:
        return
    st.caption("Quick prompts")
    cols = st.columns(len(prompts))
    for col, text in zip(cols, prompts):
        with col:
            if st.button(text):
                # Immediately show the user's message and set as pending
                st.session_state.chat_history.append({"role": "user", "content": text})
                st.session_state.pending_query = text
                st.rerun()




def handle_chat_input():
    """Handle new chat input from user."""
    # If a response is pending from a previous input, process it first
    pending_query = st.session_state.get("pending_query")
    if pending_query:
        try:
            from app.chat import process_user_query_stream
            # Stream assistant response live
            accumulated = ""
            with st.chat_message("assistant"):
                placeholder = st.empty()
                for chunk in process_user_query_stream(pending_query):
                    accumulated += chunk
                    placeholder.markdown(accumulated)
            # Add assistant response to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": accumulated
            })
            # Save to database
            user_info = get_current_user()
            from app.database import get_database
            db = get_database()
            if user_info and 'id' in user_info:
                db.save_chat_message(user_info['id'], pending_query, accumulated)
        finally:
            # Clear pending query and rerun to update UI
            st.session_state.pending_query = None
            st.rerun()




    # Capture new user input
    user_input = st.chat_input("Ask me anything about the college...")
    if user_input:
        # Immediately show the user's message
        with st.chat_message("user"):
            st.write(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        # Set as pending to process answer on the next run
        st.session_state.pending_query = user_input
        st.rerun()
