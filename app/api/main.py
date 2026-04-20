"""
FastAPI Backend for EnterpriseRAG.

Main entry point for the API, handling queries and system status.
"""

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict, Optional
import shutil
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from app.rag.engine import get_rag_engine, RAGEngine
from app.ingestion.pipeline import run_ingestion
from app.core.config import settings
from app.auth.handler import create_access_token, verify_password, hash_password
from app.auth.deps import get_current_user, UserSession

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title="EnterpriseRAG API",
    description="Backend for querying the RAG system with RBAC and Guardrails",
    version="1.0.0"
)

# --- Monitoring ---
Instrumentator().instrument(app).expose(app)


# --- Mock User Database (For Demo Purposes) ---
# In a production app, use a real database (PostgreSQL/MongoDB)
FAKE_USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": hash_password("admin123"),
        "role": "admin"
    },
    "mark": {
        "username": "mark",
        "hashed_password": hash_password("mark123"),
        "role": "marketing"
    },
    "fin": {
        "username": "fin",
        "hashed_password": hash_password("fin123"),
        "role": "finance"
    }
}

# --- Request/Response Models ---

class QueryRequest(BaseModel):
    question: str
    top_k: int = 5
    use_hyde: bool = False
    multi_query: bool = False

class Token(BaseModel):
    access_token: str
    token_type: str

# Existing models...
class SourceDoc(BaseModel):
    content: str
    metadata: Dict

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDoc]
    guardrail_triggered: bool

# --- Authentication Endpoints ---

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = FAKE_USERS_DB.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Endpoints ---

@app.get("/health")
async def health_check():
    """System health check."""
    return {"status": "healthy", "version": "0.1.0"}

@app.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    current_user: UserSession = Depends(get_current_user),
    engine: RAGEngine = Depends(get_rag_engine)
):
    """
    Process a RAG query through retrieval, generation, and guardrails.
    Requires a valid JWT token. Role is automatically derived from token.
    """
    try:
        result = await engine.query(
            question=request.question,
            role=current_user.role,
            top_k=request.top_k,
            use_hyde=request.use_hyde,
            multi_query=request.multi_query
        )
        
        # Format sources for response
        sources = [
            SourceDoc(content=doc.page_content, metadata=doc.metadata)
            for doc in result["source_documents"]
        ]
        
        return QueryResponse(
            answer=result["answer"],
            sources=sources,
            guardrail_triggered=result.get("guardrail_triggered", False)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/stream")
async def process_query_stream(
    request: QueryRequest,
    current_user: UserSession = Depends(get_current_user),
    engine: RAGEngine = Depends(get_rag_engine)
):
    """
    Process a streaming RAG query.
    Requires a valid JWT token.
    """
    return StreamingResponse(
        engine.stream_query(
            question=request.question,
            role=current_user.role,
            top_k=request.top_k,
            use_hyde=request.use_hyde,
            multi_query=request.multi_query
        ),
        media_type="application/x-ndjson"
    )
    

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: UserSession = Depends(get_current_user)
):
    """
    Upload a document to the knowledge base and trigger ingestion.
    Files are saved to data/general by default.
    """
    # 1. Create upload dir if not exists
    upload_dir = Path("data/general")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / file.filename
    
    # 2. Save file
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    
    # 3. Trigger Ingestion (Async)
    try:
        # We run the ingestion for the new file
        await run_ingestion(data_dir="data", full=False)
        return {"filename": file.filename, "status": "Uploaded and indexed successfully"}
    except Exception as e:
        return {"filename": file.filename, "status": "Uploaded but indexing failed", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
