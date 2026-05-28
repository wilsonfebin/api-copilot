import argparse
import json
import os
from statistics import mean

from backend.agents.workflow import run_agentic_flow
from backend.services.rag_service import run_query
from backend.utils.logger import logger
from evaluation.test_cases import EVALUATION_CASES


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


def build_metrics(
    model: str,
    threshold: float,
):

    (
        AnswerRelevancyMetric,
        FaithfulnessMetric,
        _,
    ) = load_deepeval()

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


def main():

    parser = argparse.ArgumentParser(
        description="Run DeepEval metrics for the API Copilot RAG pipeline."
    )

    parser.add_argument(
        "--model",
        default=os.getenv(
            "DEEPEVAL_MODEL",
            "gpt-4o-mini"
        ),
        help="Judge model used by DeepEval.",
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

    logger.info(
        f"EVALUATION START | "
        f"model={args.model} | "
        f"threshold={args.threshold}"
    )

    metrics = build_metrics(
        model=args.model,
        threshold=args.threshold,
    )

    results = [
        run_case(
            case=case,
            metrics=metrics,
        )
        for case in EVALUATION_CASES
    ]

    report = {
        "summary": summarize(results),
        "results": results,
    }

    logger.info(
        f"EVALUATION DONE | "
        f"cases={len(results)}"
    )

    print_report(report)


if __name__ == "__main__":
    main()
