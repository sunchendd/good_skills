---
name: monkey-patch
description: Comprehensive guide for creating, analyzing, and implementing monkey patches in Python and other dynamic languages. Use when Claude needs to create monkey patches to modify third-party library behavior, analyze existing monkey patches for safety and compatibility, implement workarounds for bugs in external dependencies, extend functionality of existing code without modifying source, understand monkey patch risks and best practices, or refactor existing monkey patches to be more maintainable.
---

# Monkey Patch Skill

## Overview

This skill provides comprehensive guidance for creating, analyzing, and implementing monkey patches in Python and other dynamic languages. Monkey patching is the technique of dynamically modifying runtime code to change behavior without modifying source code.

## Quick Start

### When to Use Monkey Patching

Use monkey patching for:
1. **Bug fixes** in third-party libraries when you can't wait for official patches
2. **Feature additions** to existing libraries without forking
3. **Testing** by mocking dependencies
4. **Compatibility** layers between different library versions
5. **Performance optimizations** for specific use cases

### When NOT to Use Monkey Patching

Avoid monkey patching when:
1. You can submit a proper patch to the upstream project
2. The change is complex and likely to break with library updates
3. Multiple teams depend on the same codebase
4. There's a cleaner alternative like subclassing or composition

## Core Principles

### 1. Safety First
- Always preserve original functionality when possible
- Use `try/except` blocks to handle version differences
- Document all patches with clear comments
- Consider using `warnings.warn()` for deprecated patches

### 2. Maintainability
- Keep patches in dedicated modules (e.g., `patches.py`)
- Use configuration flags to enable/disable patches
- Version-check the target library before applying patches
- Provide fallback behavior when patches fail

### 3. Transparency
- Log when patches are applied
- Include source references in patch documentation
- Make patches reversible when possible
- Document compatibility requirements

## Python Monkey Patching Patterns

### Basic Variable Patching

```python
# Patch module variable
import third_party_lib
third_party_lib.DEFAULT_TIMEOUT = 30  # Original was 10

# Patch class attribute
third_party_lib.SomeClass.some_attribute = 'new_value'
```

### Function/Method Patching

```python
import third_party_lib

# Store original function
original_func = third_party_lib.some_function

def patched_function(*args, **kwargs):
    # Add custom logic
    result = original_func(*args, **kwargs)
    # Modify result
    return modified_result

# Apply patch
third_party_lib.some_function = patched_function
```

### Class Method Patching

```python
import third_party_lib

# Method 1: Direct replacement
def new_method(self, *args, **kwargs):
    # Custom implementation
    pass

third_party_lib.SomeClass.original_method = new_method

# Method 2: Wrapper pattern
original_method = third_party_lib.SomeClass.original_method

def wrapped_method(self, *args, **kwargs):
    # Pre-processing
    result = original_method(self, *args, **kwargs)
    # Post-processing
    return result

third_party_lib.SomeClass.original_method = wrapped_method
```

### Advanced: Patching Imported Functions

```python
import sys
import importlib

def uncache(modules):
    """Remove modules from sys.modules cache to force reimport"""
    for module in modules:
        if module in sys.modules:
            del sys.modules[module]

# Example usage:
import third_party.constants
third_party.constants.SOME_VALUE = 'patched'
uncache(['third_party.functions'])
from third_party import functions  # Will use patched value
```

## Common Pitfalls and Solutions

### 1. Import Order Issues
**Problem**: Patches don't work because module was already imported.
**Solution**: Apply patches before imports or use `uncache()` function.

### 2. Multiple Patches Conflict
**Problem**: Multiple patches overwrite each other.
**Solution**: Use chainable patches or patch registry pattern.

### 3. Version Compatibility
**Problem**: Patch breaks with library updates.
**Solution**: Version checking and conditional patching.

```python
import third_party_lib

def apply_patches():
    if hasattr(third_party_lib, '__version__'):
        version = tuple(map(int, third_party_lib.__version__.split('.')))
        if version >= (2, 0, 0):
            # Apply patch for version 2.0+
            pass
        else:
            # Apply patch for older versions
            pass
```

## Best Practices

### 1. Patch Organization
```python
# patches.py
import third_party_lib

class MonkeyPatches:
    @staticmethod
    def apply_all():
        MonkeyPatches.patch_timeout()
        MonkeyPatches.patch_retry_logic()
        MonkeyPatches.patch_error_handling()
    
    @staticmethod
    def patch_timeout():
        original = third_party_lib.DEFAULT_TIMEOUT
        third_party_lib.DEFAULT_TIMEOUT = 30
        return original
    
    @staticmethod  
    def revert_all():
        # Implementation to revert patches
        pass
```

### 2. Testing Patches
```python
import unittest
import third_party_lib
from patches import MonkeyPatches

class TestMonkeyPatches(unittest.TestCase):
    def setUp(self):
        MonkeyPatches.apply_all()
    
    def tearDown(self):
        MonkeyPatches.revert_all()
    
    def test_patch_effectiveness(self):
        # Test that patch works as expected
        self.assertEqual(third_party_lib.DEFAULT_TIMEOUT, 30)
```

### 3. Documentation Template
```python
"""
Monkey Patch: Fix for issue #123 in third_party_lib

Problem: Function some_function() doesn't handle None values correctly.
Solution: Wrap function to provide default behavior.

Compatibility: Tested with third_party_lib versions 1.2.0 - 1.4.0
Risk: Low - only adds null checking, doesn't change core logic.

Usage:
    from patches import apply_some_function_patch
    apply_some_function_patch()
    
Revert:
    from patches import revert_some_function_patch  
    revert_some_function_patch()
"""
```

## Language-Specific Considerations

### Python
- Use `unittest.mock` for testing scenarios
- Consider `wrapt` library for robust decorator-based patching
- Be aware of `__dict__` vs `__slots__` differences

### JavaScript/TypeScript
- Prototype-based patching for classes
- Use `Object.defineProperty` for non-enumerable patches
- Consider module interception with Webpack/RequireJS

### Ruby
- `alias_method_chain` pattern (though deprecated in Rails 5+)
- `Module#prepend` for cleaner method overriding
- `refine` for scoped modifications

## References

For detailed examples and advanced techniques, see:
- [references/python_examples.md](references/python_examples.md) - Complete Python examples
- [references/javascript_examples.md](references/javascript_examples.md) - JavaScript/TypeScript patterns
- [references/testing_strategies.md](references/testing_strategies.md) - Testing monkey patches
- [references/security_considerations.md](references/security_considerations.md) - Security implications

## Resources

This skill includes example resource directories that demonstrate how to organize different types of bundled resources:

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Claude for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Claude's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Claude should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Claude produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Any unneeded directories can be deleted.** Not every skill requires all three types of resources.
