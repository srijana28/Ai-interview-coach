from pydantic import BaseModel
from typing import List, Optional


class AnswerFeedback(BaseModel):
    """Schema for individual answer evaluations."""
    score: int
    understanding: str
    strengths: List[str]
    improvements: List[str]
    # Adding follow_up_question allows the coach to ask tailored followups
    follow_up_question: Optional[str] = None


class InterviewReport(BaseModel):
    """Schema for the final comprehensive interview report."""
    overall_score: float
    recommendation: str
    summary: str
    strengths: List[str]
    areas_to_improve: List[str]
    suggested_topics_to_study: List[str]