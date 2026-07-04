"""
Configuration loader for FinSum.

Reads API keys, model names, and data paths from a .env file.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Project root is one level above src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")

# --- OpenAI settings ---
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL: str = os.getenv(
    "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
)
OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

# --- Data paths ---
UPLOADS_DIR: Path = PROJECT_ROOT / "data" / "uploads"
CHROMA_DIR: Path = PROJECT_ROOT / "data" / "chroma_db"  # ChromaDB persist path (Step 6)
EXTRACTED_DIR: Path = PROJECT_ROOT / "data" / "extracted"   # pandas CSV/JSON (Step 7)
CACHE_DIR: Path = PROJECT_ROOT / "data" / "cache"           # external news cache (Step 8)

# --- RAG hyperparameters ---
CHUNK_SIZE: int = 1000
CHUNK_OVERLAP: int = 200
TOP_K_RETRIEVAL: int = 4


def validate_config() -> bool:
    """
    Check that required configuration (e.g. API key) is present.

    Returns:
        True if configuration is valid, False otherwise.
    """
    # TODO: Implement validation logic
    pass
