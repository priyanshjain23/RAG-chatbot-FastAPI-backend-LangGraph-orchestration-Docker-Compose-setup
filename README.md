# NeuraChat — Retrieval-Augmented Document Chatbot

A full-stack RAG (Retrieval-Augmented Generation) application: upload any document, and chat with it in plain English. Built with a modular FastAPI backend, LangGraph orchestration, LlamaIndex retrieval, and a lightweight chat frontend — fully containerized with Docker Compose.

---

## Features

- **Upload any document** (PDF, DOCX, PPTX, TXT, MD, CSV) directly from the browser
- **Automatic indexing** — the document is chunked, embedded, and stored in a vector index the moment it's uploaded
- **Grounded, context-aware answers** via Retrieval-Augmented Generation, not the model's raw memory
- **Fresh session per document** — uploading a new file clears prior chat history and the old index, so documents never bleed into each other
- **Intent routing** — small talk ("hi", "thanks") skips retrieval entirely and goes straight to the LLM; real questions trigger document search
- **Fully containerized** — one command spins up both the API and the UI

---

## Architecture

```
┌─────────────┐      upload/ask       ┌──────────────────────────────────┐
│   Frontend  │ ───────────────────▶  │           Backend                │
│ (HTML/JS)   │  ◀─────────────────── │         (FastAPI)              	 │
└─────────────┘        answer         │                                  │
                                      │  ┌───────────────────────────┐   │
                                      │  │      LangGraph            │   │
                                      │  │  classify → retrieve/chat │   │
                                      │  └───────────────────────────┘   │
                                      │       │              │           │
                                      │       ▼              ▼           │
                                      │  ┌───────────┐   ┌───────────┐   │
                                      │  │LlamaIndex │   │ LangChain │   │
                                      │  │Retrieval  │   │  ChatGroq │   │
                                      │  └───────────┘   └───────────┘   │
                                      │       │                          │
                                      │       ▼                          │
                                      │  ┌──────────────────────────┐    │
                                      │  │  Chroma / Vector Store   │    │
                                      │  │  (HuggingFace embeddings)│    │
                                      │  └──────────────────────────┘    │
                                      └──────────────────────────────────┘
```

Each stage of the RAG pipeline lives in its own module:

| File                    | Responsibility                                                              |
| ----------------------- | --------------------------------------------------------------------------- |
| `app/config.py`       | Central settings, env vars, model names                                     |
| `app/ingestion.py`    | Loads and parses uploaded documents                                         |
| `app/vector_store.py` | Builds/persists the vector index (Chroma-backed)                            |
| `app/retrieval.py`    | Wraps the index as a query engine (the "R" in RAG)                          |
| `app/generation.py`   | LLM setup — Groq-hosted models via LangChain and LlamaIndex                |
| `app/graph.py`        | LangGraph orchestration — routes between plain chat and document retrieval |
| `app/main.py`         | FastAPI app — exposes`/upload` and `/ask`                              |

---

## Tech Stack

- **Backend:** FastAPI, Python 3.11
- **Orchestration:** LangGraph (state graph with conditional routing)
- **Retrieval:** LlamaIndex (`VectorStoreIndex`, `SimpleDirectoryReader`)
- **Embeddings:** Hugging Face `sentence-transformers/all-MiniLM-L6-v2`
- **LLM:** Groq-hosted models (`openai/gpt-oss-20b`), via both LangChain and LlamaIndex clients
- **Vector storage:** Persisted LlamaIndex vector store (Chroma-compatible)
- **Frontend:** Plain HTML/CSS/JS (no build step) — chat UI with upload, formatted responses, light markdown rendering
- **Containerization:** Docker, Docker Compose

---

## Getting Started

### Option 1 — Docker Compose (recommended)

```bash
git clone <this-repo-url>
cd rag_app

# Create a .env file with your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env

docker compose up --build
```

- Backend: [http://localhost:8000](http://localhost:8000)
- Frontend: [http://localhost:3000](http://localhost:3000)

Get a free Groq API key at [console.groq.com](https://console.groq.com).

### Option 2 — Run locally without Docker

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY=your_key_here
uvicorn app.main:app --reload
```

Then open `frontend/index.html` directly in your browser.

---

## API Reference

### `POST /upload`

Uploads a document, replaces any previous document, and rebuilds the vector index.

```bash
curl -X POST http://localhost:8000/upload -F "file=@resume.pdf"
```

**Response:**

```json
{ "status": "indexed", "filename": "resume.pdf" }
```

### `POST /ask`

Asks a question about the currently indexed document.

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What skills does this person have?", "session_id": "abc123"}'
```

**Response:**

```json
{ "answer": "..." }
```

---

## Design Decisions & Trade-offs

- **One document at a time.** Uploading a new file intentionally wipes the previous index and chat history, so documents never mix. Multi-document support would need per-document indices or metadata-tagged chunks — a deliberate scope decision, not an oversight.
- **Retrieval uses the raw question only**, not the full conversation history — wrapping history into the retrieval query was tried and found to degrade embedding search quality, since instructional boilerplate text dilutes the semantic match. Conversation context is used for *generation*, not *retrieval*.
- **CPU-only PyTorch.** The embedding model runs on CPU by default (`EMBED_DEVICE` in `config.py`) for portability across machines without a GPU; can be swapped to `"cuda"` or `"mps"` for acceleration.

---

## Known Limitations

- Single-document context only (see above)
- No authentication — sessions are tracked only by a client-generated ID, suitable for local/demo use, not production
- In-memory session store — chat history is lost on backend restart (no database persistence yet)

---

## Roadmap

- [ ] Multi-document support with source attribution per chunk
- [ ] Query rewriting for conversation-aware retrieval on follow-up questions
- [ ] Swap frontend for a React app (Vite scaffold, same API)
- [ ] Persistent session storage (Redis or a lightweight DB)
- [ ] Cloud deployment (AWS/GCP/Azure)

---

## License

MIT
