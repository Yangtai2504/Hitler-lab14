import asyncio
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

    asyncio.run(test())
