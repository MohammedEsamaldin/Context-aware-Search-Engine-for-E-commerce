from datetime import datetime, timezone
import math
from firebase_admin import firestore
from google.cloud.firestore_v1 import Transaction
from pydantic import ValidationError
from src.models.session import Session, QueryNode, Transition

from datetime import datetime, timezone
import math
from firebase_admin import firestore
from google.cloud.firestore_v1 import Transaction
from src.models.session import Session, QueryNode, Transition

class TransitionService:
    """Encapsulates transition-specific calculations"""
    
    @staticmethod
    def calculate_transition(prev_query: dict, new_query: QueryNode) -> Transition:
        """Calculate time difference and weight between consecutive queries"""
        prev_ts = prev_query["timestamp"]
        # If prev_ts is already a datetime object, use it directly;
        # otherwise, assume it's an ISO string and convert it.
        if isinstance(prev_ts, datetime):
            prev_time = prev_ts
        else:
            prev_time = datetime.fromisoformat(prev_ts)
        
        time_diff = (new_query.timestamp - prev_time).total_seconds() / 60  # minutes
        
        return Transition(
            from_query=prev_query["queryId"],
            to=new_query.dict(by_alias=True)["queryId"],
            count=1,
            timeDifference=time_diff,
            weight=math.exp(-0.1 * time_diff)  # Exponential decay
        )
class SessionManager:
    """Handles session lifecycle and transition management."""
    
    def __init__(self, db: firestore.client):
        self.db = db
        self.transition_service = TransitionService()

    def create_session(self, user_id: str, start_time: datetime) -> Session:
        """Initialize new session document"""
        session_ref = self.db.collection("Sessions").document()
        session = Session(
            sessionId=session_ref.id,
            userId=user_id,
            startTime=start_time,
            queries=[],
            transitions=[]
        )
        session_ref.set(session.dict(by_alias=True))
        return session
        

    @staticmethod
    @firestore.transactional
    def _add_query_logic(transaction: Transaction, session_ref, query_text: str) -> Session:
        """
        Core logic to add a query to a session.
        This static method is decorated with @firestore.transactional so that it does not receive self.
        """
        doc = session_ref.get(transaction=transaction)
        if not doc.exists:
            raise ValueError("Session not found")
        
        session_data = doc.to_dict()
        if session_data.get("endTime"):
            raise ValueError("Session already terminated")

        # Create new query node with current UTC time.
        new_query = QueryNode(
            queryId=f"q{len(session_data['queries']) + 1}",
            text=query_text,
            timestamp=datetime.now(timezone.utc)
        )

        # Update queries and transitions.
        updated_queries = session_data["queries"] + [new_query.dict(by_alias=True)]
        updated_transitions = session_data["transitions"]

        if len(session_data["queries"]) > 0:
            prev_query = session_data["queries"][-1]
            transition = TransitionService.calculate_transition(prev_query, new_query)
            updated_transitions.append(transition.dict(by_alias=True))

        transaction.update(session_ref, {
            "queries": updated_queries,
            "transitions": updated_transitions
        })

        session_data["queries"] = updated_queries
        session_data["transitions"] = updated_transitions
        return Session(**session_data)

    def add_query_to_session(self, session_id: str, query_text: str) -> Session:
        """Public method to add a query to a session."""
        session_ref = self.db.collection("Sessions").document(session_id)
        transaction = self.db.transaction()
        # Call the static transactional method
        return SessionManager._add_query_logic(transaction, session_ref, query_text)

    @staticmethod
    @firestore.transactional
    def _terminate_logic(transaction: Transaction, session_ref) -> Session:
        """Core logic for terminating a session."""
        doc = session_ref.get(transaction=transaction)
        if not doc.exists:
            raise ValueError("Session not found")
        session_data = doc.to_dict()
        if not session_data.get("endTime"):
            new_end_time = datetime.now(timezone.utc)
            transaction.update(session_ref, {"endTime": new_end_time.isoformat()})
            session_data["endTime"] = new_end_time.isoformat()
        return Session(**session_data)

    def terminate_session(self, session_id: str) -> Session:
        """Mark session as completed."""
        session_ref = self.db.collection("Sessions").document(session_id)
        transaction = self.db.transaction()
        return SessionManager._terminate_logic(transaction, session_ref)

    def get_active_session(self, user_id: str) -> Session | None:
        """Retrieve the current active session."""
        query = (
            self.db.collection("Sessions")
            .where("userId", "==", user_id)
            .where("endTime", "==", None)
            .order_by("startTime", direction=firestore.Query.DESCENDING)
            .limit(1)
        )
        return next((Session(**doc.to_dict()) for doc in query.stream()), None)

