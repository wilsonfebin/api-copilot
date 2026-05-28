from backend.config import ENABLE_GUARDRAILS
from backend.guardrails.models import GuardrailResult
from backend.guardrails.rules import (
    detect_excessive_length,
    detect_hallucination_risk,
    detect_prompt_injection,
    detect_unsafe_output,
    validate_response_not_empty,
    validate_sources,
)


def run_guardrails(state):

    if not ENABLE_GUARDRAILS:
        return GuardrailResult(
            passed=True
        ).to_dict()

    answer = state.get(
        "answer",
        ""
    )

    question = state.get(
        "question",
        ""
    )

    sources = state.get(
        "sources",
        []
    )

    retrieved_context = state.get(
        "retrieved_context",
        []
    )

    blocking_checks = [
        validate_response_not_empty(
            answer
        ),
        validate_sources(
            sources,
            retrieved_context
        ),
        detect_prompt_injection(
            question,
            answer
        ),
        detect_unsafe_output(
            answer
        ),
    ]

    blocked_reason = next(
        (
            check
            for check in blocking_checks
            if check
        ),
        None,
    )

    warnings = [
        warning
        for warning in [
            detect_hallucination_risk(
                answer,
                sources
            ),
            detect_excessive_length(
                answer
            ),
        ]
        if warning
    ]

    return GuardrailResult(
        passed=blocked_reason is None,
        warnings=warnings,
        blocked_reason=blocked_reason,
    ).to_dict()
