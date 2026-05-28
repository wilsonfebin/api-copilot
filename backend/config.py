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
