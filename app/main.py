import streamlit as st
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.auth import check_authentication, initialize_session_state
from app.ui import show_login_signup_tabs, show_chat_interface

def main():
    """
    Main Streamlit application entry point.
    Handles routing between login/signup and chat interface.
    """
    st.set_page_config(
        page_title="RAG Chatbot - College Information System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Add custom CSS
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #2E86AB;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    .chat-container {
        border-radius: 10px;
        padding: 1rem;
        background-color: #f8f9fa;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.8rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        text-align: right;
    }
    .assistant-message {
        background-color: #e9ecef;
        color: #495057;
        padding: 0.8rem;
        border-radius: 15px;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<h1 class="main-header">🎓 College Information Chatbot</h1>', unsafe_allow_html=True)
    
    # Check if user is authenticated
    if check_authentication():
        # Show chat interface for authenticated users
        show_chat_interface()
    else:
        # Show login/signup tabs for unauthenticated users
        show_login_signup_tabs()

if __name__ == "__main__":
    main()

