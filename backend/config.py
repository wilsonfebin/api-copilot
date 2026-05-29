import os

# ========================
# TRAFFIC
# ========================
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 20))
RATE_WINDOW = int(os.getenv("RATE_WINDOW", 60))
MAX_CONCURRENT_REQS = int(os.getenv("MAX_CONCURRENT_REQS", 5))

# ========================
# RESILIENCE
# ========================
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10))  # seconds
RETRY_COUNT = int(os.getenv("RETRY_COUNT", 2))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", 0.5))

# ========================
# CACHE
# ========================
CACHE_SIZE = int(os.getenv("CACHE_SIZE", 50))

# ========================
# RAG
# ========================
TOP_K = int(os.getenv("TOP_K", 2))

# ========================
# MCP
# ========================
ENABLE_MCP = (
    os.getenv("ENABLE_MCP", "true").lower()
    == "true"
)

# ========================
# GUARDRAILS
# ========================
ENABLE_GUARDRAILS = (
    os.getenv("ENABLE_GUARDRAILS", "true").lower()
    == "true"
)
MIN_RESPONSE_LENGTH = int(os.getenv("MIN_RESPONSE_LENGTH", 20))
MAX_RESPONSE_WORDS = int(os.getenv("MAX_RESPONSE_WORDS", 500))

# ========================
# LLM
# ========================
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 500))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.2))

SUPPORTED_MODELS = {
    "openai": [
        "gpt-4.1-mini",
    ],
    "claude": [
        "claude-haiku-4-5-20251001",
    ],
}

DEFAULT_LLM_PROVIDER = os.getenv(
    "DEFAULT_LLM_PROVIDER",
    "openai"
)


def get_supported_models(provider):
    return SUPPORTED_MODELS.get(
        provider,
        SUPPORTED_MODELS[DEFAULT_LLM_PROVIDER]
    )


def get_default_model(provider=DEFAULT_LLM_PROVIDER):
    return get_supported_models(provider)[0]


MODEL_PRICING_USD_PER_M_TOKENS = {
    (
        "openai",
        get_default_model("openai")
    ): (0.60, 1.60),
    (
        "claude",
        get_default_model("claude")
    ): (1.00, 5.00),
}
