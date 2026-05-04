from fastapi import APIRouter
from rag.vector_store import get_vector_stats

router = APIRouter()

@router.get("/metrics")
def metrics():
    stats = get_vector_stats()
    return {
        "documents": stats.get("documents", 0),
        "chunks": stats.get("chunks", 0)
    }
