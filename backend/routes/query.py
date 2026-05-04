from fastapi import APIRouter
from backend.services.rag_service import run_query

router = APIRouter()

@router.post("/query")
def query_api(payload: dict):
    question = payload.get("question")

    if not question:
        return {"error": "Missing question"}

    result = run_query(question)
    return result
