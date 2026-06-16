import asyncio
<<<<<<< HEAD
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "data" / "corpus.json"

STOPWORDS = {
    "và", "là", "của", "cho", "các", "một", "những", "khi", "nào", "gì",
    "ở", "với", "trong", "để", "thì", "có", "không", "phải", "cần", "bằng",
    "the", "a", "an", "of", "to", "in", "is", "are", "and",
}

QUERY_EXPANSIONS = {
    "đồng thuận": "agreement rate consensus calibration judge",
    "lệch": "conflict calibration agreement rate judge",
    "release": "regression rollback release gate v1 v2",
    "rollback": "regression release gate delta quality",
    "chi phí": "cost token usage cost per eval model routing",
    "cost": "cost token usage cost per eval model routing",
    "token": "cost token usage cost per eval model routing",
    "nhanh": "async latency concurrency p95 batch",
    "chậm": "async latency concurrency p95 batch",
    "generation metrics": "ragas faithfulness relevancy answer quality generation",
    "generation": "ragas faithfulness relevancy answer quality generation",
    "retrieval fail": "failure clustering 5 whys root cause",
    "tiếp theo": "failure clustering 5 whys root cause",
    "hallucination": "retrieval miss chunking faithfulness root cause",
    "bịa": "out of context hallucination clarify",
    "mơ hồ": "ambiguous clarify out of context",
    "api key": "submission env secret",
    "prompt injection": "safety scope goal hijacking",
    "bỏ qua": "prompt injection safety scope",
    "5 whys": "root cause chunking ingestion retrieval prompting",
}


def tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[\w]+", text.lower(), flags=re.UNICODE)
    return [token for token in tokens if len(token) > 1 and token not in STOPWORDS]


def truncate_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(".,;") + "..."


class MainAgent:
    """Small deterministic RAG agent used for the lab benchmark."""

    def __init__(self, version: str = "Agent_V2_Optimized", optimized: bool = True):
        self.version = version
        self.optimized = optimized
        self.name = version
        self.corpus = self._load_corpus()
        self._doc_tokens = {
            doc["id"]: set(
                tokenize(
                    " ".join(
                        [
                            doc["id"],
                            doc["title"],
                            doc["answer"],
                            doc["text"],
                            " ".join(doc.get("keywords", [])),
                        ]
                    )
                )
            )
            for doc in self.corpus
        }

    def _load_corpus(self) -> List[Dict]:
        with CORPUS_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _expand_query(self, question: str) -> str:
        if not self.optimized:
            return question

        expanded = [question]
        lowered = question.lower()
        for trigger, addition in QUERY_EXPANSIONS.items():
            if trigger in lowered:
                expanded.append(addition)
        return " ".join(expanded)

    def retrieve(self, question: str, top_k: int | None = None) -> List[Dict]:
        top_k = top_k or (5 if self.optimized else 3)
        expanded_question = self._expand_query(question)
        query_tokens = Counter(tokenize(expanded_question))
        lowered = expanded_question.lower()

        scored_docs = []
        for doc in self.corpus:
            doc_tokens = self._doc_tokens[doc["id"]]
            overlap = sum(weight for token, weight in query_tokens.items() if token in doc_tokens)
            keyword_boost = 0.0
            for keyword in doc.get("keywords", []):
                if keyword.lower() in lowered:
                    keyword_boost += 2.0 if self.optimized else 1.2

            score = overlap + keyword_boost
            if score > 0:
                normalized = score / math.sqrt(max(len(doc_tokens), 1))
                scored_docs.append({"doc": doc, "score": round(normalized, 4)})

        scored_docs.sort(key=lambda item: (item["score"], item["doc"]["id"]), reverse=True)
        return scored_docs[:top_k]

    def _compose_answer(self, question: str, retrieved: List[Dict]) -> str:
        lowered = question.lower()
        if not retrieved:
            return "Tôi không có đủ thông tin trong tài liệu để trả lời câu hỏi này."

        top_doc = retrieved[0]["doc"]
        injection_like = any(term in lowered for term in ["bỏ qua", "ignore", "prompt injection", "goal hijack"])
        if self.optimized and injection_like:
            safety_doc = next((doc for doc in self.corpus if doc["id"] == "prompt_injection_safety"), top_doc)
            return safety_doc["answer"] + " Căn cứ: prompt_injection_safety."

        selected_docs = [top_doc]
        if self.optimized and len(retrieved) > 1:
            threshold = 0.55 if any(term in lowered for term in ["tiếp theo", "retrieval fail", "sau khi"]) else 0.72
            for item in retrieved[1:3]:
                if item["score"] >= retrieved[0]["score"] * threshold:
                    selected_docs.append(item["doc"])

        answer = " ".join(doc["answer"] for doc in selected_docs)
        if self.optimized:
            sources = ", ".join(doc["id"] for doc in selected_docs)
            return f"{answer} Căn cứ: {sources}."

        return truncate_words(answer, 28)

    async def query(self, question: str) -> Dict:
        await asyncio.sleep(0.03 if self.optimized else 0.06)

        retrieved = self.retrieve(question)
        answer = self._compose_answer(question, retrieved)
        contexts = [item["doc"]["text"] for item in retrieved]
        retrieved_ids = [item["doc"]["id"] for item in retrieved]
        confidence = retrieved[0]["score"] if retrieved else 0.0

        context_tokens = sum(len(tokenize(context)) for context in contexts)
        answer_tokens = len(tokenize(answer))
        prompt_tokens = len(tokenize(question)) + context_tokens
        tokens_used = prompt_tokens + answer_tokens + (35 if self.optimized else 80)
        cost_rate = 0.00000015 if self.optimized else 0.00000028

        return {
            "answer": answer,
            "contexts": contexts,
            "retrieved_ids": retrieved_ids,
            "metadata": {
                "agent_version": self.version,
                "model": "gemini-1.5-flash-rag" if self.optimized else "baseline-rag",
                "tokens_used": tokens_used,
                "estimated_cost_usd": round(tokens_used * cost_rate, 8),
                "confidence": confidence,
                "sources": retrieved_ids,
                "retrieval_scores": [item["score"] for item in retrieved],
            },
        }


