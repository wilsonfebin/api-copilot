from backend.mcp.models import MCPToolResult


class RetrievalTool:
    name = "RetrievalTool"

    def run(self, question: str, state: dict):

        return MCPToolResult(
            tool_name=self.name,
            data={
                "mode": "rag_retrieval",
                "intent": state.get(
                    "intent",
                    "GENERAL"
                ),
                "message": (
                    "Retrieval is handled by the LangGraph "
                    "RetrievalNode using existing query_chunks logic."
                ),
            },
        ).to_dict()
