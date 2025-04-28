from datetime import datetime, timezone
import math
from firebase_admin import firestore
from google.cloud.firestore_v1 import Transaction
from pydantic import ValidationError
from src.models.session import Session, QueryNode, Transition

class TransitionService:
    """Encapsulates transition-specific calculations"""
    
    @staticmethod
    def calculate_transition(prev_query: dict, new_query: QueryNode) -> Transition:
        """Calculate time difference and weight between consecutive queries"""
        prev_time = datetime.fromisoformat(prev_query["timestamp"])
        time_diff = (new_query.timestamp - prev_time).total_seconds() / 60  # minutes
        
        return Transition(
            from_query=prev_query["queryId"],
            to=new_query.queryId,
            count=1,
            timeDifference=time_diff,
            weight=math.exp(-0.1 * time_diff)  # Exponential decay
        )

class SessionManager:
    """Handles session lifecycle and transition management"""
    
    def __init__(self, db: firestore.client):
        self.db = db
        self.transition_service = TransitionService()

    def create_session(self, user_id: str) -> Session:
        """Initialize new session document"""
        session_ref = self.db.collection("Sessions").document()
        session = Session(
            sessionId=session_ref.id,
            userId=user_id,
            startTime=datetime.now(timezone.utc),
            queries=[],
            transitions=[]
        )
        session_ref.set(session.dict(by_alias=True))
        return session

    @firestore.transactional
    def add_query(self, transaction: Transaction, session_ref, query_text: str) -> Session:
        """Transactional update for query addition"""
        doc = session_ref.get(transaction=transaction)
        if not doc.exists:
            raise ValueError("Session not found")
        
        session_data = doc.to_dict()
        if session_data.get("endTime"):
            raise ValueError("Session already terminated")

        # Create new query node
        new_query = QueryNode(
            queryId=f"q{len(session_data['queries']) + 1}",
            text=query_text,
            timestamp=datetime.now(timezone.utc)
        )

        # Update queries
        updated_queries = session_data["queries"] + [new_query.dict(by_alias=True)]
        updated_transitions = session_data["transitions"]

        # Calculate transition if previous queries exist
        if len(session_data["queries"]) > 0:
            prev_query = session_data["queries"][-1]
            transition = self.transition_service.calculate_transition(prev_query, new_query)
            updated_transitions.append(transition.dict(by_alias=True))

        # Perform update
        transaction.update(session_ref, {
            "queries": updated_queries,
            "transitions": updated_transitions
        })
        
        return Session(**{**session_data, 
                        "queries": updated_queries,
                        "transitions": updated_transitions})

    def add_query_to_session(self, session_id: str, query_text: str) -> Session:
        """Public method to add query to session"""
        session_ref = self.db.collection("Sessions").document(session_id)
        return self.add_query(self.db.transaction(), session_ref, query_text)

    def terminate_session(self, session_id: str) -> Session:
        """Mark session as completed"""
        @firestore.transactional
        def _terminate(transaction: Transaction):
            session_ref = self.db.collection("Sessions").document(session_id)
            doc = session_ref.get(transaction=transaction)
            
            if not doc.exists:
                raise ValueError("Session not found")
                
            session_data = doc.to_dict()
            if not session_data.get("endTime"):
                transaction.update(session_ref, {
                    "endTime": datetime.now(timezone.utc)
                })
                
            return Session(**{**session_data, 
                            "endTime": session_data.get("endTime")})
            
        return _terminate(self.db.transaction())

    def get_active_session(self, user_id: str) -> Session | None:
        """Retrieve current active session"""
        query = (
            self.db.collection("Sessions")
            .where("userId", "==", user_id)
            .where("endTime", "==", None)
            .order_by("startTime", direction=firestore.Query.DESCENDING)
            .limit(1)
        )
        
        return next((Session(**doc.to_dict()) for doc in query.stream()), None)