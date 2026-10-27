import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SECRET_KEY     = os.getenv("SECRET_KEY", "docudiff-dev-secret-change-me")
DATABASE_URL   = os.getenv("DATABASE_URL", "sqlite:///docudiff.db")
