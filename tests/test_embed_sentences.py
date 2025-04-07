from src.services.embedding_service import EmbeddingService
from dotenv import load_dotenv
import os
import openai

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def test_embedding_service():
    sentences = [
        "Cheap Bluetooth headphones",
        "Noise-cancelling over-ear headphones from Sony",
        "Best earbuds under $100"
    ]

    embedder = EmbeddingService()
    embeddings = embedder.embed_sentences(sentences)

    assert len(embeddings) == len(sentences)
    assert all(isinstance(e, list) for e in embeddings)
    assert all(isinstance(v, float) for v in embeddings[0])

    print("✅ Embeddings shape:", len(embeddings), "x", len(embeddings[0]))
