from src.models import UserProfile


class PromptBuilder:
    @staticmethod
    def build(query: str, user_profile: UserProfile) -> str:
        brands = user_profile.preferences.favorite_brands
        interests = user_profile.preferences.interests

        return (
            f"Rewrite this search query with correct spelling and more details: '{query}'. "
            f"Include relevant terms based on user's favorite brands: {', '.join(brands)}; "
            f"user interests: {', '.join(interests)}; "
        )
