"""GLM-4.7-Flash TurboQuant load test — max context + concurrency"""
import asyncio, aiohttp, time, requests, sys, os

BASE = os.environ.get("LLAMA_BASE_URL", "http://localhost:8000")
KEY = os.environ.get("LLAMA_API_KEY", "")
MODEL = os.environ.get("LLAMA_MODEL", "default")
H = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
FILLER = "The quick brown fox jumps over the lazy dog. " * 10  # ~100 tokens

def vram():
    import subprocess
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,memory.free", "--format=csv,noheader,nounits"], capture_output=True, text=True)
    used, free = r.stdout.strip().split(", ")
    return int(used), int(free)

def chat(prompt, max_tokens=20, timeout=300):
    r = requests.post(f"{BASE}/v1/chat/completions", headers=H, json={
        "model": MODEL, "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    }, timeout=timeout)
    return r.json()

async def async_chat(session, prompt, max_tokens=20):
    async with session.post(f"{BASE}/v1/chat/completions", headers=H, json={
        "model": MODEL, "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens
    }, timeout=aiohttp.ClientTimeout(total=300)) as r:
        return await r.json()

def test_context(target_tokens, label):
    copies = max(1, target_tokens // 100)
    prompt = (FILLER * copies)[:target_tokens * 4]  # rough char estimate
    u, f = vram()
    print(f"\n[{label}] ~{target_tokens//1000}K tokens | VRAM: {u}/{u+f} ({f} free)")
    t0 = time.time()
    try:
        r = chat(prompt, max_tokens=30, timeout=300)
        dt = time.time() - t0
        if "error" in r:
            print(f"  ❌ Error: {r['error'].get('message','?')[:120]}")
            return False
        usage = r.get("usage", {})
        timings = r.get("timings", {})
        print(f"  ✅ prompt={usage.get('prompt_n','?')} tok, gen={usage.get('predicted_n','?')} tok")
        print(f"     pp={timings.get('prompt_per_second',0):.1f} t/s, tg={timings.get('predicted_per_second',0):.1f} t/s, wall={dt:.1f}s")
        u2, f2 = vram()
        print(f"     VRAM after: {u2}/{u2+f2} ({f2} free)")
        return True
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {e}")
        return False

async def test_concurrent(n):
    print(f"\n[CONCURRENT] {n} simultaneous requests")
    prompt = "What is 2+2? Answer in one word."
    t0 = time.time()
    try:
        async with aiohttp.ClientSession() as session:
            tasks = [async_chat(session, prompt, 15) for _ in range(n)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        dt = time.time() - t0
        ok = sum(1 for r in results if isinstance(r, dict) and "choices" in r)
        errs = sum(1 for r in results if isinstance(r, Exception) or (isinstance(r, dict) and "error" in r))
        print(f"  ✅ {ok}/{n} succeeded, {errs} failed, wall={dt:.1f}s")
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                print(f"  req {i}: {type(r).__name__}: {r}")
            elif isinstance(r, dict) and "error" in r:
                print(f"  req {i}: error: {r['error'].get('message','?')[:80]}")
    except Exception as e:
        print(f"  ❌ {type(e).__name__}: {e}")

print("=" * 60)
print("GLM-4.7-Flash TurboQuant (tbq3) Load Test")
print("=" * 60)

# Phase 1: escalating context
for target in [4000, 16000, 32000, 48000, 64000, 80000]:
    ok = test_context(target, f"CTX")
    if not ok:
        print(f"  ⚠️  Failed at ~{target//1000}K — this is the practical ceiling")
        break

# Phase 2: concurrent requests (server has n_parallel=1 so they queue)
asyncio.run(test_concurrent(2))
asyncio.run(test_concurrent(4))

print("\n" + "=" * 60)
print("Done!")
