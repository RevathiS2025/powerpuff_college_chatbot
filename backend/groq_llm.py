import os
from groq import Groq
from typing import List, Optional


class GroqLLMClient:
    """
    A client for interacting with Groq's LLM API.
    Handles context-aware response generation for the RAG chatbot.
    """
   
    def __init__(self, api_key: Optional[str] = None, model_name: str = "moonshotai/kimi-k2-instruct-0905"):
        """
        Initialize the Groq client.
       
        Args:
            api_key (str, optional): Groq API key. If None, reads from environment variable.
            model_name (str): The Groq model to use for generation.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
       
        if not self.api_key:
            raise ValueError("Groq API key not provided. Set GROQ_API_KEY environment variable or pass it directly.")
       
        self.model_name = model_name
        self.client = Groq(api_key=self.api_key)
       
        # System prompt template for the RAG chatbot
        # Persona: Speak as an official representative of the college.
        self.system_prompt = """
You are the official representative of the college, answering on behalf of the institution.
Your tone is professional, friendly, and authoritative. Use first‑person plural where natural (e.g., “we”, “our”).


Strict guidelines:
- Answer based strictly on the provided context documents.
- If the context lacks the information, say so politely and offer what is available.
- Do not speculate or invent details not present in context.
- Keep responses concise and well-structured; use clear bullet points where helpful.
- Avoid phrasing that suggests you are an outsider; speak as the college.
"""


    def create_context_prompt(self, user_query: str, context_documents: List[str], user_role: str) -> str:
        """
        Create a prompt that includes context documents and the user query.
       
        Args:
            user_query (str): The user's question
            context_documents (List[str]): Retrieved document chunks
            user_role (str): The user's role (for reference)
           
        Returns:
            str: Formatted prompt for the LLM
        """
        if not context_documents:
            context_text = "No relevant documents found for your query."
        else:
            # Join all context documents
            context_text = "\n\n".join([f"Document {i+1}: {doc}" for i, doc in enumerate(context_documents)])
       
        prompt = f"""Context Information:
{context_text}


User Role: {user_role}
User Query: {user_query}


Please answer as an official representative of the college. Base your answer strictly on the context above. If the context does not contain the necessary information, state that clearly and offer any closest relevant details from the context. Avoid speculation and maintain an authoritative, helpful tone."""
       
        return prompt


    def generate_response(self,
                         user_query: str,
                         context_documents: List[str],
                         user_role: str,
                         conversation_history: Optional[List[dict]] = None,
                         max_tokens: int = 1024,
                         temperature: float = 0.7) -> str:
        """
        Generate a response using Groq LLM with context documents.
       
        Args:
            user_query (str): The user's question
            context_documents (List[str]): Retrieved document chunks
            user_role (str): The user's role
            conversation_history (List[dict], optional): Previous conversation messages
            max_tokens (int): Maximum tokens in response
            temperature (float): Sampling temperature (0.0 to 1.0)
           
        Returns:
            str: Generated response from the LLM
        """
        try:
            # Create the context-aware prompt
            context_prompt = self.create_context_prompt(user_query, context_documents, user_role)
           
            # Prepare messages for the chat completion
            messages = [{"role": "system", "content": self.system_prompt}]
           
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
           
            # Add the current query with context
            messages.append({"role": "user", "content": context_prompt})
           
            # Make API call to Groq
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )
           
            return response.choices[0].message.content.strip()
           
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."


    def generate_streaming_response(self,
                                  user_query: str,
                                  context_documents: List[str],
                                  user_role: str,
                                  conversation_history: Optional[List[dict]] = None,
                                  max_tokens: int = 1024,
                                  temperature: float = 0.7):
        """
        Generate a streaming response using Groq LLM (useful for Streamlit).
       
        Args:
            user_query (str): The user's question
            context_documents (List[str]): Retrieved document chunks
            user_role (str): The user's role
            conversation_history (List[dict], optional): Previous conversation messages
            max_tokens (int): Maximum tokens in response
            temperature (float): Sampling temperature (0.0 to 1.0)
           
        Yields:
            str: Chunks of the generated response
        """
        try:
            # Create the context-aware prompt
            context_prompt = self.create_context_prompt(user_query, context_documents, user_role)
           
            # Prepare messages
            messages = [{"role": "system", "content": self.system_prompt}]
           
            if conversation_history:
                messages.extend(conversation_history)
           
            messages.append({"role": "user", "content": context_prompt})
           
            # Make streaming API call
            stream = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True
            )
           
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                   
        except Exception as e:
            print(f"Error in streaming response: {e}")
            yield "I apologize, but I'm having trouble generating a response right now. Please try again later."
