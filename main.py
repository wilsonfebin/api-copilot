from rag.retrieve import answer_query


def main():
    print("=== API COPILOT (DAY 4 RAG) ===")

    user_query = input("\nAsk a question: ")

    result = answer_query(user_query)

    print("\n=== ANSWER ===\n")
    print(result["answer"])

    print("\n=== SOURCES ===")

    unique_sources = set()

    for source in result["sources"]:
        unique_sources.add(source["source"])

    for source in unique_sources:
        print("-", source)


if __name__ == "__main__":
    main()
