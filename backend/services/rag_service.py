import time
from functools import lru_cache

from rag.retrieve import answer_query
from utils.metrics import estimate_tokens, estimate_cost


# ========================
# CACHED RAG CALL
# ========================
@lru_cache(maxsize=50)
def cached_answer(question: str):
    """
    Cache RAG responses for repeated identical queries.
    """
    return answer_query(question, top_k=2)


# ========================
# MAIN SERVICE FUNCTION
# ========================
def run_query(question: str):
    try:
        start = time.time()

        # Use cached version
        result = cached_answer(question)

        elapsed = round(time.time() - start, 2)

        answer = result["answer"]

        in_tokens = estimate_tokens(question)
        out_tokens = estimate_tokens(answer)

        return {
            "question": question,
            "answer": answer,
            "sources": list(set([s["source"] for s in result["sources"]])),
            "response_time": elapsed,
            "tokens": in_tokens + out_tokens,
            "cost": estimate_cost(in_tokens, out_tokens)
        }

    except Exception as e:
        return {
            "question": question,
            "answer": "Error processing request",
            "sources": [],
            "response_time": 0,
            "tokens": 0,
            "cost": 0.0
        }
