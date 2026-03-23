---
name: vllm-dev
description: Use when developing vLLM features including speculative decoding (Eagle3, MTP, draft model, suffix, parallel drafting), KV cache optimization (sparsity, offloading, prefix caching), attention backends, and throughput/TPS improvements. Activates for architecture design, implementation, and parameter tuning of inference performance features.
allowed-tools: Read, Edit, Write, Grep, Glob, Bash, Agent, NotebookEdit
---

# vLLM Development Assistant

## Overview

Specialized assistant for vLLM inference engine development. Focuses on speculative decoding, KV cache optimization, attention backends, and throughput improvements. Follows the superpowers pattern: brainstorm -> design -> plan -> implement -> verify.

## Workflow

### Phase 1: Understand the Feature

Before writing code, gather context:

1. **Read the relevant config class** in `vllm/config/` to understand existing parameters
2. **Read the V1 engine implementation** - all new work targets `vllm/v1/`
3. **Check existing tests** in `tests/v1/` for the feature area
4. **Read docs** in `docs/features/` for user-facing behavior

### Phase 2: Architecture Design

For any significant feature, create a design before coding:

1. Identify which layers need changes (config -> engine -> worker -> kernel)
2. Map data flow through the system
3. Consider multi-GPU implications (tensor parallel, data parallel)
4. Assess memory impact on KV cache budget
5. Evaluate interaction with existing features (LoRA, chunked prefill, structured output)

### Phase 3: Implementation

Follow the vLLM code patterns strictly.

## Speculative Decoding Development

### Architecture Overview

```
Config Layer:     vllm/config/speculative.py (SpeculativeConfig)
                       ↓
Engine Layer:     vllm/engine/arg_utils.py (CLI arg parsing)
                       ↓
Proposer Layer:   vllm/v1/spec_decode/eagle.py (SpecDecodeBaseProposer)
                  vllm/v1/spec_decode/draft_model.py
                  vllm/v1/spec_decode/ngram_proposer.py
                  vllm/v1/spec_decode/ngram_proposer_gpu.py
                  vllm/v1/spec_decode/suffix_decoding.py
                  vllm/v1/spec_decode/medusa.py
                  vllm/v1/spec_decode/extract_hidden_states.py
                       ↓
Worker Layer:     vllm/v1/worker/gpu/spec_decode/eagle/speculator.py
                  vllm/v1/worker/gpu/spec_decode/rejection_sampler.py
                       ↓       ↑ (acceptance feedback for adaptive tuning)
Attention Layer:  vllm/v1/attention/backends/tree_attn.py (tree attention for spec decode)
                       ↓
Kernel Layer:     vllm/v1/spec_decode/utils.py (Triton kernels)
                  csrc/ (CUDA kernels)
```

### Key Speculative Config Parameters

```python
# vllm/config/speculative.py - SpeculativeConfig fields:
num_speculative_tokens: int        # Draft depth (required)
model: str                          # Draft model / eagle head path
method: SpeculativeMethod           # eagle, eagle3, deepseek_mtp, draft_model, ngram, suffix, etc.
draft_tensor_parallel_size: int     # TP for draft model (1 or match target)
parallel_drafting: bool             # Enable parallel token generation
rejection_sample_method: str        # "strict" or "probabilistic"
disable_padded_drafter_batch: bool  # Disable padding for spec decode batches
use_local_argmax_reduction: bool    # Vocab-parallel local argmax
```

### All Speculative Decoding Methods

