import re
import time

from backend.agents.intent_router import classify_query
from backend.config import (
    DEFAULT_LLM_PROVIDER,
    ENABLE_MCP,
    get_default_model,
)
from backend.guardrails.validator import run_guardrails
from backend.mcp.router import route_tool
from backend.utils.logger import logger
from llm.client import ask_llm, get_embedding
from rag.retrieve import (
    INTENT_SOURCE_MAP,
    build_compression_prompt,
    count_words,
    extract_word_limit,
    get_prompt_builder,
)
from rag.vector_store import query_chunks


def normalize_intent(intent):

    if hasattr(intent, "value"):
        return intent.value

    intent = str(intent)

    if intent.startswith("Intent."):
        return intent.split(".", 1)[1]

    return intent


def is_direct_mcp_tool(tool_result):

    if not tool_result:
        return False

    return tool_result.get(
        "tool_name"
    ) not in [
        "RetrievalTool",
        "MCPDisabled",
    ]


def build_tool_response_prompt(
    question,
    tool_name,
    tool_result,
):

    return f"""
You are API Copilot.

The user asked:
{question}

The MCP tool `{tool_name}` returned:
{tool_result}

Answer using ONLY this tool result.

Rules:
- Do not say the context is missing.
- Do not search Razorpay documents.
- Do not mention unavailable documentation.
- Be concise and operational.
- Use markdown.
"""


def intent_node(state):

    start = time.time()

    logger.info(
        "LANGGRAPH NODE | IntentNode"
    )

    question = state["question"]
    intent = state.get("intent")

    if intent:
        intent = normalize_intent(
            intent
        )
    else:
        intent = normalize_intent(
            classify_query(question)
        )

    metadata = state.get(
        "metadata",
        {}
    )

    metadata["word_limit"] = extract_word_limit(
        question
    )

    elapsed = round(
        time.time() - start,
        3
    )

    logger.info(
        f"GRAPH STATE | intent={intent}"
    )

    logger.info(
        f"NODE TIME | IntentNode | {elapsed}s"
    )

    return {
        "intent": intent,
        "metadata": metadata,
    }


