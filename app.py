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

# from src.modules.retrieval.bm25_retriever import BM25CandidateRetriever
# # Test query
# query = "noise cancelling bluetooth headphones"

# # Run retrieval
# retriever = BM25CandidateRetriever(products)
# results = retriever.retrieve(query)

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
