from llm.client import get_embedding, ask_llm
from rag.vector_store import query_chunks


def answer_query(user_query, top_k=3):
    query_embedding = get_embedding(user_query)

    results = query_chunks(query_embedding, top_k=top_k)

    retrieved_docs = results["documents"][0]
    sources = results["metadatas"][0]

    context = "\n\n".join(retrieved_docs)

    prompt = f"""
You are an expert API integration assistant.

Use ONLY the provided context to answer the user's question.

Context:
{context}

User Question:
{user_query}

Provide a clear, technical, developer-focused answer.
"""

    answer = ask_llm(prompt)

    return {
        "answer": answer,
        "sources": sources
    }
