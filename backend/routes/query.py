import json
import time

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from backend.services.rag_service import run_query
from backend.utils.logger import logger

from backend.agents.workflow import run_agentic_flow

router = APIRouter()


def sse_event(event: str, data: dict):
    return (
        f"event: {event}\n"
        f"data: {json.dumps(data)}\n\n"
    )


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


@router.post("/query/stream")
def query_stream_api(payload: dict):

    question = payload.get("question")

    def event_stream():

        try:

            logger.info(
                f"QUERY STREAM START | {question}"
            )

            yield sse_event(
                "status",
                {"message": "Routing query"}
            )

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

            yield sse_event(
                "status",
                {
                    "message": "Retrieving context",
                    "intent": str(agent_state["intent"]),
                    "tool": agent_state["tool"],
                }
            )

            # =========================
            # RAG QUERY
            # =========================
            result = run_query(
                question=question,
                intent=str(agent_state["intent"]),
                tool=agent_state["tool"]
            )

            answer = result.get("answer", "")

            yield sse_event(
                "metadata",
                {
                    "sources": result.get("sources", []),
                    "intent": result.get("intent"),
                    "tool": result.get("tool"),
                }
            )

            # =========================
            # STREAM ANSWER
            # =========================
            chunk_size = 24

            for index in range(
                0,
                len(answer),
                chunk_size
            ):

                yield sse_event(
                    "chunk",
                    {
                        "text": answer[
                            index:index + chunk_size
                        ]
                    }
                )

                time.sleep(0.01)

            logger.info(
                f"QUERY STREAM DONE | "
                f"{result['response_time']}s | "
                f"tokens={result['tokens']} | "
                f"cost={result['cost']}"
            )

            yield sse_event(
                "done",
                result
            )

        except Exception as exc:

            logger.exception(
                "QUERY STREAM FAILED"
            )

            yield sse_event(
                "error",
                {"error": str(exc)}
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
