from dotenv import load_dotenv

from src.models import Preferences, UserProfile
from src.modules.preprocessor.prompt_builder import PromptBuilder
from src.modules.preprocessor.preprocessor import QueryPreprocessor
from src.services.openai_client import OpenAIClient
from datetime import datetime
import os
load_dotenv()


def test_preprocessor_with_real_openai():
    # ✅ Use your real OpenAI API key securely
    openai_key = os.getenv("OPENAI_API_KEY")
    assert openai_key, "OPENAI_API_KEY not set in environment"

    # ✅ Create real OpenAIClient
    client = OpenAIClient(model="gpt-3.5-turbo", temperature=0.7)
    prompt_builder = PromptBuilder()
    preprocessor = QueryPreprocessor(prompt_builder=prompt_builder, openai_client=client)

    # 🧪 Sample user profile
    user_profile = UserProfile(
        userId="abc123",
        name="Dania",
        email="dania@example.com",
        preferences=Preferences(
            favoriteBrands=["Sony", "Bose"],
            interests=["music", "tech"]
        ),
        lastLogin=datetime.now()
    )

    # 🚀 Run the test
    result = preprocessor.preprocess("chep bluethoot headphons", user_profile)

    # ✅ Check results
    print("Expanded:", result["expanded_corrected_query"])
    print("Normalized:", result["normalized_query"])

    assert "headphones" in result["normalized_query"]
