from backend.mcp.tools.health_tool import HealthTool
from backend.mcp.tools.metrics_tool import MetricsTool
from backend.mcp.tools.retrieval_tool import RetrievalTool
from backend.mcp.tools.thread_tool import ThreadHistoryTool
from backend.mcp.tools.vector_tool import VectorStatsTool


TOOLS = {
    "health": HealthTool(),
    "vector_stats": VectorStatsTool(),
    "metrics": MetricsTool(),
    "retrieval": RetrievalTool(),
    "thread_history": ThreadHistoryTool(),
}
