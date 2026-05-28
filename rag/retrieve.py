import re

from llm.client import get_embedding, ask_llm
from rag.vector_store import query_chunks

from backend.utils.logger import logger


# ========================
# INTENT SOURCE MAP
# ========================
INTENT_SOURCE_MAP = {
    "AUTH": "razorpay_auth.txt",
    "PAYMENTS": "razorpay_payments.txt",
    "ERRORS": "razorpay_errors.txt",
    "WEBHOOKS": "razorpay_webhooks.txt",
}


# ========================
# WORD LIMIT EXTRACTION
# ========================
def extract_word_limit(user_query):

    match = re.search(
        r"(\\d+)\\s*words?",
        user_query.lower()
    )

    if match:
        return int(match.group(1))

    return None


# ========================
# PROMPT BUILDER
# ========================
def build_length_instruction(word_limit):

    if not word_limit:
        return ""

    return f"""
Your response MUST NOT exceed {word_limit} words.
Ensure the response is complete, coherent, technically accurate,
and fits naturally within the requested word count.
Compress aggressively when necessary.
"""


def build_base_prompt(
    context,
    user_query,
    word_limit=None,
    intent_guidance="",
):

    length_instruction = build_length_instruction(
        word_limit
    )

    return f"""
You are an expert API integration assistant.

Use ONLY the provided context to answer the user's question.

If the context is insufficient, clearly state that the available documentation
does not provide a complete answer.

Context:
{context}

User Question:
{user_query}

{length_instruction}

Intent-Specific Guidance:
{intent_guidance}

Response Requirements:
- Be concise, technical, and developer-focused
- Prioritize actionable implementation guidance
- Directly address the user's intent before adding supporting details
- Use clear markdown formatting
- Structure answers with:
  ## Summary
  ## Technical Steps
  ## Best Practices
- Avoid unnecessary verbosity
"""


def build_prompt(
    context,
    user_query,
    word_limit=None,
):

    return build_base_prompt(
        context=context,
        user_query=user_query,
        word_limit=word_limit,
        intent_guidance="""
Answer as a general API integration assistant.
Focus on the most relevant implementation details from the retrieved context.
""",
    )


def build_auth_prompt(
    context,
    user_query,
    word_limit=None,
):

    return build_base_prompt(
        context=context,
        user_query=user_query,
        word_limit=word_limit,
        intent_guidance="""
Focus on authentication concepts:
- Credentials and API keys
- Required authorization headers
- Request authentication flow
- Credential handling and security practices
- Common authentication implementation mistakes
""",
    )


def build_payments_prompt(
    context,
    user_query,
    word_limit=None,
):

    return build_base_prompt(
        context=context,
        user_query=user_query,
        word_limit=word_limit,
        intent_guidance="""
Focus on payment implementation:
- Payment creation and capture flow
- Relevant payment APIs and lifecycle states
- Reconciliation and transaction tracking
- Refunds, orders, invoices, or capture behavior when relevant
- Operational best practices for payment integrations
""",
    )


def build_errors_prompt(
    context,
    user_query,
    word_limit=None,
):

    return build_base_prompt(
        context=context,
        user_query=user_query,
        word_limit=word_limit,
        intent_guidance="""
Focus on debugging and remediation:
- Likely root causes
- What to inspect in request payloads, credentials, OTPs, callbacks, or logs
- Concrete debugging steps
- Remediation actions
- How to prevent recurrence in production integrations
""",
    )


def build_webhooks_prompt(
    context,
    user_query,
    word_limit=None,
):

    return build_base_prompt(
        context=context,
        user_query=user_query,
        word_limit=word_limit,
        intent_guidance="""
Focus on webhook implementation:
- Event delivery flow
- Signature validation and endpoint security
- Retry behavior and idempotency
- Event handling, persistence, and reconciliation
- Production validation and monitoring practices
""",
    )


PROMPT_BUILDERS = {
    "AUTH": build_auth_prompt,
    "PAYMENTS": build_payments_prompt,
    "ERRORS": build_errors_prompt,
    "WEBHOOKS": build_webhooks_prompt,
}


def get_prompt_builder(intent):

    intent = str(intent)

    if intent.startswith("Intent."):
        intent = intent.split(".", 1)[1]

    return PROMPT_BUILDERS.get(
        intent,
        build_prompt
    )


# ========================
# COMPRESSION PROMPT
# ========================
def build_compression_prompt(
    answer,
    word_limit
):

    return f"""
You are an expert technical editor.

Rewrite the following API guidance response to {word_limit} words maximum.

Requirements:
- Preserve technical accuracy
- Preserve completeness
- Preserve markdown formatting
- Preserve developer usefulness
- Keep sections:
  ## Summary
  ## Technical Steps
  ## Best Practices
- Remove redundancy
- Ensure response is polished and coherent
- Do NOT exceed {word_limit} words

Original Response:
{answer}
"""


# ========================
# WORD COUNT
# ========================
def count_words(text):
    return len(text.split())


# ========================
# MAIN RAG PIPELINE
# ========================
def answer_query(
    user_query,
    top_k=2,
    intent="GENERAL",
):

    # ========================
    # WORD LIMIT
    # ========================
    word_limit = extract_word_limit(
        user_query
    )

    # ========================
    # EMBEDDING
    # ========================
    query_embedding = get_embedding(
        user_query
    )

    # ========================
    # SOURCE FILTER
    # ========================
    source_filter = INTENT_SOURCE_MAP.get(
        intent
    )

    logger.info(
        f"RETRIEVAL START | "
        f"intent={intent} | "
        f"source_filter={source_filter}"
    )

    # ========================
    # VECTOR RETRIEVAL
    # ========================
    results = query_chunks(
        query_embedding,
        top_k=top_k,
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

    # ========================
    # CONTEXT BUILDING
    # ========================
    context = "\n\n".join(documents)

    # ========================
    # PROMPT GENERATION
    # ========================
    prompt_builder = get_prompt_builder(
        intent
    )

    primary_prompt = prompt_builder(
        context=context,
        user_query=user_query,
        word_limit=word_limit,
    )

    answer = ask_llm(primary_prompt)

    # ========================
    # COMPRESSION PASS
    # ========================
    if (
        word_limit
        and count_words(answer) > word_limit
    ):

        compression_prompt = (
            build_compression_prompt(
                answer=answer,
                word_limit=word_limit,
            )
        )

        compressed_answer = ask_llm(
            compression_prompt
        )

        if (
            count_words(compressed_answer)
            <= word_limit
        ):
            answer = compressed_answer

    # ========================
    # FINAL SAFEGUARD
    # ========================
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

            sentence_word_count = (
                count_words(sentence)
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

    # ========================
    # SOURCES
    # ========================
    sources = [
        {
            "source": metadata["source"],
            "content": document,
        }
        for document, metadata in zip(
            documents,
            metadatas,
        )
    ]

    return {
        "answer": answer,
        "sources": sources,
    }
