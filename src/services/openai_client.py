import openai
from typing import List, Dict


class OpenAIClient:
    def __init__(self, model: str = "gpt-3.5-turbo", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature

    def generate_completion(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {str(e)}")
