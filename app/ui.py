import streamlit as st
from app.auth import login_user, register_user, logout_user, get_current_user
from backend.rbac import UserRole

def show_login_signup_tabs():
    """Display login and signup tabs."""
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        show_login_form()
    
    with tab2:
        show_signup_form()

def show_login_form():
    """Display login form."""
    st.markdown("### Welcome Back!")
    st.markdown("Please enter your credentials to access the chatbot.")
    
    with st.form("login_form"):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            login_button = st.form_submit_button("🔓 Login", use_container_width=True)
            
            if login_button:
                login_user(username, password)

def show_signup_form():
    """Display signup form."""
    st.markdown("### Create New Account")
    st.markdown("Join our college information system to get personalized assistance.")
    
    with st.form("signup_form"):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="Enter your email address")
            
            col_pass1, col_pass2 = st.columns(2)
            with col_pass1:
                password = st.text_input("Password", type="password", placeholder="Enter password")
            with col_pass2:
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
            
            role = st.selectbox(
                "Select Your Role",
                options=UserRole.get_all_roles(),
                format_func=lambda x: x.title(),
                help="Select your role to get personalized information access"
            )
            
            # Role descriptions
            role_descriptions = {
                "parent": "Access college overview, placement records, courses, and fee structure",
                "student": "Access course syllabus, placement opportunities, events, and exam schedules", 
                "professor": "Access academic policies, leave applications, event coordination, and exam guidelines",
                "dean": "Full access to all information including analytics and strategic planning"
            }
            
            if role:
                st.info(f"**{role.title()}:** {role_descriptions.get(role, '')}")
            
            signup_button = st.form_submit_button("📝 Create Account", use_container_width=True)
            
            if signup_button:
                if register_user(username, email, password, confirm_password, role):
                    st.balloons()

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
    role_messages = {
        "parent": "👨‍👩‍👧‍👦 Welcome! I can help you with college information, placement records, courses, and fees.",
        "student": "🎓 Welcome! I can assist you with course syllabus, placements, events, and exam schedules.",
        "professor": "👨‍🏫 Welcome! I can help you with academic policies, leave applications, and exam guidelines.",
        "dean": "🏛️ Welcome! I have access to all college information including analytics and strategic planning."
    }
    
    st.info(role_messages.get(user_info['role'], "Welcome to the college information system!"))
    
    # Chat interface
    display_chat_history()
    handle_chat_input()

def display_chat_history():
    """Display chat history."""
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(
                        f'<div class="user-message">👤 {message["content"]}</div>', 
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="assistant-message">🤖 {message["content"]}</div>', 
                        unsafe_allow_html=True
                    )
        else:
            st.markdown("*No chat history yet. Start by asking a question!*")

def handle_chat_input():
    """Handle new chat input from user."""
    user_input = st.chat_input("Ask me anything about the college...")
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Process the query (this will be handled in chat.py)
        from app.chat import process_user_query
        response = process_user_query(user_input)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Save to database
        user_info = get_current_user()
        from app.database import get_database
        db = get_database()
        db.save_chat_message(user_info['id'], user_input, response)
        
        # Rerun to show new messages
        st.rerun()

