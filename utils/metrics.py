import tiktoken

from backend.config import (
    DEFAULT_LLM_PROVIDER,
    MODEL_PRICING_USD_PER_M_TOKENS,
    get_default_model,
)


def estimate_tokens(text, model=None):
    model = model or get_default_model(
        DEFAULT_LLM_PROVIDER
    )

    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))

    except Exception:
        return max(
            1,
            int(len(text.split()) * 1.3)
        )


def estimate_cost(
    input_tokens,
    output_tokens,
    provider=DEFAULT_LLM_PROVIDER,
    model=None,
):
    model = model or get_default_model(
        provider
    )

    input_rate, output_rate = (
        MODEL_PRICING_USD_PER_M_TOKENS.get(
            (provider, model),
            MODEL_PRICING_USD_PER_M_TOKENS[
                (
                    DEFAULT_LLM_PROVIDER,
                    get_default_model(
                        DEFAULT_LLM_PROVIDER
                    )
                )
            ]
        )
    )

    input_cost = (
        input_tokens / 1_000_000
    ) * input_rate

    output_cost = (
        output_tokens / 1_000_000
    ) * output_rate

    return round(input_cost + output_cost, 6)
