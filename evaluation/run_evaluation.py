import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from statistics import mean

from backend.agents.workflow import run_agentic_flow
from backend.config import (
    DEFAULT_LLM_PROVIDER,
    SUPPORTED_MODELS,
    get_default_model,
)
from backend.services.rag_service import run_query
from backend.utils.logger import logger
from evaluation.test_cases import EVALUATION_CASES


BASELINE_DIR = Path("evaluation/baselines")


class ClaudeJudgeModel:

    def __init__(self, model: str):

        from deepeval.models import DeepEvalBaseLLM

        class _ClaudeJudge(DeepEvalBaseLLM):

            def __init__(self, model_name: str):
                self.model_name = model_name
                super().__init__(model=model_name)

            def load_model(self):

                api_key = os.getenv(
                    "ANTHROPIC_API_KEY"
                )

                if not api_key:
                    raise RuntimeError(
                        "Claude judge selected but "
                        "ANTHROPIC_API_KEY is not configured."
                    )

                try:
                    from anthropic import (
                        Anthropic,
                        AsyncAnthropic,
                    )
                except ImportError as exc:
                    raise RuntimeError(
                        "Claude judge selected but Anthropic SDK "
                        "is not installed. Run `pip install anthropic`."
                    ) from exc

                return {
                    "sync": Anthropic(
                        api_key=api_key
                    ),
                    "async": AsyncAnthropic(
                        api_key=api_key
                    ),
                }

            def _format_prompt(self, prompt, schema=None):

                prompt_text = str(prompt)

                if schema is None:
                    return prompt_text

                if hasattr(schema, "model_json_schema"):
                    raw_schema = schema.model_json_schema()
                else:
                    raw_schema = schema.schema()

                schema_json = json.dumps(
                    raw_schema,
                    indent=2
                )

                return (
                    f"{prompt_text}\n\n"
                    "Return only valid JSON matching this schema. "
                    "Do not include markdown fences or commentary.\n"
                    f"{schema_json}"
                )

            def _parse_schema(self, text, schema):

                if schema is None:
                    return text

                cleaned = text.strip()

                try:
                    data = json.loads(
                        cleaned
                    )
                except json.JSONDecodeError:

                    start = min(
                        index
                        for index in [
                            cleaned.find("{"),
                            cleaned.find("["),
                        ]
                        if index != -1
                    )

                    end = max(
                        cleaned.rfind("}"),
                        cleaned.rfind("]"),
                    )

                    data = json.loads(
                        cleaned[start:end + 1]
                    )

                return schema(
                    **data
                )

            def generate(self, prompt, schema=None):

                response = self.model["sync"].messages.create(
                    model=self.model_name,
                    max_tokens=1000,
                    temperature=0,
                    messages=[
                        {
                            "role": "user",
                            "content": self._format_prompt(
                                prompt,
                                schema=schema
                            ),
                        }
                    ],
                )

                text = "".join(
                    block.text
                    for block in response.content
                    if getattr(block, "type", "") == "text"
                )

                return self._parse_schema(
                    text,
                    schema
                )

            async def a_generate(self, prompt, schema=None):

                response = await self.model["async"].messages.create(
                    model=self.model_name,
                    max_tokens=1000,
                    temperature=0,
                    messages=[
                        {
                            "role": "user",
                            "content": self._format_prompt(
                                prompt,
                                schema=schema
                            ),
                        }
                    ],
                )

                text = "".join(
                    block.text
                    for block in response.content
                    if getattr(block, "type", "") == "text"
                )

                return self._parse_schema(
                    text,
                    schema
                )

            def get_model_name(self):
                return self.model_name

        self.model = _ClaudeJudge(model)

    def get(self):
        return self.model


def load_deepeval():

    try:
        from deepeval.metrics import (
            AnswerRelevancyMetric,
            FaithfulnessMetric,
        )
        from deepeval.test_case import LLMTestCase

        return (
            AnswerRelevancyMetric,
            FaithfulnessMetric,
            LLMTestCase,
        )

    except ImportError as exc:
        raise RuntimeError(
            "DeepEval is not installed. Install backend requirements with "
            "`pip install -r requirements_backend.txt`."
        ) from exc


def build_judge_model(
    judge_provider: str,
    judge_model: str,
):

    if judge_provider == "openai":
        return judge_model

    if judge_provider == "claude":
        return ClaudeJudgeModel(
            judge_model
        ).get()

    raise ValueError(
        f"Unsupported judge provider: {judge_provider}"
    )


def build_metrics(
    judge_provider: str,
    judge_model: str,
    threshold: float,
):

    (
        AnswerRelevancyMetric,
        FaithfulnessMetric,
        _,
    ) = load_deepeval()

    model = build_judge_model(
        judge_provider=judge_provider,
        judge_model=judge_model,
    )

    return [
        AnswerRelevancyMetric(
            threshold=threshold,
            model=model,
            include_reason=True,
        ),
        FaithfulnessMetric(
            threshold=threshold,
            model=model,
            include_reason=True,
        ),
    ]


