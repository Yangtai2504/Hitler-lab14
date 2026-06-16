"""
Thuc nghiem do thuc te chi phi cua Cascade Judge (engine/llm_judge.py
::evaluate_multi_judge_cascade) so voi Full Multi-Judge (::evaluate_multi_judge),
tren CHINH cac cau hoi/cau tra loi/ground truth thuc te da co trong
reports/benchmark_results.json (v2) - khong goi lai Agent de tranh tinh trung
cost generation, chi do rieng phan Judge.

Chay: python analysis/cost_optimization_experiment.py
Output: analysis/cost_optimization_result.json
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.llm_judge import LLMJudge


async def main():
    with open("reports/benchmark_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    with open("data/golden_set.jsonl", "r", encoding="utf-8") as f:
        dataset = [json.loads(line) for line in f if line.strip()]

    v2_results = data["v2"]
    judge = LLMJudge()

    full_cost = sum(r["judge"]["cost"] for r in v2_results)
    full_avg_score = sum(r["judge"]["final_score"] for r in v2_results) / len(v2_results)

    cascade_results = []
    for r, case in zip(v2_results, dataset):
        cascade = await judge.evaluate_multi_judge_cascade(
            case["question"], r["agent_response"], case["expected_answer"]
        )
        cascade_results.append(cascade)

    cascade_cost = sum(r["cost"] for r in cascade_results)
    cascade_avg_score = sum(r["final_score"] for r in cascade_results) / len(cascade_results)
    escalated = sum(1 for r in cascade_results if r["escalated"])

    result = {
        "n_cases": len(v2_results),
        "full_multi_judge": {"total_cost_usd": round(full_cost, 6), "avg_score": round(full_avg_score, 3)},
        "cascade_judge": {
            "total_cost_usd": round(cascade_cost, 6),
            "avg_score": round(cascade_avg_score, 3),
            "escalated_to_pro_count": escalated,
            "escalated_pct": round(escalated / len(cascade_results) * 100, 1),
        },
        "cost_reduction_pct": round((1 - cascade_cost / full_cost) * 100, 1),
        "avg_score_delta": round(cascade_avg_score - full_avg_score, 4),
    }

    os.makedirs("analysis", exist_ok=True)
    with open("analysis/cost_optimization_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
