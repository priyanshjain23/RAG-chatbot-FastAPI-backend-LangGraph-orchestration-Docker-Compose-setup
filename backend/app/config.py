import os

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError('GROQ_API_KEY is not set. Run: export GROQ_API_KEY="your-key"')

MODEL_NAME = "openai/gpt-oss-20b"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DATA_DIRECTORY = "data"
STORAGE_DIRECTORY = "storage"  # persisted vector index lives here
EMBED_DEVICE = "cpu"  # set to "mps" on Apple Silicon, "cuda" if you have an NVIDIA GPU
