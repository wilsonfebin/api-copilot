import os
import time
from dotenv import load_dotenv
from openai import OpenAI

from backend.config import (
    DEFAULT_LLM_PROVIDER,
    MAX_TOKENS,
    TEMPERATURE,
    get_default_model,
)


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def ask_openai(prompt, model=None, retries=3):
    model = model or get_default_model("openai")

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )

            return response.choices[0].message.content

        except Exception as e:
            if attempt < retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                return f"LLM request failed after retries: {str(e)}"


def ask_claude(prompt, model=None, retries=3):
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return (
            "Claude provider selected but ANTHROPIC_API_KEY "
            "is not configured."
        )

    try:
        from anthropic import Anthropic
    except ImportError:
        return (
            "Claude provider selected but Anthropic SDK "
            "is not installed."
        )

    model = model or get_default_model("claude")
    anthropic_client = Anthropic(api_key=api_key)

    for attempt in range(retries):
        try:
            response = anthropic_client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )

            return "".join(
                block.text
                for block in response.content
                if getattr(block, "type", "") == "text"
            )

        except Exception as e:
            if attempt < retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                return f"LLM request failed after retries: {str(e)}"


def ask_llm(
    prompt,
    provider=DEFAULT_LLM_PROVIDER,
    model=None,
    retries=3,
):
    if provider == "openai":
        return ask_openai(
            prompt,
            model=model,
            retries=retries,
        )

    if provider == "claude":
        return ask_claude(
            prompt,
            model=model,
            retries=retries,
        )

    raise ValueError(
        f"Unsupported LLM provider: {provider}"
    )


def get_embedding(text, retries=3):
    for attempt in range(retries):
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )

            return response.data[0].embedding

        except Exception as e:
            if attempt < retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                raise Exception(
                    f"Embedding request failed after retries: {str(e)}"
                )
