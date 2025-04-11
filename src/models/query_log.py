from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import List, Optional
# from google.cloud.firestore import ArrayUnion

class RetrievalResults(BaseModel):
    bm25: List[str] = Field(..., alias="BM25")
    vector: List[str] = Field(..., alias="Vector")

    class Config:
        populate_by_name = True

class QueryLog(BaseModel):
    id: str = Field(..., alias="logId")
    user_id: str = Field(..., alias="userId")
    session_id: str = Field(..., alias="sessionId")
    raw_query: str = Field(..., alias="rawQuery")
    refined_query: Optional[str] = Field(None, alias="refinedQuery")
    embedding: Optional[List[float]] = Field(None, alias="queryEmbedding")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    retrieval_results: Optional[RetrievalResults] = Field(None, alias="retrievalResults")
    final_result: Optional[List[str]] = Field(default_factory=list, alias="finalResult")

    class Config:
        populate_by_name = True
    
    @classmethod
    def get(cls, log_id: str) -> "QueryLog":
        """Retrieve a QueryLog by its ID from Firestore"""
        from src.db.firebase_client import db
        
        doc_ref = db.collection("QueryLogs").document(log_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise ValueError(f"Query log with ID {log_id} not found")
            
        return cls(**doc.to_dict())
        
    @classmethod
    def create(
        cls,
        user_id: str,
        session_id: str,
        raw_query: str,
        timestamp: datetime,
        refined_query: Optional[str] = None,
        embedding: Optional[List[float]] = None
    ) -> "QueryLog":
        """Create new query log with initial data"""
        from src.db.firebase_client import db
        
        log_ref = db.collection("QueryLogs").document()
        log = cls(
            logId=log_ref.id,
            userId=user_id,
            sessionId=session_id,
            rawQuery=raw_query,
            timestamp=timestamp,
            refined_query=refined_query,
            embedding=embedding
        )
        log.save()
        return log

    @classmethod
    def load(cls, log_id: str) -> "QueryLog":
        """Load query log from DB"""
        from src.db.firebase_client import db
        
        doc = db.collection("QueryLogs").document(log_id).get()
        if not doc.exists:
            raise ValueError(f"Query log {log_id} not found")
        return cls(**doc.to_dict())

    def save(self):
        """Full document update"""
        from src.db.firebase_client import db
        
        db.collection("QueryLogs").document(self.id).set(
            self.model_dump(by_alias=True, exclude_unset=True),
            merge=True
        )
    
    def update_refined_query(self, refined_query: str):
        """Update the refined query"""
        from src.db.firebase_client import db
        
        self.refined_query = refined_query
        db.collection("QueryLogs").document(self.id).update({
            "refinedQuery": refined_query
        })
    
    def update_embedding(self, embedding: List[float]):
        """Update the query embedding"""
        from src.db.firebase_client import db
        
        self.embedding = embedding
        db.collection("QueryLogs").document(self.id).update({
            "queryEmbedding": embedding
        })

    def update_retrieval(self, bm25_results: List[dict], vector_results: List[dict]):
        """Update retrieval results"""
        from src.db.firebase_client import db
        bm25_ids = [item["product_id"] for item in bm25_results]
        vector_ids = [item["product_id"] for item in vector_results]
        
        self.retrieval_results = RetrievalResults(
            bm25=bm25_ids,
            vector=vector_ids
        )
        db.collection("QueryLogs").document(self.id).update({
            "retrievalResults": self.retrieval_results.model_dump(by_alias=True)
        })

    def add_final_result(self, new_result: Optional[List[str]] = None):
        """Append to final results (handles empty/none lists safely)"""
        from src.db.firebase_client import db
        from firebase_admin.firestore import ArrayUnion
        
        # Handle None or empty list
        if not new_result:
            return  # No action needed
        
        # Update local instance
        self.final_results.extend(new_result)
        
        # Update Firestore
        db.collection("QueryLogs").document(self.id).update({
            "finalResult": ArrayUnion(new_result)  # Correct alias
        })