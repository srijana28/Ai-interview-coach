from operator import itemgetter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from rag.loader import load_job_description, split_documents
from rag.retriever import create_vector_store, create_retriever
from config import settings

def create_question_generator_chain(retriever):
    """Creates an LCEL chain that retrieves context from the job description and generates a question."""
    
    prompt = ChatPromptTemplate.from_template(
        """You are a professional and friendly AI Interview Coach.
Conduct a tailored technical interview based on the following Job Description context:

Job Description Context:
{context}

Topic: {topic}
Difficulty Level: {difficulty}
Previous Questions Asked: {previous_questions}

Generate ONE specific, tailored, and relevant interview question about the topic. Make sure it directly relates to the requirements and skills mentioned in the Job Description context.
Do not repeat any of the previous questions. Keep your response direct, professional, and limited to only asking the question.
"""
    )

    llm = ChatGoogleGenerativeAI(
        model=settings.model_name,
        temperature=settings.temperature,
        google_api_key=settings.google_api_key
    )

    # Core LCEL chain mapping
    # 1. Takes 'topic', queries the retriever, and joins retrieved pages into 'context'
    # 2. Formats all keys into the prompt
    # 3. Passes formatted prompt to Gemini LLM
    # 4. Parses LLM's output as plain text
    chain = (
        {
            "context": itemgetter("topic") | retriever | (lambda docs: "\n\n".join(doc.page_content for doc in docs)),
            "topic": itemgetter("topic"),
            "difficulty": itemgetter("difficulty"),
            "previous_questions": itemgetter("previous_questions")
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain

def setup_interview_rag(job_description_path: str):
    """Orchestrates loading, splitting, indexing, and generating a RAG-based question chain."""
    # 1. Load job description file
    docs = load_job_description(job_description_path)
    
    # 2. Split it into smaller, manageable chunks
    chunks = split_documents(docs)
    
    # 3. Embed chunks and save in Chroma vector database
    vector_store = create_vector_store(chunks)
    
    # 4. Create standard retriever
    retriever = create_retriever(vector_store)
    
    # 5. Create tailorable question generator chain
    question_generator = create_question_generator_chain(retriever)
    
    return {
        "question_generator": question_generator,
        "retriever": retriever
    }