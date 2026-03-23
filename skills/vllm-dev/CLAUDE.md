# vLLM - AI Assistant Guide

@AGENTS.md

## Project Overview

vLLM is a high-throughput, memory-efficient LLM inference and serving engine. It uses **PagedAttention** for KV cache management, supports continuous batching, CUDA/HIP graph execution, and a wide range of quantization methods (GPTQ, AWQ, FP8, INT4/INT8).

## Tech Stack

- **Language**: Python 3.10–3.13, C++/CUDA (csrc/)
- **Build**: CMake + setuptools, compiled via `setup.py`
- **Package Manager**: `uv` (mandatory)
- **Key Dependencies**: PyTorch 2.10, Transformers >= 4.56, FastAPI, Pydantic >= 2.12
- **Linting**: ruff (formatting + linting), clang-format (C++/CUDA), mypy (type checking)
- **Testing**: pytest, pytest-asyncio
- **CI**: Buildkite (GPU tests), GitHub Actions (lint, macOS smoke)

## Repository Structure

```
vllm/                        # Main Python package
├── config/                  # All configuration classes (model, cache, scheduler, speculative, parallel, offload)
├── entrypoints/             # API servers (OpenAI-compatible), CLI (`vllm serve`, `vllm bench`)
├── engine/                  # Engine implementations and argument parsing
├── v1/                      # V1 engine (new architecture, preferred for new work)
│   ├── attention/backends/  # FlashAttention, FlashInfer, Triton, MLA, TreeAttention
│   ├── core/                # Scheduler, KV cache manager, block pool
│   ├── spec_decode/         # Speculative decoding: Eagle, Eagle3, MTP, draft model, suffix, ngram
│   ├── worker/gpu/          # GPU worker + spec decode speculators
│   ├── kv_offload/          # KV cache offloading (CPU, LRU, ARC)
│   └── structured_output/   # Guided generation (outlines, xgrammar)
├── model_executor/
│   ├── models/              # 260+ model implementations (llama, qwen, deepseek, etc.)
│   ├── layers/              # Reusable layers (attention, linear, quantization)
│   └── model_loader/        # Model loading (default, sharded, GGUF, tensorizer)
├── distributed/             # Tensor/pipeline/data/expert parallelism
├── multimodal/              # Vision, audio, video processing
├── lora/                    # LoRA adapter support
├── platforms/               # Hardware backends (CUDA, ROCm, XPU, CPU, TPU)
├── reasoning/               # Reasoning model support (DeepSeek R1, etc.)
├── tool_parsers/            # Tool-use parsing (40+ parsers)
├── sampling_params.py       # Sampling parameter definitions
├── envs.py                  # Environment variable configuration
└── logger.py                # Logging setup

csrc/                        # C++/CUDA kernels
├── attention/               # Attention kernels
├── moe/                     # Mixture of Experts kernels
├── quantization/            # Quantization kernels (GPTQ, AWQ, Marlin, etc.)
└── *.cu                     # Activation, cache, layernorm, pos_encoding kernels

tests/                       # Test suite
├── v1/spec_decode/          # Speculative decoding unit tests
├── v1/e2e/spec_decode/      # Spec decode end-to-end tests
├── models/                  # Model correctness tests
├── kernels/                 # Kernel tests
├── entrypoints/             # API tests
├── distributed/             # Multi-GPU tests
└── conftest.py              # Shared fixtures and markers

benchmarks/                  # Performance benchmarks
├── benchmark_throughput.py  # Throughput benchmarking (use `vllm bench throughput`)
├── benchmark_latency.py     # Latency benchmarking
├── benchmark_serving.py     # Online serving benchmarks
└── benchmark_ngram_proposer.py  # Speculative decoding benchmarks

requirements/                # Dependency files
├── common.txt               # Core runtime deps
├── test.txt                 # Test deps (auto-generated from test.in)
├── lint.txt                 # Linting deps (pre-commit)
├── build.txt                # Build deps
├── cuda.txt, rocm.txt       # Hardware-specific deps
└── dev.txt                  # Development deps
```

## Key Commands

```bash
# Environment setup
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements/lint.txt && pre-commit install

# Install (Python-only changes)
VLLM_USE_PRECOMPILED=1 uv pip install -e .

# Install (with C++/CUDA changes)
uv pip install -e .

# Run tests
uv pip install pytest pytest-asyncio tblib
pytest tests/path/to/test.py -v -s -k test_name

# Lint
pre-commit run --all-files
pre-commit run ruff-check --all-files
pre-commit run mypy-3.10 --all-files --hook-stage manual

# Serve a model
vllm serve <model_name> --tensor-parallel-size 2

# Benchmark
vllm bench throughput --model <model> --input-len 128 --output-len 128
```

## Key Conventions

- **Imports**: Lazy loading in `__init__.py` via `MODULE_ATTRS` pattern
- **Configuration**: All config in `vllm/config/` as dataclasses; CLI args parsed in `vllm/engine/arg_utils.py`
- **Speculative decoding config**: Passed as JSON via `--speculative-config '{"method": "eagle3", "model": "...", "num_speculative_tokens": 5}'`
- **New models**: Add to `vllm/model_executor/models/`, register in `registry.py`
- **Custom kernels**: Place in `csrc/`, add Triton kernels in `vllm/v1/` or `vllm/kernels/`
- **Pre-commit hooks**: Must pass before commit (ruff, clang-format, typos, mypy, SPDX headers, no torch.cuda usage)
- **SPDX headers**: Required on all new files: `# SPDX-License-Identifier: Apache-2.0`

## Performance-Critical Areas

| Area | Key Files | Impact |
|------|-----------|--------|
| Speculative Decoding | `vllm/v1/spec_decode/eagle.py`, `config/speculative.py` | Token generation throughput |
| KV Cache | `vllm/v1/core/kv_cache_manager.py`, `config/cache.py` | Memory efficiency, batch size |
| Attention Backends | `vllm/v1/attention/backends/` | Prefill/decode latency |
| Scheduling | `vllm/v1/core/scheduler.py`, `config/scheduler.py` | Request throughput |
| Quantization | `csrc/quantization/`, `vllm/model_executor/layers/quantization/` | Memory & compute efficiency |

## Speculative Decoding Methods

| Method | Config `method` | Use Case |
|--------|----------------|----------|
| Eagle / Eagle3 | `eagle`, `eagle3` | High acceptance rate, trained draft heads |
| Multi-Token Prediction | `deepseek_mtp`, `qwen3_5_mtp`, etc. | Models with native MTP support |
| Draft Model | `draft_model` | Separate smaller model as drafter |
| Parallel Drafting | `parallel_drafting: true` | Parallel token speculation |
| N-gram | `ngram`, `ngram_gpu` | Lightweight, no extra model needed |
| Suffix Decoding | `suffix` | Tree-based suffix matching |
| Medusa | `medusa` | Multiple draft heads |

## Common Gotchas

- Always use `uv` for package management, never raw `pip`
- Tests may need GPU; many are marked with `@pytest.mark.skipif` for hardware
- The V1 engine (`vllm/v1/`) is the active development target; V0 is legacy
- `torch.cuda` direct calls are forbidden; use `vllm.platforms` abstraction
- Pre-commit hooks enforce SPDX license headers on all files
- `requirements/test.txt` is auto-generated from `test.in` - edit `test.in` instead
