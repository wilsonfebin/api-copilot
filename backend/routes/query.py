from fastapi import APIRouter

from backend.services.rag_service import run_query
from backend.utils.logger import logger

from backend.agents.workflow import run_agentic_flow

router = APIRouter()


@router.post("/query")
def query_api(payload: dict):

    question = payload.get("question")

    logger.info(
        f"QUERY START | {question}"
    )

    try:

        # =========================
        # AGENTIC WORKFLOW
        # =========================
        agent_state = run_agentic_flow(
            question
        )

        logger.info(
            f"AGENT ROUTER | "
            f"intent={agent_state['intent']} | "
            f"tool={agent_state['tool']}"
        )

        # =========================
        # RAG QUERY
        # =========================
        result = run_query(
            question=question,
            intent=str(agent_state["intent"]),
            tool=agent_state["tool"]
        )

        logger.info(
            f"QUERY DONE | "
            f"{result['response_time']}s | "
            f"tokens={result['tokens']} | "
            f"cost={result['cost']}"
        )

        return result

    except Exception:

        logger.exception(
            "QUERY FAILED"
        )

        return {
            "error": "Something went wrong"
        }