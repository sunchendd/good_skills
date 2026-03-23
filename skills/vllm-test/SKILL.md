---
name: vllm-test
description: Use when testing vLLM performance, running benchmarks, comparing inference configurations, cleaning up GPU environments, or generating performance reports. Activates for benchmarking throughput/latency, configuring vLLM serve parameters, using evalscope or vllm bench, and producing comparison tables.
allowed-tools: Read, Edit, Write, Grep, Glob, Bash, Agent, NotebookEdit
---

# vLLM Testing & Benchmarking Assistant

## Overview

Specialized assistant for vLLM performance testing, environment management, benchmark execution, and report generation. Handles the full testing lifecycle: clean environment -> configure -> warmup -> benchmark -> analyze -> report.

## Phase 1: Environment Cleanup

Before any benchmark, ensure a clean GPU state.

### Safe GPU Cleanup

```bash
# Kill vLLM-specific processes only (avoid killing unrelated Python processes)
pkill -f "vllm.entrypoints" || true
pkill -f "vllm serve" || true

# Wait for GPU memory to free
sleep 3

# Verify GPU is clean
nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv,noheader

# Clear CUDA cache
python3 -c "import torch; torch.cuda.empty_cache(); print('CUDA cache cleared')" 2>/dev/null || true
```

### Environment Verification

```bash
# Check vLLM installation
python3 -c "import vllm; print(f'vLLM version: {vllm.__version__}')"

# Check CUDA/GPU status
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, GPUs: {torch.cuda.device_count()}')"

# Check available GPU memory
nvidia-smi --query-gpu=index,name,memory.free --format=csv,noheader

# Multi-GPU: verify topology and connectivity (for TP > 1)
python3 -c "
import torch
if torch.cuda.device_count() > 1:
    print(f'Multi-GPU: {torch.cuda.device_count()} GPUs available')
    for i in range(torch.cuda.device_count()):
        print(f'  GPU {i}: {torch.cuda.get_device_name(i)}, {torch.cuda.get_device_properties(i).total_mem // 1024**3} GB')
else:
    print('Single GPU mode')
"
```

## Phase 2: vLLM Server Configuration

See `vllm-dev` skill for full speculative decoding config parameter reference and architecture details.

### Configuration A: Baseline (no speculative decoding)

```bash
vllm serve <model> \
  --tensor-parallel-size <tp> \
  --max-model-len <max_len> \
  --gpu-memory-utilization 0.9 \
  --enable-chunked-prefill \
  --max-num-batched-tokens 2048 \
  --max-num-seqs 128
```

### Configuration B: Eagle3 Speculative Decoding

```bash
vllm serve <model> \
  --tensor-parallel-size <tp> \
  --max-model-len <max_len> \
  --gpu-memory-utilization 0.85 \
  --speculative-config '{"method": "eagle3", "model": "<eagle3_head>", "num_speculative_tokens": 5}'
```

### Configuration C: MTP (for supported models)

```bash
vllm serve <model> \
  --tensor-parallel-size <tp> \
  --max-model-len <max_len> \
  --gpu-memory-utilization 0.85 \
  --speculative-config '{"method": "deepseek_mtp", "num_speculative_tokens": 1}'
```

### Configuration D: N-gram Speculation (no extra model needed)

```bash
vllm serve <model> \
  --tensor-parallel-size <tp> \
  --max-model-len <max_len> \
  --speculative-config '{"method": "ngram", "num_speculative_tokens": 3, "prompt_lookup_max": 5}'
```

### Configuration E: KV Cache Optimized

```bash
vllm serve <model> \
  --tensor-parallel-size <tp> \
  --max-model-len <max_len> \
  --gpu-memory-utilization 0.95 \
  --enable-prefix-caching \
  --kv-cache-dtype fp8_e4m3
```

### Configuration F: Parallel Drafting (Eagle + parallel)

```bash
vllm serve <model> \
  --tensor-parallel-size <tp> \
  --max-model-len <max_len> \
  --speculative-config '{"method": "eagle3", "model": "<eagle3_head>", "num_speculative_tokens": 5, "parallel_drafting": true}'
```

## Phase 3: Benchmark Execution

### Important: Warmup

CUDA graph compilation happens on first requests. Always warmup before measuring:

```bash
# After starting server, send warmup requests before benchmarking
curl -s http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "<model>", "prompt": "Warmup request", "max_tokens": 32}' > /dev/null

# Wait for CUDA graphs to compile
sleep 5
```

For offline benchmarks (`vllm bench throughput`/`latency`), warmup is handled internally.

### Using `vllm bench` (Built-in CLI)

Available subcommands: `throughput`, `latency`, `serve`, `startup`, `sweep`, `mm-processor`.

