import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import List, Optional
import math

class QueryNode(BaseModel):
    id: str = Field(..., alias="queryId")
    text: str
    timestamp: datetime

    class Config:
        populate_by_name = True

class Transition(BaseModel):
    from_query: str = Field(..., alias="from")
    to: str
    count: int
    time_difference: float = Field(..., alias="timeDifference")
    weight: float

    class Config:
        populate_by_name = True

class Session(BaseModel):
    id: str = Field(..., alias="sessionId")
    user_id: str = Field(..., alias="userId")
    start_time: datetime = Field(..., alias="startTime")
    end_time: Optional[datetime] = Field(None, alias="endTime")
    queries: List[QueryNode] = []
    transitions: List[Transition] = []

    # Add Pydantic configuration
    class Config:
        populate_by_name = True  # Allows access via both field name and alias
        validate_by_name = True

    @classmethod
    def create(cls, user_id: str) -> "Session":
        from src.db.firebase_client import db
        session_ref = db.collection("Sessions").document()
        
        # Use field names (not aliases) for initialization
        session = cls(
            id=session_ref.id,  # Use field name 'id' not alias 'sessionId'
            user_id=user_id,  # Use field name 'user_id' not alias 'userId'
            start_time=datetime.now(timezone.utc),
            queries=[],
            transitions=[]
        )
        session.save()
        return session
    
    @classmethod
    def load(cls, session_id: str) -> "Session":
        from src.db.firebase_client import db  # Local import
        
        """Load existing session from DB"""
        doc = db.collection("Sessions").document(session_id).get()
        if not doc.exists:
            raise ValueError(f"Session {session_id} not found")
        return cls(**doc.to_dict())

    def save(self):
        from src.db.firebase_client import db
        # Use self.id instead of self.sessionId
        db.collection("Sessions").document(self.id).set(
            self.dict(by_alias=True), 
            merge=True
        )
    
    def add_query(self, query_text: str):
        from src.db.firebase_client import db
        from firebase_admin.firestore import ArrayUnion
        import math

        print(f"\n=== Adding query: {query_text} ===")
        
        # Create new query
        new_query = QueryNode(
            queryId=f"q{len(self.queries)+1}",
            text=query_text,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Update database
        db.collection("Sessions").document(self.id).update({
            "queries": ArrayUnion([new_query.model_dump(by_alias=True)])
        })
        # print(f"Added query to DB: {new_query.model_dump(by_alias=True)}")
        
        # Update local instance
        self.queries.append(new_query)
        # print(f"Local queries count: {len(self.queries)}")

        # Add transition if possible
        if len(self.queries) > 1:
            prev_query = self.queries[-2]
            time_diff = (new_query.timestamp - prev_query.timestamp).total_seconds() / 60
            
            transition = Transition(
                from_query=prev_query.id,
                to=new_query.id,
                count=1,
                time_difference=time_diff,  # Python field name
                weight=math.exp(-0.1 * time_diff)
            )
            
            # print("\nCreating transition with:")
            # print(f"From: {transition.from_query} (alias 'from')")
            # print(f"To: {transition.to}")
            # print(f"Time Difference: {transition.time_difference} (alias 'timeDifference')")
            # print(f"Firestore data: {transition.model_dump(by_alias=True)}")

            # Update database
            db.collection("Sessions").document(self.id).update({
                "transitions": ArrayUnion([transition.model_dump(by_alias=True)])
            })
            # print("Transition added to Firestore")
            
            # Update local instance
            self.transitions.append(transition)
            # print(f"Local transitions count: {len(self.transitions)}")
        # else:
        #     print("No transition created - first query in session")
    
    def terminate(self):
        """Mark session as ended and update Firestore"""
        from src.db.firebase_client import db
        
        # Set end time to current UTC time
        self.end_time = datetime.now(timezone.utc)
        
        # Update both local instance and Firestore
        db.collection("Sessions").document(self.id).update({
            "endTime": self.end_time  # Using Firestore field alias
        })