| Category | Method | Config `method` | Description |
|----------|--------|----------------|-------------|
| Eagle | Eagle | `eagle` | Trained draft head with hidden state |
| Eagle | Eagle3 | `eagle3` | Improved Eagle with extracted hidden states |
| Eagle | Extract Hidden States | `extract_hidden_states` | Hidden state extraction for Eagle variants |
| MTP | DeepSeek V3 | `deepseek_mtp` | DeepSeek native multi-token prediction |
| MTP | Qwen 3.5 | `qwen3_5_mtp` | Qwen 3.5 native MTP |
| MTP | Qwen 3 Next | `qwen3_next_mtp` | Qwen 3 Next native MTP |
| MTP | MiMo | `mimo_mtp` | MiMo native MTP |
| MTP | GLM-4-MoE | `glm4_moe_mtp` | GLM-4 MoE native MTP |
| MTP | GLM-4-MoE Lite | `glm4_moe_lite_mtp` | GLM-4 MoE Lite native MTP |
| MTP | GLM OCR | `glm_ocr_mtp` | GLM OCR native MTP |
| MTP | ERNIE | `ernie_mtp` | ERNIE native MTP |
| MTP | Nemotron-H | `nemotron_h_mtp` | Nemotron-H native MTP |
| MTP | ExaOne MoE | `exaone_moe_mtp` | ExaOne MoE native MTP |
| MTP | Pangu Ultra MoE | `pangu_ultra_moe_mtp` | Pangu Ultra MoE native MTP |
| MTP | Step 3.5 | `step3p5_mtp` | Step 3.5 native MTP |
| MTP | LongCat Flash | `longcat_flash_mtp` | LongCat Flash native MTP |
| MTP | Generic | `mtp` | Generic MTP fallback |
| Other | Draft Model | `draft_model` | Separate smaller model as drafter |
| Other | N-gram | `ngram` | CPU-based n-gram matching |
| Other | N-gram GPU | `ngram_gpu` | GPU-accelerated n-gram matching |
| Other | Suffix | `suffix` | Tree-based suffix matching |
| Other | Medusa | `medusa` | Multiple draft heads |
| Other | MLP Speculator | `mlp_speculator` | MLP-based speculation |

### Eagle/Eagle3 Development

Core proposer: `vllm/v1/spec_decode/eagle.py` (SpecDecodeBaseProposer, ~1730 lines)

Key concepts:
- **Tree attention**: `propose_tree()` builds speculative token trees for batch verification
- **CUDA graphs**: Managed via `EagleCudaGraphManager` for latency optimization
- **Hidden states**: Eagle3 extracts auxiliary hidden states from target model
- **Slot mapping**: Fused kernels in `vllm/v1/spec_decode/utils.py`

Worker: `vllm/v1/worker/gpu/spec_decode/eagle/speculator.py` (EagleSpeculator)
- Manages input buffers, draft token caching, DP synchronization
- Draft logits caching for probabilistic rejection sampling

### Adding a New Speculative Method

1. Add method enum to `vllm/config/speculative.py` SpeculativeMethod
2. Create proposer in `vllm/v1/spec_decode/` (extend SpecDecodeBaseProposer or create new)
3. Add worker logic in `vllm/v1/worker/gpu/spec_decode/`
4. Register in the factory/selection logic in the engine
5. Add tests in `tests/v1/spec_decode/` and `tests/v1/e2e/spec_decode/`
6. Add docs in `docs/features/speculative_decoding/`

### Performance Tuning for Speculative Decoding

| Parameter | Trade-off | Guidance |
|-----------|-----------|----------|
| `num_speculative_tokens` | Higher = more throughput if acceptance high, but more wasted compute if low | Start with 3-5, measure acceptance rate |
| `parallel_drafting` | Reduces draft latency but uses more GPU memory | Enable for latency-sensitive workloads |
| `gpu_memory_utilization` | Spec decode needs extra KV cache for draft tokens | Use 0.85 instead of 0.9 with spec decode |
| `max_num_seqs` | More concurrent seqs = more batched draft overhead | Reduce if OOM with spec decode enabled |

## KV Cache Optimization

### Architecture

```
Config:           vllm/config/cache.py (CacheConfig)
                       ↓
Manager:          vllm/v1/core/kv_cache_manager.py (KVCacheManager)
                  vllm/v1/core/single_type_kv_cache_manager.py
                  vllm/v1/core/block_pool.py
                       ↓
Interface:        vllm/v1/kv_cache_interface.py (KVCacheSpec, AttentionSpec)
                       ↓
Offload:          vllm/v1/kv_offload/ (CPU offloading, LRU/ARC eviction)
                       ↓
Coordinator:      vllm/v1/core/kv_cache_coordinator.py (multi-GPU)
```

### Key Cache Config Parameters

```python
# vllm/config/cache.py - CacheConfig fields:
block_size: int = 16                  # Tokens per cache block
gpu_memory_utilization: float = 0.9   # GPU memory fraction for KV cache
cache_dtype: str = "auto"             # fp16, bf16, fp8, fp8_e4m3, fp8_e5m2
enable_prefix_caching: bool = True    # Automatic prefix caching
prefix_caching_hash_algo: str         # sha256, xxhash, etc.
sliding_window: int                   # Sliding window attention size
kv_cache_memory_bytes: int            # Manual KV cache size (overrides gpu_memory_utilization)
kv_offloading_size: float             # KV offload buffer in GiB
kv_offloading_backend: str            # "native" or "lmcache"
```

