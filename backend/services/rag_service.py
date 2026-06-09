import time
from functools import lru_cache

from backend.enterprise.workflow import run_enterprise_workflow
from backend.langgraph.router import run_rag_graph
from backend.utils.logger import logger
from backend.config import (
    DEFAULT_LLM_PROVIDER,
    RETRY_COUNT,
    RETRY_DELAY,
    REQUEST_TIMEOUT,
    CACHE_SIZE,
    get_default_model,
)

from utils.metrics import estimate_tokens, estimate_cost


def normalize_intent(intent):

    if hasattr(intent, "value"):
        return intent.value

    intent = str(intent)

    if intent.startswith("Intent."):
        return intent.split(".", 1)[1]

    return intent


def is_enterprise_workflow_query(question: str) -> bool:
    q = question.lower()

    return (
        (
            "investigate" in q
            and "webhook" in q
            and "failure" in q
        )
        or "enterprise workflow" in q
        or "rca" in q
        or "incident" in q
    )


# ========================
# CACHED RAG CALL
# ========================
@lru_cache(maxsize=CACHE_SIZE)
def cached_answer(
    question: str,
    intent: str = "GENERAL",
    llm_provider: str = DEFAULT_LLM_PROVIDER,
    model: str | None = None,
):
    model = model or get_default_model(
        llm_provider
    )

    return run_rag_graph(
        question=question,
        intent=intent,
        llm_provider=llm_provider,
        model=model,
    )


# ========================
# RETRY WRAPPER
# ========================
def retry_call(fn):

    for attempt in range(RETRY_COUNT + 1):

        try:
            return fn()

        except Exception as e:

            if attempt == RETRY_COUNT:
                raise

            logger.warning(
                f"Retry {attempt + 1} after error: {str(e)}"
            )

            time.sleep(RETRY_DELAY)


# ========================
# MAIN SERVICE FUNCTION
# ========================
def run_query(
    question: str,
    intent: str = "GENERAL",
    tool: dict | None = None,
    include_context: bool = False,
    llm_provider: str = DEFAULT_LLM_PROVIDER,
    model: str | None = None,
):

    try:

        intent = normalize_intent(
            intent
        )

        model = model or get_default_model(
            llm_provider
        )

        if is_enterprise_workflow_query(
            question
        ):
            return run_enterprise_workflow(
                question=question,
                llm_provider=llm_provider,
                model=model,
            )

        start = time.time()

        logger.info(
            f"RAG START | intent={intent} | "
            f"provider={llm_provider} | "
            f"model={model} | question={question}"
        )

        # ========================
        # EXECUTE RAG
        # ========================
        def execute():

            return cached_answer(
                question,
                intent,
                llm_provider,
                model,
            )

        result = retry_call(execute)

        elapsed = round(time.time() - start, 2)

        if elapsed > REQUEST_TIMEOUT:
            logger.warning(f"SLOW RESPONSE | {elapsed}s")

        answer = result["answer"]

        in_tokens = estimate_tokens(
            question,
            model=model
        )

        out_tokens = estimate_tokens(
            answer,
            model=model
        )

        logger.info(
            f"RAG DONE | "
            f"intent={intent} | "
            f"provider={llm_provider} | "
            f"model={model} | "
            f"{elapsed}s | "
            f"tokens={in_tokens + out_tokens}"
        )

        response = {
            "question": question,
            "answer": answer,
            "sources": list(
                set([s["source"] for s in result["sources"]])
            ),
            "response_time": elapsed,
            "tokens": in_tokens + out_tokens,
            "cost": estimate_cost(
                in_tokens,
                out_tokens,
                provider=llm_provider,
                model=model,
            ),

            # ========================
            # AGENT METADATA
            # ========================
            "intent": intent,
            "tool": tool,
            "llm_provider": llm_provider,
            "model": model,
        }

        if include_context:

            response["retrieval_context"] = [
                source["content"]
                for source in result["sources"]
            ]

        return response

    except Exception:

        logger.exception("RAG FAILED")

        return {
            "question": question,
            "answer": "Error processing request",
            "sources": [],
            "response_time": 0,
            "tokens": 0,
            "cost": 0.0,
            "intent": intent,
            "tool": tool,
            "llm_provider": llm_provider,
            "model": model or get_default_model(
                llm_provider
            ),
        }
