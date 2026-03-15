"""RAGAS evaluation script for Órbita Q&A pipeline.

Usage:
    python eval/run_ragas.py

Outputs:
    - Metrics table to stdout
    - eval/results/ragas_report.json
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_golden_set() -> List[Dict]:
    """Load the golden Q&A set."""
    golden_path = Path(__file__).parent / "golden_set.json"
    with open(golden_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["questions"]


def run_question(graph, question: Dict) -> Dict[str, Any]:
    """Run a single question through the graph and collect results."""
    from src.graph.state import make_initial_state

    start_time = time.time()
    query = question["query"]

    try:
        state = make_initial_state(user_query=query)
        result = graph.invoke(state)
        latency = time.time() - start_time

        return {
            "id": question["id"],
            "query": query,
            "answer": result.get("final_response", ""),
            "retrieved_docs": [
                doc.page_content for doc in result.get("retrieved_docs", [])
            ],
            "citations": result.get("citations", []),
            "is_blocked": result.get("is_blocked", False),
            "self_check_passed": result.get("self_check_passed", False),
            "retrieval_attempts": result.get("retrieval_attempts", 0),
            "latency_s": round(latency, 2),
            "error": None,
        }
    except Exception as exc:
        logger.error("Error on question %s: %s", question["id"], exc)
        return {
            "id": question["id"],
            "query": query,
            "answer": "",
            "retrieved_docs": [],
            "citations": [],
            "is_blocked": False,
            "self_check_passed": False,
            "retrieval_attempts": 0,
            "latency_s": time.time() - start_time,
            "error": str(exc),
        }


def compute_basic_metrics(results: List[Dict], questions: List[Dict]) -> Dict:
    """Compute basic metrics without requiring RAGAS library."""
    metrics = {
        "total_questions": len(results),
        "errors": sum(1 for r in results if r.get("error")),
        "refusals_correct": 0,
        "refusals_incorrect": 0,
        "has_citations": 0,
        "self_check_passed": 0,
        "avg_latency_s": 0,
        "p50_latency_s": 0,
        "p95_latency_s": 0,
    }

    q_map = {q["id"]: q for q in questions}
    latencies = [r["latency_s"] for r in results if not r.get("error")]

    for result in results:
        q = q_map.get(result["id"], {})
        should_refuse = q.get("should_refuse", False)

        if should_refuse and result.get("is_blocked"):
            metrics["refusals_correct"] += 1
        elif should_refuse and not result.get("is_blocked"):
            metrics["refusals_incorrect"] += 1

        if result.get("citations"):
            metrics["has_citations"] += 1
        if result.get("self_check_passed"):
            metrics["self_check_passed"] += 1

    if latencies:
        latencies_sorted = sorted(latencies)
        metrics["avg_latency_s"] = round(sum(latencies) / len(latencies), 2)
        metrics["p50_latency_s"] = round(latencies_sorted[len(latencies_sorted) // 2], 2)
        metrics["p95_latency_s"] = round(latencies_sorted[int(len(latencies_sorted) * 0.95)], 2)

    return metrics


def try_ragas_metrics(results: List[Dict], questions: List[Dict]) -> Dict:
    """Attempt RAGAS evaluation if library is available."""
    try:
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )
        from datasets import Dataset

        # Build RAGAS dataset from non-refused, non-error results
        q_map = {q["id"]: q for q in questions}
        ragas_rows = []
        for r in results:
            q = q_map.get(r["id"], {})
            if q.get("should_refuse") or r.get("error") or not r.get("answer"):
                continue
            ragas_rows.append({
                "question": r["query"],
                "answer": r["answer"],
                "contexts": r["retrieved_docs"] if r["retrieved_docs"] else [""],
                "ground_truth": q.get("reference_answer", r["answer"]),
            })

        if not ragas_rows:
            return {}

        dataset = Dataset.from_list(ragas_rows)
        score = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        )
        return {
            "faithfulness": round(float(score["faithfulness"]), 3),
            "answer_relevancy": round(float(score["answer_relevancy"]), 3),
            "context_precision": round(float(score["context_precision"]), 3),
            "context_recall": round(float(score["context_recall"]), 3),
        }
    except ImportError:
        logger.warning("RAGAS library not available. Skipping RAGAS metrics.")
        return {}
    except Exception as exc:
        logger.warning("RAGAS evaluation failed: %s", exc)
        return {}


def print_metrics_table(basic: Dict, ragas: Dict) -> None:
    """Print a formatted metrics table to stdout."""
    print("\n" + "=" * 60)
    print("ÓRBITA RAG EVALUATION RESULTS")
    print("=" * 60)

    print("\n-- Basic Metrics --")
    print(f"  Total questions:        {basic['total_questions']}")
    print(f"  Errors:                 {basic['errors']}")
    print(f"  Correct refusals:       {basic['refusals_correct']}")
    print(f"  Missed refusals:        {basic['refusals_incorrect']}")
    print(f"  Responses w/ citations: {basic['has_citations']}")
    print(f"  Self-check passed:      {basic['self_check_passed']}")
    print(f"  Avg latency:            {basic['avg_latency_s']}s")
    print(f"  P50 latency:            {basic['p50_latency_s']}s")
    print(f"  P95 latency:            {basic['p95_latency_s']}s")

    if ragas:
        print("\n-- RAGAS Metrics --")
        print(f"  Faithfulness:           {ragas.get('faithfulness', 'N/A')}")
        print(f"  Answer Relevancy:       {ragas.get('answer_relevancy', 'N/A')}")
        print(f"  Context Precision:      {ragas.get('context_precision', 'N/A')}")
        print(f"  Context Recall:         {ragas.get('context_recall', 'N/A')}")
    else:
        print("\n-- RAGAS Metrics: not available (requires OPENAI_API_KEY for LLM-as-judge) --")

    print("=" * 60 + "\n")


def main() -> None:
    """Run the RAGAS evaluation pipeline."""
    from src.graph.builder import build_graph

    logger.info("Building graph...")
    graph = build_graph()

    logger.info("Loading golden set...")
    questions = load_golden_set()
    logger.info("Running %d questions through the graph...", len(questions))

    results = []
    for i, question in enumerate(questions, 1):
        logger.info("[%d/%d] %s", i, len(questions), question["id"])
        result = run_question(graph, question)
        results.append(result)
        if result.get("error"):
            logger.warning("  Error: %s", result["error"])
        else:
            logger.info("  Latency: %.1fs | Citations: %d | Blocked: %s",
                        result["latency_s"], len(result["citations"]), result["is_blocked"])

    basic_metrics = compute_basic_metrics(results, questions)
    ragas_metrics = try_ragas_metrics(results, questions)

    print_metrics_table(basic_metrics, ragas_metrics)

    # Save report
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    report = {
        "basic_metrics": basic_metrics,
        "ragas_metrics": ragas_metrics,
        "per_question_results": results,
    }
    report_path = results_dir / "ragas_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info("Report saved to %s", report_path)


if __name__ == "__main__":
    main()
