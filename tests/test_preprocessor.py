from unittest.mock import MagicMock
from src.models import Preferences, UserProfile
from src.modules.preprocessor.preprocessor import QueryPreprocessor
from src.modules.preprocessor.prompt_builder import PromptBuilder
from src.services.openai_client import OpenAIClient


def test_preprocessor_returns_expected_output():
    # 🧪 Fake OpenAIClient
    mock_openai_client = MagicMock(spec=OpenAIClient)
    mock_openai_client.generate_completion.return_value = (
        "Refined query about Bluetooth headphones from Sony for music and gaming."
    )

    # 👤 Create test user profile
    user_profile = UserProfile(
        userId="123",
        name="Test User",
        email="test@example.com",
        preferences=Preferences(
            favoriteBrands=["Sony", "Bose"],
            interests=["music", "gaming"]
        ),
        lastLogin="2024-04-01T00:00:00"
    )

    # 🧠 Build & preprocess
    builder = PromptBuilder()
    preprocessor = QueryPreprocessor(prompt_builder=builder, openai_client=mock_openai_client)
    result = preprocessor.preprocess("bluethot headfones", user_profile)

    # ✅ Assertions
    assert "refined query" in result["expanded_corrected_query"].lower()
    assert "bluetooth headphones" in result["normalized_query"]
