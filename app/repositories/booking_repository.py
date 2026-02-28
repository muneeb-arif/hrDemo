from typing import Optional, List
from app.repositories.base import BaseRepository
from app.models.booking import Booking


class BookingRepository(BaseRepository[Booking]):
    """Repository for Booking model"""
    
    def __init__(self):
        super().__init__(Booking)
    
    def get_by_booking_id(self, booking_id: str) -> Optional[Booking]:
        """Get booking by booking_id"""
        return self.model.query.filter_by(booking_id=booking_id).first()
    
    def search(self, booking_id: Optional[str] = None, 
               phone: Optional[str] = None, 
               booking_type: Optional[str] = None) -> List[Booking]:
        """Search bookings by filters"""
        query = self.model.query
        
        if booking_id:
            query = query.filter_by(booking_id=booking_id)
        if phone:
            query = query.filter_by(phone=phone)
        if booking_type:
            query = query.filter_by(booking_type=booking_type)
        
        return query.all()
    
    def get_by_phone(self, phone: str) -> List[Booking]:
        """Get all bookings by phone number"""
        return self.model.query.filter_by(phone=phone).all()
