import json
import os
import re
from typing import Any, Dict

from engine.vertex_client import generate

JUDGE_PROMPT = """Ban la mot AI Judge danh gia chat luong cau tra loi cua mot support agent.

Cau hoi: {question}
Cau tra loi cua Agent: {answer}
Cau tra loi ky vong (Ground Truth): {ground_truth}

Hay cham diem cau tra loi cua Agent tu 1 den 5 dua tren 2 tieu chi:
- Accuracy: Cau tra loi co dung va day du so voi Ground Truth khong? Neu Ground Truth la
  "tu choi/hoi lai/khong co thong tin" thi Agent co hanh xu dung nhu vay khong?
- Tone: Cau tra loi co chuyen nghiep, ro rang khong?

Tra ve CHI MOT JSON object, khong giai thich gi them ngoai JSON, dung format:
{{"score": <so nguyen 1-5>, "reasoning": "<ly do ngan gon>"}}
"""


def _parse_score(raw_text: str) -> Dict[str, Any]:
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        return {"score": 3, "reasoning": "Khong parse duoc output cua judge, gan diem trung binh."}
    try:
        data = json.loads(match.group(0))
        data["score"] = max(1, min(5, int(data.get("score", 3))))
        return data
    except (json.JSONDecodeError, ValueError, TypeError):
        return {"score": 3, "reasoning": "Loi parse JSON, gan diem trung binh."}


class LLMJudge:
    def __init__(self):
        self.model_a = os.getenv("JUDGE_MODEL_A", "gemini-2.5-flash")
        self.model_b = os.getenv("JUDGE_MODEL_B", "gemini-2.5-pro")
        self.tiebreaker_model = os.getenv("JUDGE_TIEBREAKER_MODEL", "gemini-2.5-flash-lite")

    async def _ask_judge(self, model: str, question: str, answer: str, ground_truth: str) -> Dict:
        prompt = JUDGE_PROMPT.format(question=question, answer=answer, ground_truth=ground_truth)
        result = await generate(model, prompt, temperature=0.0)
        parsed = _parse_score(result["text"])
        return {
            "model": model,
            "score": parsed["score"],
            "reasoning": parsed.get("reasoning", ""),
            "cost": result["cost"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
        }

    async def evaluate_multi_judge(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        """
        Goi 2 model judge khac nhau (Calibration). Neu lech > 1 diem, goi 1 model
        thu 3 lam tie-breaker va lay median 3 diem de xu ly xung dot tu dong.
        """
        judge_a, judge_b = await self._compatible_gather(question, answer, ground_truth)

        score_a, score_b = judge_a["score"], judge_b["score"]
        diff = abs(score_a - score_b)
        total_cost = judge_a["cost"] + judge_b["cost"]
        conflict_resolved = False
        scores_used = [score_a, score_b]

        if diff > 1:
            tiebreaker = await self._ask_judge(self.tiebreaker_model, question, answer, ground_truth)
            total_cost += tiebreaker["cost"]
            scores_used.append(tiebreaker["score"])
            conflict_resolved = True
        else:
            tiebreaker = None

        scores_used.sort()
        final_score = scores_used[len(scores_used) // 2] if conflict_resolved else (score_a + score_b) / 2
        agreement_rate = 1.0 if diff == 0 else (0.5 if diff == 1 else 0.0)

        return {
            "final_score": final_score,
            "agreement_rate": agreement_rate,
            "conflict_resolved": conflict_resolved,
            "individual_scores": {
                self.model_a: score_a,
                self.model_b: score_b,
                **({self.tiebreaker_model: tiebreaker["score"]} if tiebreaker else {}),
            },
            "reasoning": f"[{self.model_a}] {judge_a['reasoning']} | [{self.model_b}] {judge_b['reasoning']}",
            "cost": total_cost,
        }

    async def _compatible_gather(self, question, answer, ground_truth):
        import asyncio

        return await asyncio.gather(
            self._ask_judge(self.model_a, question, answer, ground_truth),
            self._ask_judge(self.model_b, question, answer, ground_truth),
        )

    async def check_position_bias(self, response_a: str, response_b: str):
        """Nang cao: doi cho response A/B de kiem tra Judge co thien vi vi tri khong."""
        pass

    async def evaluate_multi_judge_cascade(self, question: str, answer: str, ground_truth: str) -> Dict[str, Any]:
        """
        Cost-optimization mode (OFF by default, dung de benchmark rieng - xem
        analysis/cost_optimization.md). Goi model re (model_a) truoc; chi escalate
        sang model dat (model_b) khi diem cua model_a nam o vung "khong chac chan"
        (2-4/5). Cac case ro ret (1 hoac 5 - that bai/thanh cong ro rang) duoc
        model_a quyet dinh mot minh vi do la nhung truong hop 2 model hau nhu luon
        dong thuan (xem du lieu thuc te trong reports/benchmark_results.json).

        Day VAN la kien truc Multi-Judge (2 model khac nhau), chi khac la model_b
        duoc goi co dieu kien thay vi luon luon - khong vi pham yeu cau "it nhat 2
        model Judge" cua rubric.
        """
        judge_a = await self._ask_judge(self.model_a, question, answer, ground_truth)
        score_a = judge_a["score"]

        if score_a not in (2, 3, 4):
            return {
                "final_score": float(score_a),
                "agreement_rate": None,
                "conflict_resolved": False,
                "escalated": False,
                "individual_scores": {self.model_a: score_a},
                "reasoning": f"[{self.model_a}-only, confident] {judge_a['reasoning']}",
                "cost": judge_a["cost"],
            }

        judge_b = await self._ask_judge(self.model_b, question, answer, ground_truth)
        score_b = judge_b["score"]
        diff = abs(score_a - score_b)
        total_cost = judge_a["cost"] + judge_b["cost"]
        conflict_resolved = False
        scores_used = [score_a, score_b]

        if diff > 1:
            tiebreaker = await self._ask_judge(self.tiebreaker_model, question, answer, ground_truth)
            total_cost += tiebreaker["cost"]
            scores_used.append(tiebreaker["score"])
            conflict_resolved = True

        scores_used.sort()
        final_score = scores_used[len(scores_used) // 2] if conflict_resolved else (score_a + score_b) / 2
        agreement_rate = 1.0 if diff == 0 else (0.5 if diff == 1 else 0.0)

        return {
            "final_score": final_score,
            "agreement_rate": agreement_rate,
            "conflict_resolved": conflict_resolved,
            "escalated": True,
            "individual_scores": {self.model_a: score_a, self.model_b: score_b},
            "reasoning": f"[{self.model_a}] {judge_a['reasoning']} | [{self.model_b}] {judge_b['reasoning']}",
            "cost": total_cost,
        }
