from typing import Any, TypedDict


class RAGGraphState(TypedDict, total=False):
    question: str
    intent: str
    tool_result: dict[str, Any]
    retrieved_context: list[str]
    prompt: str
    answer: str
    sources: list[dict[str, str]]
    metadata: dict[str, Any]
