import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    ENV = os.getenv("FLASK_ENV", "production")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

    # Traversal settings
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", 30))
    PHILOSOPHY_URL = "https://en.wikipedia.org/wiki/Philosophy"
    SELENIUM_WAIT_TIME = int(os.getenv("SELENIUM_WAIT_TIME", 10))

    # CORS
    ALLOWED_ORIGINS = os.getenv(
        "ALLOWED_ORIGINS", "https://first-link-delta.vercel.app"
    ).split(",")