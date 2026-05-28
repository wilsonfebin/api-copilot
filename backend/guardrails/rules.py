import re

from backend.config import (
    MAX_RESPONSE_WORDS,
    MIN_RESPONSE_LENGTH,
)


PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(the\s+)?(system\s+)?prompt",
    r"system\s+prompt",
    r"bypass\s+safety",
    r"developer\s+message",
    r"act\s+as\s+if\s+you\s+are\s+not\s+bound",
]


UNSAFE_PATTERNS = [
    r"\bkill\s+yourself\b",
    r"\bself[-\s]?harm\b",
    r"\bmake\s+(a\s+)?bomb\b",
    r"\bbuild\s+(a\s+)?weapon\b",
    r"\bsteal\s+(api\s+)?keys?\b",
    r"\bexfiltrate\b",
    r"\bmalware\b",
    r"\bcredential\s+theft\b",
]


STRONG_CLAIM_PATTERNS = [
    r"\balways\b",
    r"\bnever\b",
    r"\bguaranteed\b",
    r"\bmust\b",
    r"\bwill\b",
    r"\bdefinitely\b",
]


def word_count(text):
    return len(text.split())


def contains_pattern(text, patterns):

    normalized = text.lower()

    return any(
        re.search(pattern, normalized)
        for pattern in patterns
    )


def validate_response_not_empty(answer):

    if len(answer.strip()) < MIN_RESPONSE_LENGTH:
        return "empty_response"

    return None


def validate_sources(sources, retrieved_context):

    if not sources or not retrieved_context:
        return "missing_sources"

    return None


def detect_prompt_injection(question, answer):

    text = f"{question}\n{answer}"

    if contains_pattern(
        text,
        PROMPT_INJECTION_PATTERNS
    ):
        return "prompt_injection"

    return None


def detect_unsafe_output(answer):

    if contains_pattern(
        answer,
        UNSAFE_PATTERNS
    ):
        return "unsafe_output"

    return None


def detect_hallucination_risk(answer, sources):

    if (
        len(sources) <= 1
        and word_count(answer) > 120
        and contains_pattern(
            answer,
            STRONG_CLAIM_PATTERNS
        )
    ):
        return "hallucination_risk"

    return None


def detect_excessive_length(answer):

    if word_count(answer) > MAX_RESPONSE_WORDS:
        return "excessive_length"

    return None
