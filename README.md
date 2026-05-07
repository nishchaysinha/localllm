# localllm

Self-hosted LLM inference stack using [llama-cpp-turboquant](https://github.com/TheTom/llama-cpp-turboquant) in Docker with NVIDIA GPU acceleration and optional Cloudflare tunnel for remote access.

## Stack

- **llama-cpp-turboquant** — llama.cpp fork with TurboQuant KV cache quantization (`turbo3`/`turbo4` types)
- **Docker + NVIDIA Container Toolkit** — GPU passthrough
- **Cloudflare Tunnel** — zero-config HTTPS remote access (optional)

## Requirements

- NVIDIA GPU with CUDA 12.x drivers
- Docker + [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- `docker compose` v2

## Setup

1. Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
LLAMA_API_KEY=your-secret-key        # protects the /v1 endpoint
CF_TUNNEL_TOKEN=your-tunnel-token    # optional, Cloudflare Zero Trust tunnel
```

2. Place your model files in `./models/`:

```
models/
  gemma-4-26B-A4B-it-UD-IQ4_NL.gguf
  mmproj-F16.gguf                      # multimodal projector (optional)
```

3. Start the server:

```bash
docker compose up -d
```

The OpenAI-compatible API is available at `http://localhost:8000/v1`.

## Configuration

Key environment variables in `docker-compose.yml`:

| Variable | Default | Description |
|---|---|---|
| `LLAMA_ARG_MODEL` | — | Path to the GGUF model file |
| `LLAMA_ARG_MMPROJ` | — | Multimodal projector path (vision models) |
| `LLAMA_ARG_N_GPU_LAYERS` | `999` | Layers to offload to GPU (`999` = all) |
| `LLAMA_ARG_CTX_SIZE` | `65536` | Context window size in tokens |
| `LLAMA_ARG_CACHE_TYPE_K` | `turbo4` | KV cache type for keys (TurboQuant) |
| `LLAMA_ARG_CACHE_TYPE_V` | `turbo3` | KV cache type for values (TurboQuant) |
| `LLAMA_ARG_FLASH_ATTN` | `on` | Enable flash attention |
| `LLAMA_ARG_N_PARALLEL` | `1` | Max concurrent request slots |
| `LLAMA_ARG_NO_MMAP` | `1` | Disable mmap (needed with mlock) |
| `LLAMA_ARG_MLOCK` | `1` | Lock model weights in RAM |

See [`LLAMA_SERVER_FLAGS.md`](LLAMA_SERVER_FLAGS.md) for the full flag reference.

## Cloudflare Tunnel (optional)

Set `CF_TUNNEL_TOKEN` in `.env`. The `tunnel` service in `docker-compose.yml` forwards traffic from your Cloudflare domain to the llama server automatically. No port forwarding needed.

## Test & Benchmark Scripts

All scripts read configuration from environment variables:

```bash
export LLAMA_BASE_URL=http://localhost:8000
export LLAMA_API_KEY=your-secret-key
export LLAMA_MODEL=default   # llama-server ignores this, any value works
```

| Script | Purpose |
|---|---|
| `test_tq.py` | Basic smoke tests: health, chat, streaming, context |
| `ceiling_test.py` | Throughput ceiling: many short concurrent requests |
| `stress_test.py` | Context length probe + concurrency sweep |
| `test_40k.py` | 40K token context window probe |
| `glm_loadtest.py` | Context + concurrency test for smaller models |
| `rgb_status.py` | OpenRGB LED status light (idle/active/error) |

### RGB Status Light

`rgb_status.py` changes your RGB lighting based on inference activity. Requires [OpenRGB](https://openrgb.org/) running with the SDK server enabled (Settings → SDK Server → Enable).

```bash
VLLM_URL=http://localhost:8000 VLLM_API_KEY=your-key python rgb_status.py
```

Colors are configurable via env vars (hex RGB):

```bash
RGB_COLOR_IDLE=00CCAA      # soft cyan
RGB_COLOR_ACTIVE=AA00FF    # purple
RGB_COLOR_ERROR=FF0000     # red
RGB_COLOR_STARTING=FFAA00  # orange
```

## Building the Image

The Dockerfile builds `llama-server` from source against CUDA 12.6 with OpenBLAS. To rebuild:

```bash
docker compose build --no-cache
```
