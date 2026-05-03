from llm.client import get_embedding


def embed_chunks(chunks):
    embedded_chunks = []

    for chunk in chunks:
        embedding = get_embedding(chunk["content"])

        embedded_chunks.append({
            "id": chunk["id"],
            "content": chunk["content"],
            "source": chunk["source"],
            "embedding": embedding
        })

    return embedded_chunks
