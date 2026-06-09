import json
import os
import urllib.error
import urllib.request

from backend.utils.logger import logger


GRAPH_CHANNEL_MESSAGE_URL = (
    "https://graph.microsoft.com/v1.0/teams/"
    "{team_id}/channels/{channel_id}/messages"
)
REQUIRED_PAYLOAD_FIELDS = [
    "severity",
    "service",
    "incident_type",
    "summary",
    "recommended_action",
]


def validate_notification_payload(payload: dict) -> dict:
    missing_fields = [
        field
        for field in REQUIRED_PAYLOAD_FIELDS
        if not payload.get(field)
    ]

    return {
        "valid": not missing_fields,
        "missing_fields": missing_fields,
    }


def _is_graph_configured() -> bool:
    return all([
        os.getenv("ENABLE_TEAMS_POSTING", "").lower() == "true",
        os.getenv("MS_GRAPH_ACCESS_TOKEN"),
        os.getenv("MS_TEAMS_TEAM_ID"),
        os.getenv("MS_TEAMS_CHANNEL_ID"),
    ])


def _build_message_content(payload: dict) -> str:
    return (
        "<strong>API Copilot Enterprise Incident Workflow</strong>"
        f"<br><strong>Severity:</strong> {payload.get('severity')}"
        f"<br><strong>Service:</strong> {payload.get('service')}"
        f"<br><strong>Incident Type:</strong> {payload.get('incident_type')}"
        f"<br><strong>Summary:</strong> {payload.get('summary')}"
        "<br><strong>Recommended Action:</strong> "
        f"{payload.get('recommended_action')}"
    )


def _build_webhook_message(payload: dict) -> dict:
    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": (
                        "http://adaptivecards.io/schemas/"
                        "adaptive-card.json"
                    ),
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": (
                                "API Copilot Enterprise Incident Alert"
                            ),
                            "weight": "Bolder",
                            "size": "Medium",
                        },
                        {
                            "type": "TextBlock",
                            "text": payload.get("summary", ""),
                            "wrap": True,
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {
                                    "title": "Severity",
                                    "value": payload.get("severity", ""),
                                },
                                {
                                    "title": "Service",
                                    "value": payload.get("service", ""),
                                },
                                {
                                    "title": "Incident Type",
                                    "value": payload.get(
                                        "incident_type",
                                        "",
                                    ),
                                },
                                {
                                    "title": "Recommended Action",
                                    "value": payload.get(
                                        "recommended_action",
                                        "",
                                    ),
                                },
                            ],
                        },
                    ],
                },
            }
        ],
    }


def _post_json(url: str, message: dict) -> int:
    request = urllib.request.Request(
        url=url,
        data=json.dumps(message).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=10) as response:
        return response.getcode()


def post_teams_webhook_notification(payload: dict) -> dict:
    logger.info("TEAMS WEBHOOK POST START")

    webhook_enabled = (
        os.getenv("ENABLE_TEAMS_WEBHOOK", "").lower() == "true"
    )
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")

    if not webhook_enabled or not webhook_url:
        reason = "Teams webhook not configured"
        logger.info(
            f"TEAMS WEBHOOK POST FAILED | reason={reason}"
        )
        return {
            "posted": False,
            "mode": "demo",
            "status": "skipped",
            "reason": reason,
            "status_code": None,
        }

    try:
        status_code = _post_json(
            webhook_url,
            _build_webhook_message(payload),
        )
        logger.info(
            f"TEAMS WEBHOOK POST DONE | status={status_code}"
        )
        return {
            "posted": True,
            "mode": "teams_webhook",
            "status": "posted",
            "reason": (
                "Notification posted using Teams workflow webhook"
            ),
            "status_code": status_code,
        }

    except Exception as adaptive_exc:
        logger.warning(
            "TEAMS WEBHOOK POST FAILED | "
            f"reason={adaptive_exc}"
        )

        try:
            status_code = _post_json(
                webhook_url,
                {
                    "text": (
                        "API Copilot Enterprise Incident Alert\n"
                        f"Severity: {payload.get('severity')}\n"
                        f"Service: {payload.get('service')}\n"
                        f"Summary: {payload.get('summary')}\n"
                        "Recommended Action: "
                        f"{payload.get('recommended_action')}"
                    )
                },
            )
            logger.info(
                f"TEAMS WEBHOOK POST DONE | status={status_code}"
            )
            return {
                "posted": True,
                "mode": "teams_webhook",
                "status": "posted",
                "reason": (
                    "Notification posted using Teams workflow webhook"
                ),
                "status_code": status_code,
            }

        except Exception as exc:
            logger.warning(
                f"TEAMS WEBHOOK POST FAILED | reason={exc}"
            )
            return {
                "posted": False,
                "mode": "teams_webhook",
                "status": "failed",
                "reason": str(exc),
                "status_code": getattr(exc, "code", None),
            }


