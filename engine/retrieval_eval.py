from typing import List, Dict
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


class RetrievalEvaluator:
    def __init__(self):
        pass

    def calculate_hit_rate(self, expected_ids: List[str], retrieved_ids: List[str], top_k: int = 3) -> float:
        top_retrieved = retrieved_ids[:top_k]
        hit = any(doc_id in top_retrieved for doc_id in expected_ids)
        return 1.0 if hit else 0.0

    def calculate_mrr(self, expected_ids: List[str], retrieved_ids: List[str]) -> float:
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in expected_ids:
                return 1.0 / (i + 1)
        return 0.0

    async def evaluate_batch(self, dataset: List[Dict], docs_dir: str = "data/docs", top_k: int = 10) -> Dict:
        """
        Build a simple TF-IDF index over files in `docs_dir`, run retrieval for each question
        in `dataset` and compute per-case Hit Rate and MRR. Writes `reports/retrieval_metrics.json`.
        Each dataset item is expected to have `ground_truth_doc_ids` and `question`.
        """
        # load documents
        doc_texts = {}
        for fname in os.listdir(docs_dir):
            if not fname.endswith(".txt"):
                continue
            doc_id = os.path.splitext(fname)[0]
            with open(os.path.join(docs_dir, fname), "r", encoding="utf-8") as f:
                doc_texts[doc_id] = f.read()

        doc_ids = list(doc_texts.keys())
        corpus = [doc_texts[d] for d in doc_ids]

        if not corpus:
            raise RuntimeError(f"No documents found in {docs_dir}")

        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        doc_vecs = vectorizer.fit_transform(corpus)

        per_case = []
        hit_rates = []
        mrrs = []

        for item in dataset:
            q = item.get("question", "")
            expected = item.get("ground_truth_doc_ids", [])
            q_vec = vectorizer.transform([q])
            sims = (doc_vecs @ q_vec.T).toarray().ravel()
            # get ranking
            ranked_idx = np.argsort(-sims)
            retrieved_ids = [doc_ids[i] for i in ranked_idx]

            hit = self.calculate_hit_rate(expected, retrieved_ids, top_k=top_k)
            mrr = self.calculate_mrr(expected, retrieved_ids)
            hit_rates.append(hit)
            mrrs.append(mrr)

            per_case.append({
                "id": item.get("id"),
                "question": q,
                "ground_truth_doc_ids": expected,
                "retrieved_ids_top_k": retrieved_ids[:top_k],
                "hit": hit,
                "mrr": mrr
            })

        summary = {
            "avg_hit_rate": float(np.mean(hit_rates)) if hit_rates else 0.0,
            "avg_mrr": float(np.mean(mrrs)) if mrrs else 0.0,
            "top_k": top_k,
            "num_cases": len(dataset)
        }

        os.makedirs("reports", exist_ok=True)
        out = {"summary": summary, "per_case": per_case}
        with open("reports/retrieval_metrics.json", "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

        return summary
