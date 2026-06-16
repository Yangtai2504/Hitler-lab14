import os
import threading
import time

from dotenv import load_dotenv

load_dotenv()

_client = None
_lock = threading.Lock()

# Gia chi phi tham khao (USD / 1K token), dung de tinh cost report.
PRICING_PER_1K_TOKENS = {
    "gemini-2.5-pro": {"input": 0.00125, "output": 0.005},
    "gemini-2.5-flash": {"input": 0.0003, "output": 0.0025},
    "gemini-2.5-flash-lite": {"input": 0.0001, "output": 0.0004},
}


def get_client():
    global _client
    with _lock:
        if _client is None:
            from google import genai

            _client = genai.Client(
                vertexai=True,
                project=os.getenv("VERTEX_PROJECT"),
                location=os.getenv("VERTEX_LOCATION", "us-central1"),
            )
    return _client


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    price = PRICING_PER_1K_TOKENS.get(model, {"input": 0.0005, "output": 0.0015})
    return (input_tokens / 1000) * price["input"] + (output_tokens / 1000) * price["output"]


async def generate(model: str, prompt: str, temperature: float = 0.2) -> dict:
    """Goi Gemini qua Vertex AI (sync SDK chay trong thread de khong block event loop).
    Tu dong retry voi exponential backoff khi bi 429 RESOURCE_EXHAUSTED (rate limit)."""
    import asyncio

    client = get_client()

    def _call():
        from google.genai import errors, types

        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=temperature),
                )
                usage = response.usage_metadata
                input_tokens = usage.prompt_token_count if usage else 0
                output_tokens = usage.candidates_token_count if usage else 0
                return {
                    "text": response.text or "",
                    "model": model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost": estimate_cost(model, input_tokens, output_tokens),
                }
            except errors.ClientError as e:
                if "RESOURCE_EXHAUSTED" in str(e) and attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise

    return await asyncio.to_thread(_call)
