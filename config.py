import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Literal, Optional

# Explicitly load .env so Streamlit and the app both pick up keys reliably.
load_dotenv()


class Settings(BaseSettings):
    # API Keys
    google_api_key: Optional[str] = None

    # Model settings
    model_name: str = "gemini-2.5-flash"
    embedding_model_name: str = "models/embedding-001"
    temperature: float = 0.7
    max_tokens: int = 1000

    # Interview settings
    max_questions: int = 5
    default_difficulty: Literal["easy", "medium", "hard"] = "medium"

    # RAG settings
    chunk_size: int = 500
    chunk_overlap: int = 50
    retriever_k: int = 3

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore other env variables in the system

    def __init__(self, **data):
    def _resolve_google_api_key(self) -> Optional[str]:
        """
        Resolve the API key in this order:
        1. Streamlit Cloud secrets (st.secrets)
        2. Local .env / environment variables
        """
        # Streamlit Cloud
        try:
            secrets = st.secrets
            for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY"):
                value = secrets.get(key)
                if value:
                    return str(value)
        except Exception:
            pass

        # Local development
        return (
            os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )

    # Interview settings
    max_questions: int = 5
    default_difficulty: Literal["easy", "medium", "hard"] = "medium"

    # RAG settings
    chunk_size: int = 500
    chunk_overlap: int = 50
    retriever_k: int = 3

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore other env variables in the system

# Instantiate settings globally
settings = Settings()
