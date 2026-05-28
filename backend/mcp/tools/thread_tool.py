import json
from pathlib import Path

from backend.mcp.models import MCPToolResult


THREAD_FILE = Path("data/threads.json")


class ThreadHistoryTool:
    name = "ThreadHistoryTool"

    def run(self, question: str, state: dict):

        if not THREAD_FILE.exists():
            threads = []
        else:
            try:
                with open(THREAD_FILE, "r") as f:
                    threads = json.load(f)
            except Exception:
                threads = []

        summaries = []

        for thread in threads[:5]:

            messages = thread.get(
                "messages",
                []
            )

            summaries.append({
                "title": thread.get(
                    "title",
                    "Untitled"
                ),
                "created_at": thread.get(
                    "created_at"
                ),
                "updated_at": thread.get(
                    "updated_at"
                ),
                "message_count": len(messages),
                "recent_questions": [
                    message.get(
                        "question"
                    )
                    for message in messages[-3:]
                    if message.get(
                        "question"
                    )
                ],
            })

        return MCPToolResult(
            tool_name=self.name,
            data={
                "threads": summaries,
                "thread_count": len(threads),
            },
        ).to_dict()
