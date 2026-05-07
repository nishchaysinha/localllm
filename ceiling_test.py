#!/usr/bin/env python3
"""Find the true throughput ceiling: many short requests, high concurrency."""

import asyncio, aiohttp, time, os

BASE = os.environ.get("LLAMA_BASE_URL", "http://localhost:8000")
KEY = os.environ.get("LLAMA_API_KEY", "")
MODEL = os.environ.get("LLAMA_MODEL", "default")
HEADERS = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


async def fire(session, prompt, max_tokens):
    t0 = time.time()
    try:
        async with session.post(f"{BASE}/v1/chat/completions", headers=HEADERS,
                                json={"model": MODEL, "max_tokens": max_tokens,
                                      "messages": [{"role": "user", "content": prompt}]},
                                timeout=aiohttp.ClientTimeout(total=180)) as r:
            body = await r.json()
            elapsed = time.time() - t0
            if "error" in body:
                return None, elapsed, body["error"]["message"][:80]
            return body["usage"], elapsed, None
    except Exception as e:
        return None, time.time() - t0, str(e)[:80]


async def throughput_test(n_requests, max_tokens, prompt="Write a short story about a cat."):
    async with aiohttp.ClientSession() as session:
        tasks = [fire(session, prompt, max_tokens) for _ in range(n_requests)]
        t0 = time.time()
        results = await asyncio.gather(*tasks)
        wall = time.time() - t0

    ok = [(u, t) for u, t, e in results if u]
    fails = [e for _, _, e in results if e]
    total_out = sum(u["completion_tokens"] for u, _ in ok)
    total_in = sum(u["prompt_tokens"] for u, _ in ok)
    avg_lat = sum(t for _, t in ok) / len(ok) if ok else 0
    tps = total_out / wall if wall > 0 else 0

    return {
        "n": n_requests, "ok": len(ok), "fail": len(fails),
        "wall": wall, "avg_lat": avg_lat,
        "total_in": total_in, "total_out": total_out, "tps": tps,
        "first_err": fails[0] if fails else None,
    }


async def main():
    print("=" * 70)
    print("  THROUGHPUT CEILING TEST")
    print("  Firing N requests simultaneously, 100 output tokens each")
    print("=" * 70)
    print(f"  {'N':>3} | {'OK':>3} | {'Wall':>6} | {'Avg Lat':>7} | {'Out Tok':>7} | {'Tok/s':>7} | Notes")
    print("  " + "-" * 64)

    for n in [1, 2, 3, 4, 6, 8, 10, 15, 20]:
        r = await throughput_test(n, 100)
        notes = f"❌ {r['fail']} failed" if r["fail"] else "✅"
        print(f"  {r['n']:>3} | {r['ok']:>3} | {r['wall']:5.1f}s | {r['avg_lat']:6.2f}s | {r['total_out']:>7} | {r['tps']:6.1f} | {notes}")
        if r["first_err"]:
            print(f"       err: {r['first_err']}")

    print()
    print("=" * 70)
    print("  SUSTAINED THROUGHPUT: 30 requests, 200 tokens each")
    print("=" * 70)
    r = await throughput_test(30, 200)
    print(f"  {r['ok']}/{r['n']} succeeded | wall {r['wall']:.1f}s | {r['tps']:.1f} tok/s aggregate")
    print(f"  avg latency {r['avg_lat']:.1f}s | {r['total_out']} output tokens total")
    if r["first_err"]:
        print(f"  errors: {r['first_err']}")

    print()
    print("=" * 70)
    print("  CONTEXT + CONCURRENCY: 6 requests × ~4K context × 100 tokens")
    print("=" * 70)
    filler = "The quick brown fox jumps over the lazy dog. " * 500
    r = await throughput_test(6, 100, prompt=f"Summarize: {filler}")
    print(f"  {r['ok']}/{r['n']} succeeded | wall {r['wall']:.1f}s | {r['tps']:.1f} tok/s")
    print(f"  ~{r['total_in']//r['ok'] if r['ok'] else 0} prompt tok each | avg latency {r['avg_lat']:.1f}s")


asyncio.run(main())
