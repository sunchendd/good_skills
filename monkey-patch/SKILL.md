---
name: wings-engine-patch
description: Comprehensive framework for creating and managing runtime patches for inference engines (vllm, vllm_ascend). Use when Claude needs to implement dynamic monkey patches for AI inference engines, create feature-based patch management systems, work with wrapt-based import hooks, implement version-controlled runtime modifications, design non-intrusive patch frameworks, or manage patch dependencies and propagation logic.
---

# Wings Engine Patch Skill

## Overview

This skill provides a comprehensive framework for creating runtime patches for inference engines (vllm, vllm_ascend) using Python's import hooks and wrapt. The framework enables **non-intrusive, version-controlled, feature-based patching** at runtime without modifying the original package installation.

## Core Concepts

### 1. Non-Intrusive Runtime Patching
- Patches applied at runtime using Python import hooks (`wrapt.register_post_import_hook`)
- Original package installation remains pristine
- No source code modification required

### 2. Feature-Based Management
- Users enable features (e.g., `soft_fp8`, `soft_fp4`), not individual patches
- Features group related patches together
- Configuration via environment variable: `WINGS_ENGINE_PATCH_OPTIONS`

### 3. Version Control
- Patches are strictly scoped to specific engine versions (e.g., `vllm_ascend==0.12.0rc1`)
- Automatic version matching and validation
- Fallback to default version if configured

### 4. Intelligent Dependency Resolution
- **Shared Patches**: Multiple features can reference the same patch function
- **Propagation**: Enabling one feature auto-enables others sharing the same patch
- **Deduplication**: Each patch function executes exactly once, regardless of how many features reference it

## When to Use This Skill

✅ Use when you need to:
- Patch vllm/vllm_ascend with runtime modifications
- Implement feature-based patch management
- Version-control patches for specific engine versions
- Handle complex shared patch dependencies
- Non-intrusively modify third-party packages

❌ Don't use for:
- Simple scripts without version management needs
- Modifications possible via official APIs
- Cases where upstream patches are better
- Non-Python codebases

## References

- [references/wings_engine_implementation.md](references/wings_engine_implementation.md) - Complete implementation architecture with code examples
- [references/python_examples.md](references/python_examples.md) - General Python monkey patching patterns

