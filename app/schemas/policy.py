from pydantic import BaseModel, Field
from typing import List


class PolicyUploadRequest(BaseModel):
    """Policy upload request schema"""
    # Note: Files will be handled separately in the endpoint
    pass


class PolicyUploadResponse(BaseModel):
    """Policy upload response schema"""
    message: str = Field(..., description="Upload confirmation message")
    document_count: int = Field(..., description="Number of documents uploaded")
    document_ids: List[int] = Field(..., description="IDs of uploaded documents")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "3 policy document(s) uploaded successfully",
                "document_count": 3,
                "document_ids": [1, 2, 3]
            }
        }


class PolicyQuestionRequest(BaseModel):
    """Policy question request schema"""
    question: str = Field(..., min_length=1, description="Question about HR policies")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the leave policy for employees?"
            }
        }


class PolicyQuestionResponse(BaseModel):
    """Policy question response schema"""
    answer: str = Field(..., description="Answer based on policy documents")
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "According to the HR policy, employees are entitled to 20 days of annual leave..."
            }
        }
