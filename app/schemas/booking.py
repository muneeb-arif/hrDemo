from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class BookingCreate(BaseModel):
    """Create booking request schema"""
    booking_type: str = Field(..., description="Service or Test Drive")
    name: str = Field(..., min_length=1, description="Full name")
    phone: str = Field(..., min_length=1, description="Phone number")
    vehicle_model: str = Field(..., min_length=1, description="Vehicle model")
    preferred_date: Optional[date] = Field(None, description="Preferred date")
    natural_language: Optional[str] = Field(None, description="Natural language booking text (alternative to structured fields)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "booking_type": "Service",
                "name": "John Doe",
                "phone": "+1234567890",
                "vehicle_model": "Toyota Camry",
                "preferred_date": "2024-12-25"
            }
        }


class BookingResponse(BaseModel):
    """Booking response schema"""
    id: int
    booking_id: str
    booking_type: str
    name: str
    phone: str
    vehicle_model: str
    preferred_date: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class BookingSearchParams(BaseModel):
    """Booking search parameters"""
    booking_id: Optional[str] = Field(None, description="Search by booking ID")
    phone: Optional[str] = Field(None, description="Search by phone number")
    booking_type: Optional[str] = Field(None, description="Filter by booking type")
