from typing import List, Dict
import re
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from rank_bm25 import BM25Okapi
from src.models.product import Product

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)


class BM25CandidateRetriever:
    """
    BM25-based retriever for ranking Product objects based on a textual query.
    Takes a list of Product objects during initialization, builds a BM25 index
    from their title, description, and bullet_point fields.

    Usage:
        retriever = BM25CandidateRetriever(products)
        results = retriever.retrieve(refined_query)

    Output format:
        [
            {"product": Product, "score": float},
            ...
        ]
    """

    def __init__(self, products: List[Product]):
        """
        Initialize the retriever with a list of Product instances.

        Args:
            products (List[Product]): A list of Product objects to index.
        """
        self.products = products
        self.documents = []  # List of tokenized texts
        self.index_to_product = {}  # Map from index to Product
        self.bm25 = None
        self.stop_words = set(stopwords.words('english'))

        self.preprocess_data()
        self.build_index()

    def preprocess_text(self, text: str) -> List[str]:
        """
        Lowercase, remove punctuation, tokenize, and filter stopwords from text.

        Args:
            text (str): Raw input text.

        Returns:
            List[str]: Cleaned and tokenized list of words.
        """
        text = text.lower()
        text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
        tokens = word_tokenize(text)
        tokens = [token for token in tokens if token not in self.stop_words]
        return tokens

    def preprocess_data(self):
        """
        Preprocess product data and prepare documents for BM25 indexing.
        Combines product title, description, and bullet points into one text blob per product.
        """
        for idx, product in enumerate(self.products):
            text_parts = [product.title]
            if product.description:
                text_parts.append(product.description)
            if product.bulletPoint:
                text_parts.append(product.bulletPoint)
            full_text = " ".join(text_parts)
            tokens = self.preprocess_text(full_text)
            self.documents.append(tokens)
            self.index_to_product[idx] = product

    def build_index(self):
        """
        Build a BM25 index from the tokenized product documents.
        """
        self.bm25 = BM25Okapi(self.documents)

    def retrieve(self, refined_query: str) -> List[Dict[str, object]]:
        """
        Retrieve the top 5 most relevant products based on BM25 scores.

        Args:
            refined_query (str): The cleaned query string (from QueryLog.refined_query).

        Returns:
            List[Dict[str, object]]: A list of top-5 matches, each a dictionary with:
                - "product": Product object
                - "score": BM25 relevance score as float
        """
        query_tokens = refined_query.split()
        scores = self.bm25.get_scores(query_tokens)
        top_k = 5
        top_indices = scores.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            product = self.index_to_product[idx]
            results.append({
                "product_id": product.id,
                "score": float(scores[idx]),
            })
        return results


# Sample product data
products = [
    Product(
        id="P001",
        title="Wireless Bluetooth Headphones",
        description="Over-ear, noise cancelling headphones with long battery life.",
        bullet_point="Bluetooth 5.0, 30-hour playback",
        brand="SoundMax",
        color="Black",
        locale="en"
    ),
    Product(
        id="P002",
        title="Wired In-Ear Earbuds",
        description="High quality sound with in-line mic and volume control.",
        bullet_point="Tangle-free cable, compatible with all devices",
        brand="AudioPro",
        color="White",
        locale="en"
    ),
    Product(
        id="P003",
        title="Gaming Headset with Mic",
        description="Surround sound headset for immersive gaming experience.",
        bullet_point="Detachable microphone, RGB lighting",
        brand="GamerTech",
        color="Red",
        locale="en"
    )
]
