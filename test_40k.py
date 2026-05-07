#!/usr/bin/env python3
"""Test max context at 40K."""
import requests, time, os

BASE = os.environ.get("LLAMA_BASE_URL", "http://localhost:8000")
KEY = os.environ.get("LLAMA_API_KEY", "")
MODEL = os.environ.get("LLAMA_MODEL", "default")
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
FILLER = "The quick brown fox jumps over the lazy dog. "


def test(label, target_tokens, max_tokens=20):
    repeats = max(1, (target_tokens * 4) // len(FILLER))
    payload = {
        "model": MODEL, "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": FILLER * repeats},
            {"role": "user", "content": "Reply OK."},
        ],
    }
    t0 = time.time()
    r = requests.post(f"{BASE}/v1/chat/completions", headers=H, json=payload, timeout=300)
    elapsed = time.time() - t0
    body = r.json()
    if "error" in body:
        print(f"  {label:>20} → ❌ {body['error']['message'][:100]}")
    else:
        u = body["usage"]
        print(f"  {label:>20} → {u['prompt_tokens']:>6} prompt tok | {elapsed:.1f}s ✅")


print("Context length probe (40K max):\n")
for target in [8000, 16000, 24000, 32000, 36000, 38000, 40000]:
    test(f"~{target//1000}K", target)
