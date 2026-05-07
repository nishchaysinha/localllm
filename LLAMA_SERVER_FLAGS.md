# llama-server Flags Reference
> Scraped directly from `docker exec localllm-llama-1 /app/llama-server --help`
> Binary: TheTom/llama-cpp-turboquant fork (adds turbo2/turbo3/turbo4 KV cache types)
> GPU: RTX 4070 Ti SUPER (16 GB VRAM)

---

## Common Params

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--help`, `--usage` | `-h` | — | — | Print usage and exit |
| `--version` | — | — | — | Show version and build info |
| `--license` | — | — | — | Show source code license and dependencies |
| `--cache-list` | `-cl` | — | — | Show list of models in cache |
| `--completion-bash` | — | — | — | Print source-able bash completion script |

### Threading / CPU

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--threads N` | `-t` | -1 | `LLAMA_ARG_THREADS` | CPU threads during generation |
| `--threads-batch N` | `-tb` | same as --threads | — | Threads for batch/prompt processing |
| `--cpu-mask M` | `-C` | `""` | `LLAMA_ARG_CPU_MASK` | CPU affinity mask (hex) |
| `--cpu-range lo-hi` | `-Cr` | — | — | CPU range for affinity, complements --cpu-mask |
| `--cpu-strict <0\|1>` | — | 0 | — | Use strict CPU placement |
| `--prio N` | — | 0 | — | Process priority: low(-1), normal(0), medium(1), high(2), realtime(3) |
| `--poll <0...100>` | — | 50 | — | Polling level (0 = no polling) |
| `--cpu-mask-batch M` | `-Cb` | same as --cpu-mask | — | CPU affinity mask for batch |
| `--cpu-range-batch lo-hi` | `-Crb` | — | — | CPU range for batch affinity |
| `--cpu-strict-batch <0\|1>` | — | same as --cpu-strict | — | Strict CPU placement for batch |
| `--prio-batch N` | — | 0 | — | Thread priority for batch: 0-normal, 1-medium, 2-high, 3-realtime |
| `--poll-batch <0\|1>` | — | same as --poll | — | Use polling for batch |

### Context & Generation

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--ctx-size N` | `-c` | 0 (from model) | `LLAMA_ARG_CTX_SIZE` | Prompt context window size |
| `--predict N`, `--n-predict N` | `-n` | -1 (infinity) | `LLAMA_ARG_N_PREDICT` | Tokens to predict |
| `--batch-size N` | `-b` | 2048 | `LLAMA_ARG_BATCH` | Logical max batch size |
| `--ubatch-size N` | `-ub` | 512 | `LLAMA_ARG_UBATCH` | Physical max batch size |
| `--keep N` | — | 0 | — | Tokens to keep from initial prompt (-1 = all) |
| `--swa-full` | — | false | `LLAMA_ARG_SWA_FULL` | Use full-size SWA cache |

### Attention & Performance

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--flash-attn [on\|off\|auto]` | `-fa` | auto | `LLAMA_ARG_FLASH_ATTN` | Flash Attention mode |
| `--perf`, `--no-perf` | — | false | `LLAMA_ARG_PERF` | Enable internal libllama performance timings |
| `--escape`, `--no-escape` | `-e` | true | — | Process escape sequences (\n, \r, \t, etc.) |
| `--op-offload`, `--no-op-offload` | — | true | — | Offload host tensor operations to device |

