import json
from pathlib import Path

from backend.mcp.models import MCPToolResult


BASELINE_DIR = Path("evaluation/baselines")


class MetricsTool:
    name = "MetricsTool"

    def run(self, question: str, state: dict):

        baseline_files = sorted(
            BASELINE_DIR.glob(
                "evaluation_baseline_*.json"
            )
        )

        if not baseline_files:
            return MCPToolResult(
                tool_name=self.name,
                data={
                    "latest_baseline": None,
                    "summary": {},
                    "timestamp": None,
                },
            ).to_dict()

        latest = baseline_files[-1]

        with open(latest, "r") as f:
            report = json.load(f)

        return MCPToolResult(
            tool_name=self.name,
            data={
                "latest_baseline": str(latest),
                "summary": report.get(
                    "summary",
                    {}
                ),
                "timestamp": report.get(
                    "timestamp"
                ),
                "model": report.get(
                    "model"
                ),
                "threshold": report.get(
                    "threshold"
                ),
            },
        ).to_dict()
