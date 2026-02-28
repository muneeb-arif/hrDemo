import jwt
from functools import wraps
from flask import request, g
from app.config import Config
from app.utils.response import error_response


def generate_token(user_id: int, username: str, role: str) -> str:
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'role': role
    }
    token = jwt.encode(
        payload,
        Config.JWT_SECRET_KEY,
        algorithm=Config.JWT_ALGORITHM
    )
    return token


def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def get_token_from_header() -> str:
    """Extract token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    # Support both "Bearer <token>" and just "<token>"
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == 'bearer':
        return parts[1]
    elif len(parts) == 1:
        return parts[0]
    return None


def require_auth(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            return error_response("Authentication required", status_code=401)
        
        try:
            payload = verify_token(token)
            # Store user info in Flask's g object for use in route handlers
            g.user_id = payload['user_id']
            g.username = payload['username']
            g.role = payload['role']
        except ValueError as e:
            return error_response(str(e), status_code=401)
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_role(required_role: str):
    """Decorator factory to require specific role"""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            if g.role != required_role:
                return error_response(f"Access denied. Required role: {required_role}", status_code=403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
