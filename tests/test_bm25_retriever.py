import unittest
from src.modules.retrieval.bm25_retriever import BM25CandidateRetriever
from src.models.product import Product  


class TestBM25CandidateRetriever(unittest.TestCase):
    """
    Unit tests for the BM25CandidateRetriever class.
    This test suite verifies the retriever's ability to return relevant products,
    handle edge cases like empty queries, and maintain consistency.
    """

    def setUp(self):
        """
        Set up the test environment by creating a sample list of Product instances
        and initializing the retriever with them.
        """
        self.products = [
            Product(
                id="1",
                title="Wireless Headphones",
                description="High quality wireless headphones with noise cancellation",
                bullet_point="Great sound quality",
                brand="TestBrand",
                color="Black",
                locale="en"
            ),
            Product(
                id="2",
                title="Wired Earphones",
                description="Affordable wired earphones with clear sound",
                bullet_point="Comfortable design",
                brand="TestBrand",
                color="White",
                locale="en"
            ),
            Product(
                id="3",
                title="Smartphone",
                description="Latest model smartphone with advanced features",
                bullet_point="High performance",
                brand="TestBrand",
                color="Gray",
                locale="en"
            ),
            Product(
                id="4",
                title="Laptop",
                description="Lightweight laptop with long battery life",
                bullet_point="Portable and efficient",
                brand="TestBrand",
                color="Silver",
                locale="en"
            ),
            Product(
                id="5",
                title="Wireless Mouse",
                description="Ergonomic wireless mouse with fast response",
                bullet_point="Smooth navigation",
                brand="TestBrand",
                color="Black",
                locale="en"
            )
        ]
        self.retriever = BM25CandidateRetriever(self.products)

    def test_retrieve_results(self):
        """Test that the retriever returns relevant products and that scores are sorted."""
        query = "wireless"
        results = self.retriever.retrieve(query)
        self.assertTrue(len(results) > 0)
        self.assertEqual(len(results), min(5, len(self.products)))

        # Check that BM25 scores are sorted in descending order
        scores = [res["score"] for res in results]
        for i in range(len(scores) - 1):
            self.assertGreaterEqual(scores[i], scores[i + 1])

    def test_empty_query(self):
        """Test that an empty query returns zero scores for all products."""
        results = self.retriever.retrieve("")
        for res in results:
            self.assertEqual(res["score"], 0.0)

    def test_no_matching_terms(self):
        """Test that a query with no matching terms returns zero scores."""
        results = self.retriever.retrieve("xylophone")
        for res in results:
            self.assertEqual(res["score"], 0.0)

    def test_whitespace_query(self):
        """Test that a query containing only whitespace returns zero scores."""
        results = self.retriever.retrieve("   ")
        for res in results:
            self.assertEqual(res["score"], 0.0)

    def test_output_structure(self):
        """Test that each result contains a Product and a float score."""
        results = self.retriever.retrieve("wireless")
        for res in results:
            self.assertIn("product", res)
            self.assertIn("score", res)
            self.assertIsInstance(res["product"], Product)
            self.assertIsInstance(res["score"], float)

    def test_top_k_exceeds_document_count(self):
        """Test that top_k retrieval does not exceed available documents."""
        results = self.retriever.retrieve("wireless")
        self.assertLessEqual(len(results), 5)

    def test_repeated_calls_consistency(self):
        """Test that repeated calls with the same query return consistent results."""
        query = "wireless"
        first_call = self.retriever.retrieve(query)
        second_call = self.retriever.retrieve(query)
        ids_first = [res["product"].id for res in first_call]
        ids_second = [res["product"].id for res in second_call]
        self.assertEqual(ids_first, ids_second)

