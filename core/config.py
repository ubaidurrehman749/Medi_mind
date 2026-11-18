import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("MEDIMIND_DB_PATH", "data/medimind.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
