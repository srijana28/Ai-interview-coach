from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from config import settings

def create_vector_store(chunks):
    """Creates an in-memory Chroma vector store from document chunks using Gemini embeddings."""
    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model_name,
        google_api_key=settings.google_api_key
    )
    # Creating an in-memory Chroma vector store (no persist_directory specified)
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings
    )
    return vector_store

def create_retriever(vector_store):
    """Creates a LangChain retriever from an initialized vector store."""
    retriever = vector_store.as_retriever(
        search_kwargs={"k": settings.retriever_k}
    )
    return retriever