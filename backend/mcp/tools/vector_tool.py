from backend.mcp.models import MCPToolResult
from rag.vector_store import get_vector_stats


class VectorStatsTool:
    name = "VectorStatsTool"

    def run(self, question: str, state: dict):

        stats = get_vector_stats()

        return MCPToolResult(
            tool_name=self.name,
            data={
                "documents": stats["documents"],
                "chunks": stats["chunks"],
                "collection_status": "active",
            },
        ).to_dict()
