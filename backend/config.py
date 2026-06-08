import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/ai_auction")
AGNES_API_KEY = os.getenv("AGNES_API_KEY", "sk-bchEYgDebbqGGcqupTB1ccQ6eoo4D8MOcL6MnmAIeQFXDLU3")
AGNES_BASE_URL = os.getenv("AGNES_BASE_URL", "https://apihub.agnes-ai.com/v1")