### RoPE / YaRN

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--rope-scaling {none,linear,yarn}` | — | from model | `LLAMA_ARG_ROPE_SCALING_TYPE` | RoPE frequency scaling method |
| `--rope-scale N` | — | — | `LLAMA_ARG_ROPE_SCALE` | RoPE context scaling factor |
| `--rope-freq-base N` | — | from model | `LLAMA_ARG_ROPE_FREQ_BASE` | RoPE base frequency |
| `--rope-freq-scale N` | — | — | `LLAMA_ARG_ROPE_FREQ_SCALE` | RoPE frequency scaling factor (1/N) |
| `--yarn-orig-ctx N` | — | 0 | `LLAMA_ARG_YARN_ORIG_CTX` | YaRN: original context size |
| `--yarn-ext-factor N` | — | -1.00 | `LLAMA_ARG_YARN_EXT_FACTOR` | YaRN: extrapolation mix factor |
| `--yarn-attn-factor N` | — | -1.00 | `LLAMA_ARG_YARN_ATTN_FACTOR` | YaRN: scale sqrt(t) / attention magnitude |
| `--yarn-beta-slow N` | — | -1.00 | `LLAMA_ARG_YARN_BETA_SLOW` | YaRN: high correction dim / alpha |
| `--yarn-beta-fast N` | — | -1.00 | `LLAMA_ARG_YARN_BETA_FAST` | YaRN: low correction dim / beta |

### KV Cache

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--kv-offload`, `--no-kv-offload` | `-kvo` / `-nkvo` | enabled | `LLAMA_ARG_KV_OFFLOAD` | KV cache GPU offloading |
| `--cache-type-k TYPE` | `-ctk` | f16 | `LLAMA_ARG_CACHE_TYPE_K` | KV cache K data type |
| `--cache-type-v TYPE` | `-ctv` | f16 | `LLAMA_ARG_CACHE_TYPE_V` | KV cache V data type |
| `--cache-type-k-draft TYPE` | `-ctkd` | f16 | `LLAMA_ARG_CACHE_TYPE_K_DRAFT` | KV cache K type for draft model |
| `--cache-type-v-draft TYPE` | `-ctvd` | f16 | `LLAMA_ARG_CACHE_TYPE_V_DRAFT` | KV cache V type for draft model |
| `--defrag-thold N` | `-dt` | — | `LLAMA_ARG_DEFRAG_THOLD` | KV cache defrag threshold (DEPRECATED) |

**KV cache allowed types:** `f32`, `f16`, `bf16`, `q8_0`, `q4_0`, `q4_1`, `iq4_nl`, `q5_0`, `q5_1`, `turbo2`, `turbo3`, `turbo4`

**TurboQuant types (turboquant fork only):**
- `turbo2`: ~2-bit, most aggressive compression
- `turbo3`: ~3.0625 bits/element, ~5.2x vs F16 — good for V (values)
- `turbo4`: ~4.0625 bits/element, ~3.9x vs F16, near-lossless — good for K (keys)
- **Recommended:** `-ctk turbo4 -ctv turbo3` (keys need higher precision than values)
- Flash attention (`-fa on`) recommended with turbo types

