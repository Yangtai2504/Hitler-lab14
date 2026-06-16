from typing import List, Dict


class RetrievalEvaluator:
    def __init__(self):
        pass

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        """Hit Rate: it nhat 1 trong expected_ids co nam trong top_k cua retrieved_ids khong."""
        top_retrieved = retrieved_ids[:top_k]
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        """Mean Reciprocal Rank: 1 / vi tri 1-indexed cua expected_id dau tien tim thay."""
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    def evaluate_case(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> Dict:
        """
        Eval cho 1 case. Cac case khong co ground-truth retrieval (vi du out-of-context,
        prompt-injection) duoc bo qua khoi metric Retrieval (applicable=False) vi khong
        co "tai lieu dung" de so sanh - dung de tinh hit_rate/mrr se lam sai lech trung binh.
        """
        if not expected_ids:
            return {"applicable": False, "hit_rate": None, "mrr": None}
        return {
            "applicable": True,
            "hit_rate": self.calculate_hit_rate(expected_ids, retrieved_ids, top_k),
            "mrr": self.calculate_mrr(expected_ids, retrieved_ids),
        }

    async def evaluate_batch(self, dataset: List[Dict], retrieved_ids_list: List[List[str]], top_k: int = 3) -> Dict:
        """
        Chay eval cho toan bo dataset. dataset[i]['expected_retrieval_ids'] duoc so sanh
        voi retrieved_ids_list[i] (retrieved_ids thuc te tu Agent).
        """
        per_case = []
        for case, retrieved_ids in zip(dataset, retrieved_ids_list):
            per_case.append(self.evaluate_case(case.get("expected_retrieval_ids", []), retrieved_ids, top_k))

        applicable = [c for c in per_case if c["applicable"]]
        avg_hit_rate = sum(c["hit_rate"] for c in applicable) / len(applicable) if applicable else 0.0
        avg_mrr = sum(c["mrr"] for c in applicable) / len(applicable) if applicable else 0.0

        return {
            "avg_hit_rate": avg_hit_rate,
            "avg_mrr": avg_mrr,
            "applicable_cases": len(applicable),
            "total_cases": len(dataset),
            "per_case": per_case,
        }