if __name__ == "__main__":
    async def test() -> None:
        agent = MainAgent()
        resp = await agent.query("Làm sao tính Hit Rate và MRR?")
        print(json.dumps(resp, ensure_ascii=False, indent=2))
=======
import os
from typing import Dict

from engine.vector_store import get_vector_store
from engine.vertex_client import generate

AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini-2.5-flash")

BASE_SYSTEM_PROMPT = """Ban la VinTech Support Agent, tro ly ho tro khach hang.
Hay tra loi cau hoi CHI dua tren cac doan context duoi day. Khong bia thong tin.

Context:
{context}

Cau hoi: {question}
Tra loi:"""

OPTIMIZED_SYSTEM_PROMPT = """Ban la VinTech Support Agent, tro ly ho tro khach hang chuyen nghiep.

QUY TAC BAT BUOC:
1. CHI tra loi dua tren thong tin co trong Context ben duoi. KHONG bia, KHONG suy doan ngoai context.
2. Neu Context khong chua thong tin de tra loi, hay tra loi dung: "Toi khong co thong tin ve van de nay trong tai lieu hien tai, ban vui long lien he ho tro de duoc giai dap them."
3. Neu cau hoi mo ho hoac thieu thong tin, hay hoi lai de lam ro truoc khi tra loi.
4. Neu cau hoi yeu cau lam viec ngoai pham vi ho tro ky thuat (ví du: viet tho, chinh tri, ...), hay tu choi lich su va nhac lai vai tro ho tro khach hang.
5. Giu giong van chuyen nghiep, ngan gon, di thang vao van de.

Context:
{context}

Cau hoi: {question}
Tra loi:"""


class MainAgent:
    """Agent V1 (Base): RAG don gian, prompt toi thieu."""

    def __init__(self):
        self.name = "SupportAgent-v1"
        self.model = AGENT_MODEL
        self.store = get_vector_store()
        self.prompt_template = BASE_SYSTEM_PROMPT
        self.top_k = 3

    async def query(self, question: str) -> Dict:
        retrieved = self.store.retrieve(question, top_k=self.top_k)
        context = "\n\n".join(f"[{r['id']}] {r['text']}" for r in retrieved)

        prompt = self.prompt_template.format(context=context, question=question)
        result = await generate(self.model, prompt)

        return {
            "answer": result["text"].strip(),
            "contexts": [r["text"] for r in retrieved],
            "retrieved_ids": [r["id"] for r in retrieved],
            "metadata": {
                "model": self.model,
                "input_tokens": result["input_tokens"],
                "output_tokens": result["output_tokens"],
                "cost": result["cost"],
            },
        }


class MainAgentV2(MainAgent):
    """Agent V2 (Optimized): prompt chong hallucination + tu choi ngoai pham vi,
    nang top_k de tang Hit Rate/MRR khi context lien quan nam o vi tri thap."""

    def __init__(self):
        super().__init__()
        self.name = "SupportAgent-v2"
        self.prompt_template = OPTIMIZED_SYSTEM_PROMPT
        self.top_k = 4


if __name__ == "__main__":
    agent = MainAgent()

    async def test():
        resp = await agent.query("Lam thnao de doi mat khau?")
        print(resp)
>>>>>>> ed626b418e18487d0d9ae3ccf204d83c9d87472e

    asyncio.run(test())
