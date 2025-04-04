from sentence_transformers import SentenceTransformer
from annoy import AnnoyIndex
import numpy as np

# Step 1: Initialize Sentence-BERT model for embedding generation
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # Example model, can be changed

# Sample documents and a refined query
documents = [
            "This is the first document about artificial intelligence.",
            "Machine learning is a subset of artificial intelligence.",
            "Deep learning models are powerful for many tasks.",
            "Natural language processing focuses on the interaction between computers and human languages.",
            "Reinforcement learning is a type of machine learning where agents learn to make decisions.",
            "this document is talking about how Mohammed is awsome, and cool.",
            "this document is mentioning that mohammed does want to get a sleep"
        ]

refined_query = str(input("please enter you query?"))

# Step 2: Create vectors for documents and the refined query
document_vectors = model.encode(documents)  # Get embeddings for documents

query_vector = model.encode([refined_query])[0]  # Get embedding for the query

# Step 3: Initialize Annoy index
vector_dimension = len(document_vectors[0])  # Dimension of the vector
annoy_index = AnnoyIndex(vector_dimension, 'angular')  # Use angular distance (cosine similarity)


# Step 4: Add document vectors to Annoy index
for i, vector in enumerate(document_vectors):
    annoy_index.add_item(i, vector)

# Build the Annoy index (this is an offline process)
annoy_index.build(10)  # 10 trees for speed/accuracy trade-off
print(annoy_index)
print(100*"-")

# Step 5: Query the Annoy index to find the most similar document
nearest_neighbors = annoy_index.get_nns_by_vector(query_vector, 2, include_distances=True)

# Step 6: Output the results
print(f"Query: {refined_query}")
print("\nMost similar documents:")
for idx, dist in zip(nearest_neighbors[0], nearest_neighbors[1]):
    print(f"Document: {documents[idx]} (Distance: {dist})")
