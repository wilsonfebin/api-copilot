from typing import Any, TypedDict


class RAGGraphState(TypedDict, total=False):
    question: str
    intent: str
    llm_provider: str
    model: str
    tool_name: str
    tool_result: dict[str, Any]
    is_direct_tool_response: bool
    retrieved_context: list[str]
    prompt: str
    answer: str
    sources: list[dict[str, str]]
    metadata: dict[str, Any]
