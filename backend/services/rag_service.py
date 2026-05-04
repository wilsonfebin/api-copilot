import time
from functools import lru_cache
from backend.utils.logger import logger
from backend.config import RETRY_COUNT, RETRY_DELAY, REQUEST_TIMEOUT, TOP_K, CACHE_SIZE

from rag.retrieve import answer_query
from utils.metrics import estimate_tokens, estimate_cost


# ========================
# CACHED RAG CALL
# ========================
@lru_cache(maxsize=CACHE_SIZE)
def cached_answer(question: str):
    return answer_query(question, top_k=TOP_K)


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
            logger.warning(f"Retry {attempt+1} after error: {str(e)}")
            time.sleep(RETRY_DELAY)


# ========================
# MAIN SERVICE FUNCTION
# ========================
def run_query(question: str):
    try:
        start = time.time()
        logger.info(f"RAG START | {question}")

        def execute():
            return cached_answer(question)

        result = retry_call(execute)

        elapsed = round(time.time() - start, 2)

        if elapsed > REQUEST_TIMEOUT:
            logger.warning(f"SLOW RESPONSE | {elapsed}s")

        answer = result["answer"]

        in_tokens = estimate_tokens(question)
        out_tokens = estimate_tokens(answer)

        logger.info(f"RAG DONE | {elapsed}s | tokens={in_tokens + out_tokens}")

        return {
            "question": question,
            "answer": answer,
            "sources": list(set([s["source"] for s in result["sources"]])),
            "response_time": elapsed,
            "tokens": in_tokens + out_tokens,
            "cost": estimate_cost(in_tokens, out_tokens)
        }

    except Exception:
        logger.exception("RAG FAILED")

        return {
            "question": question,
            "answer": "Error processing request",
            "sources": [],
            "response_time": 0,
            "tokens": 0,
            "cost": 0.0
        }
