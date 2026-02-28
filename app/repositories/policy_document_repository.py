from typing import List
from app.repositories.base import BaseRepository
from app.models.policy_document import PolicyDocument


class PolicyDocumentRepository(BaseRepository[PolicyDocument]):
    """Repository for PolicyDocument model"""
    
    def __init__(self):
        super().__init__(PolicyDocument)
    
    def get_all_content(self) -> str:
        """Get all policy content combined"""
        documents = self.get_all()
        return "\n\n---\n\n".join([doc.content for doc in documents])
    
    def get_recent(self, limit: int = 10) -> List[PolicyDocument]:
        """Get most recently uploaded policies"""
        return self.model.query.order_by(
            PolicyDocument.uploaded_at.desc()
        ).limit(limit).all()
