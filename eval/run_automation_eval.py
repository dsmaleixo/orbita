"""Automation evaluation script for Órbita.

Usage:
    python eval/run_automation_eval.py

Outputs:
    - Results table to stdout
    - eval/results/automation_report.json
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_automation_tasks() -> List[Dict]:
    tasks_path = Path(__file__).parent / "automation_tasks.json"
    with open(tasks_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["tasks"]


def evaluate_task(graph, task: Dict) -> Dict[str, Any]:
    """Run a single automation task and evaluate against expected output."""
    from src.graph.state import make_initial_state

    start_time = time.time()
    task_input = task["input"]
    expected = task["expected_output"]

    try:
        state = make_initial_state(
            user_query=f"Automation: {task['name']}",
            intent="automation",
            automation_type=task["automation_type"],
            automation_input=task_input,
        )
        result = graph.invoke(state)
        latency = time.time() - start_time

        output = result.get("automation_output", {})
        final_response = result.get("final_response", "")
        mcp_tool_calls = result.get("mcp_tool_calls", [])

        # Evaluate against expected output
        success, checks = _evaluate_output(task["automation_type"], output, final_response, expected)

        return {
            "id": task["id"],
            "name": task["name"],
            "automation_type": task["automation_type"],
            "success": success,
            "checks": checks,
            "latency_s": round(latency, 2),
            "num_mcp_calls": len(mcp_tool_calls),
            "num_steps": len(mcp_tool_calls) + 1,
            "error": None,
        }

    except Exception as exc:
        logger.error("Task %s failed: %s", task["id"], exc)
        return {
            "id": task["id"],
            "name": task["name"],
            "automation_type": task["automation_type"],
            "success": False,
            "checks": {"error": str(exc)},
            "latency_s": round(time.time() - start_time, 2),
            "num_mcp_calls": 0,
            "num_steps": 0,
            "error": str(exc),
        }


def _evaluate_output(
    automation_type: str,
    output: Dict,
    final_response: str,
    expected: Dict,
) -> tuple[bool, Dict]:
    """Evaluate automation output against expected criteria."""
    checks = {}
    passed = 0
    total = 0

    if automation_type == "categorize":
        categories = output.get("categories", {})
        total_txns = output.get("total_transactions", 0)

        for expected_cat in expected.get("categories_present", []):
            present = expected_cat in categories
            checks[f"category_{expected_cat}"] = present
            total += 1
            if present:
                passed += 1

        exp_total = expected.get("total_transactions", 0)
        if exp_total:
            match = total_txns == exp_total
            checks["total_transactions_correct"] = match
            total += 1
            if match:
                passed += 1

    elif automation_type == "goal_alert":
        alerts = output.get("alerts", [])
        has_alerts = len(alerts) > 0
        checks["has_alerts"] = has_alerts
        total += 1
        if has_alerts == expected.get("has_alerts", True):
            passed += 1

        if expected.get("alert_contains"):
            keyword = expected["alert_contains"]
            alert_msgs = " ".join(a.get("message", "") for a in alerts)
            found = keyword.lower() in alert_msgs.lower() or keyword.lower() in final_response.lower()
            checks["alert_contains_keyword"] = found
            total += 1
            if found:
                passed += 1

    elif automation_type == "report":
        for field in ["has_period", "has_summary", "has_insights", "has_top_categories"]:
            if expected.get(field):
                if field == "has_period":
                    present = bool(output.get("period"))
                elif field == "has_summary":
                    present = bool(output.get("summary"))
                elif field == "has_insights":
                    present = bool(output.get("insights"))
                elif field == "has_top_categories":
                    present = bool(output.get("top_spending_categories"))
                else:
                    present = False
                checks[field] = present
                total += 1
                if present:
                    passed += 1

    success = total > 0 and (passed / total) >= 0.8
    checks["_pass_rate"] = f"{passed}/{total}"
    return success, checks


def main() -> None:
    from src.graph.builder import build_graph

    logger.info("Building graph...")
    graph = build_graph()

    tasks = load_automation_tasks()
    logger.info("Running %d automation tasks...", len(tasks))

    results = []
    for i, task in enumerate(tasks, 1):
        logger.info("[%d/%d] %s (%s)", i, len(tasks), task["id"], task["name"])
        result = evaluate_task(graph, task)
        results.append(result)
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        logger.info("  %s | Latency: %.1fs | MCP calls: %d",
                    status, result["latency_s"], result["num_mcp_calls"])

    # Compute aggregate metrics
    total = len(results)
    successes = sum(1 for r in results if r["success"])
    success_rate = successes / total if total > 0 else 0
    avg_steps = sum(r["num_steps"] for r in results) / total if total > 0 else 0
    avg_latency = sum(r["latency_s"] for r in results) / total if total > 0 else 0

    print("\n" + "=" * 60)
    print("ÓRBITA AUTOMATION EVALUATION RESULTS")
    print("=" * 60)
    print(f"\n  Success rate:     {successes}/{total} ({success_rate*100:.0f}%)")
    print(f"  Avg steps/task:   {avg_steps:.1f}")
    print(f"  Avg latency:      {avg_latency:.1f}s")
    print("\n── Per-task results ──")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} [{r['id']}] {r['name']}: {r['checks'].get('_pass_rate', 'N/A')}")
    print("=" * 60 + "\n")

    # Save report
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)
    report = {
        "summary": {
            "success_rate": round(success_rate, 3),
            "successes": successes,
            "total": total,
            "avg_steps": round(avg_steps, 2),
            "avg_latency_s": round(avg_latency, 2),
        },
        "task_results": results,
    }
    report_path = results_dir / "automation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info("Report saved to %s", report_path)


if __name__ == "__main__":
    main()