### Memory & Storage

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--repack`, `--no-repack` | — / `-nr` | enabled | `LLAMA_ARG_REPACK` | Weight repacking |
| `--no-host` | — | — | `LLAMA_ARG_NO_HOST` | Bypass host buffer (allows extra buffers) |
| `--mlock` | — | — | `LLAMA_ARG_MLOCK` | Force model to stay in RAM (no swap/compress) |
| `--mmap`, `--no-mmap` | — | enabled | `LLAMA_ARG_MMAP` | Memory-map model file |
| `--direct-io`, `--no-direct-io` | `-dio` / `-ndio` | disabled | `LLAMA_ARG_DIO` | Use DirectIO if available |

### GPU / Device

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--numa TYPE` | — | — | `LLAMA_ARG_NUMA` | NUMA optimizations: `distribute`, `isolate`, `numactl` |
| `--device <dev1,dev2,...>` | `-dev` | — | `LLAMA_ARG_DEVICE` | Comma-separated devices for offloading (`none` = no offload) |
| `--list-devices` | — | — | — | Print available devices and exit |
| `--override-tensor <pattern>=<type>,...` | `-ot` | — | `LLAMA_ARG_OVERRIDE_TENSOR` | Override tensor buffer type |
| `--cpu-moe` | `-cmoe` | — | `LLAMA_ARG_CPU_MOE` | Keep ALL MoE expert weights in CPU |
| `--n-cpu-moe N` | `-ncmoe` | — | `LLAMA_ARG_N_CPU_MOE` | Keep first N layers of MoE weights in CPU |
| `--gpu-layers N` | `-ngl` | auto | `LLAMA_ARG_N_GPU_LAYERS` | Layers to store in VRAM (`auto`, `all`, or number) |
| `--split-mode {none,layer,row,tensor}` | `-sm` | layer | `LLAMA_ARG_SPLIT_MODE` | Multi-GPU split strategy |
| `--tensor-split N0,N1,...` | `-ts` | — | `LLAMA_ARG_TENSOR_SPLIT` | GPU offload proportions |
| `--main-gpu INDEX` | `-mg` | 0 | `LLAMA_ARG_MAIN_GPU` | Primary GPU index |
| `--fit [on\|off]` | `-fit` | on | `LLAMA_ARG_FIT` | Auto-adjust args to fit device memory |
| `--fit-target MiB0,MiB1,...` | `-fitt` | 1024 | `LLAMA_ARG_FIT_TARGET` | Target memory margin per device for --fit |
| `--fit-ctx N` | `-fitc` | 4096 | `LLAMA_ARG_FIT_CTX` | Minimum ctx size --fit can set |
| `--check-tensors` | — | false | — | Validate tensor data for invalid values |

### Model Loading

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--model FNAME` | `-m` | — | `LLAMA_ARG_MODEL` | Model file path |
| `--model-url URL` | `-mu` | — | `LLAMA_ARG_MODEL_URL` | Model download URL |
| `--docker-repo [repo/]model[:quant]` | `-dr` | — | `LLAMA_ARG_DOCKER_REPO` | Docker Hub model repo (default repo: `ai/`) |
| `--hf-repo <user>/<model>[:quant]` | `-hf` / `-hfr` | — | `LLAMA_ARG_HF_REPO` | HuggingFace repo (default quant: Q4_K_M; auto-downloads mmproj) |
| `--hf-repo-draft <user>/<model>[:quant]` | `-hfd` / `-hfrd` | — | `LLAMA_ARG_HFD_REPO` | HF repo for draft model |
| `--hf-file FILE` | `-hff` | — | `LLAMA_ARG_HF_FILE` | Override quant file from --hf-repo |
| `--hf-repo-v <user>/<model>[:quant]` | `-hfv` / `-hfrv` | — | `LLAMA_ARG_HF_REPO_V` | HF repo for vocoder model |
| `--hf-file-v FILE` | `-hffv` | — | `LLAMA_ARG_HF_FILE_V` | HF file for vocoder model |
| `--hf-token TOKEN` | `-hft` | `HF_TOKEN` env | `HF_TOKEN` | HuggingFace access token |
| `--offline` | — | — | `LLAMA_OFFLINE` | Offline mode: force cache, block network |
| `--override-kv KEY=TYPE:VALUE,...` | — | — | — | Override model metadata (types: int, float, bool, str) |
| `--lora FNAME` | — | — | — | LoRA adapter path (comma-separated for multiple) |
| `--lora-scaled FNAME:SCALE,...` | — | — | — | LoRA adapter with custom scaling |
| `--lora-init-without-apply` | — | disabled | — | Load LoRA without applying (apply later via POST /lora-adapters) |
| `--control-vector FNAME` | — | — | — | Control vector path (comma-separated for multiple) |
| `--control-vector-scaled FNAME:SCALE,...` | — | — | — | Control vector with scaling |
| `--control-vector-layer-range START END` | — | — | — | Layer range to apply control vectors |

### Logging

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--log-disable` | — | — | — | Disable logging |
| `--log-file FNAME` | — | — | `LLAMA_LOG_FILE` | Log to file |
| `--log-colors [on\|off\|auto]` | — | auto | `LLAMA_LOG_COLORS` | Colored logging output |
| `--verbose`, `--log-verbose` | `-v` | — | — | Set verbosity to infinity |
| `--verbosity N`, `--log-verbosity N` | `-lv` | 3 | `LLAMA_LOG_VERBOSITY` | Verbosity threshold: 0=generic, 1=error, 2=warn, 3=info, 4=debug |
| `--log-prefix` | — | — | `LLAMA_LOG_PREFIX` | Enable prefix in log messages |
| `--log-timestamps` | — | — | `LLAMA_LOG_TIMESTAMPS` | Add timestamps to log messages |

