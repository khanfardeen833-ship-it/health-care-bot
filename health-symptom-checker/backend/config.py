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
ALLOWED_ORIGINS = ["*"]  # Allow all origins temporarily for testing
