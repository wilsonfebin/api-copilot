import tiktoken


def estimate_tokens(text, model="gpt-4o-mini"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def estimate_cost(input_tokens, output_tokens):
    input_cost = (input_tokens / 1_000_000) * 0.15
    output_cost = (output_tokens / 1_000_000) * 0.60

    return round(input_cost + output_cost, 6)