---

## Sampling Params

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--samplers SAMPLERS` | — | `penalties;dry;top_n_sigma;top_k;typ_p;top_p;min_p;xtc;temperature` | — | Sampler order, semicolon-separated |
| `--sampler-seq SEQUENCE` | — | `edskypmxt` | — | Simplified sampler sequence |
| `--seed SEED` | `-s` | -1 (random) | — | RNG seed |
| `--ignore-eos` | — | — | — | Ignore EOS token, continue generating |
| `--temperature N`, `--temp N` | — | 0.80 | — | Sampling temperature |
| `--top-k N` | — | 40 | `LLAMA_ARG_TOP_K` | Top-k sampling (0 = disabled) |
| `--top-p N` | — | 0.95 | — | Top-p nucleus sampling (1.0 = disabled) |
| `--min-p N` | — | 0.05 | — | Min-p sampling (0.0 = disabled) |
| `--top-nsigma N`, `--top-n-sigma N` | — | -1.00 | — | Top-n-sigma sampling (-1 = disabled) |
| `--xtc-probability N` | — | 0.00 | — | XTC token removal probability (0 = disabled) |
| `--xtc-threshold N` | — | 0.10 | — | XTC minimum probability (1.0 = disabled) |
| `--typical N`, `--typical-p N` | — | 1.00 | — | Locally typical sampling (1.0 = disabled) |
| `--repeat-last-n N` | — | 64 | — | Last N tokens to consider for penalty (0=off, -1=ctx) |
| `--repeat-penalty N` | — | 1.00 | — | Repetition penalty (1.0 = disabled) |
| `--presence-penalty N` | — | 0.00 | — | Presence penalty (0 = disabled) |
| `--frequency-penalty N` | — | 0.00 | — | Frequency penalty (0 = disabled) |
| `--dry-multiplier N` | — | 0.00 | — | DRY sampling multiplier (0 = disabled) |
| `--dry-base N` | — | 1.75 | — | DRY sampling base |
| `--dry-allowed-length N` | — | 2 | — | DRY allowed repetition length |
| `--dry-penalty-last-n N` | — | -1 | — | DRY penalty window (0=off, -1=ctx) |
| `--dry-sequence-breaker STRING` | — | `\n : " *` | — | DRY sequence breakers (use "none" for no breakers) |
| `--adaptive-target N` | — | -1.00 | — | Adaptive-p: target probability (0–1, negative = disabled) |
| `--adaptive-decay N` | — | 0.90 | — | Adaptive-p: decay rate (0–0.99) |
| `--dynatemp-range N` | — | 0.00 | — | Dynamic temperature range (0 = disabled) |
| `--dynatemp-exp N` | — | 1.00 | — | Dynamic temperature exponent |
| `--mirostat N` | — | 0 | — | Mirostat mode: 0=off, 1=Mirostat, 2=Mirostat 2.0 |
| `--mirostat-lr N` | — | 0.10 | — | Mirostat learning rate (eta) |
| `--mirostat-ent N` | — | 5.00 | — | Mirostat target entropy (tau) |
| `--logit-bias TOKEN_ID(+/-)BIAS` | `-l` | — | — | Modify token likelihood |
| `--grammar GRAMMAR` | — | — | — | BNF-like grammar constraint |
| `--grammar-file FNAME` | — | — | — | Grammar from file |
| `--json-schema SCHEMA` | `-j` | — | — | JSON schema constraint |
| `--json-schema-file FILE` | `-jf` | — | — | JSON schema from file |
| `--backend-sampling` | `-bs` | disabled | `LLAMA_ARG_BACKEND_SAMPLING` | Enable backend sampling (experimental) |

