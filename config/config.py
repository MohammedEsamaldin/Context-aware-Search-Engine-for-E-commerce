# Configuration (API keys, model paths, etc.)
import os
import openai
from dotenv import load_dotenv

FIREBASE_CREDENTIALS_PATH = "config/firebase_cart_admin.json"
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
