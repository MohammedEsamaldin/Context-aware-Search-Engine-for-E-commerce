from src.models import UserProfile


class PromptBuilder:
    @staticmethod
    def build(query: str, user_profile: UserProfile) -> str:
        brands = user_profile.preferences.favorite_brands
        interests = user_profile.preferences.interests

        return (
            f"Refine and correct the spelling of the search query: '{query}'. "
            f"Enrich with related terms if they are relevant to the query."
            f"User preferences: favorite brands - {', '.join(brands)}; interests - {', '.join(interests)}. "
            f"Do not include unrelated preferences if not the same categories as the query. Prioritise interests over brands."
        )