---

## Server / Example-Specific Params

### Context Checkpointing & Cache

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--lookup-cache-static FNAME` | `-lcs` | — | — | Static lookup cache for lookup decoding |
| `--lookup-cache-dynamic FNAME` | `-lcd` | — | — | Dynamic lookup cache (updated by generation) |
| `--ctx-checkpoints N`, `--swa-checkpoints N` | `-ctxcp` | 32 | `LLAMA_ARG_CTX_CHECKPOINTS` | Max context checkpoints per slot |
| `--checkpoint-every-n-tokens N` | `-cpent` | 8192 | `LLAMA_ARG_CHECKPOINT_EVERY_NT` | Create checkpoint every N tokens during prefill (-1 = off) |
| `--cache-ram N` | `-cram` | 8192 | `LLAMA_ARG_CACHE_RAM` | Max cache size in MiB (-1 = no limit, 0 = disable) |
| `--kv-unified`, `--no-kv-unified` | `-kvu` / `-no-kvu` | auto | `LLAMA_ARG_KV_UNIFIED` | Single unified KV buffer across all sequences |
| `--cache-idle-slots`, `--no-cache-idle-slots` | — | enabled | `LLAMA_ARG_CACHE_IDLE_SLOTS` | Save and clear idle slots on new task (requires unified KV + cache-ram) |
| `--cache-prompt`, `--no-cache-prompt` | — | enabled | `LLAMA_ARG_CACHE_PROMPT` | Enable prompt caching |
| `--cache-reuse N` | — | 0 | `LLAMA_ARG_CACHE_REUSE` | Min chunk size to reuse from cache via KV shifting |

### Server Behavior

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--context-shift`, `--no-context-shift` | — | disabled | `LLAMA_ARG_CONTEXT_SHIFT` | Context shift for infinite text generation |
| `--reverse-prompt PROMPT` | `-r` | — | — | Halt generation at PROMPT |
| `--special` | `-sp` | false | — | Enable special token output |
| `--warmup`, `--no-warmup` | — | enabled | — | Perform warmup with empty run |
| `--spm-infill` | — | disabled | — | Use Suffix/Prefix/Middle infill pattern |
| `--pooling {none,mean,cls,last,rank}` | — | from model | `LLAMA_ARG_POOLING` | Pooling type for embeddings |
| `--parallel N` | `-np` | -1 (auto) | `LLAMA_ARG_N_PARALLEL` | Number of server slots |
| `--cont-batching`, `--no-cont-batching` | `-cb` / `-nocb` | enabled | `LLAMA_ARG_CONT_BATCHING` | Continuous (dynamic) batching |
| `--sleep-idle-seconds SECONDS` | — | -1 (off) | — | Auto-sleep after N seconds idle |

### Multimodal / Vision

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--mmproj FILE` | `-mm` | — | `LLAMA_ARG_MMPROJ` | Multimodal projector file path |
| `--mmproj-url URL` | `-mmu` | — | `LLAMA_ARG_MMPROJ_URL` | Multimodal projector URL |
| `--mmproj-auto`, `--no-mmproj`, `--no-mmproj-auto` | — | enabled | `LLAMA_ARG_MMPROJ_AUTO` | Auto-use mmproj if available (useful with -hf) |
| `--mmproj-offload`, `--no-mmproj-offload` | — | enabled | `LLAMA_ARG_MMPROJ_OFFLOAD` | GPU offload for multimodal projector |
| `--image-min-tokens N` | — | from model | `LLAMA_ARG_IMAGE_MIN_TOKENS` | Min tokens per image (dynamic resolution models) |
| `--image-max-tokens N` | — | from model | `LLAMA_ARG_IMAGE_MAX_TOKENS` | Max tokens per image (dynamic resolution models) |

### Draft Model / MoE for Draft

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--override-tensor-draft <pattern>=<type>,...` | `-otd` | — | — | Override tensor buffer type for draft model |
| `--cpu-moe-draft` | `-cmoed` | — | `LLAMA_ARG_CPU_MOE_DRAFT` | Keep all MoE weights in CPU for draft model |
| `--n-cpu-moe-draft N` | `-ncmoed` | — | `LLAMA_ARG_N_CPU_MOE_DRAFT` | Keep first N MoE layers in CPU for draft model |

