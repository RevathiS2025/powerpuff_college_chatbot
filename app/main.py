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
    :root {
        --brand-primary: #1f6feb;
        --brand-secondary: #0b3d91;
        --assistant-bg: #f0f6ff;
        --user-bg: #e6f2ff;
        --accent-green: #2ecc71;
        --accent-pink: #ff7aa2;
        --accent-yellow: #f4d03f;
    }
    .stApp {
        background: linear-gradient(135deg, #f9fbff 0%, #eef5ff 40%, #fff6fb 100%);
    }
    .main-header {
        text-align: center;
        color: var(--brand-primary);
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
    }
    /* Auth hero */
    .auth-hero {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem 1.25rem;
        border-radius: 14px;
        backdrop-filter: blur(6px);
        background: rgba(31, 111, 235, 0.08);
        border: 1px solid rgba(31, 111, 235, 0.15);
        margin-bottom: 1rem;
    }
    .auth-hero-icon { font-size: 2rem; }
    .auth-hero-text h2 {
        margin: 0; color: var(--brand-primary);
    }
    .auth-hero-text p { margin: 0; color: #4a4a4a; }


    /* Card-style forms */
    .stForm {
        background: #ffffff;
        border: 1px solid #e6eefc;
        border-radius: 14px;
        box-shadow: 0 6px 20px rgba(32, 64, 128, 0.08);
        padding: 1rem !important;
    }
    .auth-header {
        display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.5rem;
    }
    .auth-header-icon { font-size: 1.6rem; }
    .auth-header h3 { margin: 0; color: var(--brand-secondary); }
    .auth-header .muted { margin: 0; color: #6b7280; }


    /* Inputs & labels */
    .stTextInput > label, .stPasswordInput > label, .stSelectbox > label {
        color: var(--brand-secondary);
        font-weight: 600;
    }
    .stTextInput input, .stPasswordInput input, .stSelectbox select {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
    }
    .stCheckbox { margin-top: 0.5rem; }


    .stChatMessage[class*="assistant"] {
        background: var(--assistant-bg);
        border-left: 4px solid var(--brand-primary);
        border-radius: 12px;
        padding: 0.5rem 0.75rem;
        margin: 0.4rem 0;
    }
    .stChatMessage[class*="user"] {
        background: var(--user-bg);
        border-left: 4px solid var(--brand-secondary);
        border-radius: 12px;
        padding: 0.5rem 0.75rem;
        margin: 0.4rem 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, var(--brand-primary), var(--brand-secondary));
        color: white;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 14px rgba(31, 111, 235, 0.25);
    }
    </style>
    """, unsafe_allow_html=True)
   
    # Check if user is authenticated
    if check_authentication():
        # Show chat interface for authenticated users
        show_chat_interface()
    else:
        # Show login/signup tabs for unauthenticated users
        show_login_signup_tabs()


if __name__ == "__main__":
    main()
