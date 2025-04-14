
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pydantic import ValidationError
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
from src.modules.Dynamic_context_modelling.Session_Graph_Builder import ContextEmbedder ,SessionGraphBuilder
from src.modules.Dynamic_context_modelling.fusion import VectorFuser

from src.modules.retrieval.bm25_retriever import BM25CandidateRetriever
from src.modules.retrieval.vector_retrieval_model import ProductSearchEngine
from src.modules.fusion.fuse import fuse_candidates


class CartSearchEngine:
    def __init__(self):
        """
        Parameters:
        - current_user: UserProfile object for the current user
        - current_session: Session object for the current session
        - search_components: Dictionary containing initialized search components
        - context_alpha: Float for session vs user context balance
        - context_fusion_beta: Float for query vs context balance for unified embedding
        - search_K: Integer for number of results to retrieve
        - retrieval_fusion_beta: Float for fusion weight for BM25 and vector results
        """
        self.current_user = None
        self.current_session = None
        self.search_components = None
        self.context_alpha = 0.7            
        self.context_fusion_beta = 0.8      
        self.search_K = 10                  
        self.retrieval_fusion_beta = 0.5
    
    def run(self):
        print("🛒 CART Search Engine")
        user_id = input("Please enter your user_id: ").strip().upper()
        
        if self.verify_user(user_id):
            UserProfile.update_last_login(self.current_user)
            self.create_session()
            self.show_main_menu()
        else:
            print("User not found. Exiting...")
    
    def verify_user(self, user_id):
        try:
            # Get returns None instead of raising DoesNotExist
            self.current_user = UserProfile.get(user_id.upper())
            return self.current_user is not None
        except ValidationError as e:
            print(f"Invalid user data: {str(e)}")
            return False
        
    def create_session(self):
        self.current_session = Session.create(user_id=self.current_user.id)
        print(f"\nNew session {self.current_session.id} "
              f"for user {self.current_user.id} "
              f"started at {self.current_session.start_time}")
    
    def terminate_session(self):
        self.current_session.terminate()
        print(f"\nSession terminated at {self.current_session.end_time} with {len(self.current_session.queries)} queries.")
    
    def show_main_menu(self):
        try:
            while True:
                print(f"\n⭐ Main Menu - Welcome {self.current_user.name} ({self.current_user.id})!")
                print("\nWhat would you like to do?")
                print("1️⃣: Search")
                print("2️⃣: Log out")
                
                choice = input("Enter your choice (1 or 2): ").strip()
                
                if choice == "1":
                    self.search_loop()
                elif choice == "2":
                    self.terminate_session()
                    print(f"Goodbye, {self.current_user.name}! 👋")
                    return
                else:
                    print("Invalid choice. Please try again.")
        finally:
            if self.current_session and not self.current_session.end_time:
                self.terminate_session()
    
    def search_loop(self):        
        try:
            ## Initialise search components once entering search
            self._initialize_search_components()

            while True:
                query = input("\nSubmit your query: ").strip()
                
                # Add search implementation here
                self.perform_search(query)
                print("\nSearch completed!")
                print("-"*30)
                
                print("\nWhat would you like to do?")
                print("1️⃣: Submit another query")
                print("2️⃣: Logout")
                
                choice = input("Enter your choice (1 or 2): ").strip()
                
                if choice == "2":
                    self.terminate_session()
                    print(f"Goodbye, {self.current_user.name} 😃👋!\n")
                    exit()

        finally:
            if self.current_session and not self.current_session.end_time:
                self.terminate_session()

    def perform_search(self, raw_query):
        """Main search pipeline executor"""
        ## 1. Query logging
        query_log = self._create_query_log(raw_query)
        print(f"\nQuery log {query_log.id} added at {query_log.timestamp}")
        print(f"# Queries in Session: {len(self.current_session.queries)}")

        ## 2. Query pre-processing
        refined_query = self._preprocess_query(query_log, self.current_user)
        # print(f"Refined search query: {query_log.refined_query}")

        ## 3. Embedding generation
        query_embedding = self._generate_query_embeddings(query_log)
        # print(f"Query Vector: {query_log.embedding}")

        ## 4. Session context processing (Session + User)
        context_vector = self._build_session_context(alpha=self.context_alpha)
        # print(f"Context Vector: {context_vector}")

        ## 5. Unified Context Embedding (context + query embeddings)
        unified_vector = self._generate_unified_embedding(query_embedding, context_vector, alpha=self.context_fusion_beta)
        # print(f"Unified Context Vector: {unified_vector}")

        ## 6. Dual retrieval
        bm25_results, vector_results = self._retrieve_results(refined_query, unified_vector)

        ## 7. Result fusion
        fused_results = self._fuse_search_results(bm25_results, vector_results, beta=self.retrieval_fusion_beta, top_n=self.search_K)

        ## 8. Final logging
        self._display_and_log_results(query_log, bm25_results, vector_results, fused_results, self.product_lookup)

        # return bm25_results, vector_results, fused_results

    def _initialize_search_components(self):
        """One-time initialization of search resources"""
        if not hasattr(self, '_search_initialized'):
            self.products = Product.load_all()
            self.product_lookup = {product.id: product for product in self.products}
            self.search_engine = ProductSearchEngine(
                embedding_dim=1536,
                index_path="products.ann",
                products=self.products
            )            
            self.embedding_service = EmbeddingService()
            self.bm25_retriever = BM25CandidateRetriever(self.products)
            self._search_initialized = True
    
    def _create_query_log(self, raw_query, query=None):
        """Create query log entry with safety checks"""
        # Add query to session first
        self.current_session.add_query(raw_query)
        
        # Get timestamp safely
        if self.current_session.queries:
            timestamp = self.current_session.queries[-1].timestamp
        else:
            timestamp = datetime.now(timezone.utc)
            print("Warning: No queries in session, using current time")

        return QueryLog.create(
            user_id=self.current_user.id,
            session_id=self.current_session.id,
            raw_query=raw_query,
            timestamp=timestamp
        )

    def _preprocess_query(self, query_log, user):
        """Handle query refinement and normalization"""
        preprocessor = QueryPreprocessor(
            prompt_builder=PromptBuilder(),
            openai_client=OpenAIClient()
        )
        refined_query = preprocessor.preprocess(query_log, user)
        normalized_query = refined_query.get("normalized_query")
        query_log.update_refined_query(normalized_query)
        
        return normalized_query
    
    def _generate_query_embeddings(self, query_log):
        """Generate and log query embeddings with validation"""
        try:
            # 1. Get embeddings from service
            embeddings = self.embedding_service.embed_sentences([query_log.refined_query])
            
            # 2. Validate response structure
            if not embeddings or len(embeddings) == 0:
                raise ValueError("Empty embedding response from service")
                
            if len(embeddings) > 1:
                print(f"Warning: Received {len(embeddings)} embeddings, using first")
                
            # 3. Handle numpy arrays
            embedding = embeddings[0]
            if hasattr(embedding, 'tolist'):
                embedding = embedding.tolist()
                
            # 4. Type validation
            if not isinstance(embedding, list) or not all(isinstance(x, float) for x in embedding):
                raise TypeError("Invalid embedding format - expected list of floats")
                
            # 5. Update and return
            query_log.update_embedding(embedding)
            return embedding
            
        except Exception as e:
            print(f"Embedding generation failed: {str(e)}")
            if 'embedding' in locals():
                print(f"Problematic embedding: {embedding[:3]}...")  # First 3 elements
            return []

    def _build_session_context(self, alpha=0.5):
        """Build session-aware context vector using session graph and user embeddings."""
        try:
            uid = self.current_user.id
            user_pro = self.current_user[0]  
            embedding_service = EmbeddingService()
            context_embedder = ContextEmbedder(embedding_service=embedding_service, alpha=self.context_alpha)
            # graph_builder = SessionGraphBuilder()
            # session_graphs = graph_builder.build_graph([self.current_session])

            # Unified embedding (fused session + profile vector for one user)
            context_vectors = context_embedder.embed_single_user_and_session(
                user=user_pro,
                session=self.current_session,
                fuse=True
            )
            print(context_vectors)
            return context_vectors.get(uid)
        
            # # Generate session graph embeddings
            # session_embedder = SessionGraphEmbedder()
            # session_vectors = session_embedder.embed_session_graphs([self.current_session])
            # # print("Session Embedding:", session_vectors)  # Expected: dict -> {user_id: array([...], dtype=float32)}
            
            # # Convert user's embedding list to a NumPy array with dtype=float32
            # user_vectors = {self.current_user.id: np.array(self.current_user.embedding, dtype=np.float32)}
            # # print("User Embedding:", user_vectors)
            
            # 
            # # If first query submission (no session context), use only user embedding.
            # if uid not in session_vectors or len(session_vectors[uid]) == 0:
            #     print("No session context available, using only user context.")
            #     return { uid: user_vectors.get(uid, []) } # return user_vectors.get(uid, [])
            # else:
            #     # Align dimensions of session and user vectors for current user
            #     s_vec = session_vectors[uid]
            #     u_vec = user_vectors[uid]
            #     common_dim = min(s_vec.shape[0], u_vec.shape[0])
            #     s_vec_aligned = s_vec[:common_dim]
            #     u_vec_aligned = u_vec[:common_dim]
            #     session_vectors[uid] = s_vec_aligned
            #     user_vectors[uid] = u_vec_aligned
                
            #     # Fuse session and user embeddings
            #     fuser = ContextFusion(alpha)
            #     context_vectors = fuser.fuse(session_vectors, user_vectors)
            #     # print("Fused Context Embedding:", context_vectors)
                
            #     return context_vectors.get(uid, [])

            # return context_vectors.get(uid, []) #what does this like of code do?
        except Exception as e:
            print(f"Failed to build session context: {e}")
            return []
        
    def _generate_unified_embedding(self, query_embedding, context_embedding, alpha=0.6):
        """Generate unified embedding using  context and query vectors."""
        # Wrap context_embedding in a dictionary if it's not one already
        if not isinstance(context_embedding, dict):
            context_embedding = {self.current_user.id: context_embedding}
            fuser = VectorFuser(alpha=self.context_fusion_beta)
            unified_embedding = fuser(query_embedding, context_embedding)            
        # unified_embedding = fuse_vectors(alpha, self.current_user.id, query_embedding, context_embedding)

        return unified_embedding
    
    def _retrieve_results(self, refined_query, unfied_embedding=None):
        """Execute dual retrieval strategies"""
        bm25 = self.bm25_retriever.retrieve(refined_query, self.search_K)
        vector = [] #self.search_engine.search(unfied_embedding, self.search_K)
        return bm25, vector
    
    def _fuse_search_results(self, bm25_results, vector_results, beta=0.5, top_n=5):
        """Fuse BM25 and vector results"""
        if len(bm25_results) == 0 and len(vector_results) == 0:
            raise ValueError("Neither BM25 nor Vector results are available.")
        elif len(bm25_results) == 0:
            return vector_results
        elif len(vector_results) == 0:
            return bm25_results
        else:
            return fuse_candidates(bm25_results, vector_results, beta, top_n)
    
    def _display_and_log_results(self, query_log, bm25_results, vector_results, fused, product_mapping=None):
        """Display and log search results into query log"""
        bm25_products = [
            product_mapping.get(pid["product_id"] if isinstance(pid, dict) else pid, "Unknown Title").title
            for pid in bm25_results
        ]
        vector_products = [
            product_mapping.get(pid["product_id"] if isinstance(pid, dict) else pid, "Unknown Title").title
            for pid in vector_results
        ]
        final_products = [
            product_mapping.get(pid["product_id"] if isinstance(pid, dict) else pid, "Unknown Title").title
            for pid in fused
        ]

        # Print final products
        print("\nSearch Results:")
        for i, product in enumerate(final_products):
            print(f"{i+1}. {product}")

        # Update query log with titles
        query_log.update_results(bm25_products,vector_products, final_products)

if __name__ == "__main__":
    # U78644
    app = CartSearchEngine()
    app.run()