### Server Identity & API

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--alias STRING` | `-a` | — | `LLAMA_ARG_ALIAS` | Model name aliases (comma-separated, used by API) |
| `--tags STRING` | — | — | `LLAMA_ARG_TAGS` | Model tags (informational, comma-separated) |
| `--host HOST` | — | 127.0.0.1 | `LLAMA_ARG_HOST` | Listen IP (use .sock suffix for UNIX socket) |
| `--port PORT` | — | 8080 | `LLAMA_ARG_PORT` | Listen port |
| `--reuse-port` | — | disabled | `LLAMA_ARG_REUSE_PORT` | Allow multiple sockets on same port |
| `--path PATH` | — | — | `LLAMA_ARG_STATIC_PATH` | Static files directory |
| `--api-prefix PREFIX` | — | — | `LLAMA_ARG_API_PREFIX` | API route prefix (no trailing slash) |
| `--timeout N` | `-to` | 600 | `LLAMA_ARG_TIMEOUT` | Server read/write timeout (seconds) |
| `--threads-http N` | — | -1 | `LLAMA_ARG_THREADS_HTTP` | HTTP request processing threads |
| `--api-key KEY` | — | none | `LLAMA_API_KEY` | API auth key(s), comma-separated |
| `--api-key-file FNAME` | — | none | — | File containing API keys |
| `--ssl-key-file FNAME` | — | — | `LLAMA_ARG_SSL_KEY_FILE` | PEM SSL private key file |
| `--ssl-cert-file FNAME` | — | — | `LLAMA_ARG_SSL_CERT_FILE` | PEM SSL certificate file |

### Web UI

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--webui`, `--no-webui` | — | enabled | `LLAMA_ARG_WEBUI` | Enable Web UI |
| `--webui-config JSON` | — | — | `LLAMA_ARG_WEBUI_CONFIG` | JSON for default WebUI settings |
| `--webui-config-file PATH` | — | — | `LLAMA_ARG_WEBUI_CONFIG_FILE` | JSON file for WebUI settings |
| `--webui-mcp-proxy`, `--no-webui-mcp-proxy` | — | disabled | `LLAMA_ARG_WEBUI_MCP_PROXY` | Enable MCP CORS proxy (experimental, do not use in untrusted environments) |
| `--tools TOOL1,TOOL2,...` | — | none | `LLAMA_ARG_TOOLS` | Enable built-in agent tools (experimental). Use `all` for all. Available: `read_file`, `file_glob_search`, `grep_search`, `exec_shell_command`, `write_file`, `edit_file`, `apply_diff` |

### Endpoints

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--embedding`, `--embeddings` | — | disabled | `LLAMA_ARG_EMBEDDINGS` | Embedding-only mode |
| `--rerank`, `--reranking` | — | disabled | `LLAMA_ARG_RERANKING` | Enable reranking endpoint |
| `--metrics` | — | disabled | `LLAMA_ARG_ENDPOINT_METRICS` | Prometheus metrics endpoint |
| `--props` | — | disabled | `LLAMA_ARG_ENDPOINT_PROPS` | Allow POST /props to change global properties |
| `--slots`, `--no-slots` | — | enabled | `LLAMA_ARG_ENDPOINT_SLOTS` | Expose slot monitoring endpoint |
| `--slot-save-path PATH` | — | disabled | — | Directory to save slot KV cache |
| `--media-path PATH` | — | disabled | — | Directory for local media files (accessible via file:// URLs) |

### Multi-Model Router

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--models-dir PATH` | — | disabled | `LLAMA_ARG_MODELS_DIR` | Directory containing models for router server |
| `--models-preset PATH` | — | disabled | `LLAMA_ARG_MODELS_PRESET` | INI file with model presets for router |
| `--models-max N` | — | 4 | `LLAMA_ARG_MODELS_MAX` | Max simultaneous models (0 = unlimited) |
| `--models-autoload`, `--no-models-autoload` | — | enabled | `LLAMA_ARG_MODELS_AUTOLOAD` | Auto-load router models |

