from functools import lru_cache

from langgraph.graph import END, START, StateGraph

from backend.langgraph.nodes import (
    intent_node,
    prompt_node,
    response_generation_node,
    retrieval_node,
    tool_node,
    validation_node,
)
from backend.langgraph.state import RAGGraphState


@lru_cache(maxsize=1)
def get_rag_graph():

    graph = StateGraph(
        RAGGraphState
    )

    graph.add_node(
        "intent",
        intent_node
    )

    graph.add_node(
        "retrieval",
        retrieval_node
    )

    graph.add_node(
        "tool",
        tool_node
    )

    graph.add_node(
        "prompt",
        prompt_node
    )

    graph.add_node(
        "response_generation",
        response_generation_node
    )

    graph.add_node(
        "validation",
        validation_node
    )

    graph.add_edge(
        START,
        "intent"
    )

    graph.add_edge(
        "intent",
        "tool"
    )

    graph.add_edge(
        "tool",
        "retrieval"
    )

    graph.add_edge(
        "retrieval",
        "prompt"
    )

    graph.add_edge(
        "prompt",
        "response_generation"
    )

    graph.add_edge(
        "response_generation",
        "validation"
    )

    graph.add_edge(
        "validation",
        END
    )

    return graph.compile()
