"""
Chat LLM helper — re-exports initialize_llm from chatbot for backward compatibility.
"""

from src.rag.chatbot import initialize_llm

# Alias used by older imports
get_chat_model = initialize_llm
