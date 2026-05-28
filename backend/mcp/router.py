from backend.mcp.registry import TOOLS


def normalize_intent(intent):

    if hasattr(intent, "value"):
        return intent.value

    intent = str(intent)

    if intent.startswith("Intent."):
        return intent.split(".", 1)[1]

    return intent


def route_tool(intent, question):

    intent = normalize_intent(
        intent
    )

    q = question.lower()

    if (
        intent == "HEALTH"
        or any(
            keyword in q
            for keyword in [
                "healthy",
                "health",
                "status",
                "diagnostic",
                "is the vector db healthy",
            ]
        )
    ):
        return "health", TOOLS["health"]

    if (
        intent == "METRICS"
        or any(
            keyword in q
            for keyword in [
                "evaluation metrics",
                "deepeval",
                "baseline",
                "latest metrics",
                "score",
            ]
        )
    ):
        return "metrics", TOOLS["metrics"]

    if (
        intent == "VECTOR"
        or any(
            keyword in q
            for keyword in [
                "chunks",
                "indexed",
                "vector",
                "collection",
                "documents indexed",
            ]
        )
    ):
        return "vector_stats", TOOLS["vector_stats"]

    if (
        intent == "THREAD"
        or any(
            keyword in q
            for keyword in [
                "discuss earlier",
                "previous conversation",
                "thread",
                "history",
                "earlier",
                "conversation history",
                "recent questions",
                "chat history",
            ]
        )
    ):
        return "thread_history", TOOLS["thread_history"]

    return "retrieval", TOOLS["retrieval"]
