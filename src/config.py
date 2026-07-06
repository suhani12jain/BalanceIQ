"""
Configuration loader for BalanceIQ.

Reads API keys, model names, and data paths from a .env file.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root is one level above src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

# --- Google Gemini settings ---
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

# Chat model — answers user questions (RAG Step 15)
GEMINI_CHAT_MODEL: str = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")

# Embedding model — local HuggingFace model (RAG Step 5, no API key needed)
EMBEDDING_MODEL_NAME: str = os.getenv(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)

# --- Data paths ---
UPLOADS_DIR: Path = PROJECT_ROOT / "data" / "uploads"
CHROMA_DIR: Path = PROJECT_ROOT / "data" / "chroma_db"
EXTRACTED_DIR: Path = PROJECT_ROOT / "data" / "extracted"
CACHE_DIR: Path = PROJECT_ROOT / "data" / "cache"

# --- RAG hyperparameters ---
CHUNK_SIZE: int = 1000
CHUNK_OVERLAP: int = 200
TOP_K_RETRIEVAL: int = 4


def validate_config() -> bool:
    """
    Check that required configuration (Google API key) is present.

    Returns:
        True if configuration is valid, False otherwise.
    """
    if not GOOGLE_API_KEY or not GOOGLE_API_KEY.strip():
        return False
    if GOOGLE_API_KEY.strip() == "your_google_api_key_here":
        return False
    return True
