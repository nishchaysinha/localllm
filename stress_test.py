#!/usr/bin/env python3
"""Stress test: max context + concurrency sweep for vLLM + TurboQuant."""

import asyncio, aiohttp, time, json, sys, os

BASE = os.environ.get("LLAMA_BASE_URL", "http://localhost:8000")
KEY = os.environ.get("LLAMA_API_KEY", "")
MODEL = os.environ.get("LLAMA_MODEL", "default")
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
FILLER_SENTENCE = "The quick brown fox jumps over the lazy dog. "  # ~10 tokens


def make_payload(target_prompt_tokens, max_tokens=30):
    repeats = max(1, (target_prompt_tokens * 4) // len(FILLER_SENTENCE))
    filler = FILLER_SENTENCE * repeats
    return {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": filler},
            {"role": "user", "content": "Reply with OK."},
        ],
        "max_tokens": max_tokens,
    }


async def single_request(session, payload, req_id=""):
    t0 = time.time()
    try:
        async with session.post(f"{BASE}/v1/chat/completions",
                                headers=HEADERS, json=payload,
                                timeout=aiohttp.ClientTimeout(total=120)) as r:
            body = await r.json()
            elapsed = time.time() - t0
            if "error" in body:
                return {"id": req_id, "ok": False, "error": body["error"]["message"][:120], "time": elapsed}
            usage = body["usage"]
            return {
                "id": req_id, "ok": True, "time": elapsed,
                "prompt_tokens": usage["prompt_tokens"],
                "completion_tokens": usage["completion_tokens"],
            }
    except Exception as e:
        return {"id": req_id, "ok": False, "error": str(e)[:120], "time": time.time() - t0}


# ── Part 1: Max context length probe ──
async def probe_max_context():
    print("=" * 65)
    print("  PART 1: Maximum Context Length Probe")
    print("=" * 65)
    # max_model_len=16384, try filling up to that
    targets = [8000, 12000, 14000, 15000, 15500, 16000, 16200, 16350]
    async with aiohttp.ClientSession() as session:
        for target in targets:
            payload = make_payload(target, max_tokens=10)
            result = await single_request(session, payload, f"{target}tok")
            if result["ok"]:
                print(f"  {target:>6} target → {result['prompt_tokens']:>6} actual prompt tokens | "
                      f"{result['time']:.2f}s ✅")
            else:
                print(f"  {target:>6} target → FAILED: {result['error'][:80]} ❌")
                break  # no point going higher


# ── Part 2: Concurrency sweep ──
async def concurrency_sweep():
    print("\n" + "=" * 65)
    print("  PART 2: Concurrent Request Sweep")
    print("  (short prompts, 100 output tokens each)")
    print("=" * 65)

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": "Write a haiku about the ocean."}],
        "max_tokens": 100,
    }

    levels = [1, 2, 3, 4, 5, 6, 8, 10]
    async with aiohttp.ClientSession() as session:
        for n in levels:
            tasks = [single_request(session, payload, f"r{i}") for i in range(n)]
            t0 = time.time()
            results = await asyncio.gather(*tasks)
            wall = time.time() - t0

            ok = [r for r in results if r["ok"]]
            fail = [r for r in results if not r["ok"]]
            total_comp = sum(r["completion_tokens"] for r in ok)
            total_prompt = sum(r["prompt_tokens"] for r in ok)
            avg_latency = sum(r["time"] for r in ok) / len(ok) if ok else 0
            throughput = total_comp / wall if wall > 0 else 0

            status = "✅" if not fail else f"⚠️  {len(fail)} failed"
            print(f"  {n:>2} concurrent | wall {wall:5.2f}s | avg latency {avg_latency:5.2f}s | "
                  f"{throughput:6.1f} tok/s | {len(ok)}/{n} ok {status}")
            if fail:
                print(f"     errors: {fail[0]['error'][:80]}")
                if n > 3 and len(fail) == n:
                    print("     All failed, stopping sweep.")
                    break


# ── Part 3: Concurrency + longer context ──
async def concurrency_with_context():
    print("\n" + "=" * 65)
    print("  PART 3: Concurrent Requests with ~4K Context Each")
    print("=" * 65)

    payload = make_payload(4000, max_tokens=50)
    levels = [1, 2, 3, 4, 5]
    async with aiohttp.ClientSession() as session:
        for n in levels:
            tasks = [single_request(session, payload, f"r{i}") for i in range(n)]
            t0 = time.time()
            results = await asyncio.gather(*tasks)
            wall = time.time() - t0

            ok = [r for r in results if r["ok"]]
            fail = [r for r in results if not r["ok"]]
            total_comp = sum(r["completion_tokens"] for r in ok)
            avg_latency = sum(r["time"] for r in ok) / len(ok) if ok else 0
            throughput = total_comp / wall if wall > 0 else 0
            prompt_tok = ok[0]["prompt_tokens"] if ok else "?"

            status = "✅" if not fail else f"⚠️  {len(fail)} failed"
            print(f"  {n:>2} concurrent | ~{prompt_tok} prompt tok each | wall {wall:5.2f}s | "
                  f"avg lat {avg_latency:5.2f}s | {throughput:5.1f} tok/s | {len(ok)}/{n} ok {status}")
            if fail:
                print(f"     errors: {fail[0]['error'][:80]}")
                if len(fail) == n:
                    break


async def main():
    print(f"Stress testing vLLM + TurboQuant @ {BASE}")
    print(f"Model: {MODEL}\n")
    await probe_max_context()
    await concurrency_sweep()
    await concurrency_with_context()
    print(f"\n{'='*65}\n  Done.\n{'='*65}")


if __name__ == "__main__":
    asyncio.run(main())