def retrieval_node(state):

    start = time.time()

    logger.info(
        "LANGGRAPH NODE | RetrievalNode"
    )

    question = state["question"]
    intent = state.get(
        "intent",
        "GENERAL"
    )

    tool_result = state.get(
        "tool_result"
    )

    is_direct_tool_response = state.get(
        "is_direct_tool_response",
        False
    )

    if (
        is_direct_tool_response
        and tool_result
    ):

        tool_name = tool_result["tool_name"]
        tool_content = str(
            tool_result.get(
                "data",
                {}
            )
        )

        elapsed = round(
            time.time() - start,
            3
        )

        logger.info(
            "SKIP RETRIEVAL | "
            "direct_tool_response=True"
        )

        logger.info(
            f"RETRIEVAL SKIPPED | "
            f"intent={intent} | "
            f"tool={tool_name}"
        )

        logger.info(
            f"GRAPH STATE | sources=['mcp:{tool_name}']"
        )

        logger.info(
            f"NODE TIME | RetrievalNode | {elapsed}s"
        )

        return {
            "retrieved_context": [
                tool_content
            ],
            "sources": [
                {
                    "source": f"mcp:{tool_name}",
                    "content": tool_content,
                }
            ],
        }

    query_embedding = get_embedding(
        question
    )

    source_filter = INTENT_SOURCE_MAP.get(
        intent
    )

    logger.info(
        f"RETRIEVAL START | "
        f"intent={intent} | "
        f"source_filter={source_filter}"
    )

    metadata = state.get(
        "metadata",
        {}
    )

    results = query_chunks(
        query_embedding,
        top_k=metadata.get(
            "top_k",
            2
        ),
        source_filter=source_filter
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    retrieved_sources = [
        meta["source"]
        for meta in metadatas
    ]

    logger.info(
        f"RETRIEVAL SOURCES | "
        f"{retrieved_sources}"
    )

    sources = [
        {
            "source": meta["source"],
            "content": document,
        }
        for document, meta in zip(
            documents,
            metadatas,
        )
    ]

    elapsed = round(
        time.time() - start,
        3
    )

    logger.info(
        f"GRAPH STATE | sources={retrieved_sources}"
    )

    logger.info(
        f"NODE TIME | RetrievalNode | {elapsed}s"
    )

    return {
        "retrieved_context": documents,
        "sources": sources,
    }


def tool_node(state):

    start = time.time()

    logger.info(
        "LANGGRAPH NODE | ToolNode"
    )

    intent = state.get(
        "intent",
        "GENERAL"
    )

    metadata = state.get(
        "metadata",
        {}
    )

    if not ENABLE_MCP:

        result = {
            "tool_name": "MCPDisabled",
            "data": {},
            "error": None,
        }

        metadata["mcp_tool"] = "disabled"
        metadata["tool_name"] = result["tool_name"]
        metadata["is_direct_tool_response"] = False

    else:

        tool_key, tool = route_tool(
            intent=intent,
            question=state["question"]
        )

        logger.info(
            f"MCP ROUTER | intent={intent} | "
            f"tool={tool_key}"
        )

        result = tool.run(
            question=state["question"],
            state=state,
        )

        logger.info(
            f"MCP TOOL | {result['tool_name']}"
        )

        logger.info(
            f"MCP RESULT | {result}"
        )

        metadata["mcp_tool"] = tool_key
        metadata["tool_name"] = result["tool_name"]
        metadata["is_direct_tool_response"] = (
            is_direct_mcp_tool(
                result
            )
        )

        if metadata["is_direct_tool_response"]:
            logger.info(
                f"MCP DIRECT RESPONSE | "
                f"tool={result['tool_name']}"
            )

    elapsed = round(
        time.time() - start,
        3
    )

    logger.info(
        f"NODE TIME | ToolNode | {elapsed}s"
    )

    return {
        "tool_name": result["tool_name"],
        "tool_result": result,
        "is_direct_tool_response": metadata[
            "is_direct_tool_response"
        ],
        "metadata": metadata,
    }


def prompt_node(state):

    start = time.time()

    logger.info(
        "LANGGRAPH NODE | PromptNode"
    )

    metadata = state.get(
        "metadata",
        {}
    )

    tool_result = state.get(
        "tool_result"
    )

    is_direct_tool_response = state.get(
        "is_direct_tool_response",
        False
    )

    if (
        is_direct_tool_response
        and tool_result
    ):

        tool_name = state.get(
            "tool_name",
            tool_result["tool_name"]
        )

        logger.info(
            f"TOOL RESPONSE PROMPT | "
            f"tool={tool_name}"
        )

        prompt = build_tool_response_prompt(
            question=state["question"],
            tool_name=tool_name,
            tool_result=tool_result,
        )

        elapsed = round(
            time.time() - start,
            3
        )

        logger.info(
            f"NODE TIME | PromptNode | {elapsed}s"
        )

        return {
            "prompt": prompt,
        }

    prompt_builder = get_prompt_builder(
        state.get(
            "intent",
            "GENERAL"
        )
    )

    context = "\n\n".join(
        state.get(
            "retrieved_context",
            []
        )
    )

    if tool_result:

        tool_context = (
            f"Tool Context:\n{tool_result}"
        )

        if is_direct_mcp_tool(
            tool_result
        ):
            context = tool_context
        else:
            context = (
                f"{context}\n\n"
                f"{tool_context}"
            )

    prompt = prompt_builder(
        context=context,
        user_query=state["question"],
        word_limit=metadata.get(
            "word_limit"
        ),
    )

    elapsed = round(
        time.time() - start,
        3
    )

    logger.info(
        f"NODE TIME | PromptNode | {elapsed}s"
    )

    return {
        "prompt": prompt,
    }


def response_generation_node(state):

    start = time.time()

    logger.info(
        "LANGGRAPH NODE | ResponseNode"
    )

    metadata = state.get(
        "metadata",
        {}
    )

    llm_provider = state.get(
        "llm_provider",
        metadata.get(
            "llm_provider",
            DEFAULT_LLM_PROVIDER
        )
    )

    model = state.get(
        "model",
        metadata.get(
            "model",
            get_default_model(
                llm_provider
            )
        )
    )

    logger.info(
        f"LLM PROVIDER | provider={llm_provider} | "
        f"model={model}"
    )

    answer = ask_llm(
        state["prompt"],
        provider=llm_provider,
        model=model,
    )

    word_limit = metadata.get(
        "word_limit"
    )

    if (
        word_limit
        and count_words(answer) > word_limit
    ):

        compression_prompt = build_compression_prompt(
            answer=answer,
            word_limit=word_limit,
        )

        compressed_answer = ask_llm(
            compression_prompt,
            provider=llm_provider,
            model=model,
        )

        if (
            count_words(compressed_answer)
            <= word_limit
        ):
            answer = compressed_answer

    if (
        word_limit
        and count_words(answer) > word_limit
    ):

        sentences = re.split(
            r'(?<=[.!?]) +',
            answer
        )

        trimmed = []
        current_word_count = 0

        for sentence in sentences:

            sentence_word_count = count_words(
                sentence
            )

            if (
                current_word_count
                + sentence_word_count
                <= word_limit
            ):

                trimmed.append(sentence)
                current_word_count += (
                    sentence_word_count
                )

            else:
                break

        answer = " ".join(trimmed)

    elapsed = round(
        time.time() - start,
        3
    )

    logger.info(
        f"NODE TIME | ResponseNode | {elapsed}s"
    )

    return {
        "answer": answer,
    }


def validation_node(state):

    start = time.time()

    logger.info(
        "LANGGRAPH NODE | ValidationNode"
    )

    answer = state.get(
        "answer",
        ""
    )

    sources = state.get(
        "sources",
        []
    )

    if not answer:
        logger.warning(
            "GRAPH VALIDATION | missing_answer"
        )

    if not sources:
        logger.warning(
            "GRAPH VALIDATION | missing_sources"
        )

    guardrail_result = run_guardrails(
        state
    )

    logger.info(
        f"GUARDRAIL CHECK | "
        f"passed={guardrail_result['passed']}"
    )

    for warning in guardrail_result["warnings"]:
        logger.warning(
            f"GUARDRAIL WARNING | {warning}"
        )

    metadata = state.get(
        "metadata",
        {}
    )

    metadata["guardrails"] = guardrail_result

    if not guardrail_result["passed"]:

        logger.error(
            f"GUARDRAIL BLOCKED | "
            f"{guardrail_result['blocked_reason']}"
        )

        elapsed = round(
            time.time() - start,
            3
        )

        logger.info(
            f"NODE TIME | ValidationNode | {elapsed}s"
        )

        return {
            "answer": "Request blocked by safety validation.",
            "sources": [],
            "metadata": metadata,
        }

    elapsed = round(
        time.time() - start,
        3
    )

    logger.info(
        f"NODE TIME | ValidationNode | {elapsed}s"
    )

    return {
        "answer": answer or "Error processing request",
        "sources": sources,
        "metadata": metadata,
    }
