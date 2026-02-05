# Wings Engine Patch Skill

A specialized OpenCode skill for creating runtime patches for AI inference engines (vllm, vllm_ascend).

## Overview

This skill provides a comprehensive framework for:
- **Non-intrusive patching**: Modify engine behavior without touching source code
- **Feature-based management**: Enable/disable patches via configuration
- **Version control**: Scope patches to specific engine versions
- **Intelligent dependencies**: Auto-propagation and deduplication of shared patches

## Key Concepts

1. **Lazy Imports**: All engine imports inside patch functions to avoid circular dependencies
2. **wrapt Hooks**: Use `wrapt.register_post_import_hook` for post-import patching
3. **Registry Pattern**: Central registry maps features → patch functions
4. **Propagation**: Shared patches automatically enable related features
5. **Deduplication**: Each patch executes exactly once

## Structure

```
monkey-patch/
├── SKILL.md                              # Main skill definition
├── README.md                             # This file
└── references/
    ├── wings_engine_implementation.md    # Complete implementation guide (541 lines)
    ├── python_examples.md                # General Python patching patterns
    ├── testing_strategies.md             # Testing approaches
    └── security_considerations.md        # Security implications
```

## Quick Example

**Enable soft_fp8 quantization for vllm_ascend v0.12.0rc1:**

```bash
export WINGS_ENGINE_PATCH_OPTIONS='{
    "vllm_ascend": {
        "version": "0.12.0rc1",
        "features": ["soft_fp8"]
    }
}'

python3 -m vllm.entrypoints.api_server --model /path/to/model
```

## Use Cases

- ✅ Bug fixes in upstream libraries while waiting for official patches
- ✅ Adding experimental features (e.g., new quantization methods)
- ✅ Performance optimizations (e.g., caching expensive computations)
- ✅ Version-specific compatibility layers

## Documentation

- **[SKILL.md](SKILL.md)** - Concise skill overview and when to use
- **[wings_engine_implementation.md](references/wings_engine_implementation.md)** - Complete implementation guide with:
  - Architecture overview
  - Entry point (`.pth` file mechanism)
  - Registry module design
  - Patch implementation patterns
  - Build system
  - Testing strategies
  - Debugging tips

## Critical Rules

1. ❌ **Never** import engine modules at module level
2. ✅ **Always** use lazy imports inside patch functions
3. ✅ **Always** use `wrapt.register_post_import_hook`
4. ✅ **Merge** patches targeting the same function
5. ✅ **Keep** patches granular and focused

## Installation

```bash
# Build
python3 build_wheel.py

# Install
pip install dist/wings_engine_patch-*.whl --force-reinstall
```

## Configuration

Set `WINGS_ENGINE_PATCH_OPTIONS` environment variable with JSON:

```json
{
    "engine_name": {
        "version": "x.y.z",
        "features": ["feature1", "feature2"]
    }
}
```

## Related Skills

- General monkey patching patterns (see python_examples.md)
- Testing monkey patches (see testing_strategies.md)
- Security considerations (see security_considerations.md)
