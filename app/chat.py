import streamlit as st
from app.auth import get_current_user_role
from backend.vector_store import VectorStore
from backend.groq_llm import GroqLLMClient

# Initialize components (cached for performance)
@st.cache_resource
def get_vector_store():
    """Get vector store instance (cached)."""
    return VectorStore()

@st.cache_resource  
def get_llm_client():
    """Get LLM client instance (cached)."""
    try:
        return GroqLLMClient()
    except Exception as e:
        st.error(f"Failed to initialize Groq LLM: {e}")
        return None

def process_user_query(user_query: str) -> str:
    """
    Process user query through the RAG pipeline with role-based access control.
    
    Args:
        user_query (str): The user's question
        
    Returns:
        str: Generated response from the system
    """
    user_role = get_current_user_role()
    
    if not user_role:
        return "Error: Unable to determine user role. Please login again."
    
    # Get vector store and LLM client
    vector_store = get_vector_store()
    llm_client = get_llm_client()
    
    if not vector_store or not vector_store.collection:
        return "⚠️ Knowledge base is not available. Please contact administrator."
    
    if not llm_client:
        return "⚠️ AI service is not available. Please try again later."
    
    try:
        # Step 1: Retrieve relevant documents based on user role
        with st.spinner("🔍 Searching for relevant information..."):
            context_documents = vector_store.retrieve_documents(
                query_text=user_query,
                user_role=user_role,
                n_results=5
            )
        
        # Handle case where no documents are found
        if not context_documents or not context_documents[0]:
            return f"""
            I apologize, but I couldn't find any information relevant to your query that you have access to as a **{user_role}**.
            
            This might be because:
            - The information you're looking for is not available in our knowledge base
            - Your current role doesn't have permission to access this type of information
            - The query might be too specific or unclear
            
            Please try rephrasing your question or contact an administrator if you believe you should have access to this information.
            """
        
        # Step 2: Generate response using LLM with context
        with st.spinner("🤖 Generating response..."):
            # Get conversation history for context (last 6 messages)
            conversation_history = []
            if len(st.session_state.chat_history) > 1:
                recent_history = st.session_state.chat_history[-6:]  # Last 3 exchanges
                for msg in recent_history:
                    conversation_history.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            response = llm_client.generate_response(
                user_query=user_query,
                context_documents=context_documents[0],  # ChromaDB returns list of lists
                user_role=user_role,
                conversation_history=conversation_history,
                max_tokens=1024,
                temperature=0.7
            )
        
        return response
        
    except Exception as e:
        st.error(f"Error processing query: {e}")
        return "I apologize, but I encountered an error while processing your request. Please try again."

def get_role_specific_suggestions(user_role: str) -> list:
    """
    Get role-specific query suggestions for users.
    
    Args:
        user_role (str): The user's role
        
    Returns:
        list: List of suggested queries
    """
    suggestions = {
        "parent": [
            "What programs does the college offer?",
            "What are the college facilities?", 
            "What is the fee structure?",
            "What are the placement records?",
            "How can I contact the college?"
        ],
        "student": [
            "What is the course syllabus for my program?",
            "When are the upcoming exams?",
            "What placement opportunities are available?",
            "What events are happening this semester?",
            "How do I check my exam results?"
        ],
        "professor": [
            "What are the academic policies?",
            "How do I apply for leave?",
            "What are the exam scheduling guidelines?",
            "How can I coordinate events?",
            "What are the evaluation guidelines?"
        ],
        "dean": [
            "Show me the performance analytics",
            "What are the administrative policies?",
            "What is our strategic planning data?",
            "How are faculty performing?",
            "What are the enrollment trends?"
        ]
    }
    
    return suggestions.get(user_role, [])

# You can add this to your chat interface to show suggestions
def show_query_suggestions():
    """Display role-specific query suggestions."""
    user_role = get_current_user_role()
    suggestions = get_role_specific_suggestions(user_role)
    
    if suggestions:
        st.markdown("### 💡 Suggested Questions:")
        cols = st.columns(2)
        
        for i, suggestion in enumerate(suggestions):
            col = cols[i % 2]
            with col:
                if st.button(suggestion, key=f"suggestion_{i}"):
                    # Add suggestion to chat
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": suggestion
                    })
                    
                    response = process_user_query(suggestion)
                    
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": response
                    })
                    
                    st.rerun()


