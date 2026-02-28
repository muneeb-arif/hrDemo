from app.database import db
from datetime import datetime


class Booking(db.Model):
    """Booking model for AutoSphere service/test drive bookings"""
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    booking_type = db.Column(db.String(20), nullable=False)  # Service or Test Drive
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, index=True)
    vehicle_model = db.Column(db.String(100), nullable=False)
    preferred_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Booking {self.booking_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'booking_type': self.booking_type,
            'name': self.name,
            'phone': self.phone,
            'vehicle_model': self.vehicle_model,
            'preferred_date': self.preferred_date.isoformat() if self.preferred_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
