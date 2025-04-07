import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "modules", "retrieval")))

import unittest
import pandas as pd
from bm25_retriever import BM25CandidateRetriever


class TestBM25CandidateRetriever(unittest.TestCase):
    def setUp(self):
        # Create sample JSON data as a list of product dictionaries.
        sample_data = [
            {
                "product_id": "1",
                "product_title": "Wireless Headphones",
                "product_description": "High quality wireless headphones with noise cancellation",
                "product_bullet_point": "Great sound quality"
            },
            {
                "product_id": "2",
                "product_title": "Wired Earphones",
                "product_description": "Affordable wired earphones with clear sound",
                "product_bullet_point": "Comfortable design"
            },
            {
                "product_id": "3",
                "product_title": "Smartphone",
                "product_description": "Latest model smartphone with advanced features",
                "product_bullet_point": "High performance"
            },
            {
                "product_id": "4",
                "product_title": "Laptop",
                "product_description": "Lightweight laptop with long battery life",
                "product_bullet_point": "Portable and efficient"
            },
            {
                "product_id": "5",
                "product_title": "Wireless Mouse",
                "product_description": "Ergonomic wireless mouse with fast response",
                "product_bullet_point": "Smooth navigation"
            }
        ]
        # Create a DataFrame from the sample data and write it to a temporary JSON file.
        self.data = pd.DataFrame(sample_data)
        self.temp_file = "temp_products.json"
        self.data.to_json(self.temp_file, orient="records")
        self.retriever = BM25CandidateRetriever(self.temp_file)

    def tearDown(self):
        # Remove the temporary file after tests.
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def test_retrieve_results(self):
        # Use a query that should match some products.
        query = "wireless"
        results = self.retriever.retrieve(query)
        # Expect the number of returned results to be equal to min(5, total products). Here, 5.
        expected_len = min(5, len(self.data))
        self.assertTrue(len(results) > 0)
        self.assertEqual(len(results), expected_len)
        
        # Check that BM25 scores are in descending order.
        scores = [result["bm25_score"] for result in results]
        for i in range(len(scores) - 1):
            self.assertGreaterEqual(scores[i], scores[i + 1])

    def test_empty_query(self):
        # An empty query should yield tokens list empty and thus BM25 scores of 0.
        results = self.retriever.retrieve("")
        for res in results:
            self.assertEqual(res["bm25_score"], 0.0)

    def test_no_matching_terms(self):
        # A query that doesn't match any terms should yield BM25 scores of 0.
        results = self.retriever.retrieve("xylophone")
        for res in results:
            self.assertEqual(res["bm25_score"], 0.0)

    def test_whitespace_query(self):
        # A query with only whitespace should result in BM25 scores of 0.
        results = self.retriever.retrieve("   ")
        for res in results:
            self.assertEqual(res["bm25_score"], 0.0)

    def test_output_keys(self):
        # Each result should contain only "product_id" and "bm25_score".
        results = self.retriever.retrieve("wireless")
        expected_keys = {"product_id", "bm25_score"}
        for res in results:
            self.assertTrue(expected_keys.issubset(res.keys()))

    def test_top_k_exceeds_document_count(self):
        # Since top_k is hardcoded to 5, with exactly 5 products, it should return 5.
        results = self.retriever.retrieve("wireless")
        self.assertEqual(len(results), 5)

    def test_repeated_calls_consistency(self):
        # Multiple calls with the same query should return the same order of product_ids.
        query = "wireless"
        first_call = self.retriever.retrieve(query)
        second_call = self.retriever.retrieve(query)
        ids_first = [res["product_id"] for res in first_call]
        ids_second = [res["product_id"] for res in second_call]
        self.assertEqual(ids_first, ids_second)

