# RAG Chatbot — Modular Architecture

```
backend/app/
  config.py        settings, env vars, model names
  ingestion.py      load + parse documents          (Ingestion)
  vector_store.py   build/persist the vector index   (Vector DB storage)
  retrieval.py      query engine over the index      (Retrieval)
  generation.py     LLM setup (Groq)                 (Generation)
  graph.py          LangGraph routing between chat/retrieval
  main.py           FastAPI app, exposes /ask
frontend/
  index.html        chat UI, calls the backend API
```

## Run locally without Docker

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export GROQ_API_KEY=your_key_here
uvicorn app.main:app --reload
```

Then open `frontend/index.html` directly in a browser (double-click it, or `open index.html`).

## Run everything with Docker Compose (recommended)

From the project root (`rag_app/`):

```bash
export GROQ_API_KEY=your_key_here
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

`docker compose` builds and starts both containers together, networked so the frontend can reach the backend. The vector index is persisted to `backend/storage/` via a volume mount, so it survives container restarts — no re-indexing needed unless you change the source documents.

## Adding a new document

Drop a file into `backend/data/`, delete the `backend/storage/` folder (forces a rebuild of the index), and restart the backend.

## Next step: swap the frontend for React

This plain HTML/JS frontend was chosen to avoid Node.js build tooling for a fast first pass. To upgrade to React later: scaffold with `npm create vite@latest frontend -- --template react`, move the fetch logic from `index.html` into a component, and change the frontend Dockerfile to a multi-stage build (`node:20-alpine` to build, `nginx:alpine` to serve the built static files).
