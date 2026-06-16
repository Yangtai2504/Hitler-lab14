from typing import Dict, Tuple


DEFAULT_THRESHOLDS = {
    "min_avg_score": 3.8,
    "min_hit_rate": 0.85,
    "min_agreement_rate": 0.65,
    "max_score_regression": -0.05,
    "max_hit_rate_regression": -0.05,
    "max_cost_increase_pct": 0.15,
    "max_p95_latency_seconds": 2.0,
}


def compare_metrics(baseline: Dict, candidate: Dict) -> Dict:
    base_cost = max(baseline.get("total_cost_usd", 0.0), 0.000001)
    candidate_cost = candidate.get("total_cost_usd", 0.0)
    return {
        "avg_score_delta": round(candidate.get("avg_score", 0.0) - baseline.get("avg_score", 0.0), 4),
        "hit_rate_delta": round(candidate.get("hit_rate", 0.0) - baseline.get("hit_rate", 0.0), 4),
        "mrr_delta": round(candidate.get("mrr", 0.0) - baseline.get("mrr", 0.0), 4),
        "cost_delta_usd": round(candidate_cost - baseline.get("total_cost_usd", 0.0), 8),
        "cost_change_pct": round((candidate_cost - baseline.get("total_cost_usd", 0.0)) / base_cost, 4),
        "p95_latency_delta": round(candidate.get("p95_latency", 0.0) - baseline.get("p95_latency", 0.0), 4),
    }


def decide_release(baseline: Dict, candidate: Dict, thresholds: Dict | None = None) -> Tuple[str, Dict]:
    thresholds = thresholds or DEFAULT_THRESHOLDS
    deltas = compare_metrics(baseline, candidate)
    checks = {
        "quality_floor": candidate.get("avg_score", 0.0) >= thresholds["min_avg_score"],
        "retrieval_floor": candidate.get("hit_rate", 0.0) >= thresholds["min_hit_rate"],
        "judge_reliability_floor": candidate.get("agreement_rate", 0.0) >= thresholds["min_agreement_rate"],
        "no_score_regression": deltas["avg_score_delta"] >= thresholds["max_score_regression"],
        "no_retrieval_regression": deltas["hit_rate_delta"] >= thresholds["max_hit_rate_regression"],
        "cost_guardrail": deltas["cost_change_pct"] <= thresholds["max_cost_increase_pct"],
        "latency_guardrail": candidate.get("p95_latency", 0.0) <= thresholds["max_p95_latency_seconds"],
    }
    decision = "Release" if all(checks.values()) else "Rollback"
    rationale = [
        name for name, passed in checks.items() if not passed
    ] or ["All quality, retrieval, cost, and latency guardrails passed."]
    return decision, {
        "decision": decision,
        "thresholds": thresholds,
        "deltas": deltas,
        "checks": checks,
        "rationale": rationale,
    }