> **Note**: Legacy scripts `benchmarks/benchmark_serving.py` and `benchmarks/benchmark_latency.py` are **deprecated**. Use `vllm bench serve` and `vllm bench latency` instead.

#### Throughput Benchmark

```bash
# Offline throughput test (use --output-json for automated comparison)
vllm bench throughput \
  --model <model> \
  --input-len 128 \
  --output-len 128 \
  --num-prompts 1000 \
  --tensor-parallel-size <tp> \
  --output-json results_baseline.json

# With speculative decoding
vllm bench throughput \
  --model <model> \
  --input-len 128 \
  --output-len 128 \
  --num-prompts 1000 \
  --speculative-config '{"method": "eagle3", "model": "<head>", "num_speculative_tokens": 5}' \
  --output-json results_eagle3.json
```

#### Latency Benchmark

```bash
vllm bench latency \
  --model <model> \
  --batch-size 1 \
  --input-len 128 \
  --output-len 128 \
  --num-iters 100 \
  --tensor-parallel-size <tp> \
  --output-json results_latency.json
```

#### Online Serving Benchmark

```bash
# Start server first, then run:
vllm bench serve \
  --backend vllm \
  --model <model> \
  --dataset-name sharegpt \
  --dataset-path <path_to_sharegpt.json> \
  --request-rate 10 \
  --num-prompts 500 \
  --port 8000 \
  --output-json results_serve.json
```

### Using EvalScope

```bash
# Install evalscope (must use uv)
uv pip install evalscope

# Run performance evaluation
evalscope perf \
  --url http://localhost:8000/v1/chat/completions \
  --model <model> \
  --api openai \
  --dataset openqa \
  --num 200 \
  --parallel 16 \
  --max-tokens 512 \
  --stream
```

### Using Custom Benchmark Scripts

```bash
# Prefix caching benchmark
python3 benchmarks/benchmark_prefix_caching.py \
  --model <model> \
  --enable-prefix-caching

# N-gram proposer benchmark
python3 benchmarks/benchmark_ngram_proposer.py \
  --model <model> \
  --ngram-size 3 \
  --num-speculative-tokens 5
```

## Phase 4: Performance Report Generation

### Key Metrics to Collect

| Metric | Unit | Description |
|--------|------|-------------|
| Throughput | tokens/s | Total tokens generated per second |
| TTFT | ms | Time to first token (latency) |
| TPOT | ms | Time per output token (inter-token latency) |
| ITL p50/p99 | ms | Inter-token latency percentiles |
| Request throughput | req/s | Requests completed per second |
| Acceptance rate | % | Speculative token acceptance rate |
| Mean acceptance length | tokens | Average accepted draft tokens |
| GPU memory usage | GB | Peak GPU memory utilization |
| Batch size | - | Average concurrent batch size |

### Report Template

Generate comparison reports in this format:

```markdown
# vLLM Performance Report

## Test Environment
- Model: <model_name>
- GPUs: <gpu_count> x <gpu_type>
- vLLM version: <version>
- CUDA version: <cuda_version>
- Date: <date>

## Configuration Comparison

| Parameter | Config A (Baseline) | Config B (Eagle3) | Config C (MTP) |
|-----------|--------------------|--------------------|-----------------|
| Spec method | None | eagle3 | deepseek_mtp |
| Spec tokens | - | 5 | 1 |
| TP size | 2 | 2 | 2 |
| KV dtype | auto | auto | auto |
| Max batch tokens | 2048 | 2048 | 2048 |

## Results

| Metric | Config A | Config B | Config C | Best |
|--------|----------|----------|----------|------|
| Throughput (tok/s) | | | | |
| TTFT p50 (ms) | | | | |
| TPOT p50 (ms) | | | | |
| ITL p99 (ms) | | | | |
| Acceptance rate | - | | | |
| GPU memory (GB) | | | | |

## Regression Check (vs previous baseline)

| Metric | Previous | Current | Delta | Status |
|--------|----------|---------|-------|--------|
| Throughput | | | | OK/REGRESSED |
| TTFT p50 | | | | OK/REGRESSED |

## Analysis
- [Which config gives best throughput and why]
- [Latency vs throughput tradeoffs observed]
- [Recommendations for production deployment]
```

### Automated Comparison Script

When running multiple configurations, use this pattern:

