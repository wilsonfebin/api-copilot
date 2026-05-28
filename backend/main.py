from fastapi import FastAPI, Request, Response
import time
from collections import defaultdict
import asyncio

from backend.routes.query import router as query_router
from backend.routes.health import router as health_router
from backend.routes.metrics import router as metrics_router

from backend.utils.logger import logger
from backend.config import RATE_LIMIT, RATE_WINDOW, MAX_CONCURRENT_REQS

app = FastAPI()

QUERY_PATHS = {
    "/query",
    "/query/stream",
}

# ========================
# RATE LIMIT (per IP, /query only)
# ========================
request_log = defaultdict(list)

# ========================
# CONCURRENCY CONTROL
# ========================
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQS)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):

    # Only limit expensive query endpoints
    if request.url.path not in QUERY_PATHS:
        return await call_next(request)

    client_ip = request.client.host
    now = time.time()
    window_start = now - RATE_WINDOW

    # Clean old
    request_log[client_ip] = [
        t for t in request_log[client_ip] if t > window_start
    ]

    current_count = len(request_log[client_ip])
    logger.info(f"RATE STATUS | {client_ip} | {current_count}/{RATE_LIMIT}")

    if current_count >= RATE_LIMIT:
        logger.warning(f"RATE LIMIT HIT | {client_ip}")
        return Response(content="Too many requests", status_code=429)

    request_log[client_ip].append(now)

    return await call_next(request)


@app.middleware("http")
async def concurrency_limit_middleware(request: Request, call_next):
    # Only gate expensive query endpoints
    if request.url.path not in QUERY_PATHS:
        return await call_next(request)

    async with semaphore:
        return await call_next(request)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        duration = round(time.time() - start, 3)
        logger.info(f"{request.method} {request.url.path} | {response.status_code} | {duration}s")
        return response
    except Exception:
        logger.exception(f"Request failed: {request.url.path}")
        raise


# ========================
# ROUTES
# ========================
app.include_router(query_router)
app.include_router(health_router)
app.include_router(metrics_router)
