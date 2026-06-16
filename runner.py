import time
from typing import List, Dict


class BenchmarkRunner:
    def __init__(self, agent, evaluator, judge, top_k: int = 3):
        self.agent = agent
        self.evaluator = evaluator
        self.judge = judge
        self.top_k = top_k

    async def run_single_test(self, test_case: Dict) -> Dict:
        start_time = time.perf_counter()

        # 1. Goi Agent (RAG: retrieval + generation)
        response = await self.agent.query(test_case["question"])
        latency = time.perf_counter() - start_time

        # 2. Retrieval metrics (Hit Rate / MRR) cho rieng case nay
        retrieval_scores = self.evaluator.evaluate_case(
            test_case.get("expected_retrieval_ids", []),
            response.get("retrieved_ids", []),
            top_k=self.top_k,
        )

        # 3. Multi-Judge
        judge_result = await self.judge.evaluate_multi_judge(
            test_case["question"],
            response["answer"],
            test_case["expected_answer"],
        )

        agent_cost = response.get("metadata", {}).get("cost", 0.0)
        total_cost = agent_cost + judge_result.get("cost", 0.0)

        return {
            "test_case": test_case["question"],
            "agent_response": response["answer"],
            "retrieved_ids": response.get("retrieved_ids", []),
            "expected_retrieval_ids": test_case.get("expected_retrieval_ids", []),
            "latency": latency,
            "retrieval": retrieval_scores,
            "judge": judge_result,
            "cost": total_cost,
            "case_type": test_case.get("metadata", {}).get("type", "fact-check"),
            "status": "fail" if judge_result["final_score"] < 3 else "pass",
        }

    async def run_all(self, dataset: List[Dict], batch_size: int = 5) -> List[Dict]:
        """Chay song song bang asyncio.gather theo batch_size de khong bi Rate Limit."""
        import asyncio

        results = []
        for i in range(0, len(dataset), batch_size):
            batch = dataset[i:i + batch_size]
            tasks = [self.run_single_test(case) for case in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
        return results
