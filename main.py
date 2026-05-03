from rag.ingest import load_documents
from rag.chunk import chunk_text


def main():
    documents = load_documents("data")

    total_chunks = 0

    print("=== DOCUMENT INGESTION TEST ===")

    for doc in documents:
        chunks = chunk_text(doc["content"])

        total_chunks += len(chunks)

        print(f"\nLoaded File: {doc['filename']}")
        print(f"Total Chunks: {len(chunks)}")

        for i, chunk in enumerate(chunks[:2], start=1):
            print(f"\n--- Chunk {i} Preview ---")
            print(chunk[:300])
            print()

    print(f"\n=== TOTAL DOCUMENTS: {len(documents)} ===")
    print(f"=== TOTAL CHUNKS: {total_chunks} ===")


if __name__ == "__main__":
    main()
