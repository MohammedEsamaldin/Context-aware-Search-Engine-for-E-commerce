import pandas as pd
import re
import os
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from rank_bm25 import BM25Okapi

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

class BM25CandidateRetriever:
    """
    BM25CandidateRetriever loads product data from a JSON file, preprocesses text,
    builds a BM25 index, and retrieves the top 5 relevant products for a given query.

    The JSON file is expected to contain a list of product dictionaries with at least the following keys:
        - product_id
        - product_title
        - product_description
        - product_bullet_point

    The retrieve() function accepts a query that is returned from the embedding module.
    This query is expected to be a dictionary with a key "query" whose value is a cleaned string.
    """
    def __init__(self, data_path: str):
        """
        Initialize the BM25 Candidate Retriever.

        :param data_path: Path to the JSON file containing the product catalog.
        """
        self.data_path = data_path
        self.data = None
        self.documents = []  # List of tokenized product texts
        self.index_to_product = {}  # Maps document index to full product info
        self.bm25 = None
        self.stop_words = set(stopwords.words('english'))

        self.load_data()
        self.preprocess_data()
        self.build_index()

    def load_data(self):
        """
        Load product data from a JSON file.
        The JSON file should contain a list of product dictionaries.
        """
        self.data = pd.read_json(self.data_path)

    def preprocess_text(self, text: str) -> list:
        """
        Normalize, tokenize, and remove stop words from text.

        :param text: Raw text to preprocess.
        :return: A list of processed tokens.
        """
        text = text.lower()
        # Remove punctuation
        text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
        tokens = word_tokenize(text)
        # Remove stop words
        tokens = [token for token in tokens if token not in self.stop_words]
        return tokens

    def preprocess_data(self):
        """
        Process each product by combining relevant text fields and tokenizing.
        Relevant fields include: product_title, product_description, product_bullet_point.
        """
        for idx, row in self.data.iterrows():
            text = ""
            # Check if each field exists and is not null
            if 'product_title' in row and pd.notnull(row['product_title']):
                text += row['product_title'] + " "
            if 'product_description' in row and pd.notnull(row['product_description']):
                text += row['product_description'] + " "
            if 'product_bullet_point' in row and pd.notnull(row['product_bullet_point']):
                text += row['product_bullet_point']
            tokens = self.preprocess_text(text)
            self.documents.append(tokens)
            self.index_to_product[idx] = row.to_dict()

    def build_index(self):
        """
        Build the BM25 index using the preprocessed product documents.
        """
        self.bm25 = BM25Okapi(self.documents)

    def retrieve(self, query) -> list:
        """
        Retrieve the top 5 most relevant products based on BM25 scores.

        :param query: The input query which is expected to be:
                      - A dictionary containing a key "query" with the cleaned query string,
                        or
                      - A cleaned string.
        :return: A list of dictionaries, each containing:
                 product_id, bm25_score
        """
        # If the query is a dictionary, extract the cleaned query string using key "query"
        if isinstance(query, dict):
            query_str = query.get("query", "")
        else:
            query_str = query

        # Since the query is already cleaned, simply split it into tokens
        query_tokens = query_str.split()
        scores = self.bm25.get_scores(query_tokens)
        top_k = 5  # Number of top results
        top_indices = scores.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            product = self.index_to_product[idx]
            results.append({
                "product_id": product.get("product_id"),
                "bm25_score": float(scores[idx]),
            })
        return results
