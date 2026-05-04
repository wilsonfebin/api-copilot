from fastapi import APIRouter
import os

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "services": {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "vector_db": True,
            "rag": True
        }
    }
