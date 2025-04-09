<<<<<<< Updated upstream
# import os
# from fastapi import FastAPI, HTTPException
# import firebase_admin
# from firebase_admin import credentials, firestore

# # Import your models from src/models using absolute imports.
# from src.models import UserProfile, Preferences, Product, QueryLog, RetrievalResults, Session, QueryNode, Transition, UnifiedEmbedding

# # Initialize Firebase Admin using your service account file.
# # Replace "path/to/serviceAccountKey.json" with the actual path.
# cred_path = "config/firebase_cart_admin.json"
# if not firebase_admin._apps:
#     cred = credentials.Certificate(cred_path)
#     firebase_admin.initialize_app(cred)
# db = firestore.client()
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone
from src.db.firebase_client import db
from src.modules.session.session_manager import SessionManager
from src.models import UserProfile, Preferences, Product, QueryLog, RetrievalResults, Session, QueryNode, Transition, UnifiedEmbedding

app = FastAPI(title="Context-Aware Search Engine Backend")

# Instantiate the session manager with the Firestore client
session_manager = SessionManager(db)

# --- Session Endpoints ---
@app.post("/sessions", response_model=Session)
def create_session(user_id: str):
    """
    Create a new session for the specified user.
    """
    try:
        new_session = session_manager.create_session(user_id, datetime.now(timezone.utc))
        return new_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/{session_id}/query", response_model=Session)
def add_query_to_session(session_id: str, query_text: str):
    """
    Add a query to the session and update transitions.
    """
    try:
        updated_session = session_manager.add_query_to_session(session_id, query_text)
        return updated_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/{session_id}/terminate", response_model=Session)
def terminate_session(session_id: str):
    """
    Terminate a session.
    """
    try:
        terminated_session = session_manager.terminate_session(session_id)
        return terminated_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/active/{user_id}", response_model=Session)
def get_active_session(user_id: str):
    """
    Retrieve the current active session for a given user.
    """
    try:
        active_session = session_manager.get_active_session(user_id)
        if active_session is None:
            raise HTTPException(status_code=404, detail="Active session not found")
        return active_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- User Profile Endpoints ---
@app.post("/users", response_model=UserProfile)
def create_user(user: UserProfile):
    doc_ref = db.collection("users").document(user.id)
    doc_ref.set(user.dict(by_alias=True))
    return user
=======
"""
Main pipeline for the IR system.

Each step is marked by its number and includes:
- Input types
- Output types
- TODO placeholder for implementation

# NOTE for @riya:
# Please make sure to add the `embedding` attribute to the relevant QueryLog class so it can store the vector here.

Team members: Please stick to the input/output contracts and update your section.
"""

# 1. Create session
# Input: None
# Output: session (Session object)
session = None  # TODO: Implement session creation
>>>>>>> Stashed changes

# 2. Get user info from DB
# Input: session.user_id
# Output: user (User object)
user = None  # TODO: Fetch user info from DB

# 3. Get product data from DB
# Input: None
# Output: products (list of Product objects)
products = []  # TODO: Load products from DB

# 4. Fill query inside session
# Input: raw_query (str)
# Output: updated session (Session object)
raw_query = "example query"
# TODO: Add query to session

# 5. Create query log (fill raw + refined query)
# Input: raw_query (str)
# Output: query_log (QueryLog object)
query_log = None  # TODO: Create and store query log

# 6. Update session graph
# Input: query_log (QueryLog), session (Session object)
# Output: session_graph (SessionGraph object)
session_graph = None  # TODO: Update session graph structure

# 7. Preprocess query
# Input: query_log.raw_query (str)
# Output: query_log.refined_query (str)
# TODO: Clean and refine query, update QueryLog

# 8. Embed refined query
# Input: query_log.refined_query (str)
# Output: query_log.embedding (list of floats)
# TODO: Generate embeddings and update QueryLog

# 9. BM25 retrieval
# Input: query_log.refined_query (str), products (list of Product)
# Output: bm25_results (list[dict{'product': Product, 'score': float}])
bm25_results = []  # TODO: Apply BM25 ranking

# 10. Vector search
# Input: query_log.embedding (list of floats), products (list of Product)
# Output: vector_results (list[dict{'product': Product, 'score': float}])
vector_results = []  # TODO: Vector-based similarity retrieval

# 11. Fusion
# Input: bm25_results, vector_results
# Output: fused_results (list[dict{'product': Product, 'score': float}])
fused_results = []  # TODO: Combine result lists with weights/strategy

# 12. Update query log
# Input: raw_query, refined_query
# Output: updated query_log
# TODO: Log and persist final query log state

# 13. Close session
# Input: session
# Output: None
# TODO: Finalize and close session
