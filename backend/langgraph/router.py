from backend.config import (
    DEFAULT_LLM_PROVIDER,
    TOP_K,
    get_default_model,
)
from backend.langgraph.graph import get_rag_graph


def run_rag_graph(
    question: str,
    intent: str = "GENERAL",
    tool: dict | None = None,
    llm_provider: str = DEFAULT_LLM_PROVIDER,
    model: str | None = None,
):
    model = model or get_default_model(
        llm_provider
    )

    graph = get_rag_graph()

    initial_state = {
        "question": question,
        "intent": intent,
        "llm_provider": llm_provider,
        "model": model,
        "metadata": {
            "tool": tool,
            "top_k": TOP_K,
            "llm_provider": llm_provider,
            "model": model,
        },
    }

    return graph.invoke(
        initial_state
    )
