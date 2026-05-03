import chromadb

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection("api_docs")


def store_chunks(embedded_chunks):
    for chunk in embedded_chunks:
        collection.add(
            ids=[chunk["id"]],
            embeddings=[chunk["embedding"]],
            documents=[chunk["content"]],
            metadatas=[{"source": chunk["source"]}]
        )


def query_chunks(query_embedding, top_k=3):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results
