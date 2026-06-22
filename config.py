import os
import streamlit as st
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Literal, Optional

# Load local .env file for development
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
        extra = "ignore"

    def __init__(self, **data):
        super().__init__(**data)

        if self.google_api_key is None:
            self.google_api_key = (
                st.secrets.get("GEMINI_API_KEY")
                or os.getenv("GEMINI_API_KEY")
                or os.getenv("GOOGLE_API_KEY")
                or os.getenv("OPENAI_API_KEY")
            )


# Instantiate settings globally
settings = Settings()