```bash
#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# benchmark_compare.sh - Run A/B comparison benchmarks
# Usage: bash benchmark_compare.sh <model> [tp_size]

set -euo pipefail

MODEL="${1:?Usage: $0 <model> [tp_size]}"
TP="${2:-1}"
RESULTS_DIR="benchmark_results_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULTS_DIR"

# Define configs as associative array (avoids eval injection)
declare -A SPEC_CONFIGS
SPEC_CONFIGS[baseline]=""
SPEC_CONFIGS[eagle3]="--speculative-config {\"method\": \"eagle3\", \"model\": \"<head>\", \"num_speculative_tokens\": 5}"
SPEC_CONFIGS[mtp]="--speculative-config {\"method\": \"deepseek_mtp\", \"num_speculative_tokens\": 1}"
SPEC_CONFIGS[ngram]="--speculative-config {\"method\": \"ngram\", \"num_speculative_tokens\": 3}"

for config in baseline eagle3 mtp ngram; do
  echo "=== Running config: $config ==="

  # Clean GPU state (vLLM-specific only)
  pkill -f "vllm.entrypoints" || true
  sleep 5

  # Run offline throughput benchmark with JSON output
  vllm bench throughput \
    --model "$MODEL" \
    --tensor-parallel-size "$TP" \
    --input-len 128 \
    --output-len 128 \
    --num-prompts 500 \
    ${SPEC_CONFIGS[$config]} \
    --output-json "$RESULTS_DIR/${config}_throughput.json" \
    2>&1 | tee "$RESULTS_DIR/${config}_throughput.log"

  echo "=== Done: $config ==="
done

echo "Results saved to $RESULTS_DIR/"
echo ""
echo "Compare results with:"
echo "  python3 -c \"import json, sys; [print(f.split('/')[-1], json.load(open(f))) for f in sys.argv[1:]]\" $RESULTS_DIR/*.json"
```

### Regression Detection

Compare current results against a saved baseline:

```python
#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compare benchmark results against a baseline for regression detection."""
import json
import sys

THRESHOLDS = {
    "throughput": -0.05,    # alert if throughput drops > 5%
    "mean_ttft_ms": 0.10,   # alert if TTFT increases > 10%
    "mean_tpot_ms": 0.10,   # alert if TPOT increases > 10%
}

def compare(baseline_path: str, current_path: str) -> bool:
    with open(baseline_path) as f:
        baseline = json.load(f)
    with open(current_path) as f:
        current = json.load(f)

    passed = True
    for metric, threshold in THRESHOLDS.items():
        if metric not in baseline or metric not in current:
            continue
        b, c = baseline[metric], current[metric]
        if b == 0:
            continue
        delta = (c - b) / abs(b)
        # For throughput (negative threshold): delta should be >= threshold (not drop too much)
        # For latency (positive threshold): delta should be <= threshold (not increase too much)
        status = "OK" if (delta >= threshold if threshold < 0 else delta <= threshold) else "REGRESSED"
        if status == "REGRESSED":
            passed = False
        print(f"  {metric}: {b:.2f} -> {c:.2f} ({delta:+.1%}) [{status}]")
    return passed

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <baseline.json> <current.json>")
        sys.exit(1)
    ok = compare(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 1)
```

## Phase 5: Unit Test Execution

### Running Speculative Decoding Tests

```bash
# Unit tests
pytest tests/v1/spec_decode/test_eagle.py -v -s
pytest tests/v1/spec_decode/test_mtp.py -v -s
pytest tests/v1/spec_decode/test_ngram.py -v -s
pytest tests/v1/spec_decode/test_tree_attention.py -v -s
pytest tests/v1/spec_decode/test_speculators_eagle3.py -v -s

# End-to-end tests (require GPU + model downloads)
pytest tests/v1/e2e/spec_decode/test_spec_decode.py -v -s

# Specific test
pytest tests/v1/spec_decode/test_eagle.py -v -s -k "test_eagle3"
```

### Running KV Cache Tests

```bash
pytest tests/v1/ -v -s -k "kv_cache"
pytest tests/v1/core/ -v -s
```

## Troubleshooting

### Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| OOM during spec decode | KV cache too large with draft expansion | Reduce `gpu-memory-utilization` to 0.85 |
| Low acceptance rate | Draft model mismatch or too many spec tokens | Reduce `num_speculative_tokens`, verify draft model quality |
| Server won't start | Port in use or GPU occupied | `pkill -f "vllm.entrypoints"; sleep 5; nvidia-smi` |
| Slow first request | CUDA graph compilation | Expected - warmup before benchmarking |
| TTFT regression with spec decode | Draft model adding prefill overhead | Normal for low-QPS; spec decode benefits high-throughput |
| NCCL timeout (multi-GPU) | Network config or driver issue | Set `NCCL_DEBUG=INFO` to diagnose; check `nvidia-smi topo -m` |

### Monitoring During Benchmark

```bash
# Watch GPU utilization in real-time
watch -n 1 nvidia-smi

# Monitor vLLM metrics endpoint
curl -s http://localhost:8000/metrics | grep -E "vllm:(num_requests|gpu_cache|spec)"

# Check speculative decoding acceptance rate in server logs
# (appears in server output when speculative decoding is enabled)
```
