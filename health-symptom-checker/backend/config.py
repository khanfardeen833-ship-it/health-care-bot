import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Validate API key is set
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))

# CORS Configuration - Allow all origins for deployment
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://health-symptom-checker.vercel.app",  # Vercel deployment URL
    "https://*.vercel.app",  # Any Vercel subdomain
    "https://*.railway.app",  # Any Railway subdomain
]