# class TransitionService:
#     """Encapsulates transition-specific calculations"""
    
#     @staticmethod
#     def calculate_transition(prev_query: dict, new_query: QueryNode) -> Transition:
#         """Calculate time difference and weight between consecutive queries"""
#         prev_time = datetime.fromisoformat(prev_query["timestamp"])
#         time_diff = (new_query.timestamp - prev_time).total_seconds() / 60  # minutes
#         return Transition(
#             from_query=prev_query["queryId"],
#             to=new_query.queryId,
#             count=1,
#             timeDifference=time_diff,
#             weight=math.exp(-0.1 * time_diff)  # Exponential decay
#         )

# class SessionManager:
#     """Handles session lifecycle and transition management"""
    
#     def __init__(self, db: firestore.client):
#         self.db = db
#         self.transition_service = TransitionService()

#     def create_session(self, user_id: str, start_time: datetime) -> Session:
#         """Initialize new session document"""
#         session_ref = self.db.collection("Sessions").document()
#         session = Session(
#             sessionId=session_ref.id,
#             userId=user_id,
#             startTime=start_time,
#             queries=[],
#             transitions=[]
#         )
#         session_ref.set(session.dict(by_alias=True))
#         return session

#     def _add_query_logic(self, transaction: Transaction, session_ref, query_text: str) -> Session:
#         """
#         Core logic to add a query to a session.
#         This method is not decorated so that testing and argument passing work correctly.
#         """
#         doc = session_ref.get(transaction=transaction)
#         if not doc.exists:
#             raise ValueError("Session not found")
        
#         session_data = doc.to_dict()
#         if session_data.get("endTime"):
#             raise ValueError("Session already terminated")

#         # Create new query node with current UTC time.
#         new_query = QueryNode(
#             queryId=f"q{len(session_data['queries']) + 1}",
#             text=query_text,
#             timestamp=datetime.now(timezone.utc)
#         )

#         # Update queries and transitions.
#         updated_queries = session_data["queries"] + [new_query.dict(by_alias=True)]
#         updated_transitions = session_data["transitions"]

#         if len(session_data["queries"]) > 0:
#             prev_query = session_data["queries"][-1]
#             transition = self.transition_service.calculate_transition(prev_query, new_query)
#             updated_transitions.append(transition.dict(by_alias=True))

#         transaction.update(session_ref, {
#             "queries": updated_queries,
#             "transitions": updated_transitions
#         })

#         # Update local session_data and return a new Session instance.
#         session_data["queries"] = updated_queries
#         session_data["transitions"] = updated_transitions
#         return Session(**session_data)

#     @firestore.transactional
#     def add_query(self, transaction: Transaction, session_ref, query_text: str) -> Session:
#         """Transactionally adds a query to the session using the helper logic."""
#         return self._add_query_logic(transaction, session_ref, query_text)

#     def add_query_to_session(self, session_id: str, query_text: str) -> Session:
#         """Public method to add query to session"""
#         session_ref = self.db.collection("Sessions").document(session_id)
#         return self.add_query(self.db.transaction(), session_ref, query_text)

#     def terminate_session(self, session_id: str) -> Session:
#         """Mark session as completed"""
#         @firestore.transactional
#         def _terminate(transaction: Transaction):
#             session_ref = self.db.collection("Sessions").document(session_id)
#             doc = session_ref.get(transaction=transaction)
            
#             if not doc.exists:
#                 raise ValueError("Session not found")
                
#             session_data = doc.to_dict()
#             if not session_data.get("endTime"):
#                 new_end_time = datetime.now(timezone.utc)
#                 transaction.update(session_ref, {
#                     "endTime": new_end_time.isoformat()
#                 })
#                 session_data["endTime"] = new_end_time.isoformat()
#             return Session(**session_data)
            
#         return _terminate(self.db.transaction())

