import re
from typing import Dict, List, Set


STOPWORDS = {
    "và", "là", "của", "cho", "các", "một", "những", "khi", "nào", "gì",
    "ở", "với", "trong", "để", "thì", "có", "không", "phải", "cần", "bằng",
    "the", "a", "an", "of", "to", "in", "is", "are", "and",
}


def token_set(text: str) -> Set[str]:
    tokens = re.findall(r"[\w]+", text.lower(), flags=re.UNICODE)
    return {token for token in tokens if len(token) > 1 and token not in STOPWORDS}


def overlap_ratio(reference: str, candidate: str) -> float:
    reference_tokens = token_set(reference)
    if not reference_tokens:
        return 0.0
    candidate_tokens = token_set(candidate)
    return len(reference_tokens & candidate_tokens) / len(reference_tokens)



class RetrievalEvaluator:
    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
<<<<<<< HEAD
        if not expected_ids:
            return 1.0 if not retrieved_ids else 0.0
=======
        """Hit Rate: it nhat 1 trong expected_ids co nam trong top_k cua retrieved_ids khong."""
>>>>>>> ed626b418e18487d0d9ae3ccf204d83c9d87472e
        top_retrieved = retrieved_ids[:top_k]
        return 1.0 if any(doc_id in top_retrieved for doc_id in expected_ids) else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
<<<<<<< HEAD
        if not expected_ids:
            return 1.0 if not retrieved_ids else 0.0
        for index, doc_id in enumerate(retrieved_ids, start=1):
=======
        """Mean Reciprocal Rank: 1 / vi tri 1-indexed cua expected_id dau tien tim thay."""
        for i, doc_id in enumerate(retrieved_ids):
>>>>>>> ed626b418e18487d0d9ae3ccf204d83c9d87472e
            if doc_id in expected_ids:
                return 1.0 / index
        return 0.0

<<<<<<< HEAD
    async def score(self, test_case: Dict, response: Dict) -> Dict:
        expected_ids = test_case.get("expected_retrieval_ids", [])
        retrieved_ids = response.get("retrieved_ids", [])
        expected_answer = test_case.get("expected_answer", "")
        answer = response.get("answer", "")
        context_text = " ".join(response.get("contexts", []))

        hit_rate = self.calculate_hit_rate(expected_ids, retrieved_ids, top_k=3)
        mrr = self.calculate_mrr(expected_ids, retrieved_ids)
        faithfulness = overlap_ratio(answer, context_text)
        relevancy = overlap_ratio(expected_answer, answer)

        return {
            "faithfulness": round(faithfulness, 4),
            "relevancy": round(relevancy, 4),
            "retrieval": {
                "expected_ids": expected_ids,
                "retrieved_ids": retrieved_ids,
                "hit_rate": hit_rate,
                "mrr": round(mrr, 4),
            },
        }

    async def evaluate_batch(self, dataset: List[Dict], responses: List[Dict]) -> Dict:
        scores = [await self.score(case, response) for case, response in zip(dataset, responses)]
        total = max(len(scores), 1)
        return {
            "avg_hit_rate": sum(item["retrieval"]["hit_rate"] for item in scores) / total,
            "avg_mrr": sum(item["retrieval"]["mrr"] for item in scores) / total,
            "avg_faithfulness": sum(item["faithfulness"] for item in scores) / total,
            "avg_relevancy": sum(item["relevancy"] for item in scores) / total,
=======
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
>>>>>>> ed626b418e18487d0d9ae3ccf204d83c9d87472e
        }
