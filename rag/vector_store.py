import chromadb


CHROMA_PATH = "./chroma_db"


def get_collection():

    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    collection = client.get_or_create_collection(
        name="api_docs"
    )

    return collection


def store_embeddings(chunks):

    collection = get_collection()

    ids = [
        f"chunk_{i}"
        for i in range(len(chunks))
    ]

    documents = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = [
        chunk["embedding"]
        for chunk in chunks
    ]

    metadatas = [
        {
            "source": chunk["source"]
        }
        for chunk in chunks
    ]

    # ========================
    # RESET COLLECTION
    # ========================
    existing = collection.count()

    if existing > 0:

        existing_data = collection.get()

        if existing_data["ids"]:
            collection.delete(
                ids=existing_data["ids"]
            )

    # ========================
    # STORE EMBEDDINGS
    # ========================
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )


# ========================
# QUERY CHUNKS
# ========================
def query_chunks(
    query_embedding,
    top_k=2,
    source_filter=None,
):

    collection = get_collection()

    query_params = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
    }

    # ========================
    # SOURCE FILTERING
    # ========================
    if source_filter:

        query_params["where"] = {
            "source": source_filter
        }

    results = collection.query(
        **query_params
    )

    return results


# ========================
# VECTOR STATS
# ========================
def get_vector_stats():

    collection = get_collection()

    total_chunks = collection.count()

    collection_data = collection.get()

    unique_sources = set()

    if collection_data["metadatas"]:

        for metadata in collection_data["metadatas"]:

            if (
                metadata
                and "source" in metadata
            ):

                unique_sources.add(
                    metadata["source"]
                )

    return {
        "documents": len(unique_sources),
        "chunks": total_chunks
    }