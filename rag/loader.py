from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings

def load_job_description(path: str):
    """Loads a job description from a local text file."""
    with open(path, "r", encoding="utf-8") as file:
        text = file.read()
    return [Document(page_content=text)]

def create_docs_from_text(text: str):
    """Converts a raw string input into a list containing a LangChain Document."""
    return [Document(page_content=text)]

def split_documents(documents):
    """Splits high-level documents into smaller, retrieveable chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    return splitter.split_documents(documents)