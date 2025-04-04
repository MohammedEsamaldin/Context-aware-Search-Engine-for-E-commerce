from datetime import datetime
from pydantic import BaseModel, Field
from typing import List

class RetrievalResults(BaseModel):
    bm25: List[str] = Field(..., alias="BM25")
    vector: List[str] = Field(..., alias="Vector")

class QueryLog(BaseModel):
    id: str = Field(..., alias="logId")
    user_id: str = Field(..., alias="userId")
    session_id: str = Field(..., alias="sessionId")
    raw_query: str = Field(..., alias="rawQuery")
    refined_query: str = Field(..., alias="refinedQuery")
    timestamp: datetime
    retrieval_results: RetrievalResults = Field(..., alias="retrievalResults")
    final_results: List[str] = Field(..., alias="finalResults")