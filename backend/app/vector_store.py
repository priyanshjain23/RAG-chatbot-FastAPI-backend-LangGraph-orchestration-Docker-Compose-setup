import os
import shutil
import time
from llama_index.core import (
    VectorStoreIndex,
    Settings,
    StorageContext,
    load_index_from_storage,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.config import EMBEDDING_MODEL, EMBED_DEVICE, STORAGE_DIRECTORY
from app.ingestion import load_documents

Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL, device=EMBED_DEVICE)


def get_index(force_rebuild: bool = False):
    """
    Load the index from disk if it already exists (fast).
    Pass force_rebuild=True (e.g. after a new document is uploaded)
    to wipe the old index and build fresh from whatever is in data/.
    """
    if force_rebuild and os.path.exists(STORAGE_DIRECTORY):
        # Clear the CONTENTS of the folder, not the folder itself —
        # storage/ is a mounted Docker volume, so removing the mount
        # point directory itself raises "Device or resource busy"
        for entry in os.listdir(STORAGE_DIRECTORY):
            entry_path = os.path.join(STORAGE_DIRECTORY, entry)
            if os.path.isdir(entry_path):
                shutil.rmtree(entry_path)
            else:
                os.remove(entry_path)

    has_existing_index = os.path.exists(os.path.join(STORAGE_DIRECTORY, "docstore.json"))

    if has_existing_index:
        storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIRECTORY)
        index = load_index_from_storage(storage_context)
        print("[vector_store] Loaded existing index from disk")
        return index

    documents = load_documents()
    start = time.time()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=STORAGE_DIRECTORY)
    print(f"[vector_store] Built new index in {time.time() - start:.2f}s and saved to disk")
    return index