### Chat / Templating / Reasoning

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--jinja`, `--no-jinja` | — | enabled | `LLAMA_ARG_JINJA` | Use Jinja template engine |
| `--chat-template JINJA_TEMPLATE` | — | from model | `LLAMA_ARG_CHAT_TEMPLATE` | Custom Jinja chat template. Built-ins: gemma, llama3, chatml, deepseek, mistral-v7, phi4, etc. |
| `--chat-template-file FILE` | — | from model | `LLAMA_ARG_CHAT_TEMPLATE_FILE` | Chat template from file |
| `--chat-template-kwargs STRING` | — | — | `LLAMA_CHAT_TEMPLATE_KWARGS` | Additional JSON params for template parser |
| `--skip-chat-parsing`, `--no-skip-chat-parsing` | — | disabled | `LLAMA_ARG_SKIP_CHAT_PARSING` | Force pure content parser (bypass Jinja) |
| `--prefill-assistant`, `--no-prefill-assistant` | — | enabled | `LLAMA_ARG_PREFILL_ASSISTANT` | Prefill assistant response if last message is assistant |
| `--reasoning-format FORMAT` | — | auto | `LLAMA_ARG_THINK` | Thought tag handling: `none`, `deepseek`, `deepseek-legacy` |
| `--reasoning [on\|off\|auto]` | `-rea` | auto | `LLAMA_ARG_REASONING` | Enable reasoning/thinking mode |
| `--reasoning-budget N` | — | -1 | `LLAMA_ARG_THINK_BUDGET` | Token budget for thinking (-1=unrestricted, 0=immediate end) |
| `--reasoning-budget-message MESSAGE` | — | none | `LLAMA_ARG_THINK_BUDGET_MESSAGE` | Message injected when reasoning budget exhausted |

### Slot Management

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--slot-prompt-similarity SIMILARITY` | `-sps` | 0.10 | — | Prompt match threshold for slot reuse (0 = disabled) |

