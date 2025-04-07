import openai
from typing import List


class EmbeddingService:
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model

    def embed_sentences(self, sentences: List[str]) -> List[List[float]]:
        try:
            response = openai.embeddings.create(
                model=self.model,
                input=sentences
            )
            # Sort to ensure outputs are in the same order as inputs
            embeddings = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
            return embeddings
        except Exception as e:
            raise RuntimeError(f"OpenAI Embedding API error: {str(e)}")
