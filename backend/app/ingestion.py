from llama_index.core import SimpleDirectoryReader
from app.config import DATA_DIRECTORY


def load_documents():
    """Load and parse all supported files from the data directory."""
    documents = SimpleDirectoryReader(DATA_DIRECTORY).load_data()
    if not documents:
        raise RuntimeError(f"No documents found in '{DATA_DIRECTORY}'")
    return documents
