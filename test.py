
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from datetime import datetime, timezone
import numpy as np

from src.models.user import UserProfile
from src.models.session import Session
from src.models.product import Product
from src.models.query_log import QueryLog
from src.models.unified_embedding import UnifiedEmbedding

from src.services.embedding_service import EmbeddingService
from src.services.openai_client import OpenAIClient
from src.modules.preprocessor.preprocessor import QueryPreprocessor
from src.modules.preprocessor.prompt_builder import PromptBuilder
from src.modules.Dynamic_context_modelling.Session_Graph_Builder \
    import ContextEmbedder #SessionGraphEmbedder, SessionGraphBuilder, ContextFusion,
# from src.modules.Dynamic_context_modelling.fusion import fuse_vectors
from src.modules.Dynamic_context_modelling.fusion import VectorFuser

from src.modules.retrieval.bm25_retriever import BM25CandidateRetriever
from src.modules.retrieval.vector_retrieval_model import ProductSearchEngine
from src.modules.fusion.fuse import fuse_candidates

print("*"*30, "TESTING", "*"*30)

# products = Product.load_all()
# product_lookup = {prod.id: prod.title for prod in products}

# search_engine = ProductSearchEngine(
#     embedding_dim=1536,
#     index_path="products.ann",
#     products=products
# )            
embedding_service = EmbeddingService()

# bm25_retriever = BM25CandidateRetriever(products)

## Test embedding service embed_single_user_and_session
user_id = 'U78644'
session_id = 'ScFPGizvQ0L5M2rTFLMn'
session = Session.load(session_id)
user = UserProfile.get(user_id)

embedding_service = EmbeddingService()
context_embedder = ContextEmbedder(embedding_service, alpha=0.5)
fused_vector = context_embedder.embed_single_user_and_session(user, session, fuse=True)
print(f"Fused vector for user {user_id} and session {session_id}: {fused_vector}")

# ## Get Session ID
# session_id = 'r9vm7zllqMbyTzadgRAP' #input("Enter existing session ID: ").strip()
# first_log_id = 'T8E86CgNFBTE01dVY4J1'
# second_log_id = 'UVyhe49swk9HZGCkyhzN'

# ## Check if exists and intialise session object
# session = Session.load(session_id)
# print("Session:", session.id)

# ## Get user_id from session and initialise user object
# user = UserProfile.get(session.user_id)
# print(f"\nUser {user.id} - {user.name}")

# ## === Submit query -> add to session, query_log
# raw_query = session.queries[-1].text  #input("Enter a query: ").strip() #
# print("\nRaw Query: ", raw_query)
# # session.add_query(raw_query)
# # if session.queries:
# #     timestamp = session.queries[-1].timestamp
# # else:
# #     timestamp = datetime.now(timezone.utc)
# #     print("Warning: No queries in session, using current time")
# # query_log = QueryLog.create(
# #     user_id=user.id,
# #     session_id=session.id,
# #     raw_query=raw_query,
# #     timestamp=timestamp
# # )
# query_log = QueryLog.get(second_log_id)
# print(f"\nQuery log {query_log.id} added at {query_log.timestamp}")

# ## === Query Preprocessing
# # preprocessor = QueryPreprocessor(
# #     prompt_builder=PromptBuilder(),
# #     openai_client=OpenAIClient()
# # )
# # refined_query = preprocessor.preprocess(query_log, user)
# # query_log.update_refined_query(refined_query["normalized_query"])
# refined_query = query_log.refined_query
# print(f"\nRefined query: {refined_query}")

# ## === Embed refined query
# # query_embeddings = embedding_service.embed_sentences([query_log.refined_query])
# # query_embedding = query_embeddings[0]
# # if hasattr(query_embedding, 'tolist'):
# #     query_embedding = query_embedding.tolist()
# # query_log.update_embedding(query_embedding)
# query_embedding = query_log.embedding
# # print("Query Embedding:", query_embedding)

# ## === START: Unified Context Query ===
# ## = Session Context Embedding
# # graph_builder = SessionGraphBuilder()
# # session_graphs = graph_builder.build_graph([session])  # Pass session as a list of sessions

# session_embedder = SessionGraphEmbedder()
# session_vectors = session_embedder.embed_session_graphs([session])
# # print(session_vectors)  ## out: dict -> {user_id: array([], dtype=float32)}

# user_vectors = {user.id: np.array(user.embedding, dtype=np.float32)}  # dict -> {user_id: array([], dtype=float32)}
# # print(user_vectors)

# ## = Fused Context Embedding (Session + User)
# uid = user.id
# if uid not in session_vectors or len(session_vectors[uid]) == 0:
#     print(f"Warning: No session vector found for user {uid}. Using user vector only.")
#     context_vectors = user_vectors[uid]
# else:
#     # Align dimensions of session and user vectors
#     s_vec = session_vectors[uid]
#     u_vec = user_vectors[uid]
#     common_dim = min(len(s_vec), len(u_vec))
#     s_vec_aligned = s_vec[:common_dim]
#     u_vec_aligned = u_vec[:common_dim]
#     session_vectors[uid] = s_vec_aligned
#     user_vectors[uid] = u_vec_aligned
    
#     # Fuse session and user embeddings
#     fuser = ContextFusion(alpha=0.5)
#     context_vectors = fuser.fuse(session_vectors, user_vectors)
# # print("Context Embedding:", context_vectors)

# ## = Unified Embedding (Fused + Query)
# alpha = 0.6  # You can tune this weight
# fused_vector = fuse_vectors(alpha, user.id, query_embedding, context_vectors)
# print("Unified Embedding:", fused_vector)

# ## === END: Unified Context Query ===

# ## === START: Dual Retrieval ===
# K = 3  # Number of top results to retrieve
# # ## = BM25
# bm25_results = bm25_retriever.retrieve(query_log.refined_query, K)  ## {product_id: score}
# print(f"\nBM25 Results: {bm25_results}")

# # ## = Vector
# vector_results = search_engine.search(fused_vector, K)  ## {product_id: score}
# print(f"\nVector Results: {vector_results}")
# # ## === END: Dual Retrieval ===

# # ## === Result Fusion
# if len(bm25_results) == 0 and len(vector_results) == 0:
#     raise ValueError("Neither BM25 nor Vector results are available.")
# elif len(bm25_results) == 0:
#     fused_result = vector_results
# elif len(vector_results) == 0:
#     fused_result = bm25_results
# else:
#     fused_result = fuse_candidates(bm25_results, vector_results, beta=0.5, top_n=5)
# print(f"\nFused Results: {fused_result}")

# # ## === Final logging
# # # Save list of product titles to update to query log later
# # final_products = [
# #     product_lookup.get(pid["product_id"] if isinstance(pid, dict) else pid, "Unknown Title")
# #     for pid in fused_result
# # ]
# # bm25_products = [
# #     product_lookup.get(pid["product_id"] if isinstance(pid, dict) else pid, "Unknown Title")
# #     for pid in bm25_results
# # ]
# # vector_products = [
# #     product_lookup.get(pid["product_id"] if isinstance(pid, dict) else pid, "Unknown Title")
# #     for pid in vector_results
# # ]

# # # query_log.update_results(
# # #     bm25_results=bm25_products,
# # #     vector_results=vector_products,
# # #     final_results=final_products
# # # )
# # for i, product in enumerate(final_products):
# #             print(f"{i+1}. {product.title()}")
