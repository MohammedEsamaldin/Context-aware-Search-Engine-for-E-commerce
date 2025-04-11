
import sys
import os
import traceback
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
from src.modules.Dynamic_context_modelling.Session_Graph_Builder \
    import SessionGraphEmbedder, SessionGraphBuilder, ContextFusion
from src.modules.Dynamic_context_modelling.fusion import fuse_vectors

from src.modules.retrieval.bm25_retriever import BM25CandidateRetriever
from src.modules.retrieval.vector_retrieval_model import ProductSearchEngine
from src.modules.fusion.fuse import fuse_candidates



class CartSearchEngine:
    def __init__(self):
        self.current_user = None
        self.current_session = None
        self.search_components = None
        self.context_alpha = 0.4  # Session vs user context balance
        self.fusion_beta = 0.7    # Query vs context balance
    
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
        print(f"\nSession terminated at {self.current_session.end_time}")
    
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
                results = self.perform_search(query)
                
                print("\nSearch Results:")
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result}")
                
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
        print(f"# Session Queries: {len(self.current_session.queries)}")

        ## 2. Query pre-processing
        refined_query = self._preprocess_query(query_log, self.current_user)
        print(f"Refined search query: {query_log.refined_query}")

        ## 3. Embedding generation
        query_embedding = self._generate_query_embeddings(query_log)
        # print(f"Query Embedding: {query_log.embedding}")

        ## 4. Session context processing
        # print(f"User Embedding: {self.current_user.embedding}")
        context_vector = [] #self._build_session_context()
        # print(f"Context Embedding: {context_vector}")

        ## 5. Context-Aware embedding generation (user + session graph embeddings)
        fused_context_vector = self._get_unified_context_vector(query_log.embedding, )

        ## 6. Unified Context Embedding (context_vector + query embeddings)
        unified_vector = self._get_unified_context_vector(
            refined_query=query_log.refined_query,
            query_vector=query_log.embedding,
            context_vector=fused_context_vector,  # From _build_session_context()
            alpha=0.6
        )
        print(unified_vector)

        ## 6. Dual retrieval
        # bm25_results, vector_results = self._retrieve_results(
        #     refined_query, query_embedding
        # )

        ## 7. Result fusion


        ## 8. Final logging
        
        return []

    def _initialize_search_components(self):
        """One-time initialization of search resources"""
        if not hasattr(self, '_search_initialized'):
            self.products = Product.load_all()
            self.search_engine = ProductSearchEngine(
                embedding_dim=1536,
                index_path="products.ann",
                products=self.products
            )            
            self.embedding_service = EmbeddingService()
            self.retriever = BM25CandidateRetriever(self.products)
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
        refined = preprocessor.preprocess(query_log, user)
        query_log.update_refined_query(refined["normalized_query"])
        
        return refined
    
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

    def _build_session_context(self):
        """Build session-aware context vector"""
        try:
            # Get session graph embedding
            session_embedding = self._get_session_graph_embedding() or []
            
            # Get user profile embedding
            user_embedding = self.current_user.embedding or []
            
            # Fuse session and user context
            return session_embedding
            # return self._fuse_context_vectors(session_embedding, user_embedding)
            
        except Exception as e:
            print(f"Context processing failed: {str(e)}")
            return []
        
    def _get_session_graph_embedding(self):
        """Generate session graph embedding with proper error handling"""
        try:
            if len(self.current_session.queries) <= 1:
                return None  # Use None instead of empty list for clarity
                
            # 1. Build graph(s) - match original pattern's input type
            graph_builder = SessionGraphBuilder()
            session_graphs = graph_builder.build_graph([self.current_session])  # List input
            
            # 2. Embed graphs - add empty result handling
            embedder = SessionGraphEmbedder()
            embeddings = embedder.embed_session_graphs([self.current_session]) #session_graphs
            
            # 3. Validate and return
            if embeddings and len(embeddings) > 0:
                return embeddings[0]  # Return first embedding
            return None
            
        except Exception as e:
            print(f"Session graph embedding failed: {str(e)}")
            return None

    def _fuse_context_vectors(self, session_embedding, user_embedding, alpha=0.4):
        """Combine session and user context"""
        user_id = self.current_user.id
        session_dict = {user_id: session_embedding} if session_embedding else {}
        user_dict = {user_id: user_embedding} if user_embedding else {}
        
        fuser = ContextFusion(alpha=alpha)
        fused = fuser.fuse(session_dict, user_dict)
        return fused.get(user_id) or []
        
    def _get_unified_context_vector(self, refined_query: str, query_vector: list, context_vector: list, alpha: float = 0.6) -> list:
        """Generate and store unified context-aware embedding"""
        if context_vector == []:
            print("No context available, using pure query embedding")
            return query_vector
        
        try:
            fused_vector = fuse_vectors(
                query_vector=query_vector,
                context_vector=context_vector,
                alpha=alpha
            )
            
            # Create and store unified embedding
            UnifiedEmbedding.create(
                user_id=self.current_user.id,
                session_id=self.current_session.id,
                query=refined_query,
                embedding=fused_vector
            )  
            return fused_vector
            
        except Exception as e:
            print(f"Context fusion failed: {str(e)}")
            return query_vector  # Fallback to original query embedding
    
    def _retrieve_results(self, refined_query, query_embedding):
        """Execute dual retrieval strategies"""
        bm25 = self.retriever.retrieve(refined_query)
        vector = self.search_engine.search(query_embedding, k=5)
        return bm25, vector
    
if __name__ == "__main__":
    # U78644
    app = CartSearchEngine()
    app.run()
