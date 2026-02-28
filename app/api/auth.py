from flask import Blueprint, request
from pydantic import ValidationError
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import AuthService
from app.utils.response import success_response, error_response, validation_error_response

bp = Blueprint('auth', __name__)
auth_service = AuthService()


@bp.route('/login', methods=['POST'])
def login():
    """Login endpoint - returns JWT token"""
    try:
        # Validate request
        login_data = LoginRequest(**request.json)
    except ValidationError as e:
        errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return validation_error_response(errors)
    
    # Authenticate
    result = auth_service.login(login_data.username, login_data.password)
    
    if not result:
        return error_response("Invalid username or password", status_code=401)
    
    # Return token and user info
    response_data = LoginResponse(
        token=result['token'],
        user=result['user']
    )
    
    return success_response(data=response_data.dict(), message="Login successful")
