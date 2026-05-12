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
    Intent.GENERAL: {
        "collection": "general"
    },
}