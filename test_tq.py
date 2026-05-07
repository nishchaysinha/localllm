#!/usr/bin/env python3
"""Quick vLLM + TurboQuant integration test."""

import requests, time, json, sys, os

BASE = os.environ.get("LLAMA_BASE_URL", "http://localhost:8000")
KEY = os.environ.get("LLAMA_API_KEY", "")
MODEL = os.environ.get("LLAMA_MODEL", "default")
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def chat(messages, max_tokens=100, **kw):
    r = requests.post(f"{BASE}/v1/chat/completions",
                      headers=HEADERS,
                      json={"model": MODEL, "messages": messages,
                            "max_tokens": max_tokens, **kw})
    return r.json()


def test(name, fn):
    print(f"\n{'='*60}\n  {name}\n{'='*60}")
    try:
        fn()
        print(f"  ✅ PASSED")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")


# --- 1. Health check ---
def t_health():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200, f"health returned {r.status_code}"
    print(f"  Status: {r.status_code}")

# --- 2. Basic chat ---
def t_basic():
    t0 = time.time()
    resp = chat([{"role": "user", "content": "What is 2+2? Answer with just the number."}], max_tokens=20)
    elapsed = time.time() - t0
    content = resp["choices"][0]["message"]["content"]
    usage = resp["usage"]
    print(f"  Response: {content[:100]}")
    print(f"  Tokens: {usage['prompt_tokens']} prompt, {usage['completion_tokens']} completion")
    print(f"  Latency: {elapsed:.2f}s")

# --- 3. Longer generation ---
def t_generation():
    t0 = time.time()
    resp = chat([{"role": "user", "content": "Write a short poem about AI."}], max_tokens=200)
    elapsed = time.time() - t0
    content = resp["choices"][0]["message"]["content"]
    usage = resp["usage"]
    tps = usage["completion_tokens"] / elapsed if elapsed > 0 else 0
    print(f"  Response ({usage['completion_tokens']} tokens):\n    {content[:300]}...")
    print(f"  Throughput: {tps:.1f} tok/s | Latency: {elapsed:.2f}s")

# --- 4. Long context - fill ~8K tokens ---
def t_context_8k():
    # ~4 chars per token, aim for ~8K tokens of context
    filler = "The quick brown fox jumps over the lazy dog. " * 500  # ~4500 words ≈ 6K tokens
    t0 = time.time()
    resp = chat([
        {"role": "system", "content": f"You have been given a long document. Here it is:\n{filler}"},
        {"role": "user", "content": "How many times does the word 'fox' appear in the document above? Just give the number."}
    ], max_tokens=30)
    elapsed = time.time() - t0
    content = resp["choices"][0]["message"]["content"]
    usage = resp["usage"]
    print(f"  Prompt tokens: {usage['prompt_tokens']}")
    print(f"  Response: {content[:150]}")
    print(f"  TTFT + generation: {elapsed:.2f}s")

# --- 5. Long context - fill ~14K tokens (near max_model_len=16384) ---
def t_context_14k():
    filler = "The quick brown fox jumps over the lazy dog. " * 1200  # ~10800 words ≈ 14K tokens
    t0 = time.time()
    resp = chat([
        {"role": "system", "content": f"You have been given a long document. Here it is:\n{filler}"},
        {"role": "user", "content": "Summarize the document in one sentence."}
    ], max_tokens=50)
    elapsed = time.time() - t0
    if "error" in resp:
        raise RuntimeError(resp["error"]["message"][:200])
    content = resp["choices"][0]["message"]["content"]
    usage = resp["usage"]
    print(f"  Prompt tokens: {usage['prompt_tokens']}")
    print(f"  Response: {content[:200]}")
    print(f"  TTFT + generation: {elapsed:.2f}s")

# --- 6. Streaming ---
def t_streaming():
    t0 = time.time()
    r = requests.post(f"{BASE}/v1/chat/completions", headers=HEADERS, stream=True,
                      json={"model": MODEL, "stream": True, "max_tokens": 60,
                            "messages": [{"role": "user", "content": "Count from 1 to 10."}]})
    chunks = 0
    first_token_time = None
    for line in r.iter_lines():
        if line and line.startswith(b"data: ") and b"[DONE]" not in line:
            chunks += 1
            if first_token_time is None:
                first_token_time = time.time()
    elapsed = time.time() - t0
    ttft = (first_token_time - t0) if first_token_time else 0
    print(f"  Chunks received: {chunks}")
    print(f"  TTFT: {ttft:.2f}s | Total: {elapsed:.2f}s")


if __name__ == "__main__":
    print(f"Testing vLLM + TurboQuant @ {BASE}")
    print(f"Model: {MODEL}")
    test("1. Health Check", t_health)
    test("2. Basic Chat (2+2)", t_basic)
    test("3. Longer Generation (poem)", t_generation)
    test("4. ~8K Context Window", t_context_8k)
    test("5. ~14K Context Window (near limit)", t_context_14k)
    test("6. Streaming", t_streaming)
    print(f"\n{'='*60}\n  All tests complete.\n{'='*60}")
