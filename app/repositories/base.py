from typing import TypeVar, Generic, List, Optional, Type
from app.database import db

ModelType = TypeVar('ModelType')


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def create(self, **kwargs) -> ModelType:
        """Create a new record"""
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get record by ID"""
        return self.model.query.get(id)
    
    def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[ModelType]:
        """Get all records with optional pagination"""
        query = self.model.query
        if limit:
            query = query.limit(limit).offset(offset)
        return query.all()
    
    def update(self, instance: ModelType, **kwargs) -> ModelType:
        """Update an existing record"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        db.session.commit()
        return instance
    
    def delete(self, instance: ModelType) -> bool:
        """Delete a record"""
        db.session.delete(instance)
        db.session.commit()
        return True
    
    def count(self) -> int:
        """Get total count of records"""
        return self.model.query.count()
