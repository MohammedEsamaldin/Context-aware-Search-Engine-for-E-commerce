import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import List

class UnifiedEmbedding(BaseModel):
    id: str = Field(..., alias="embeddingId")
    user_id: str = Field(..., alias="userId")
    session_id: str = Field(..., alias="sessionId")
    query: str
    embedding: List[float] = Field(..., alias="unifiedEmbedding")
    timestamp: datetime

    class Config:
        populate_by_name = True
        validate_by_name = True

    @classmethod
    def create(cls, user_id: str, session_id: str, query: str, embedding: List[float]) -> "UnifiedEmbedding":
        from src.db.firebase_client import db
        embed_ref = db.collection("UnifiedEmbedding").document()
        
        # Use field names (not aliases) for initialization
        embedding = cls(
            id=embed_ref.id,
            user_id=user_id,
            session_id=session_id,
            query=query,
            embedding=embedding,
            timestamp=datetime.now(timezone.utc)
        )
        embedding.save()
        return embedding