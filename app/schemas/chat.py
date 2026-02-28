from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ChatMessage(BaseModel):
    """Chat message schema"""
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request schema"""
    message: str = Field(..., min_length=1, description="User message")
    chat_history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Previous chat messages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What services do you offer?",
                "chat_history": []
            }
        }


class ChatResponse(BaseModel):
    """Chat response schema"""
    response: str = Field(..., description="AI assistant response")
    intent: Optional[str] = Field(None, description="Detected intent (service_booking, test_drive_booking, general_question)")
    booking_flow: Optional[bool] = Field(None, description="Whether booking flow is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "We offer comprehensive vehicle services including...",
                "intent": "general_question",
                "booking_flow": False
            }
        }
