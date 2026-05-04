from fastapi import FastAPI
from backend.routes.query import router as query_router
from backend.routes.health import router as health_router

app = FastAPI(
    title="API Copilot Backend",
    version="1.0.0"
)

# Routes
app.include_router(query_router)
app.include_router(health_router)
