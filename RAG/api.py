from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import shutil

from RAG.query_data import query_rag
from RAG import populate_database
from UI import Send_Email

HERE = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(HERE, "data")
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


@app.post("/query")
async def query_endpoint(req: QueryRequest):
    try:
        result = query_rag(req.query)
        if isinstance(result, dict):
            return {"answer": result.get("answer"), "sources": result.get("sources")}
        else:
            return {"answer": result, "sources": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_files(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    saved = []
    try:
        for upload in files:
            filename = upload.filename
            dest = os.path.join(DATA_DIR, filename)
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(dest):
                dest = os.path.join(DATA_DIR, f"{base}_{counter}{ext}")
                counter += 1
            with open(dest, "wb") as f:
                f.write(await upload.read())
            saved.append(os.path.basename(dest))

        # Rebuild or load embeddings in background
        background_tasks.add_task(populate_database.load)
        return {"saved": saved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/refresh")
async def refresh(background_tasks: BackgroundTasks):
    try:
        background_tasks.add_task(populate_database.load)
        return {"status": "refresh started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clear_db")
async def clear_db():
    try:
        # delete docs in DATA_DIR
        removed = []
        for fname in os.listdir(DATA_DIR):
            if fname.lower().endswith((".pdf", ".doc", ".docx")):
                try:
                    os.remove(os.path.join(DATA_DIR, fname))
                    removed.append(fname)
                except Exception:
                    pass

        # clear chroma DB
        try:
            populate_database.clear_database_new()
        except Exception:
            # fallback: remove chroma folder
            chroma = os.path.join(HERE, "..", "chroma")
            if os.path.exists(chroma):
                shutil.rmtree(chroma, ignore_errors=True)

        return {"removed": removed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files")
async def list_files():
    try:
        files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class EmailRequest(BaseModel):
    name: str
    email: str


@app.post("/send_email")
async def send_email(req: EmailRequest, background_tasks: BackgroundTasks):
    try:
        # Run notification in background
        background_tasks.add_task(Send_Email.add_contract_and_notify, req.name, req.email)
        return {"status": "email scheduled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run with:
# uvicorn RAG.api:app --host 0.0.0.0 --port 8000