def run_case(
    case: dict,
    metrics: list,
    provider: str,
    model: str,
):

    _, _, LLMTestCase = load_deepeval()

    question = case["question"]

    agent_state = run_agentic_flow(
        question
    )

    result = run_query(
        question=question,
        intent=agent_state["intent"],
        tool=agent_state["tool"],
        include_context=True,
        llm_provider=provider,
        model=model,
    )

    retrieval_context = result.get(
        "retrieval_context",
        []
    )

    test_case = LLMTestCase(
        input=question,
        actual_output=result["answer"],
        retrieval_context=retrieval_context,
    )

    metric_results = []

    for metric in metrics:

        metric.measure(test_case)

        metric_results.append({
            "name": metric.__class__.__name__,
            "score": metric.score,
            "success": metric.is_successful(),
            "reason": metric.reason,
        })

    return {
        "name": case["name"],
        "question": question,
        "answer": result["answer"],
        "intent": result["intent"],
        "sources": result["sources"],
        "response_time": result["response_time"],
        "tokens": result["tokens"],
        "cost": result["cost"],
        "provider": result.get(
            "llm_provider",
            provider
        ),
        "model": result.get(
            "model",
            model
        ),
        "metrics": metric_results,
    }


def summarize(results: list):

    metric_names = sorted({
        metric["name"]
        for result in results
        for metric in result["metrics"]
    })

    summary = {}

    for metric_name in metric_names:

        scores = [
            metric["score"]
            for result in results
            for metric in result["metrics"]
            if metric["name"] == metric_name
        ]

        summary[metric_name] = {
            "average_score": round(mean(scores), 4),
            "passed": sum(
                1
                for result in results
                for metric in result["metrics"]
                if (
                    metric["name"] == metric_name
                    and metric["success"]
                )
            ),
            "total": len(scores),
        }

    return summary


def print_report(report: dict):

    print(json.dumps(report, indent=2))


def save_baseline(report: dict):

    BASELINE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = report["timestamp"]

    path = BASELINE_DIR / (
        f"evaluation_baseline_{timestamp}.json"
    )

    with open(path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(
        f"BASELINE SAVED | {path}"
    )

    print(
        f"BASELINE SAVED | {path}"
    )

    return path


def main():

    parser = argparse.ArgumentParser(
        description="Run DeepEval metrics for the API Copilot RAG pipeline."
    )

    parser.add_argument(
        "--provider",
        default=os.getenv(
            "DEEPEVAL_PROVIDER",
            DEFAULT_LLM_PROVIDER
        ),
        choices=list(SUPPORTED_MODELS.keys()),
        help="LLM provider used by the local RAG pipeline.",
    )

    parser.add_argument(
        "--model",
        default=os.getenv(
            "DEEPEVAL_MODEL",
            None
        ),
        help="Model used by the selected provider for answer generation.",
    )

    parser.add_argument(
        "--judge-model",
        default=os.getenv(
            "DEEPEVAL_JUDGE_MODEL",
            None
        ),
        help="Judge model used by DeepEval metrics.",
    )

    parser.add_argument(
        "--judge-provider",
        default=os.getenv(
            "DEEPEVAL_JUDGE_PROVIDER",
            "openai"
        ),
        choices=list(SUPPORTED_MODELS.keys()),
        help="Judge provider used by DeepEval metrics.",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=float(
            os.getenv(
                "DEEPEVAL_THRESHOLD",
                "0.7"
            )
        ),
        help="Passing threshold for each DeepEval metric.",
    )

    args = parser.parse_args()

    args.model = args.model or get_default_model(
        args.provider
    )

    args.judge_model = args.judge_model or get_default_model(
        args.judge_provider
    )

    logger.info(
        f"EVALUATION START | "
        f"provider={args.provider} | "
        f"model={args.model} | "
        f"judge_provider={args.judge_provider} | "
        f"judge_model={args.judge_model} | "
        f"threshold={args.threshold}"
    )

    metrics = build_metrics(
        judge_provider=args.judge_provider,
        judge_model=args.judge_model,
        threshold=args.threshold,
    )

    results = [
        run_case(
            case=case,
            metrics=metrics,
            provider=args.provider,
            model=args.model,
        )
        for case in EVALUATION_CASES
    ]

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    report = {
        "timestamp": timestamp,
        "provider": args.provider,
        "model": args.model,
        "judge_provider": args.judge_provider,
        "judge_model": args.judge_model,
        "threshold": args.threshold,
        "summary": summarize(results),
        "results": results,
    }

    logger.info(
        f"EVALUATION DONE | "
        f"cases={len(results)}"
    )

    save_baseline(report)

    print_report(report)


if __name__ == "__main__":
    main()
