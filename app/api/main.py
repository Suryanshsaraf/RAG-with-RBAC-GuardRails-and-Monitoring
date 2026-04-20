"""
FastAPI Backend for EnterpriseRAG.

Main entry point for the API, handling queries and system status.
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional

from app.rag.engine import get_rag_engine, RAGEngine
from app.core.config import settings

app = FastAPI(
    title="EnterpriseRAG API",
    description="Backend for querying the RAG system with RBAC and Guardrails",
    version="0.1.0"
)

# --- Request/Response Models ---

class QueryRequest(BaseModel):
    question: str
    role: str = "general"
    top_k: int = 5

class SourceDoc(BaseModel):
    content: str
    metadata: Dict

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDoc]
    guardrail_triggered: bool

# --- Endpoints ---

@app.get("/health")
async def health_check():
    """System health check."""
    return {"status": "healthy", "version": "0.1.0"}

@app.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    engine: RAGEngine = Depends(get_rag_engine)
):
    """
    Process a RAG query through retrieval, generation, and guardrails.
    """
    try:
        result = await engine.query(
            question=request.question,
            role=request.role,
            top_k=request.top_k
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
