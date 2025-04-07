from datetime import datetime
from pydantic import BaseModel, Field
from typing import List

class UnifiedEmbedding(BaseModel):
    id: str = Field(..., alias="embeddingId")
    user_id: str = Field(..., alias="userId")
    session_id: str = Field(..., alias="sessionId")
    query: str
    unified_embedding: List[float] = Field(..., alias="unifiedEmbedding")
    timestamp: datetime