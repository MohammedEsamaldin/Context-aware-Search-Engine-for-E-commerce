# annoy_search.py
from annoy import AnnoyIndex
import numpy as np
import pandas as pd

class ProductSearchEngine:
    def __init__(self, embedding_dim, index_path, product_df):
        self.embedding_dim = embedding_dim
        self.index_path = index_path
        self.product_df = product_df
        self.index = AnnoyIndex(embedding_dim, 'angular')
        self.index.load(index_path)

    def search(self, query_embedding, k=5):
        nearest_neighbors = self.index.get_nns_by_vector(query_embedding, k, include_distances=True)
        
        # Format results as a structured DataFrame
        results = []
        for idx, dist in zip(*nearest_neighbors):
            results.append({
                "Product ID": self.product_df['product_id'][idx],
                "Product Title": self.product_df['product_title'][idx],
                "Distance": round(dist, 4)
            })
        return pd.DataFrame(results)

    @staticmethod
    def build_index(embeddings, index_path):
        embedding_dim = embeddings.shape[1]
        index = AnnoyIndex(embedding_dim, 'angular')
        for i, vec in enumerate(embeddings):
            index.add_item(i, vec)
        index.build(100)  # You can tune the number of trees
        index.save(index_path)
