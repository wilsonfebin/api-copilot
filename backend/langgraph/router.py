from backend.config import TOP_K
from backend.langgraph.graph import get_rag_graph


def run_rag_graph(
    question: str,
    intent: str = "GENERAL",
    tool: dict | None = None,
):

    graph = get_rag_graph()

    initial_state = {
        "question": question,
        "intent": intent,
        "metadata": {
            "tool": tool,
            "top_k": TOP_K,
        },
    }

    return graph.invoke(
        initial_state
    )
