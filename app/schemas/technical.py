from pydantic import BaseModel, Field
from typing import List, Optional


class TechnicalQuestionGenerateRequest(BaseModel):
    """Generate technical questions request schema"""
    job_description: str = Field(..., min_length=1, description="Job description text")
    # Note: CV file will be handled separately in the endpoint
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_description": "We are looking for a senior Python developer..."
            }
        }


class TechnicalQuestionResponse(BaseModel):
    """Technical questions response schema"""
    questions: List[str] = Field(..., description="List of technical questions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    "What is the difference between a list and a tuple in Python?",
                    "Explain how Flask handles routing...",
                    # ... more questions
                ]
            }
        }


class QuestionAnswer(BaseModel):
    """Question and answer pair"""
    question: str = Field(..., description="Technical question")
    answer: str = Field(..., description="Candidate's answer")


class TechnicalAnswerEvaluateRequest(BaseModel):
    """Evaluate technical answers request schema"""
    questions: List[str] = Field(..., min_items=1, description="List of questions")
    answers: List[str] = Field(..., min_items=1, description="List of answers (must match questions length)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "questions": ["Question 1", "Question 2"],
                "answers": ["Answer 1", "Answer 2"]
            }
        }


class QuestionEvaluation(BaseModel):
    """Individual question evaluation"""
    question_number: int = Field(..., description="Question number (1-indexed)")
    question: str = Field(..., description="Question text")
    answer: str = Field(..., description="Candidate's answer")
    score: float = Field(..., ge=0, le=20, description="Score out of 20")
    feedback: str = Field(..., description="Detailed feedback")


class TechnicalAnswerEvaluateResponse(BaseModel):
    """Technical answer evaluation response schema"""
    evaluations: List[QuestionEvaluation] = Field(..., description="Evaluation for each question")
    total_score: float = Field(..., description="Total score")
    max_score: float = Field(..., description="Maximum possible score")
    overall_feedback: str = Field(..., description="Overall evaluation feedback")
    
    class Config:
        json_schema_extra = {
            "example": {
                "evaluations": [],
                "total_score": 75.0,
                "max_score": 100.0,
                "overall_feedback": "The candidate demonstrated good understanding..."
            }
        }
