# annoy_search.py
from annoy import AnnoyIndex
import pandas as pd
import os
from typing import List

from src.models import Product

class ProductSearchEngine:
    def __init__(self, embedding_dim: int, index_path: str, products: List[Product]):
        self.embedding_dim = embedding_dim
        self.index_path = index_path
        self.products = products
        self.index = AnnoyIndex(embedding_dim, 'angular')
        
        # Create directory if not exists
        if os.path.dirname(index_path):
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
        
        # Load or build index
        if os.path.exists(index_path):
            try:
                self.index.load(index_path)
            except Exception as e:
                print(f"Error loading index: {str(e)}, rebuilding...")
                self._build_new_index()
        else:
            print("Index file not found, building new index...")
            self._build_new_index()

    def _build_new_index(self):
        """Internal method to handle index building"""
        self.index = AnnoyIndex(self.embedding_dim, 'angular')
        valid_products = [p for p in self.products if p.embedding]
        
        if not valid_products:
            raise ValueError("No products with embeddings available to build index")
            
        for i, product in enumerate(valid_products):
            self.index.add_item(i, product.embedding)
        
        self.index.build(100)
        self.index.save(self.index_path)
        print(f"Successfully built new index at {self.index_path}")

    def search(self, query_embedding: List[float], k: int = 5) -> pd.DataFrame:
        """
        Search with enhanced error handling
        
        Parameters:
        - query_embedding: List of floats representing the query embedding.
        - k: Number of nearest neighbors to return.
        
        """
        try:
            nearest_neighbors = self.index.get_nns_by_vector(
                query_embedding, 
                k, 
                include_distances=True
            )
        except Exception as e:
            print(f"Search failed: {str(e)}")
            return []

        results = []
        for idx, dist in zip(*nearest_neighbors):
            try:
                product = self.products[idx]
                results.append({
                    "product_id": product.id,
                    "score": round(1/(1+dist), 3)  # Convert distance to similarity score
                })
            except IndexError:
                print(f"Index {idx} out of bounds for products list")
                
        return results

    @staticmethod
    def build_index(products: List[Product], index_path: str):
        """Public method for manual index building"""
        if not products:
            raise ValueError("No products provided.")

        valid_products = [p for p in products if p.embedding]
        if not valid_products:
            raise ValueError("No products with embeddings available")
            
        embedding_dim = len(valid_products[0].embedding)
        index = AnnoyIndex(embedding_dim, 'angular')

        for i, product in enumerate(valid_products):
            index.add_item(i, product.embedding)

        index.build(100)
        index.save(index_path)
        print(f"Index built with {len(valid_products)} items at {index_path}")
# class ProductSearchEngine:
#     def __init__(self, embedding_dim, index_path, products: list[Product]):
#         self.embedding_dim = embedding_dim
#         self.index_path = index_path
#         self.products = products
#         self.index = AnnoyIndex(embedding_dim, 'angular')
#         self.index.load(index_path)

#     def search(self, query_embedding, k=5):
#         nearest_neighbors = self.index.get_nns_by_vector(query_embedding, k, include_distances=True)

#         results = []
#         for idx, dist in zip(*nearest_neighbors):
#             product = self.products[idx]
#             results.append({
#                 "product_id": product.id,
#                 "score": round(dist, 3)
#             })
#         return pd.DataFrame(results)

#     @staticmethod
#     def build_index(products: list[Product], index_path: str):
#         if not products:
#             raise ValueError("No products provided.")

#         embedding_dim = len(products[0].embedding)
#         index = AnnoyIndex(embedding_dim, 'angular')

#         for i, product in enumerate(products):
#             if product.embedding:
#                 index.add_item(i, product.embedding)

#         index.build(100)
#         index.save(index_path)
