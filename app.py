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
import sys
import os
import json

from src.modules.preprocessor.preprocessor import QueryPreprocessor
from src.modules.preprocessor.prompt_builder import PromptBuilder
from src.services.openai_client import OpenAIClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.models.session import Session
from src.models.product import Product
from src.models.query_log import QueryLog
from src.models.user import UserProfile
from src.modules.Dynamic_context_modelling.Session_Graph_Builder import SessionGraphEmbedder, SessionGraphBuilder ,UserProfileEmbedder, ContextFusion
from src.modules.retrieval.vector_retrieval_model import ProductSearchEngine
from src.modules.fusion.fuse import fuse_candidates
from src.modules.retrieval.bm25_retriever import BM25CandidateRetriever


## Initialise
# user = UserProfile.create_with_generated_id(
#     name="John Doe",
#     email="john.doe@example.com"
# )
# print(f"Created user with ID: {user.id}") 
# print(f"User {user.id} logged in at {user.last_login}.")
user = UserProfile.get(user_id='U78644')
print(f"\nUser {user.id} logged in at {user.last_login}.")

# 1. Create session
# Input: None
# Output: session (Session object)
# TODO: Implement session creation
# session = Session.create(user_id=user.id)
# print(f"New session {session.id} for user {user.id} started at {session.start_time}")

# Test get session start_time based on 
session_id = 'c6PKuTerJRUqbDoUzmvB'
session = Session.load(session_id=session_id)
print(f"\nNew session {session.id} for user {user.id} started at {session.start_time}")

# NOTE: Riya - this step needs to be initialised first, because a session creation is dependent on user_id
# 2. Get user info from DB
# Input: session.user_id
# Output: user (User object)
# user = None  # TODO: Fetch user info from DB

# 3. Get product data from DB
# Input: None
# Output: products (list of Product objects)
# TODO: Load products from DB
products = Product.load_all()
print("\nSample Product Title:", products[0].title)

# 4. Fill query inside session
# Input: raw_query (str)
# Output: updated session (Session object)
raw_query = "example query"
# # TODO: Add query to session
# if session.end_time is None:
#     session.add_query(raw_query)

# ## Add another query
# session.add_query("another example query")
# Check the last query
# print(len(session.queries))
# if session.queries:
#     latest = session.queries[-1]
#     print(f"Latest query ID: {latest.id}")
#     print(f"Query text: {latest.text}")
#     print(f"Timestamp: {latest.timestamp}")

# print(f"Total transitions: {len(session.transitions)}")
# if session.transitions:
#     latest = session.transitions[-1]
#     print(f"From: {latest.from_query} → To: {latest.to}")
#     print(f"Time between: {latest.time_difference} minutes")

# 5. Create query log (fill raw + refined query)
# Input: raw_query (str)
# Output: query_log (QueryLog object)
# TODO: Create and store query log
# query_log = QueryLog.create(
#     user_id=user.id,
#     session_id=session.id,
#     raw_query=raw_query,
#     timestamp=session.queries[-1].timestamp,
# )
# print(f"\nQuery log {query_log.id} added at {query_log.timestamp}")

# test get log id
dummy_log_id = 'Mo7buBbNabiNWtwWljeR'
query_log = QueryLog.get(dummy_log_id)

# 6. Update session graph
# Input: query_log (QueryLog), session (Session object)
# Output: session_graph (SessionGraph object)

with open("path/session.json") as f:
    session_data = json.load(f)

with open("path/users.json") as f:
    user_data = json.load(f)

# Build session graph (optional if using weights from dataset)
graph_builder = SessionGraphBuilder()
session_graphs = graph_builder.build_graph(session_data)

# Embed session transitions
session_embedder = SessionGraphEmbedder()
session_vectors = session_embedder.embed_session_graphs(session_data)

# Embed user profiles
user_embedder = UserProfileEmbedder()
user_vectors = user_embedder.embed_users(user_data)

# Fuse embeddings into unified context vector per user
fuser = ContextFusion(alpha=0.5)
context_vectors = fuser.fuse(session_vectors, user_vectors)

# Example: Get the context vector for a specific user
target_user_id = "user002"

alpha = 0.6  # You can tune this weight
query_vector = []
if target_user_id in context_vectors:
    context_vec = context_vectors[target_user_id]
    fused_vector = alpha * query_vector + (1 - alpha) * context_vec
    # print(f"Fused vector shape: {fused_vector.shape}")
    print(f"Fused vector preview: {fused_vector[:5]}")
else:
    print(f"User {target_user_id} not found in context vectors.")

session_graph = None  # TODO: Update session graph structure

# 7. Preprocess query
gpt_client = OpenAIClient()
preprocessor = QueryPreprocessor(prompt_builder=PromptBuilder(), openai_client=gpt_client)
refined_query = preprocessor.preprocess(query_log, user)
query_log.update_refined_query(refined_query=refined_query["normalized_query"])

# # 8. Embed refined query
# # Input: query_log.refined_query (str)
# # Output: query_log.embedding (list of floats)
# # TODO: Generate embeddings and update QueryLog
query_embedding = [0, 0, 0, 1]
query_log.update_embedding(embedding=query_embedding)

# 9. BM25 retrieval
# Input: query_log.refined_query (str), products (list of Product)
# Output: bm25_results (list[dict{'product': Product, 'score': float}])
bm25_results = []  # TODO: Apply BM25 ranking

retriever = BM25CandidateRetriever(products)
bm25_results = retriever.retrieve(query_log.refined_query)

# 10. Vector search
# Input: query_log.embedding (list of floats), products (list of Product)
# Output: vector_results (list[dict{'product': Product, 'score': float}])

# Load the index and search
#  requierments :
    # embedding_dim = product_embeddings.shape[1]   this is the dimentions of the product embeddings
    # product_df = the dataframe which contain product id and details
engine = ProductSearchEngine(embedding_dim=embedding_dim, index_path='product_index.ann', product_df=product_df)

vector_results = []  # TODO: Vector-based similarity retrieval

query_log.update_retrieval(bm25_results=bm25_results, vector_results=vector_results)

# 11. Fusion
# Input: bm25_results, vector_results
# Output: fused_results (list[dict{'product': Product, 'score': float}])
fused_result = []  # TODO: Combine result lists with weights/strategy
fused_result = fuse_candidates(bm25_candidates=bm25_results, vector_candidates=vector_results)

# 12. Update query log
# Input: raw_query, refined_query
# Output: updated query_log
# TODO: Log and persist final query log state
query_log.add_final_result(fused_result)

# 13. Close session
# Input: session
# Output: None
# TODO: Finalize and close session

session.terminate()
print(f"\nSession {session.id} terminated at {session.end_time}")
