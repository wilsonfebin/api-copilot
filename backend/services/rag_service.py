import time
from functools import lru_cache

from backend.utils.logger import logger
from backend.config import (
    RETRY_COUNT,
    RETRY_DELAY,
    REQUEST_TIMEOUT,
    TOP_K,
    CACHE_SIZE,
)

from rag.retrieve import answer_query
from utils.metrics import estimate_tokens, estimate_cost


def normalize_intent(intent):

    if hasattr(intent, "value"):
        return intent.value

    intent = str(intent)

    if intent.startswith("Intent."):
        return intent.split(".", 1)[1]

    return intent


# ========================
# CACHED RAG CALL
# ========================
@lru_cache(maxsize=CACHE_SIZE)
def cached_answer(question: str, intent: str = "GENERAL"):
    return answer_query(
        question,
        top_k=TOP_K,
        intent=intent
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
):

    try:

        intent = normalize_intent(
            intent
        )

        start = time.time()

        logger.info(
            f"RAG START | intent={intent} | question={question}"
        )

        # ========================
        # EXECUTE RAG
        # ========================
        def execute():

            return cached_answer(
                question,
                intent
            )

        result = retry_call(execute)

        elapsed = round(time.time() - start, 2)

        if elapsed > REQUEST_TIMEOUT:
            logger.warning(f"SLOW RESPONSE | {elapsed}s")

        answer = result["answer"]

        in_tokens = estimate_tokens(question)
        out_tokens = estimate_tokens(answer)

        logger.info(
            f"RAG DONE | "
            f"intent={intent} | "
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
            "cost": estimate_cost(in_tokens, out_tokens),

            # ========================
            # AGENT METADATA
            # ========================
            "intent": intent,
            "tool": tool,
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
        }
