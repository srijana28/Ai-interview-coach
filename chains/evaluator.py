from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config import settings

# Re-export feedback models so interview_coach.py can import them from this module
from models.feedback import AnswerFeedback, InterviewReport

def create_evaluator_simple():
    """Creates a chain to evaluate a single candidate answer."""
    
    # Initialize the structured parser using the AnswerFeedback model
    parser = JsonOutputParser(pydantic_object=AnswerFeedback)

    prompt = ChatPromptTemplate.from_template(
        """You are a professional technical interviewer.
Evaluate the candidate's answer to the interview question below.

Context:
Candidate Level: {level}
Question Asked: {question}
Candidate's Answer: {answer}

Assess their answer and provide:
1. An integer score out of 10.
2. A brief analysis of their understanding of the topic.
3. Bullets listing strengths.
4. Bullets listing areas for improvement.
5. An optional, tailored follow-up question to probe deeper if necessary (set to null if not needed).

{format_instructions}
"""
    )

    # Initialize Gemini model
    llm = ChatGoogleGenerativeAI(
        model=settings.model_name,
        temperature=0,  # Use 0 temperature for objective evaluations
        google_api_key=settings.google_api_key
    )

    # Combine using LCEL (LangChain Expression Language)
    chain = (
        prompt.partial(format_instructions=parser.get_format_instructions())
        | llm
        | parser
    )

    return chain

def create_report_generator():
    """Creates a chain to compile the entire interview transcript into a final report."""
    
    # Initialize the structured parser using the InterviewReport model
    parser = JsonOutputParser(pydantic_object=InterviewReport)

    prompt = ChatPromptTemplate.from_template(
        """You are a senior hiring manager.
Compile a comprehensive, professional interview feedback report for the candidate based on the complete transcript.

Candidate Context:
Role: {position}
Seniority: {level}
Interview Type: {interview_type}

Scores across all questions: {scores}

Full Interview Transcript:
{transcript}

Synthesize this transcript and compile:
1. An overall score out of 10 (average or weighted score).
2. A formal recommendation (e.g., "Strong Hire", "Hire", "No Hire").
3. A summary of the candidate's performance.
4. Top strengths they demonstrated.
5. Critical areas they need to improve.
6. A list of suggested topics they should study further.

{format_instructions}
"""
    )

    # Initialize Gemini model
    llm = ChatGoogleGenerativeAI(
        model=settings.model_name,
        temperature=0.2,  # Low temperature for analytical report generation
        google_api_key=settings.google_api_key
    )

    # Combine using LCEL
    chain = (
        prompt.partial(format_instructions=parser.get_format_instructions())
        | llm
        | parser
    )

    return chain