def post_teams_notification(payload: dict) -> dict:
    logger.info("MICROSOFT GRAPH POST START")

    posting_flag = os.getenv("ENABLE_TEAMS_POSTING")
    access_token = os.getenv("MS_GRAPH_ACCESS_TOKEN")
    team_id = os.getenv("MS_TEAMS_TEAM_ID")
    channel_id = os.getenv("MS_TEAMS_CHANNEL_ID")

    if (
        posting_flag
        and posting_flag.lower() != "true"
    ):
        reason = "Microsoft Graph posting disabled"
        logger.info(
            f"MICROSOFT GRAPH POST SKIPPED | reason={reason}"
        )
        return {
            "posted": False,
            "mode": "demo",
            "status": "skipped",
            "reason": reason,
            "status_code": None,
        }

    if not all([access_token, team_id, channel_id]):
        reason = "Microsoft Graph credentials not configured"
        logger.info(
            f"MICROSOFT GRAPH POST SKIPPED | reason={reason}"
        )
        return {
            "posted": False,
            "mode": "demo",
            "status": "skipped",
            "reason": reason,
            "status_code": None,
        }

    if (posting_flag or "").lower() != "true":
        reason = "Microsoft Graph posting disabled"
        logger.info(
            f"MICROSOFT GRAPH POST SKIPPED | reason={reason}"
        )
        return {
            "posted": False,
            "mode": "demo",
            "status": "skipped",
            "reason": reason,
            "status_code": None,
        }

    url = GRAPH_CHANNEL_MESSAGE_URL.format(
        team_id=team_id,
        channel_id=channel_id,
    )
    body = {
        "body": {
            "contentType": "html",
            "content": _build_message_content(payload),
        }
    }

    request = urllib.request.Request(
        url=url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status_code = response.getcode()

        logger.info(
            f"MICROSOFT GRAPH POST DONE | status={status_code}"
        )
        return {
            "posted": True,
            "mode": "graph",
            "status": "posted",
            "reason": "Posted successfully",
            "status_code": status_code,
        }

    except urllib.error.HTTPError as exc:
        logger.warning(
            f"MICROSOFT GRAPH POST DONE | status={exc.code}"
        )
        return {
            "posted": False,
            "mode": "graph",
            "status": "failed",
            "reason": str(exc),
            "status_code": exc.code,
        }

    except Exception as exc:
        logger.warning(
            f"MICROSOFT GRAPH POST DONE | status=failed | error={exc}"
        )
        return {
            "posted": False,
            "mode": "graph",
            "status": "failed",
            "reason": str(exc),
            "status_code": None,
        }


def send_enterprise_notification(
    payload: dict,
    approved: bool = False,
) -> dict:
    validation = validate_notification_payload(payload)

    if not validation["valid"]:
        reason = (
            "Payload validation failed: missing "
            + ", ".join(validation["missing_fields"])
        )
        logger.info(
            f"ENTERPRISE NOTIFICATION DEMO MODE | reason={reason}"
        )
        return {
            "posted": False,
            "mode": "demo",
            "status": "validation_failed",
            "reason": reason,
            "status_code": None,
            "validation": validation,
        }

    if not approved:
        logger.info(
            "HITL APPROVAL PENDING | notification_not_sent"
        )
        return {
            "posted": False,
            "mode": "hitl",
            "status": "awaiting_approval",
            "reason": (
                "Human approval required before enterprise "
                "notification execution"
            ),
            "status_code": None,
            "validation": validation,
        }

    logger.info(
        "HITL APPROVED | workflow=enterprise_incident_workflow"
    )

    webhook_enabled = (
        os.getenv("ENABLE_TEAMS_WEBHOOK", "").lower() == "true"
    )
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")

    if webhook_enabled and webhook_url:
        webhook_result = post_teams_webhook_notification(
            payload
        )
        webhook_result["validation"] = validation

        if webhook_result.get("posted"):
            return webhook_result

    if _is_graph_configured():
        logger.info("MICROSOFT GRAPH FALLBACK START")
        graph_result = post_teams_notification(
            payload
        )
        graph_result["validation"] = validation
        return graph_result

    reason = "No Teams webhook or Microsoft Graph credentials configured"
    logger.info(
        f"ENTERPRISE NOTIFICATION DEMO MODE | reason={reason}"
    )
    return {
        "posted": False,
        "mode": "demo",
        "status": "skipped",
        "reason": reason,
        "status_code": None,
        "validation": validation,
    }
