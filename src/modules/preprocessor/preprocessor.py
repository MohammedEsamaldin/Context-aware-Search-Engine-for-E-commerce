from typing import Dict

from src.models import UserProfile
from src.modules.preprocessor.prompt_builder import PromptBuilder
from src.services.openai_client import OpenAIClient


class QueryPreprocessor:
    def __init__(self, prompt_builder: PromptBuilder, openai_client: OpenAIClient):
        self.prompt_builder = prompt_builder
        self.openai_client = openai_client

    def preprocess(self, query: str, user_profile: UserProfile) -> Dict[str, str]:
        prompt = self.prompt_builder.build(query, user_profile)

        response = self.openai_client.generate_completion([
            {"role": "user", "content": prompt}
        ])

        normalized = self.normalize_tokenize(response)

        return {
            "expanded_corrected_query": response,
            "normalized_query": normalized
        }

    @staticmethod
    def normalize_tokenize(query: str) -> str:
        import re
        query = query.lower()
        query = re.sub(r"[^\w\s]", "", query)
        return " ".join(query.split())
