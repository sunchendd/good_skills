---
name: vllm-ascend-profiler-diff
description: >-
  Use when comparing two vLLM-Ascend / torch_npu / Ascend runtime Profiler outputs to locate performance differences or regressions.
  Applies when the user provides two ASCEND_PROFILER_OUTPUT directories and needs analysis across prefill/decoding, kernel/op deltas,
  Host/sync behavior, trace distribution, or optional source/PR attribution.
---

# vLLM-Ascend Profiler Diff Workflow

## Overview

This skill provides a structured workflow to compare two Ascend Profiler runs, quantify performance deltas, and optionally trace findings back to source and PRs. Conclusions should be driven by aligned evidence across multiple dimensions.

## Required Inputs

- Profile A directory (baseline): ASCEND_PROFILER_OUTPUT path
- Profile B directory (regression): ASCEND_PROFILER_OUTPUT path

## Optional Inputs (Strongly Recommended)

- Benchmark JSON A/B (throughput, TTFT, TPOT alignment)
- Source repo path (vLLM-Ascend) for `git blame` attribution
- A/B version tags/commits

## Workflow (Execute in Order)

### 1) Directory Sanity Check

Verify each profile directory contains (note any missing):

- step_trace_time.csv
- op_statistic.csv
- api_statistic.csv
- kernel_details.csv (or equivalent)
- operator_details.csv (if PyTorch op stats exist)
- trace_view.json (may be large)

Output a presence table for A/B and whether deeper analysis is possible.

### 2) Overall Metrics Alignment

If benchmark JSON is provided, extract and compare:

- Throughput (tokens/s or req/s)
- TTFT (time to first token)
- TPOT (time per output token)

State whether the regression appears mainly in prefill or decode.

If benchmark JSON is not provided, use step-level timing trends from step_trace_time.csv for a directional judgment.

### 3) Stage-Level Attribution

From step_trace_time.csv, compare stage breakdowns:

- Computing
- Free (Host wait)
- Communication/Memcpy/Stage fields if present

Provide A/B totals and an evidence-based conclusion.

### 4) Kernel/Op Dimension

From op_statistic.csv and kernel_details.csv:

- List TopN by total time, call count, and average time
- Compare new hotspots or large deltas on shared items
- Relate changes to stage-level shifts where possible

Provide a data-backed assessment of whether kernel/op shifts contribute to the regression.

### 5) API Dimension

From api_statistic.csv, compare A/B across dimensions:

- TopN APIs (total time, count, average)
- Newly appearing or significantly changed APIs
- Alignment with stage-level changes (Computing/Free/Communication, etc.)

Only conclude when the data aligns; otherwise proceed to other dimensions.

### 6) PyTorch Operator Dimension (Optional)

If operator_details.csv exists, compare A/B across dimensions:

- TopN operators (total time, count, average)
- Newly appearing or significantly changed operators
- Consistency with stage-level or API-level shifts

Treat findings as signals, not definitive causes.

### 7) Large Trace Scan (trace_view.json)

When trace_view.json is too large to open, stream/scan to estimate:

- Event counts
- Total duration (if available)
- Time span (max(ts) - min(ts))
- Distribution histogram (e.g., 50 bins)

Use the temporal distribution to infer whether changes concentrate in prefill/initialization or are evenly spread during decode.

### 8) Source Attribution (If Repo Provided)

Search the repo for plausible trigger points (explicit/implicit/observer logic), then identify top 3 suspects (file, function, rationale).

### 9) PR/Commit Attribution

Use git blame for suspect lines and git show to identify PR numbers when available.

Output an evidence chain: trigger point → commit hash → PR link → change intent.

### 10) Final Deliverables (Always Provide)

1. **Summary (3–6 lines)**:
   - prefill vs decode impact
   - dominant dimension(s) based on evidence
   - key metric magnitudes and direction

2. **Evidence Tables**:
   - step_trace_time breakdown
   - api_statistic dimension comparison
   - op/kernel TopN deltas

3. **Trace distribution stats** (if trace_view.json exists)

4. **Source + PR attribution** (if repo provided)

5. **Actionable mitigations**:
   - configuration/env workarounds
   - isolate or reduce high-cost paths
   - possible revert/cherry-pick options

## User Prompt Template

Ask the user to provide:

```
Please execute the “vLLM-Ascend Profiler Diff Workflow”.

Profile A (baseline): <ASCEND_PROFILER_OUTPUT path>
Profile B (regression): <ASCEND_PROFILER_OUTPUT path>

(Optional) Benchmark JSON A: <path or empty>
(Optional) Benchmark JSON B: <path or empty>

(Optional) Source repo path: /data/tjl/vllm-workspace/vllm-ascend
(Optional) Version/Tag: A=<tag/commit>, B=<tag/commit>

Focus: prefill / decode / both
Output: final conclusion + evidence tables + PR link if caused by code change
```
