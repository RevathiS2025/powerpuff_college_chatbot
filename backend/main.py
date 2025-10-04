import os
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()

# Import your backend modules
from vector_store import VectorStore
from groq_llm import GroqLLMClient
from rbac import UserRole, get_accessible_roles

# ==================== CONFIGURATION ====================
# Simple user roles without database
DEMO_USERS = {
    "parent_user": "parent",
    "student_user": "student", 
    "professor_user": "professor",
    "dean_user": "dean"
}

# ==================== AUTHENTICATION ====================
def select_user_role() -> tuple:
    """Simple role selection without database."""
    print("\n=== SELECT USER ROLE ===")
    print("Available demo users:")
    for i, (username, role) in enumerate(DEMO_USERS.items(), 1):
        print(f"{i}. {username} ({role})")
    
    while True:
        try:
            choice = int(input(f"\nSelect user (1-{len(DEMO_USERS)}): "))
            if 1 <= choice <= len(DEMO_USERS):
                username, role = list(DEMO_USERS.items())[choice-1]
                return username, role
            else:
                print("❌ Invalid choice!")
        except ValueError:
            print("❌ Please enter a valid number!")

def display_role_access(role: str):
    """Display what the current role can access."""
    role_descriptions = {
        "parent": "College overview, placements, courses offered, fees structure",
        "student": "Course syllabus, placement opportunities, college events, exam schedule", 
        "professor": "Academic policies, leave application, event coordination, exam evaluation",
        "dean": "All information (complete access)"
    }
    
    print(f"\n=== ROLE ACCESS INFORMATION ===")
    print(f"Role: {role}")
    print(f"Access: {role_descriptions.get(role, 'Unknown role')}")
    print(f"Accessible roles: {get_accessible_roles(role)}")

# ==================== MAIN FUNCTIONS ====================
def initialize_system():
    """Initialize all backend components."""
    print("🚀 Initializing RAG Chatbot System...")
    
    # Check prerequisites
    if not os.path.exists("chromadb_data"):
        print("❌ Vector database not found!")
        print("Please run: python backend/document_ingest.py first")
        return None, None
    
    if not os.getenv("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY environment variable not set!")
        return None, None
    
    # Initialize vector store
    print("📚 Loading vector store...")
    vector_store = VectorStore()
    if not vector_store.collection:
        print("❌ Failed to initialize vector store!")
        return None, None
    
    # Initialize LLM client
    print("🤖 Initializing LLM client...")
    try:
        llm_client = GroqLLMClient()
        print("✅ System initialization complete!")
        return vector_store, llm_client
    except Exception as e:
        print(f"❌ Failed to initialize LLM client: {e}")
        return None, None

def process_user_query(query: str, user_role: str, vector_store: VectorStore, 
                      llm_client: GroqLLMClient, conversation_history: List[Dict]) -> str:
    """Process user query with role-based access."""
    try:
        # Step 1: Role-based document retrieval
        print(f"🔍 Retrieving documents for role: {user_role}")
        retrieved_docs = vector_store.retrieve_documents(
            query_text=query,
            user_role=user_role,
            n_results=5
        )
        
        print(f"📄 Found {len(retrieved_docs)} relevant documents")
        
        if not retrieved_docs:
            return f"Sorry, I couldn't find any relevant information for your role ({user_role}) regarding: {query}"
        
        # Step 2: Generate LLM response
        print("💭 Generating response...")
        response = llm_client.generate_response(
            user_query=query,
            context_documents=retrieved_docs,
            user_role=user_role,
            conversation_history=conversation_history
        )
        
        return response
        
    except Exception as e:
        print(f"❌ Error processing query: {e}")
        return "Sorry, I encountered an error while processing your query. Please try again."

def chat_session(username: str, user_role: str, vector_store: VectorStore, llm_client: GroqLLMClient):
    """Main chat session loop."""
    conversation_history = []
    
    print(f"\n=== CHAT SESSION ===")
    print(f"User: {username} | Role: {user_role}")
    display_role_access(user_role)
    print("\nType 'quit' to exit, 'clear' to clear history, 'info' for role info")
    print("-" * 60)
    
    while True:
        try:
            # Get user input
            user_input = input(f"\n[{username}]: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'clear':
                conversation_history = []
                print("🧹 Conversation history cleared!")
                continue
            elif user_input.lower() == 'info':
                display_role_access(user_role)
                continue
            elif not user_input:
                continue
            
            # Process the query
            response = process_user_query(
                query=user_input,
                user_role=user_role,
                vector_store=vector_store,
                llm_client=llm_client,
                conversation_history=conversation_history
            )
            
            # Display response
            print(f"\n[Assistant]: {response}")
            
            # Update conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})
            
            # Keep only last 10 messages
            if len(conversation_history) > 10:
                conversation_history = conversation_history[-10:]
                
        except KeyboardInterrupt:
            print("\n\n Session ended!")
            break
        except Exception as e:
            print(f"\n Unexpected error: {e}")

def main():
    """Main application entry point."""
    print(" COLLEGE RAG CHATBOT WITH ROLE-BASED ACCESS CONTROL")
    print("=" * 60)
    
    # Initialize system components
    vector_store, llm_client = initialize_system()
    if not vector_store or not llm_client:
        print("❌ System initialization failed. Exiting...")
        return
    
    # User role selection
    username, user_role = select_user_role()
    
    # Validate role
    if not UserRole.is_valid_role(user_role):
        print(f"❌ Invalid role: {user_role}")
        return
    
    print(f"✅ Logged in as: {username} ({user_role})")
    
    # Start chat session
    chat_session(username, user_role, vector_store, llm_client)

if __name__ == "__main__":
    # Environment check
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️  Warning: GROQ_API_KEY not found in environment variables")
        print("Please set it before running the application")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Application terminated. Goodbye!")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
