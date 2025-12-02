import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Agent Config
MAX_REACT_STEPS = 7
TEMPERATURE = 0.1  # Low pour plus de cohérence
MAX_TOKENS = 500

# Embedding Config
EMBEDDING_DIMENSION = 1536  # text-embedding-3-small dimension
SIMILARITY_THRESHOLD = 0.7