from fastapi import APIRouter

from backend.services.rag_service import run_query
from backend.utils.logger import logger

router = APIRouter()


@router.post("/query")
def query_api(payload: dict):
    question = payload.get("question")

    logger.info(f"QUERY START | {question}")

    try:
        result = run_query(question)

        logger.info(
            f"QUERY DONE | {result['response_time']}s | tokens={result['tokens']} | cost={result['cost']}"
        )

        return result

    except Exception:
        logger.exception("QUERY FAILED")
        return {"error": "Something went wrong"}
