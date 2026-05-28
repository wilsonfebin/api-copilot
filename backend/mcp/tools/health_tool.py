from backend.config import ENABLE_GUARDRAILS, ENABLE_MCP
from backend.mcp.models import MCPToolResult
from llm.client import client
from rag.vector_store import get_collection


class HealthTool:
    name = "HealthTool"

    def run(self, question: str, state: dict):

        openai_ok = bool(
            getattr(
                client,
                "api_key",
                None
            )
        )

        try:
            get_collection()
            vector_ok = True
        except Exception:
            vector_ok = False

        return MCPToolResult(
            tool_name=self.name,
            data={
                "openai": openai_ok,
                "vector_db": vector_ok,
                "langgraph": True,
                "guardrails": ENABLE_GUARDRAILS,
                "mcp": ENABLE_MCP,
            },
        ).to_dict()
