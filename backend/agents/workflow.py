from backend.agents.intent_router import classify_query
from backend.agents.tool_registry import TOOL_REGISTRY


def run_agentic_flow(query: str):

    # STEP 1 — classify intent
    intent = classify_query(query)

    # STEP 2 — select retrieval tool
    tool = TOOL_REGISTRY[intent]

    return {
        "intent": intent,
        "tool": tool
    }