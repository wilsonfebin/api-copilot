from llm.client import ask_llm, get_embedding

if __name__ == "__main__":
    print("=== LLM Test ===")
    print(ask_llm("What is an API?"))

    print("\n=== Embedding Test ===")
    emb = get_embedding("API authentication using keys")
    print(f"Embedding length: {len(emb)}")