#     def get_active_session(self, user_id: str) -> Session | None:
#         """Retrieve current active session"""
#         query = (
#             self.db.collection("Sessions")
#             .where("userId", "==", user_id)
#             .where("endTime", "==", None)
#             .order_by("startTime", direction=firestore.Query.DESCENDING)
#             .limit(1)
#         )
#         return next((Session(**doc.to_dict()) for doc in query.stream()), None)

# class TransitionService:
#     """Encapsulates transition-specific calculations"""
    
#     @staticmethod
#     def calculate_transition(prev_query: dict, new_query: QueryNode) -> dict:
#         """Calculate time difference and weight between consecutive queries"""
#         # Convert Firestore timestamp to datetime if necessary
#         prev_time = prev_query["timestamp"]
#         if isinstance(prev_time, str):
#             prev_time = datetime.fromisoformat(prev_time)
        
#         time_diff = (new_query.timestamp - prev_time).total_seconds() / 60
        
#         return Transition(
#             from_query=prev_query["queryId"],
#             to=new_query.queryId,
#             count=1,
#             timeDifference=time_diff,
#             weight=math.exp(-0.1 * time_diff)
#         ).dict(by_alias=True)

# class SessionManager:
#     """Handles session lifecycle and transition management"""
    
#     def __init__(self, db: firestore.client):
#         self.db = db
#         self.transition_service = TransitionService()

#     def create_session(self, user_id: str, start_time: datetime) -> Session:
#         """Initialize new session document"""
#         session_ref = self.db.collection("Sessions").document()
#         session = Session(
#             sessionId=session_ref.id,
#             userId=user_id,
#             startTime=start_time,
#             queries=[],
#             transitions=[]
#         )
#         session_ref.set(session.dict(by_alias=True))
#         return session

#     @firestore.transactional
#     def add_query(self, transaction: Transaction, session_ref, query_text: str) -> Session:
#         doc = session_ref.get(transaction=transaction)
#         if not doc.exists:
#             raise ValueError("Session not found")
        
#         session_data = doc.to_dict()
#         if session_data.get("endTime"):
#             raise ValueError("Session already terminated")

#         # Create new query node with proper datetime
#         new_query = QueryNode(
#             queryId=f"q{len(session_data['queries']) + 1}",
#             text=query_text,
#             timestamp=datetime.now(timezone.utc)
#         )

#         # Prepare Firestore data
#         query_data = new_query.dict(by_alias=True)
#         query_data["timestamp"] = new_query.timestamp  # Ensure datetime object
        
#         updated_queries = session_data["queries"] + [query_data]
#         updated_transitions = session_data["transitions"]

#         if session_data["queries"]:
#             prev_query = session_data["queries"][-1]
#             transition = self.transition_service.calculate_transition(prev_query, new_query)
#             updated_transitions.append(transition)

#         transaction.update(session_ref, {
#             "queries": updated_queries,
#             "transitions": updated_transitions
#         })
        
#         return Session.parse_obj({
#             **session_data,
#             "queries": updated_queries,
#             "transitions": updated_transitions
#         })


#     def add_query_to_session(self, session_id: str, query_text: str) -> Session:
#         """Public method to add query to session"""
#         session_ref = self.db.collection("Sessions").document(session_id)
#         transaction = self.db.transaction()
#         return self.add_query(transaction, session_ref, query_text)

#     def terminate_session(self, session_id: str) -> Session:
#         """Mark session as completed"""
#         @firestore.transactional
#         def _terminate(transaction: Transaction):
#             session_ref = self.db.collection("Sessions").document(session_id)
#             doc = session_ref.get(transaction=transaction)
            
#             if not doc.exists:
#                 raise ValueError("Session not found")
                
#             session_data = doc.to_dict()
#             if not session_data.get("endTime"):
#                 new_end_time = datetime.now(timezone.utc)
#                 transaction.update(session_ref, {
#                     "endTime": new_end_time.isoformat()
#                 })
#                 session_data["endTime"] = new_end_time.isoformat()
#             return Session(**session_data)
            
#         return _terminate(self.db.transaction())

#     def get_active_session(self, user_id: str) -> Session | None:
#         """Retrieve current active session"""
#         query = (
#             self.db.collection("Sessions")
#             .where("userId", "==", user_id)
#             .where("endTime", "==", None)
#             .order_by("startTime", direction=firestore.Query.DESCENDING)
#             .limit(1)
#         )
#         return next((Session(**doc.to_dict()) for doc in query.stream()), None)
