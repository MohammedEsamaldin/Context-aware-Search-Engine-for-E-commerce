from src.models import UserProfile


class PromptBuilder:
    @staticmethod
    def build(query: str, user_profile: UserProfile) -> str:
        brands = user_profile.preferences.favorite_brands
        interests = user_profile.preferences.interests

        return (
            f"Improve and correct the search query: '{query}'. "
            f"Only include related terms if they are clearly connected to the original query. "
            f"User preferences: favorite brands - {', '.join(brands)}; interests - {', '.join(interests)}. "
            f"Do not include unrelated preferences. Keep the rewritten query natural and relevant."
        )
