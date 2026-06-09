import json
import os
import urllib.error
import urllib.request

from backend.utils.logger import logger


GRAPH_CHANNEL_MESSAGE_URL = (
    "https://graph.microsoft.com/v1.0/teams/"
    "{team_id}/channels/{channel_id}/messages"
)


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
            "mode": "live",
            "reason": "Posted successfully",
            "status_code": status_code,
        }

    except urllib.error.HTTPError as exc:
        logger.warning(
            f"MICROSOFT GRAPH POST DONE | status={exc.code}"
        )
        return {
            "posted": False,
            "mode": "live",
            "reason": str(exc),
            "status_code": exc.code,
        }

    except Exception as exc:
        logger.warning(
            f"MICROSOFT GRAPH POST DONE | status=failed | error={exc}"
        )
        return {
            "posted": False,
            "mode": "live",
            "reason": str(exc),
            "status_code": None,
        }
