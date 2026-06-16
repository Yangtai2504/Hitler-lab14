from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from data.knowledge_base import DOCUMENTS


class VectorStore:
    """
    Vector DB don gian dung TF-IDF + cosine similarity tren knowledge base
    co san (data/knowledge_base.py). Du khong dung embedding model, no van
    mo phong dung hanh vi cua mot retriever thuc su: tra ve danh sach doc_id
    da xep hang theo do lien quan, phuc vu tinh Hit Rate / MRR.
    """

    def __init__(self, documents: List[Dict] = None):
        self.documents = documents or DOCUMENTS
        self.ids = [d["id"] for d in self.documents]
        self.vectorizer = TfidfVectorizer()
        self.matrix = self.vectorizer.fit_transform([d["text"] for d in self.documents])

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix)[0]
        ranked = sorted(zip(self.ids, scores, self.documents), key=lambda x: x[1], reverse=True)
        results = []
        for doc_id, score, doc in ranked[:top_k]:
            results.append({"id": doc_id, "score": float(score), "text": doc["text"]})
        return results


_store = None


def get_vector_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
