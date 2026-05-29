import json
from pathlib import Path

from backend.config import (
    DEFAULT_LLM_PROVIDER,
    SUPPORTED_MODELS,
    get_default_model,
)
from backend.mcp.models import MCPToolResult


BASELINE_DIR = Path("evaluation/baselines")


class MetricsTool:
    name = "MetricsTool"

    def _load_reports(self):

        reports = []

        baseline_files = sorted(
            BASELINE_DIR.glob(
                "evaluation_baseline_*.json"
            ),
            reverse=True
        )

        for path in baseline_files:

            try:

                with open(path, "r") as f:
                    report = json.load(f)

                provider = report.get(
                    "provider",
                    DEFAULT_LLM_PROVIDER
                )

                report["provider"] = provider

                report["model"] = report.get(
                    "model",
                    get_default_model(provider)
                )

                reports.append(
                    {
                        "path": path,
                        "report": report,
                    }
                )

            except Exception:
                continue

        return reports

    def _latest_for_provider(
        self,
        reports,
        provider,
        model,
    ):

        for item in reports:

            report = item["report"]

            if (
                report.get("provider") == provider
                and report.get("model") == model
            ):
                return item

        for item in reports:

            report = item["report"]

            if report.get("provider") == provider:
                return item

        return None

    def run(self, question: str, state: dict):

        metadata = state.get(
            "metadata",
            {}
        )

        provider = state.get(
            "llm_provider",
            metadata.get(
                "llm_provider",
                DEFAULT_LLM_PROVIDER
            )
        )

        model = state.get(
            "model",
            metadata.get(
                "model",
                get_default_model(provider)
            )
        )

        reports = self._load_reports()

        latest_by_provider = {}

        for supported_provider in SUPPORTED_MODELS:

            supported_model = get_default_model(
                supported_provider
            )

            item = self._latest_for_provider(
                reports=reports,
                provider=supported_provider,
                model=supported_model,
            )

            latest_by_provider[supported_provider] = {
                "configured_model": supported_model,
                "latest_baseline": (
                    str(item["path"])
                    if item
                    else None
                ),
                "baseline_model": (
                    item["report"].get("model")
                    if item
                    else None
                ),
                "summary": (
                    item["report"].get("summary", {})
                    if item
                    else {}
                ),
                "timestamp": (
                    item["report"].get("timestamp")
                    if item
                    else None
                ),
                "threshold": (
                    item["report"].get("threshold")
                    if item
                    else None
                ),
            }

        selected = self._latest_for_provider(
            reports=reports,
            provider=provider,
            model=model,
        )

        if not selected:
            return MCPToolResult(
                tool_name=self.name,
                data={
                    "latest_baseline": None,
                    "provider": provider,
                    "model": model,
                    "summary": {},
                    "timestamp": None,
                    "threshold": None,
                    "latest_by_provider": latest_by_provider,
                },
            ).to_dict()

        report = selected["report"]

        return MCPToolResult(
            tool_name=self.name,
            data={
                "latest_baseline": str(
                    selected["path"]
                ),
                "provider": provider,
                "model": model,
                "baseline_provider": report.get(
                    "provider"
                ),
                "baseline_model": report.get(
                    "model"
                ),
                "summary": report.get(
                    "summary",
                    {}
                ),
                "timestamp": report.get(
                    "timestamp"
                ),
                "threshold": report.get(
                    "threshold"
                ),
                "latest_by_provider": latest_by_provider,
            },
        ).to_dict()