### Sparse Attention / MLA

Sparse attention backends in `vllm/v1/attention/backends/`:
- `flashmla.py` - FlashMLA (Multi-head Latent Attention)
- `flashmla_sparse.py` - FlashMLA with sparsity
- `xpu_mla_sparse.py` - XPU sparse MLA
- `rocm_aiter_mla.py` - ROCm MLA

### KV Cache Offloading

`vllm/v1/kv_offload/` provides:
- **LRU manager** (`lru_manager.py`): Least-recently-used eviction
- **ARC manager** (`arc_manager.py`): Adaptive replacement cache
- **CPU backend** (`backends/cpu.py`): Host memory offloading
- **Reuse manager** (`reuse_manager.py`): Cross-request cache reuse

## Throughput Optimization Checklist

When optimizing TPS/throughput, consider these parameters:

### Scheduler Tuning (`vllm/config/scheduler.py`)

```python
max_num_batched_tokens: int = 2048    # Max tokens per iteration
max_num_seqs: int = 128                # Max concurrent sequences
enable_chunked_prefill: bool = True    # Enable prefill chunking
max_num_partial_prefills: int = 1      # Concurrent partial prefills
max_num_scheduled_tokens: int          # Tokens per scheduler step (spec decode needs headroom)
```

### Parallelism (`vllm/config/parallel.py`)

```python
tensor_parallel_size: int              # GPUs for tensor parallelism
data_parallel_size: int                # Data parallel workers
pipeline_parallel_size: int            # Pipeline stages
```

### Weight Offloading (`vllm/config/offload.py`)

```python
cpu_offload_gb: float                  # CPU offload memory per GPU
offload_backend: str                   # "auto", "uva", "prefetch"
offload_group_size: int                # Layer grouping for prefetch
```

## Profiling & Debugging

### Built-in Profiling

```bash
# Enable torch profiler via environment variable
VLLM_TORCH_PROFILER_DIR=./profiles vllm serve <model> ...

# Then access profiler traces at http://localhost:8000/start_profile / stop_profile
# Or use the API:
curl http://localhost:8000/start_profile
# ... run workload ...
curl http://localhost:8000/stop_profile
# Traces saved to ./profiles/
```

### Useful Debug Environment Variables

```bash
VLLM_LOGGING_LEVEL=DEBUG              # Verbose logging
VLLM_TRACE_FUNCTION=1                 # Trace function calls
CUDA_LAUNCH_BLOCKING=1                # Synchronous CUDA for debugging
NCCL_DEBUG=INFO                       # Debug multi-GPU communication
VLLM_PP_LAYER_PARTITION=...           # Manual pipeline parallel partition
```

### Common Error Patterns

| Error | Likely Cause | Debug Steps |
|-------|-------------|-------------|
| `CUDA out of memory` | KV cache overallocated | Reduce `gpu_memory_utilization`, check `nvidia-smi` |
| `RuntimeError: Expected all tensors on same device` | TP/PP routing issue | Check `distributed/` mapping logic |
| `Assertion in rejection sampler` | Logits shape mismatch | Verify draft/target vocab sizes match |
| `NCCL timeout` | GPU communication failure | Set `NCCL_DEBUG=INFO`, check topology |
| `KeyError in model loader` | Missing weight mapping | Check `hf_to_vllm_mapper` in model class |

## Code Quality Rules

1. **Always read before editing** - understand the existing pattern
2. **Follow V1 patterns** - new features go in `vllm/v1/`, not root `vllm/`
3. **Use platform abstractions** - never call `torch.cuda` directly, use `vllm.platforms`
4. **Add SPDX headers** to all new files:
   ```python
   # SPDX-License-Identifier: Apache-2.0
   # SPDX-FileCopyrightText: Copyright contributors to the vLLM project
   ```
5. **Run pre-commit** before finalizing: `pre-commit run --all-files`
6. **Write tests** for every new feature in the matching `tests/` subdirectory
7. **Use Triton** for new GPU kernels when possible (over raw CUDA)
8. **Config-driven design** - expose new parameters via `vllm/config/` dataclasses
