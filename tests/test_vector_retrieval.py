import unittest
from sentence_transformers import SentenceTransformer
from annoy import AnnoyIndex

class TestAnnoySearchSystem(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Set up the model and sample documents
        cls.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        cls.documents = [
            "This is the first document about artificial intelligence.",
            "Machine learning is a subset of artificial intelligence.",
            "Deep learning models are powerful for many tasks.",
            "Natural language processing focuses on the interaction between computers and human languages.",
            "Reinforcement learning is a type of machine learning where agents learn to make decisions.",
            "this document is talking about how Mohammed is awsome, and cool.",
            "this document is mentioning that mohammed does want to get a sleep"
        ]
        cls.refined_query = ""

        # Encode documents and the query
        cls.document_vectors = cls.model.encode(cls.documents)
        cls.query_vector = cls.model.encode([cls.refined_query])[0]

        # Initialize Annoy index
        cls.vector_dimension = len(cls.document_vectors[0])
        cls.annoy_index = AnnoyIndex(cls.vector_dimension, 'angular')

        # Add document vectors to Annoy index
        for i, vector in enumerate(cls.document_vectors):
            cls.annoy_index.add_item(i, vector)

        # Build the index
        cls.annoy_index.build(10)

    def test_document_embedding_generation(self):
        # Test that document vectors are generated properly
        self.assertEqual(len(self.document_vectors), len(self.documents))
        self.assertEqual(len(self.document_vectors[0]), self.vector_dimension)
    
    def test_query_embedding_generation(self):
        # Test that query vector is generated properly
        self.assertEqual(len(self.query_vector), self.vector_dimension)

    def test_annoy_index_creation(self):
        # Test that the Annoy index is built correctly by checking the number of items
        self.assertEqual(self.annoy_index.get_n_items(), len(self.documents))

    def test_similarity_search(self):
        # Perform a similarity search for the query and check if results make sense
        nearest_neighbors = self.annoy_index.get_nns_by_vector(self.query_vector, 3, include_distances=True)
        
        # Assert that we get exactly 3 nearest neighbors
        self.assertEqual(len(nearest_neighbors[0]), 3)

        # Check that the first result is the most similar document (should be related to reinforcement learning)
        expected_document = "Reinforcement learning is a type of machine learning where agents learn to make decisions."
        closest_doc_idx = nearest_neighbors[0][0]
        self.assertEqual(self.documents[closest_doc_idx], expected_document)

    def test_cosine_similarity_behavior(self):
        # Check that the cosine similarity is reasonable (distance should be small for similar documents)
        nearest_neighbors = self.annoy_index.get_nns_by_vector(self.query_vector, 3, include_distances=True)
        
        for dist in nearest_neighbors[1]:
            # Cosine distance should be between 0 (similar) and 2 (opposite direction)
            self.assertGreaterEqual(dist, 0)
            self.assertLessEqual(dist, 2)

if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)