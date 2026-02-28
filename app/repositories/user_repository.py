from typing import Optional, List
from app.repositories.base import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository[User]):
    """Repository for User model"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.model.query.filter_by(username=username).first()
    
    def get_by_role(self, role: str) -> List[User]:
        """Get all users by role"""
        return self.model.query.filter_by(role=role).all()
