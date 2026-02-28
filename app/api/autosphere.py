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
    """
    AI Assistant Chat
    Chat with AutoSphere AI assistant. Supports intent classification and booking flow.
    ---
    tags:
      - AutoSphere Motors
    consumes:
      - application/json
    produces:
      - application/json
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - message
          properties:
            message:
              type: string
              example: What services do you offer?
            chat_history:
              type: array
              items:
                type: object
                properties:
                  role:
                    type: string
                    example: user
                  content:
                    type: string
                    example: Hello
    responses:
      200:
        description: Chat response generated
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Chat response generated
            data:
              type: object
              properties:
                response:
                  type: string
                  example: We offer comprehensive vehicle services...
                intent:
                  type: string
                  example: general_question
                booking_flow:
                  type: boolean
                  example: false
      401:
        description: Unauthorized
      422:
        description: Validation error
      500:
        description: Server error
    """
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
    """
    Create Booking
    Create a service or test drive booking. Supports both structured fields and natural language.
    ---
    tags:
      - AutoSphere Motors
    consumes:
      - application/json
    produces:
      - application/json
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - booking_type
            - name
            - phone
            - vehicle_model
          properties:
            booking_type:
              type: string
              enum: [Service, Test Drive]
              example: Service
            name:
              type: string
              example: John Doe
            phone:
              type: string
              example: +1234567890
            vehicle_model:
              type: string
              example: Toyota Camry
            preferred_date:
              type: string
              format: date
              example: "2024-12-25"
            natural_language:
              type: string
              example: "I want to book a service for my Toyota Camry on December 25th"
              description: Alternative to structured fields - natural language booking text
    responses:
      200:
        description: Booking created successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Service booking confirmed! Booking ID: AS-20241225-1234"
            data:
              type: object
              properties:
                id:
                  type: integer
                booking_id:
                  type: string
                  example: AS-20241225-1234
                booking_type:
                  type: string
                name:
                  type: string
                phone:
                  type: string
                vehicle_model:
                  type: string
                preferred_date:
                  type: string
                created_at:
                  type: string
      400:
        description: Bad request
      401:
        description: Unauthorized
      422:
        description: Validation error
      500:
        description: Server error
    """
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
    """
    Search Bookings
    Search bookings by booking ID, phone number, or booking type
    ---
    tags:
      - AutoSphere Motors
    produces:
      - application/json
    security:
      - Bearer: []
    parameters:
      - in: query
        name: booking_id
        type: string
        required: false
        description: Search by booking ID
        example: AS-20241225-1234
      - in: query
        name: phone
        type: string
        required: false
        description: Search by phone number
        example: +1234567890
      - in: query
        name: booking_type
        type: string
        enum: [Service, Test Drive]
        required: false
        description: Filter by booking type
    responses:
      200:
        description: Bookings found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Found 2 booking(s)
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  booking_id:
                    type: string
                  booking_type:
                    type: string
                  name:
                    type: string
                  phone:
                    type: string
                  vehicle_model:
                    type: string
                  preferred_date:
                    type: string
                  created_at:
                    type: string
      401:
        description: Unauthorized
      500:
        description: Server error
    """
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
    """
    Get Booking by ID
    Retrieve a specific booking by its booking ID
    ---
    tags:
      - AutoSphere Motors
    produces:
      - application/json
    security:
      - Bearer: []
    parameters:
      - in: path
        name: booking_id
        type: string
        required: true
        description: Booking ID
        example: AS-20241225-1234
    responses:
      200:
        description: Booking found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Booking found
            data:
              type: object
              properties:
                id:
                  type: integer
                booking_id:
                  type: string
                booking_type:
                  type: string
                name:
                  type: string
                phone:
                  type: string
                vehicle_model:
                  type: string
                preferred_date:
                  type: string
                created_at:
                  type: string
      401:
        description: Unauthorized
      404:
        description: Booking not found
      500:
        description: Server error
    """
    try:
        booking = autosphere_service.get_booking_by_id(booking_id)
        
        if not booking:
            return error_response("Booking not found", status_code=404)
        
        return success_response(data=booking, message="Booking found")
    
    except Exception as e:
        return error_response(f"Error retrieving booking: {str(e)}", status_code=500)
