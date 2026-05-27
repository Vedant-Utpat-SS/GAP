"""
FastAPI HTTP backend for the Contract Analysis RAG UI.

Run from the UI/ directory:
    pip install fastapi uvicorn
    python Backend.py

The server starts on http://localhost:8000
Endpoints:
    POST /query   { "query": "..." }  → { "answer": "...", "sources": [...] }
    GET  /files                       → { "files": ["doc1.pdf", ...] }
"""

import os
import sys

# Load .env from UI/ or project root if present
def _load_env():
    for env_path in [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
    ]:
        if os.path.isfile(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, _, v = line.partition("=")
                        os.environ.setdefault(k.strip(), v.strip())
            break

_load_env()

# Add project root so that `from RAG import ...` works
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

# Change working directory to UI/ so that relative paths ("chroma", "data") resolve correctly
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
from RAG import query_data, populate_database

# ── supported document extensions ──────────────────────────────
DOC_EXTENSIONS = (".pdf", ".doc", ".docx")
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


# ── startup: load / refresh the Chroma vector store ────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[INFO] Loading documents into Chroma …")
    try:
        populate_database.load()
        print("[INFO] Chroma ready.")
    except Exception as e:
        print(f"[WARN] Could not load documents: {e}")
    yield


app = FastAPI(title="Contract Analysis API", lifespan=lifespan)

# ── CORS: allow the Vite dev server (and any origin in dev) ────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to your domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


@app.post("/query")
async def query_endpoint(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")
    try:
        answer = query_data.query_rag_claude(req.query)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files")
async def list_files():
    try:
        if not os.path.isdir(DATA_PATH):
            return {"files": []}
        files = [
            f for f in os.listdir(DATA_PATH)
            if f.lower().endswith(DOC_EXTENSIONS)
        ]
        return {"files": sorted(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Backend:app", host="0.0.0.0", port=8000, reload=False)
