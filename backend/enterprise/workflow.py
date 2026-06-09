import json
import time

from backend.config import DEFAULT_LLM_PROVIDER, get_default_model
from backend.enterprise.microsoft_graph import send_enterprise_notification
from backend.utils.logger import logger
from llm.client import ask_llm, get_embedding
from rag.vector_store import get_collection, query_chunks
from utils.metrics import estimate_cost, estimate_tokens


WEBHOOK_SOURCE = "razorpay_webhooks.txt"
MAX_CONTEXT_CHARS = 1800
REQUIRED_PAYLOAD_FIELDS = [
    "severity",
    "service",
    "incident_type",
    "summary",
    "recommended_action",
]


def build_incident_payload() -> dict:
    return {
        "severity": "high",
        "service": "webhook-service",
        "incident_type": "webhook_failure",
        "summary": (
            "Repeated webhook retry or signature validation failures detected"
        ),
        "recommended_action": (
            "Validate webhook signature handling, retry processing, "
            "endpoint uptime, and idempotency controls"
        ),
    }


def validate_payload(payload: dict) -> dict:
    missing_fields = [
        field
        for field in REQUIRED_PAYLOAD_FIELDS
        if not payload.get(field)
    ]

    return {
        "valid": not missing_fields,
        "missing_fields": missing_fields,
    }


def compact_context(context: str) -> str:
    return context[:MAX_CONTEXT_CHARS].strip()


def retrieve_webhook_context(question: str) -> tuple[str, list[dict[str, str]]]:
    try:
        query_embedding = get_embedding(question)
        results = query_chunks(
            query_embedding,
            top_k=2,
            source_filter=WEBHOOK_SOURCE,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        sources = [
            {
                "source": metadata.get("source", WEBHOOK_SOURCE),
                "content": document,
            }
            for document, metadata in zip(documents, metadatas)
        ]

        if documents:
            logger.info(
                f"ENTERPRISE RETRIEVAL DONE | source={WEBHOOK_SOURCE}"
            )
            return compact_context(
                "\n\n".join(documents)
            ), sources

    except Exception as exc:
        logger.warning(
            f"ENTERPRISE RETRIEVAL FALLBACK | reason={exc}"
        )

    collection = get_collection()
    fallback = collection.get(
        where={
            "source": WEBHOOK_SOURCE
        }
    )
    documents = fallback.get("documents") or []
    metadatas = fallback.get("metadatas") or []

    sources = [
        {
            "source": metadata.get("source", WEBHOOK_SOURCE),
            "content": document,
        }
        for document, metadata in zip(documents[:2], metadatas[:2])
    ]

    logger.info(
        f"ENTERPRISE RETRIEVAL DONE | source={WEBHOOK_SOURCE}"
    )
    return compact_context(
        "\n\n".join(documents[:2])
    ), sources


def build_rca_prompt(question: str, context: str) -> str:
    return f"""
You are API Copilot executing an enterprise incident workflow.

User request:
{question}

Retrieved Razorpay webhook context:
{context}

Generate a concise enterprise RCA summary for webhook failures.
Return:
1. Incident Summary
2. Probable Root Causes
3. Failure Pattern Analysis
4. Recommended Remediation
5. Teams Notification Payload

Target 350-500 words maximum.
Use compact bullets where helpful.
Keep the Teams Notification Payload to 3-5 short lines.
Keep the answer operational, technical, and enterprise-ready.
Do not invent facts not supported by context.
"""


def sanitize_answer(answer: str) -> str:
    return answer.replace("</div>", "").strip()


def format_answer(
    rca_summary: str,
    incident_payload: dict,
    validation: dict,
    notification_status: dict,
) -> str:
    validation_status = (
        "valid"
        if validation["valid"]
        else "invalid: missing "
        + ", ".join(validation["missing_fields"])
    )

    answer = f"""
## Enterprise Workflow Execution
✓ Retrieved relevant Razorpay documentation
✓ Analyzed webhook retry failure patterns
✓ Generated AI-assisted RCA summary
✓ Created enterprise incident workflow
✓ Prepared Teams notification for human approval

## RCA Summary
{rca_summary}

## Incident Payload
```json
{json.dumps(incident_payload, indent=2)}
```

## Validation
Payload validation: {validation_status}

## HITL Approval Status
Status: Awaiting human approval

No external notification has been sent yet.
Review the RCA and incident payload, then approve execution.

## Notification Status
Mode: {notification_status.get("mode")}
Status: {notification_status.get("status")}
Reason: {notification_status.get("reason")}
"""

    return sanitize_answer(answer)


def run_enterprise_workflow(
    question: str,
    llm_provider: str = DEFAULT_LLM_PROVIDER,
    model: str | None = None,
) -> dict:
    start = time.time()
    model = model or get_default_model(llm_provider)

    logger.info(
        f"ENTERPRISE WORKFLOW START | question={question}"
    )

    context, retrieved_sources = retrieve_webhook_context(
        question
    )
    prompt = build_rca_prompt(
        question=question,
        context=context,
    )
    rca_summary = ask_llm(
        prompt,
        provider=llm_provider,
        model=model,
    )
    rca_summary = sanitize_answer(
        rca_summary
    )
    logger.info("ENTERPRISE RCA GENERATED")

    incident_payload = build_incident_payload()
    validation = validate_payload(incident_payload)

    logger.info(
        "HITL REQUIRED | workflow=enterprise_incident_workflow"
    )
    notification_status = send_enterprise_notification(
        incident_payload,
        approved=False,
    )

    answer = format_answer(
        rca_summary=rca_summary,
        incident_payload=incident_payload,
        validation=validation,
        notification_status=notification_status,
    )
    elapsed = round(time.time() - start, 2)

    in_tokens = estimate_tokens(
        prompt,
        model=model,
    )
    out_tokens = estimate_tokens(
        answer,
        model=model,
    )
    workflow_status = "awaiting_human_approval"

    logger.info(
        f"ENTERPRISE WORKFLOW DONE | status={workflow_status}"
    )

    return {
        "question": question,
        "answer": answer,
        "sources": list(
            {
                source.get("source", WEBHOOK_SOURCE)
                for source in retrieved_sources
            }
        ) or [WEBHOOK_SOURCE],
        "response_time": elapsed,
        "tokens": in_tokens + out_tokens,
        "cost": estimate_cost(
            in_tokens,
            out_tokens,
            provider=llm_provider,
            model=model,
        ),
        "provider": llm_provider,
        "llm_provider": llm_provider,
        "model": model,
        "workflow_type": "enterprise_incident_workflow",
        "tool_used": "TeamsNotificationTool",
        "workflow_status": workflow_status,
        "graph_status": notification_status,
        "notification_status": notification_status,
        "incident_payload": incident_payload,
        "payload_validation": validation,
        "hitl_required": True,
        "approval_status": "pending",
        "intent": "ENTERPRISE_WORKFLOW",
        "tool": {
            "name": "TeamsNotificationTool",
            "mode": notification_status.get("mode"),
        },
    }
