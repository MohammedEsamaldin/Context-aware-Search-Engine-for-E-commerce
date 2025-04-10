# annoy_search.py
from annoy import AnnoyIndex
import pandas as pd

from src.models import Product


class ProductSearchEngine:
    def __init__(self, embedding_dim, index_path, products: list[Product]):
        self.embedding_dim = embedding_dim
        self.index_path = index_path
        self.products = products
        self.index = AnnoyIndex(embedding_dim, 'angular')
        self.index.load(index_path)

    def search(self, query_embedding, k=5):
        nearest_neighbors = self.index.get_nns_by_vector(query_embedding, k, include_distances=True)

        results = []
        for idx, dist in zip(*nearest_neighbors):
            product = self.products[idx]
            results.append({
                "product_id": product.id,
                "score": round(dist, 3)
            })
        return pd.DataFrame(results)

    @staticmethod
    def build_index(products: list[Product], index_path: str):
        if not products:
            raise ValueError("No products provided.")

        embedding_dim = len(products[0].embedding)
        index = AnnoyIndex(embedding_dim, 'angular')

        for i, product in enumerate(products):
            if product.embedding:
                index.add_item(i, product.embedding)

        index.build(100)
        index.save(index_path)