### Speculative Decoding

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--draft N`, `--draft-max N` | — | 16 | `LLAMA_ARG_DRAFT_MAX` | Max draft tokens for speculative decoding |
| `--draft-min N` | — | 0 | `LLAMA_ARG_DRAFT_MIN` | Min draft tokens |
| `--draft-p-min P` | — | 0.75 | `LLAMA_ARG_DRAFT_P_MIN` | Min speculative decoding probability (greedy) |
| `--ctx-size-draft N` | `-cd` | 0 (from model) | `LLAMA_ARG_CTX_SIZE_DRAFT` | Context size for draft model |
| `--device-draft <dev1,dev2,...>` | `-devd` | — | — | Devices for draft model offloading |
| `--gpu-layers-draft N` | `-ngld` | auto | `LLAMA_ARG_N_GPU_LAYERS_DRAFT` | Draft model layers in VRAM |
| `--model-draft FNAME` | `-md` | — | `LLAMA_ARG_MODEL_DRAFT` | Draft model path |
| `--threads-draft N` | `-td` | same as --threads | — | Draft model generation threads |
| `--threads-batch-draft N` | `-tbd` | same as --threads-draft | — | Draft model batch threads |
| `--spec-replace TARGET DRAFT` | — | — | — | Translate TARGET string to DRAFT string for cross-model compat |
| `--spec-type TYPE` | — | none | `LLAMA_ARG_SPEC_TYPE` | Speculative type without draft model: `none`, `ngram-cache`, `ngram-simple`, `ngram-map-k`, `ngram-map-k4v`, `ngram-mod` |
| `--spec-ngram-size-n N` | — | 12 | — | N-gram size N for ngram-simple/map |
| `--spec-ngram-size-m N` | — | 48 | — | N-gram size M for ngram-simple/map |
| `--spec-ngram-min-hits N` | — | 1 | — | Min hits for ngram-map speculative decoding |
| `--spec-default` | — | — | — | Enable default speculative decoding config |

### Audio / TTS

| Flag | Short | Default | Env Var | Description |
|------|-------|---------|---------|-------------|
| `--model-vocoder FNAME` | `-mv` | — | — | Vocoder model for audio generation |
| `--tts-use-guide-tokens` | — | — | — | Use guide tokens to improve TTS word recall |

### Quick-Start Presets (download weights automatically)

| Flag | Description |
|------|-------------|
| `--embd-gemma-default` | Default EmbeddingGemma model |
| `--fim-qwen-1.5b-default` | Qwen 2.5 Coder 1.5B (FIM) |
| `--fim-qwen-3b-default` | Qwen 2.5 Coder 3B (FIM) |
| `--fim-qwen-7b-default` | Qwen 2.5 Coder 7B (FIM) |
| `--fim-qwen-7b-spec` | Qwen 2.5 Coder 7B + 0.5B draft (speculative) |
| `--fim-qwen-14b-spec` | Qwen 2.5 Coder 14B + 0.5B draft (speculative) |
| `--fim-qwen-30b-default` | Qwen 3 Coder 30B A3B Instruct |
| `--gpt-oss-20b-default` | gpt-oss-20b |
| `--gpt-oss-120b-default` | gpt-oss-120b |
| `--vision-gemma-4b-default` | Gemma 3 4B QAT |
| `--vision-gemma-12b-default` | Gemma 3 12B QAT |

---

## Environment Variable Notes

- Boolean env vars accept: `true`, `1`, `on`, `enabled` to enable; `false`, `0`, `off`, `disabled` to disable
- `LLAMA_API_KEY` supports comma-separated multiple keys
- `HF_TOKEN` is used automatically if set

---

## Current docker-compose.yml Config (Gemma 4 26B)

```yaml
LLAMA_ARG_MODEL: /models/gemma-4-26B-A4B-it-UD-IQ4_NL.gguf
LLAMA_ARG_MMPROJ: /models/mmproj-F16.gguf
LLAMA_ARG_N_GPU_LAYERS: "999"          # all layers on GPU
# LLAMA_ARG_CPU_MOE: "1"              # commented out = MoE on GPU too
LLAMA_ARG_NO_MMAP: "1"                # no memory mapping
LLAMA_ARG_MLOCK: "1"                  # pin model in RAM
LLAMA_ARG_CACHE_TYPE_K: turbo4        # 4-bit keys (higher precision)
LLAMA_ARG_CACHE_TYPE_V: turbo3        # 3-bit values (more compression)
LLAMA_ARG_CTX_SIZE: "65536"           # 65K ctx (131K loses vision, 262K OOMs)
LLAMA_ARG_FLASH_ATTN: "on"
LLAMA_ARG_N_PARALLEL: "1"
LLAMA_ARG_HOST: 0.0.0.0
LLAMA_ARG_PORT: "8000"
LLAMA_API_KEY: <from .env>
```

**VRAM budget on RTX 4070 Ti SUPER (16 GB):**
- 65K ctx + mmproj: ~15.6 GB used, 333 MB free ✅ usable
- 131K ctx + mmproj: ~15.9 GB used, 37 MB free ❌ OOMs during inference
- 262K ctx, no mmproj: ~15.5 GB used, ~900 MB free ✅ text-only
