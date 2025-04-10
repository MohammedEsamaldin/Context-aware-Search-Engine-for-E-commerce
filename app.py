import sys
import os

import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.modules.preprocessor.preprocessor import QueryPreprocessor
from src.modules.preprocessor.prompt_builder import PromptBuilder
from src.services.embedding_service import EmbeddingService
from src.services.openai_client import OpenAIClient
from src.models.session import Session
from src.models.product import Product
from src.models.query_log import QueryLog
from src.models.user import UserProfile
from src.models.unified_embedding import UnifiedEmbedding

from src.modules.Dynamic_context_modelling.Session_Graph_Builder import SessionGraphEmbedder, SessionGraphBuilder, \
    UserProfileEmbedder, ContextFusion
from src.modules.retrieval.vector_retrieval_model import ProductSearchEngine
from src.modules.fusion.fuse import fuse_candidates
from src.modules.retrieval.bm25_retriever import BM25CandidateRetriever
from src.modules.Dynamic_context_modelling.Session_Graph_Builder import fusion

# Hard code for now:
user_id = 'U78644'
session_id = 'c6PKuTerJRUqbDoUzmvB'
raw_query = "example query"

# 1. Create user
user = UserProfile.get(user_id=user_id)
print(f"\nUser {user.id} logged in at {user.last_login}.")

# 2. Create session
session = Session.create(user_id=user.id)
print(f"New session {session.id} for user {user.id} started at {session.start_time}")

# Test get session start_time based on
session = Session.load(session_id=session_id)
print(f"\nNew session {session.id} for user {user.id} started at {session.start_time}")

# 3. Get product data from DB
products = Product.load_all()
print("\nSample Product Title:", products[0].title)

##Initialization and creating indices
embedding_service = EmbeddingService()
products_with_embedding = [p for p in products if p.embedding]
engine = ProductSearchEngine(embedding_dim=1536, index_path="products.ann", products=products)
ProductSearchEngine.build_index(products_with_embedding, "products.ann")
retriever = BM25CandidateRetriever(products)


# 4. Fill query inside session
session.add_query(raw_query)
print(len(session.queries))

# 5. Create query log (fill raw + refined query)
query_log = QueryLog.create(
    user_id=user.id,
    session_id=session.id,
    raw_query=raw_query,
    timestamp=session.queries[-1].timestamp,
)
print(f"\nQuery log {query_log.id} added at {query_log.timestamp}")

# 6. Update session graph
# Correct usage: Pass a list of UserProfile objects
user_data_for_emb = [UserProfile.get("U78644")]  # A list containing UserProfile objects

# user_vectors = user_embedder.embed_users(user_data)

# Assuming 'session' is a Session object and 'user_data' is a list of UserProfile objects
graph_builder = SessionGraphBuilder()
session_graphs = graph_builder.build_graph([session])  # Pass session as a list of sessions

session_embedder = SessionGraphEmbedder()
session_vectors = session_embedder.embed_session_graphs([session])  # Again pass as a list

user_embedder = UserProfileEmbedder()
user_vectors = user_embedder.embed_users(user_data_for_emb)  # Pass the correct user data here

fuser = ContextFusion(alpha=0.5)
context_vectors = fuser.fuse(session_vectors, user_vectors)

# 7. Preprocess and Embed Query
gpt_client = OpenAIClient()
preprocessor = QueryPreprocessor(prompt_builder=PromptBuilder(), openai_client=gpt_client)
refined_query = preprocessor.preprocess(query_log, user)
query_log.update_refined_query(refined_query=refined_query["normalized_query"])

##8. Unified Context Vectorisation
alpha = 0.6  # You can tune this weight
target_user_id = user.id
query_vector = query_log.embedding
fused_vector = fuse_vectors(alpha =0.6, user_id = target_user_id, query_vector = query_vector, context_vector = context_vectors)
unified_embedding = UnifiedEmbedding.create(user_id=user.id, session_id=session.id, query=refined_query,
                                            embedding=fused_vector)

## =====
query_embedding = embedding_service.embed_sentences([query_log.refined_query])
query_log.update_embedding(query_embedding[0])

# # 9. BM25 retrieval
bm25_results = retriever.retrieve(query_log.refined_query)

# # 10. Vector search
vector_results = engine.search(query_embedding, k=5)

query_log.update_retrieval(bm25_results=bm25_results, vector_results=vector_results)

# 11. Fusion
fused_result = fuse_candidates(bm25_candidates=bm25_results, vector_candidates=vector_results)

# # 12. Update query log
query_log.add_final_result(fused_result)

# # 13. Close session
session.terminate()
print(f"\nSession {session.id} terminated at {session.end_time}")
