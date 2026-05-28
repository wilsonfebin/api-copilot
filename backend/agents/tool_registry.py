from backend.agents.intent_router import Intent


TOOL_REGISTRY = {
    Intent.AUTH: {
        "collection": "auth"
    },
    Intent.PAYMENTS: {
        "collection": "payments"
    },
    Intent.ERRORS: {
        "collection": "errors"
    },
    Intent.WEBHOOKS: {
        "collection": "webhooks"
    },
    Intent.VECTOR: {
        "collection": "mcp_vector_stats"
    },
    Intent.METRICS: {
        "collection": "mcp_metrics"
    },
    Intent.HEALTH: {
        "collection": "mcp_health"
    },
    Intent.THREAD: {
        "collection": "mcp_thread_history"
    },
    Intent.GENERAL: {
        "collection": "general"
    },
}
