import asyncio
import time
from typing import Dict, List


class BenchmarkRunner:
    def __init__(self, agent, evaluator, judge, concurrency: int = 10):
        self.agent = agent
        self.evaluator = evaluator
        self.judge = judge
        self.concurrency = concurrency

    async def run_single_test(self, test_case: Dict) -> Dict:
        start_time = time.perf_counter()

        response = await self.agent.query(test_case["question"])
        latency = time.perf_counter() - start_time

        ragas_scores = await self.evaluator.score(test_case, response)
        judge_result = await self.judge.evaluate_multi_judge(
            test_case["question"],
            response["answer"],
            test_case["expected_answer"],
            response=response,
            test_case=test_case,
        )

        status = "pass"
        if judge_result["final_score"] < 3.5 or ragas_scores["retrieval"]["hit_rate"] < 1.0:
            status = "fail"

        metadata = response.get("metadata", {})
        return {
            "case_id": test_case.get("case_id"),
            "test_case": test_case["question"],
            "expected_answer": test_case["expected_answer"],
            "expected_retrieval_ids": test_case.get("expected_retrieval_ids", []),
            "case_metadata": test_case.get("metadata", {}),
            "agent_response": response["answer"],
            "retrieved_ids": response.get("retrieved_ids", []),
            "latency": round(latency, 4),
            "tokens_used": metadata.get("tokens_used", 0),
            "estimated_cost_usd": metadata.get("estimated_cost_usd", 0.0),
            "agent_metadata": metadata,
            "ragas": ragas_scores,
            "judge": judge_result,
            "status": status,
        }

    async def run_all(self, dataset: List[Dict]) -> List[Dict]:
        semaphore = asyncio.Semaphore(self.concurrency)

        async def guarded(case: Dict) -> Dict:
            async with semaphore:
                return await self.run_single_test(case)

        return await asyncio.gather(*(guarded(case) for case in dataset))
