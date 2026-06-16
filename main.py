import asyncio
import json
import os
import time

from engine.runner import BenchmarkRunner
from engine.retrieval_eval import RetrievalEvaluator
from engine.llm_judge import LLMJudge
from agent.main_agent import MainAgent, MainAgentV2

# Nguong cho Release Gate (Quality / Cost / Performance)
QUALITY_DELTA_THRESHOLD = 0.0   # V2 phai >= V1 ve diem judge
HIT_RATE_REGRESSION_TOLERANCE = 0.95  # V2 khong duoc giam Hit Rate qua 5% so voi V1
MAX_AVG_LATENCY_SEC = 15.0
TOTAL_BUDGET_SECONDS = 120.0    # Yeu cau: < 2 phut cho 50 cases


def build_summary(agent_version: str, results: list, total_runtime: float) -> dict:
    total = len(results)
    retrieval_eval = RetrievalEvaluator()
    per_case = [r["retrieval"] for r in results]
    applicable = [c for c in per_case if c["applicable"]]

    avg_hit_rate = sum(c["hit_rate"] for c in applicable) / len(applicable) if applicable else 0.0
    avg_mrr = sum(c["mrr"] for c in applicable) / len(applicable) if applicable else 0.0

    return {
        "metadata": {
            "version": agent_version,
            "total": total,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_runtime_sec": round(total_runtime, 2),
        },
        "metrics": {
            "avg_score": sum(r["judge"]["final_score"] for r in results) / total,
            "pass_rate": sum(1 for r in results if r["status"] == "pass") / total,
            "hit_rate": avg_hit_rate,
            "mrr": avg_mrr,
            "agreement_rate": sum(r["judge"]["agreement_rate"] for r in results) / total,
            "conflict_resolved_count": sum(1 for r in results if r["judge"]["conflict_resolved"]),
            "avg_latency_sec": sum(r["latency"] for r in results) / total,
            "total_cost_usd": round(sum(r["cost"] for r in results), 6),
            "avg_cost_per_case_usd": round(sum(r["cost"] for r in results) / total, 6),
        },
    }


async def run_benchmark_with_results(agent, agent_version: str, dataset: list):
    print(f"Khoi dong Benchmark cho {agent_version}...")
    runner = BenchmarkRunner(agent, RetrievalEvaluator(), LLMJudge())

    start = time.perf_counter()
    results = await runner.run_all(dataset, batch_size=8)
    runtime = time.perf_counter() - start

    summary = build_summary(agent_version, results, runtime)
    return results, summary


def release_gate(v1_summary: dict, v2_summary: dict) -> dict:
    """Auto-Gate: quyet dinh Release/Rollback dua tren Chat luong / Hit Rate / Hieu nang / Chi phi."""
    delta_score = v2_summary["metrics"]["avg_score"] - v1_summary["metrics"]["avg_score"]
    hit_rate_ratio = (
        v2_summary["metrics"]["hit_rate"] / v1_summary["metrics"]["hit_rate"]
        if v1_summary["metrics"]["hit_rate"] > 0
        else 1.0
    )

    checks = {
        "quality_ok": delta_score >= QUALITY_DELTA_THRESHOLD,
        "retrieval_ok": hit_rate_ratio >= HIT_RATE_REGRESSION_TOLERANCE,
        "latency_ok": v2_summary["metrics"]["avg_latency_sec"] <= MAX_AVG_LATENCY_SEC,
    }

    decision = "APPROVE_RELEASE" if all(checks.values()) else "BLOCK_ROLLBACK"
    return {
        "decision": decision,
        "delta_score": round(delta_score, 3),
        "hit_rate_ratio": round(hit_rate_ratio, 3),
        "checks": checks,
    }


async def main():
    if not os.path.exists("data/golden_set.jsonl"):
        print("Thieu data/golden_set.jsonl. Hay chay 'python data/synthetic_gen.py' truoc.")
        return

    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    if not dataset:
        print("File data/golden_set.jsonl rong. Hay tao it nhat 1 test case.")
        return

    pipeline_start = time.perf_counter()

    v1_results, v1_summary = await run_benchmark_with_results(MainAgent(), "Agent_V1_Base", dataset)
    v2_results, v2_summary = await run_benchmark_with_results(MainAgentV2(), "Agent_V2_Optimized", dataset)

    total_pipeline_sec = time.perf_counter() - pipeline_start

    print("\n--- KET QUA SO SANH (REGRESSION) ---")
    delta = v2_summary["metrics"]["avg_score"] - v1_summary["metrics"]["avg_score"]
    print(f"V1 Score: {v1_summary['metrics']['avg_score']:.2f} | Hit Rate: {v1_summary['metrics']['hit_rate']:.2f}")
    print(f"V2 Score: {v2_summary['metrics']['avg_score']:.2f} | Hit Rate: {v2_summary['metrics']['hit_rate']:.2f}")
    print(f"Delta: {'+' if delta >= 0 else ''}{delta:.2f}")

    gate = release_gate(v1_summary, v2_summary)
    v2_summary["regression"] = {
        "baseline_version": "Agent_V1_Base",
        "v1_metrics": v1_summary["metrics"],
        "gate": gate,
    }
    v2_summary["metadata"]["pipeline_runtime_sec"] = round(total_pipeline_sec, 2)

    os.makedirs("reports", exist_ok=True)
    with open("reports/summary.json", "w", encoding="utf-8") as f:
        json.dump(v2_summary, f, ensure_ascii=False, indent=2)
    with open("reports/benchmark_results.json", "w", encoding="utf-8") as f:
        json.dump({"v1": v1_results, "v2": v2_results}, f, ensure_ascii=False, indent=2)

    print(f"\nQUYET DINH RELEASE GATE: {gate['decision']}")
    print(f"Tong thoi gian pipeline: {total_pipeline_sec:.1f}s cho {len(dataset)*2} lan goi agent (V1+V2)")


if __name__ == "__main__":
    asyncio.run(main())
