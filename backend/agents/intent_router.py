from enum import Enum


class Intent(str, Enum):
    AUTH = "AUTH"
    PAYMENTS = "PAYMENTS"
    ERRORS = "ERRORS"
    WEBHOOKS = "WEBHOOKS"
    VECTOR = "VECTOR"
    METRICS = "METRICS"
    HEALTH = "HEALTH"
    THREAD = "THREAD"
    GENERAL = "GENERAL"


def classify_query(query: str) -> Intent:

    q = query.lower()

    vector_keywords = [
        "chunks",
        "documents",
        "indexed",
        "vector db",
        "vector database",
    ]

    metrics_keywords = [
        "evaluation",
        "metrics",
        "deepeval",
        "baseline",
        "faithfulness",
        "relevancy",
    ]

    health_keywords = [
        "healthy",
        "health",
        "diagnostics",
        "system status",
        "vector database healthy",
    ]

    thread_keywords = [
        "discuss earlier",
        "previous conversation",
        "thread",
        "history",
        "earlier",
    ]

    auth_keywords = [
        "auth",
        "authentication",
        "authorization",
        "api key",
        "token",
        "oauth",
        "credential",
    ]

    payment_keywords = [
        "payment",
        "capture",
        "refund",
        "order",
        "invoice",
        "transaction",
    ]

    error_keywords = [
        "error",
        "failed",
        "otp",
        "timeout",
        "invalid",
        "exception",
    ]

    webhook_keywords = [
        "webhook",
        "callback",
        "event",
        "signature",
    ]

    if any(k in q for k in health_keywords):
        return Intent.HEALTH

    if any(k in q for k in metrics_keywords):
        return Intent.METRICS

    if any(k in q for k in vector_keywords):
        return Intent.VECTOR

    if any(k in q for k in thread_keywords):
        return Intent.THREAD

    if any(k in q for k in auth_keywords):
        return Intent.AUTH

    if any(k in q for k in payment_keywords):
        return Intent.PAYMENTS

    if any(k in q for k in error_keywords):
        return Intent.ERRORS

    if any(k in q for k in webhook_keywords):
        return Intent.WEBHOOKS

    return Intent.GENERAL
