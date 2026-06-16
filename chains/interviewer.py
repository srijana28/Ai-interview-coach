from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from config import settings

# Global dictionary to store session history in memory
session_histories = {}

def get_session_history(session_id: str):
    """Retrieves or creates a chat history list for a specific session."""
    if session_id not in session_histories:
        session_histories[session_id] = ChatMessageHistory()
    return session_histories[session_id]

def create_interviewer_with_history():
    """Creates a Gemini-based interviewer chain equipped with conversational history."""
    
    # We define a ChatPromptTemplate with a MessagesPlaceholder for conversational history
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a professional and friendly AI Interview Coach.
Conducting a {level} {interview_type} interview focused on {focus_area}.

Your job is to ask ONE single question at a time.
Maintain a realistic, professional interviewing persona. Keep your responses focused, and ask clear, challenging but appropriate questions.
Do not evaluate the candidate's answers yet (that is done by another component). Only ask the next question or follow up on their answer."""),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    # Initialize Google Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model=settings.model_name,
        temperature=settings.temperature,
        google_api_key=settings.google_api_key
    )

    # Core LCEL chain
    chain = prompt | llm | StrOutputParser()

    # Wrap the chain with RunnableWithMessageHistory to automatically handle memory injection
    interviewer_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    return interviewer_with_history