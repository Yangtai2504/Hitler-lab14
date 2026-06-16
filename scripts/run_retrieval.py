import json
import asyncio
from engine.retrieval_eval import RetrievalEvaluator

async def main():
    with open('data/golden_set.jsonl', 'r', encoding='utf-8') as f:
        dataset = [json.loads(line) for line in f if line.strip()]
    ev = RetrievalEvaluator()
    summary = await ev.evaluate_batch(dataset, docs_dir='data/docs', top_k=5)
    print('Retrieval summary:', summary)

if __name__ == '__main__':
    asyncio.run(main())
