import streamlit as st
from app.database import get_database
from backend.rbac import UserRole

def initialize_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def check_authentication() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get('authenticated', False)

def login_user(username: str, password: str) -> bool:
    """
    Authenticate user and set session state.
    
    Args:
        username (str): Username
        password (str): Password
        
    Returns:
        bool: True if login successful, False otherwise
    """
    if not username or not password:
        st.error("Please enter both username and password.")
        return False
    
    db = get_database()
    user_info = db.authenticate_user(username, password)
    
    if user_info:
        st.session_state.authenticated = True
        st.session_state.user_info = user_info
        
        # Load chat history
        chat_history = db.get_chat_history(user_info['id'])
        st.session_state.chat_history = []
        
        # Convert to chat format
        for chat in chat_history:
            st.session_state.chat_history.append({
                "role": "user",
                "content": chat['message']
            })
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": chat['response']
            })
        
        st.success(f"Welcome back, {user_info['username']}!")
        st.rerun()
        return True
    else:
        st.error("Invalid username or password.")
        return False

def register_user(username: str, email: str, password: str, confirm_password: str, role: str) -> bool:
    """
    Register a new user.
    
    Args:
        username (str): Username
        email (str): Email
        password (str): Password
        confirm_password (str): Password confirmation
        role (str): User role
        
    Returns:
        bool: True if registration successful, False otherwise
    """
    # Validation
    if not all([username, email, password, confirm_password, role]):
        st.error("Please fill in all fields.")
        return False
    
    if password != confirm_password:
        st.error("Passwords do not match.")
        return False
    
    if len(password) < 6:
        st.error("Password must be at least 6 characters long.")
        return False
    
    if not UserRole.is_valid_role(role):
        st.error("Invalid role selected.")
        return False
    
    db = get_database()
    
    if db.register_user(username, email, password, role):
        st.success("Registration successful! Please login with your credentials.")
        return True
    else:
        st.error("Username or email already exists. Please choose different ones.")
        return False

def logout_user():
    """Logout user and clear session state."""
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.chat_history = []
    st.success("Logged out successfully!")
    st.rerun()

def get_current_user():
    """Get current user information."""
    return st.session_state.get('user_info')

def get_current_user_role():
    """Get current user's role."""
    user_info = get_current_user()
    return user_info['role'] if user_info else None

