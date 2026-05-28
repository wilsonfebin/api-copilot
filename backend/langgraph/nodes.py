import re
import time

from backend.agents.intent_router import classify_query
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


def prompt_node(state):

    start = time.time()

    logger.info(
        "LANGGRAPH NODE | PromptNode"
    )

    metadata = state.get(
        "metadata",
        {}
    )

    prompt_builder = get_prompt_builder(
        state.get(
            "intent",
            "GENERAL"
        )
    )

    prompt = prompt_builder(
        context="\n\n".join(
            state.get(
                "retrieved_context",
                []
            )
        ),
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

    answer = ask_llm(
        state["prompt"]
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
            compression_prompt
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
    }
