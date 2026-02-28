from werkzeug.security import check_password_hash
from app.repositories.user_repository import UserRepository
from app.middleware.auth import generate_token


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        self.user_repo = UserRepository()
    
    def login(self, username: str, password: str) -> dict:
        """
        Authenticate user and return JWT token
        Returns: dict with token and user info, or None if authentication fails
        """
        user = self.user_repo.get_by_username(username)
        
        if not user:
            return None
        
        if not check_password_hash(user.password, password):
            return None
        
        # Generate JWT token
        token = generate_token(user.id, user.username, user.role)
        
        return {
            'token': token,
            'user': user.to_dict()
        }
