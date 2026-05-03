import re
from llm.client import get_embedding, ask_llm
from rag.vector_store import query_chunks


def extract_word_limit(user_query):
    """
    Detect requested word count from user query.
    Examples:
    - 'reply in 150 words'
    - 'explain in 200 words'
    """
    match = re.search(r'(\d+)\s*words?', user_query.lower())
    if match:
        return int(match.group(1))
    return None


def build_prompt(context, user_query, word_limit=None):
    """
    Build primary answer generation prompt.
    """

    length_instruction = ""

    if word_limit:
        length_instruction = f"""
Your response MUST NOT exceed {word_limit} words.
Ensure the response is complete, coherent, technically accurate,
and fits naturally within the requested word count.
Compress aggressively when necessary.
"""

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

Response Requirements:
- Be concise, technical, and developer-focused
- Prioritize actionable implementation guidance
- Use clear markdown formatting
- Structure answers with:
  ## Summary
  ## Technical Steps
  ## Best Practices
- Avoid unnecessary verbosity
"""


def build_compression_prompt(answer, word_limit):
    """
    Secondary compression pass if initial answer exceeds limit.
    """

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


def count_words(text):
    return len(text.split())


def answer_query(user_query, top_k=3):
    """
    Full RAG pipeline:
    - Retrieve relevant chunks
    - Generate answer
    - Intelligently compress if user requested length
    """

    # Detect word limit
    word_limit = extract_word_limit(user_query)

    # Embed query
    query_embedding = get_embedding(user_query)

    # Retrieve chunks
    results = query_chunks(query_embedding, top_k=top_k)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Build context
    context = "\n\n".join(documents)

    # Generate initial answer
    primary_prompt = build_prompt(
        context=context,
        user_query=user_query,
        word_limit=word_limit
    )

    answer = ask_llm(primary_prompt)

    # Intelligent compression pass
    if word_limit and count_words(answer) > word_limit:

        compression_prompt = build_compression_prompt(
            answer=answer,
            word_limit=word_limit
        )

        compressed_answer = ask_llm(compression_prompt)

        # Use compressed version only if valid
        if count_words(compressed_answer) <= word_limit:
            answer = compressed_answer

    # Final safeguard: sentence-aware fallback
    if word_limit and count_words(answer) > word_limit:
        sentences = re.split(r'(?<=[.!?]) +', answer)

        trimmed = []
        current_word_count = 0

        for sentence in sentences:
            sentence_word_count = count_words(sentence)

            if current_word_count + sentence_word_count <= word_limit:
                trimmed.append(sentence)
                current_word_count += sentence_word_count
            else:
                break

        answer = " ".join(trimmed)

    # Sources
    sources = [
        {
            "source": metadata["source"],
            "content": document
        }
        for document, metadata in zip(documents, metadatas)
    ]

    return {
        "answer": answer,
        "sources": sources
    }
