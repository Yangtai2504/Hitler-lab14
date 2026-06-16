import json
import os
import random
from typing import List, Dict

# Simple synthetic data generator for Golden Dataset
DOCS_DIR = "data/docs"
GOLDEN_PATH = "data/golden_set.jsonl"

SAMPLE_TOPICS = [
    "privacy policy",
    "password reset",
    "refund policy",
    "account deletion",
    "data retention",
    "two-factor authentication",
    "usage limits",
    "billing cycle",
    "subscription upgrade",
    "terms of service",
]

def _make_sentence(topic: str, i: int) -> str:
    return f"{topic.capitalize()} guideline example sentence number {i}. It explains a concrete detail about {topic}."

def generate_documents(n_docs: int = 80) -> Dict[str, str]:
    os.makedirs(DOCS_DIR, exist_ok=True)
    docs = {}
    for i in range(1, n_docs + 1):
        doc_id = f"doc_{i:03d}"
        topic = random.choice(SAMPLE_TOPICS)
        sentences = [_make_sentence(topic, j) for j in range(1, random.randint(6, 12))]
        # inject some overlapping sentences across documents to create realistic retrieval noise
        if i % 10 == 0:
            sentences.append("This document shares a common sentence used for distractor tests.")
        text = " ".join(sentences)
        path = os.path.join(DOCS_DIR, f"{doc_id}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        docs[doc_id] = text
    return docs

def generate_cases(docs: Dict[str, str], n_cases: int = 60) -> List[Dict]:
    cases = []
    doc_ids = list(docs.keys())
    for i in range(1, n_cases + 1):
        case_id = f"case_{i:03d}"
        # pick a ground truth doc
        gt_doc = random.choice(doc_ids)
        sentences = docs[gt_doc].split(". ")
        answer = sentences[0].strip() if sentences else "No answer available."
        # create a simple question referencing the topic
        question = f"What does the document say about {answer.split()[0]}?"
        # occasionally make adversarial cases with multiple ground-truth docs
        if random.random() < 0.15:
            other = random.choice(doc_ids)
            expected_docs = list({gt_doc, other})
            # slightly paraphrase expected answer
            expected_answer = answer + " (paraphrased)"
            difficulty = "hard"
        else:
            expected_docs = [gt_doc]
            expected_answer = answer
            difficulty = "medium"

        case = {
            "id": case_id,
            "question": question,
            "expected_answer": expected_answer,
            "ground_truth_doc_ids": expected_docs,
            "metadata": {"difficulty": difficulty}
        }
        cases.append(case)
    return cases

def write_golden(cases: List[Dict]):
    os.makedirs(os.path.dirname(GOLDEN_PATH), exist_ok=True)
    with open(GOLDEN_PATH, "w", encoding="utf-8") as f:
        for case in cases:
            f.write(json.dumps(case, ensure_ascii=False) + "\n")

def main():
    random.seed(42)
    docs = generate_documents(n_docs=80)
    cases = generate_cases(docs, n_cases=60)
    write_golden(cases)
    print(f"Generated {len(docs)} docs and {len(cases)} cases to {GOLDEN_PATH}")

if __name__ == "__main__":
    main()
