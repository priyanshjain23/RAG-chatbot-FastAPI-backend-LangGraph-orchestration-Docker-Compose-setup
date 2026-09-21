from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Tuple
import os
import shutil
from app.graph import app_graph
from app.retrieval import reindex
from app.config import DATA_DIRECTORY

app = FastAPI(title="RAG Chatbot API")

# Allow the frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend's real URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store: {session_id: [(question, answer), ...]}
sessions: dict[str, List[Tuple[str, str]]] = {}

# Formats LlamaIndex's SimpleDirectoryReader can parse out of the box
# (with the matching optional packages installed — see requirements.txt)
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


class Question(BaseModel):
    question: str
    session_id: str = "default"


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return {
            "error": f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}"
        }

    # Wipe any previous document(s) so each upload starts completely fresh —
    # no mixing of old and new document content in the index
    if os.path.exists(DATA_DIRECTORY):
        for existing_file in os.listdir(DATA_DIRECTORY):
            path = os.path.join(DATA_DIRECTORY, existing_file)
            if os.path.isfile(path):
                os.remove(path)
    os.makedirs(DATA_DIRECTORY, exist_ok=True)

    save_path = os.path.join(DATA_DIRECTORY, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Rebuild the vector index from scratch (old index is discarded)
    reindex()

    # Fresh document = fresh conversation. Clear all prior chat memory
    # so nothing from a previous document leaks into this one.
    sessions.clear()

    return {"status": "indexed", "filename": file.filename}


@app.post("/ask")
def ask(q: Question):
    history = sessions.get(q.session_id, [])
    result = app_graph.invoke(
        {
            "question": q.question,
            "needs_retrieval": False,
            "answer": "",
            "history": history,
        },
        config={"configurable": {"thread_id": q.session_id}},
    )
    answer = result["answer"]
    history.append((q.question, answer))
    sessions[q.session_id] = history
    return {"answer": answer}


@app.get("/")
def health():
    return {"status": "ok"}
