from flask import Blueprint, request
from pydantic import ValidationError
from app.schemas.auth import LoginRequest, LoginResponse
from app.services.auth_service import AuthService
from app.utils.response import success_response, error_response, validation_error_response

bp = Blueprint('auth', __name__)
auth_service = AuthService()


@bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and receive JWT token
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        description: Login credentials
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: john_doe
            password:
              type: string
              example: password123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: Login successful
            data:
              type: object
              properties:
                token:
                  type: string
                  example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
                user:
                  type: object
                  properties:
                    id:
                      type: integer
                      example: 1
                    username:
                      type: string
                      example: john_doe
                    role:
                      type: string
                      example: HR Manager
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: Invalid username or password
      422:
        description: Validation error
    """
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
