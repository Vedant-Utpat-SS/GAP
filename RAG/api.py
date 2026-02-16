from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from RAG.query_data import query_rag

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


# Run with:
# uvicorn RAG.api:app --host 0.0.0.0 --port 8000
