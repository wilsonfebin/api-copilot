from enum import Enum


class Intent(str, Enum):
    AUTH = "AUTH"
    PAYMENTS = "PAYMENTS"
    ERRORS = "ERRORS"
    WEBHOOKS = "WEBHOOKS"
    GENERAL = "GENERAL"


def classify_query(query: str) -> Intent:

    q = query.lower()

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

    if any(k in q for k in auth_keywords):
        return Intent.AUTH

    if any(k in q for k in payment_keywords):
        return Intent.PAYMENTS

    if any(k in q for k in error_keywords):
        return Intent.ERRORS

    if any(k in q for k in webhook_keywords):
        return Intent.WEBHOOKS

    return Intent.GENERAL