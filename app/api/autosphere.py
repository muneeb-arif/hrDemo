from flask import Blueprint, request
from pydantic import ValidationError
from app.middleware.auth import require_auth
from app.services.autosphere_service import AutoSphereService
from app.utils.response import success_response, error_response, validation_error_response
from app.schemas.booking import BookingCreate, BookingResponse, BookingSearchParams
from app.schemas.chat import ChatRequest, ChatResponse

bp = Blueprint('autosphere', __name__)
autosphere_service = AutoSphereService()


@bp.route('/chat', methods=['POST'])
@require_auth
def chat():
    """AI assistant chat endpoint"""
    try:
        chat_data = ChatRequest(**request.json)
    except ValidationError as e:
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return validation_error_response(errors)
    
    try:
        # Convert chat history format if needed
        chat_history = []
        if chat_data.chat_history:
            chat_history = [
                {"role": msg.role, "content": msg.content}
                for msg in chat_data.chat_history
            ]
        
        result = autosphere_service.chat(chat_data.message, chat_history)
        
        response_data = ChatResponse(
            response=result['response'],
            intent=result.get('intent'),
            booking_flow=result.get('booking_flow')
        )
        
        return success_response(data=response_data.dict(), message="Chat response generated")
    
    except Exception as e:
        return error_response(f"Error in chat: {str(e)}", status_code=500)


@bp.route('/bookings', methods=['POST'])
@require_auth
def create_booking():
    """Create a booking (Service or Test Drive)"""
    try:
        booking_data = BookingCreate(**request.json)
    except ValidationError as e:
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return validation_error_response(errors)
    
    try:
        # If natural language provided, use it; otherwise use structured fields
        if booking_data.natural_language:
            # Extract from natural language
            extracted = autosphere_service.extract_booking_details(booking_data.natural_language)
            if not extracted:
                return error_response("Could not extract booking details from natural language", status_code=400)
            
            booking = autosphere_service.create_booking(
                booking_type=booking_data.booking_type,
                name=extracted.get("Name", ""),
                phone=extracted.get("Phone", ""),
                vehicle_model=extracted.get("Vehicle Model", ""),
                preferred_date=extracted.get("Preferred Date")
            )
        else:
            # Use structured fields
            booking = autosphere_service.create_booking(
                booking_type=booking_data.booking_type,
                name=booking_data.name,
                phone=booking_data.phone,
                vehicle_model=booking_data.vehicle_model,
                preferred_date=booking_data.preferred_date.isoformat() if booking_data.preferred_date else None
            )
        
        return success_response(
            data=booking,
            message=f"{booking_data.booking_type} booking confirmed! Booking ID: {booking['booking_id']}"
        )
    
    except Exception as e:
        return error_response(f"Error creating booking: {str(e)}", status_code=500)


@bp.route('/bookings', methods=['GET'])
@require_auth
def search_bookings():
    """Search bookings by filters"""
    try:
        # Get query parameters
        booking_id = request.args.get('booking_id')
        phone = request.args.get('phone')
        booking_type = request.args.get('booking_type')
        
        bookings = autosphere_service.search_bookings(
            booking_id=booking_id,
            phone=phone,
            booking_type=booking_type
        )
        
        return success_response(data=bookings, message=f"Found {len(bookings)} booking(s)")
    
    except Exception as e:
        return error_response(f"Error searching bookings: {str(e)}", status_code=500)


@bp.route('/bookings/<booking_id>', methods=['GET'])
@require_auth
def get_booking(booking_id: str):
    """Get booking by ID"""
    try:
        booking = autosphere_service.get_booking_by_id(booking_id)
        
        if not booking:
            return error_response("Booking not found", status_code=404)
        
        return success_response(data=booking, message="Booking found")
    
    except Exception as e:
        return error_response(f"Error retrieving booking: {str(e)}", status_code=500)
