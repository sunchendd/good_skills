# Wings Engine Patch Implementation Guide

## Architecture Overview

Wings Engine Patch is a runtime patching framework for AI inference engines (vllm, vllm_ascend) that uses Python import hooks to apply non-intrusive modifications.

### Key Components

```
wings_engine_patch/
├── wings_engine_patch/
│   ├── _auto_patch.py           # Entry point (.pth file trigger)
│   ├── registry.py              # Feature → Patch mapping
│   └── patch_<engine>/          # Engine-specific patches
│       └── <version>/           # Version-scoped patches
│           ├── patch_utils.py   # Shared utilities
│           └── patch_<feature>.py
├── build_wheel.py               # Custom build (includes .pth)
└── setup.py
```

## Entry Point: `.pth` File

The framework uses a `.pth` file to automatically execute code on Python startup.

### `wings_engine_patch.pth`
```python
import wings_engine_patch._auto_patch; wings_engine_patch._auto_patch.init()
```

Placed in site-packages, this executes `_auto_patch.init()` before any user code runs.

## Auto Patch Module

### `_auto_patch.py`

```python
import os
import json
import wrapt

def init():
    """Entry point called by .pth file"""
    # Read configuration from environment
    config_str = os.environ.get('WINGS_ENGINE_PATCH_OPTIONS')
    if not config_str:
        return
    
    try:
        config = json.loads(config_str)
    except json.JSONDecodeError:
        return
    
    # Apply patches for each engine
    for engine_name, engine_config in config.items():
        version = engine_config.get('version')
        features = engine_config.get('features', [])
        
        if not features:
            continue
        
        # Get patches from registry
        from . import registry
        patch_funcs = registry.get_patches(engine_name, version, features)
        
        # Execute each patch function
        for patch_func in patch_funcs:
            try:
                patch_func()
            except Exception as e:
                # Log error but continue
                pass
```

## Registry Module

### `registry.py`

The registry maps features to patch functions and handles propagation/deduplication.

```python
# registry.py

PATCH_REGISTRY = {
    'vllm_ascend': {
        '0.12.0rc1': '_build_vllm_ascend_v0_12_0rc1_features',
    },
}

def _build_vllm_ascend_v0_12_0rc1_features():
    """Build feature registry for vllm_ascend v0.12.0rc1
    
    Returns:
        tuple: (features_dict, non_propagating_patches_set)
    """
    from .patch_vllm_ascend.v0_12_0rc1 import (
        patch_soft_fp8,
        patch_utils,
    )
    
    features = {
        'soft_fp8': [
            patch_soft_fp8.patch_AscendQuantConfig,
            patch_utils.patch_QUANTIZATION_MAP,
        ],
        'soft_fp4': [
            patch_utils.patch_QUANTIZATION_MAP,  # Shared patch
        ],
    }
    
    # Patches that should NOT trigger feature propagation
    non_propagating_patches = set()
    
    return features, non_propagating_patches


def get_patches(engine_name, version, requested_features):
    """Get deduplicated patch functions for requested features
    
    Args:
        engine_name: Engine identifier (e.g., 'vllm_ascend')
        version: Engine version (e.g., '0.12.0rc1')
        requested_features: List of feature names to enable
    
    Returns:
        list: Deduplicated patch functions to execute
    """
    if engine_name not in PATCH_REGISTRY:
        return []
    
    engine_registry = PATCH_REGISTRY[engine_name]
    
    # Get version-specific builder
    builder_name = engine_registry.get(version)
    if not builder_name:
        builder_name = engine_registry.get('default')
    if not builder_name:
        return []
    
    # Build features
    builder_func = globals()[builder_name]
    features, non_propagating = builder_func()
    
    # Resolve features with propagation
    enabled_features = resolve_features(
        features, 
        requested_features,
        non_propagating
    )
    
    # Collect and deduplicate patches
    patches = []
    seen = set()
    
    for feature in enabled_features:
        if feature not in features:
            continue
        for patch_func in features[feature]:
            if id(patch_func) not in seen:
                patches.append(patch_func)
                seen.add(id(patch_func))
    
    return patches


def resolve_features(features, requested, non_propagating):
    """Resolve feature dependencies via propagation
    
    Args:
        features: Dict mapping feature names to patch function lists
        requested: List of requested feature names
        non_propagating: Set of patch functions that don't trigger propagation
    
    Returns:
        set: All enabled features (including propagated ones)
    """
    enabled = set(requested)
    
    # Build patch → features reverse mapping
    patch_to_features = {}
    for feature, patches in features.items():
        for patch in patches:
            patch_id = id(patch)
            if patch_id not in patch_to_features:
                patch_to_features[patch_id] = []
            patch_to_features[patch_id].append(feature)
    
    # Propagate features
    changed = True
    while changed:
        changed = False
        for feature in list(enabled):
            if feature not in features:
                continue
            
            for patch in features[feature]:
                # Skip non-propagating patches
                if patch in non_propagating:
                    continue
                
                # Enable all features sharing this patch
                patch_id = id(patch)
                for other_feature in patch_to_features.get(patch_id, []):
                    if other_feature not in enabled:
                        enabled.add(other_feature)
                        changed = True
    
    return enabled
```

## Patch Implementation

### Template Structure

```python
# patch_vllm_ascend/v0.12.0rc1/patch_soft_fp8.py
"""
Patch: Add soft_fp8 quantization support

Target: vllm_ascend v0.12.0rc1
Feature: soft_fp8
"""
import wrapt

def patch_AscendQuantConfig():
    """Patch AscendQuantConfig to support soft_fp8"""
    
    def hook():
        # CRITICAL: Lazy import inside hook function
        import vllm_ascend.quantization.config as config
        
        # Store original
        original_get_method = config.AscendQuantConfig.get_quant_method
        
        # Define patched function
        def patched_get_method(self):
            if self.quant_method == 'soft_fp8':
                return 'soft_fp8'
            return original_get_method(self)
        
        # Apply patch
        config.AscendQuantConfig.get_quant_method = patched_get_method
    
    # Register hook to execute after module import
    wrapt.register_post_import_hook(hook, 'vllm_ascend.quantization')
```

### Using wrapt Wrappers

For more complex wrapping (access to args, kwargs):

```python
import wrapt

def patch_ComplexFunction():
    """Wrap function with argument inspection"""
    
    def wrapper(wrapped, instance, args, kwargs):
        """
        Args:
            wrapped: Original function
            instance: Instance object (None for module functions)
            args: Positional arguments tuple
            kwargs: Keyword arguments dict
        """
        # Pre-processing
        modified_args = list(args)
        modified_kwargs = kwargs.copy()
        
        # Call original
        result = wrapped(*modified_args, **modified_kwargs)
        
        # Post-processing
        return result
    
    wrapt.register_post_import_hook(
        lambda: wrapt.wrap_function_wrapper(
            'vllm_ascend.module',
            'function_name',
            wrapper
        ),
        'vllm_ascend.module'
    )
```

## Build System

### `build_wheel.py`

Custom build script to ensure `.pth` file is included:

```python
# build_wheel.py
import os
import subprocess
import shutil

def build():
    # Clean previous builds
    shutil.rmtree('dist', ignore_errors=True)
    shutil.rmtree('build', ignore_errors=True)
    
    # Build wheel
    subprocess.run(['python', 'setup.py', 'bdist_wheel'], check=True)
    
    print("Build complete. Wheel in dist/")

if __name__ == '__main__':
    build()
```

### `setup.py`

```python
from setuptools import setup, find_packages

setup(
    name='wings_engine_patch',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'wrapt>=1.14.0',
    ],
    # CRITICAL: Include .pth file in data_files
    data_files=[
        ('', ['wings_engine_patch.pth']),
    ],
    include_package_data=True,
)
```

## Advanced Patterns

### Pattern 1: Conditional Patching Based on Runtime Checks

```python
def patch_ConditionalFeature():
    """Apply patch only if certain conditions are met"""
    
    def hook():
        import vllm_ascend
        
        # Check if feature is available
        if not hasattr(vllm_ascend, 'some_required_module'):
            # Skip patching if dependency missing
            return
        
        # Apply patch
        # ...
    
    wrapt.register_post_import_hook(hook, 'vllm_ascend')
```

### Pattern 2: Patching with Error Recovery

```python
def patch_WithFallback():
    """Patch with graceful fallback on error"""
    
    def hook():
        import vllm_ascend
        import logging
        
        try:
            # Attempt patch
            original = vllm_ascend.some_function
            vllm_ascend.some_function = patched_version
        except AttributeError:
            # Fallback: Function doesn't exist in this version
            logging.warning("Could not apply patch - function not found")
        except Exception as e:
            # Fallback: Unexpected error
            logging.error(f"Patch failed: {e}")
    
    wrapt.register_post_import_hook(hook, 'vllm_ascend')
```

### Pattern 3: Multi-Module Coordination

```python
def patch_CrossModule():
    """Patch that coordinates changes across multiple modules"""
    
    def hook_module_a():
        import vllm_ascend.module_a as module_a
        module_a.SHARED_STATE = 'patched'
    
    def hook_module_b():
        import vllm_ascend.module_b as module_b
        # Use shared state from module_a
        import vllm_ascend.module_a as module_a
        
        original = module_b.some_function
        def patched_func(*args, **kwargs):
            # Access shared state
            if module_a.SHARED_STATE == 'patched':
                # Custom behavior
                pass
            return original(*args, **kwargs)
        module_b.some_function = patched_func
    
    # Register both hooks
    wrapt.register_post_import_hook(hook_module_a, 'vllm_ascend.module_a')
    wrapt.register_post_import_hook(hook_module_b, 'vllm_ascend.module_b')
```

## Testing

### Unit Test Template

```python
# tests/test_patch_soft_fp8.py
import unittest
import os
import sys

class TestSoftFP8Patch(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        # Set environment before importing
        os.environ['WINGS_ENGINE_PATCH_OPTIONS'] = '''{
            "vllm_ascend": {
                "version": "0.12.0rc1",
                "features": ["soft_fp8"]
            }
        }'''
        
        # Clear module cache
        for module in list(sys.modules.keys()):
            if module.startswith('vllm_ascend'):
                del sys.modules[module]
    
    def test_quantization_map_updated(self):
        """Test that QUANTIZATION_MAP includes soft_fp8"""
        # Trigger patch by importing
        import vllm_ascend.quantization.utils as utils
        
        self.assertIn('soft_fp8', utils.ASCEND_QUANTIZATION_METHOD_MAP)
        self.assertEqual(
            utils.ASCEND_QUANTIZATION_METHOD_MAP['soft_fp8'],
            'SoftFP8'
        )
    
    def test_config_recognizes_soft_fp8(self):
        """Test that AscendQuantConfig handles soft_fp8"""
        import vllm_ascend.quantization.config as config
        
        quant_config = config.AscendQuantConfig(quant_method='soft_fp8')
        result = quant_config.get_quant_method()
        
        self.assertEqual(result, 'soft_fp8')
```

### Integration Test

```python
# tests/integration/test_end_to_end.py
import unittest
import subprocess
import os

class TestEndToEnd(unittest.TestCase):
    
    def test_full_pipeline(self):
        """Test full pipeline from config to execution"""
        
        # Set environment
        env = os.environ.copy()
        env['WINGS_ENGINE_PATCH_OPTIONS'] = '''{
            "vllm_ascend": {
                "version": "0.12.0rc1",
                "features": ["soft_fp8"]
            }
        }'''
        
        # Run vllm command
        result = subprocess.run(
            ['python', '-m', 'vllm.entrypoints.api_server', '--help'],
            env=env,
            capture_output=True,
            text=True
        )
        
        # Verify no errors
        self.assertEqual(result.returncode, 0)
```

## Debugging Tips

### 1. Enable Verbose Logging

```python
# _auto_patch.py
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def init():
    logger.info("Wings Engine Patch initializing...")
    # ... rest of init
```

### 2. Verify Patch Application

```python
def patch_WithVerification():
    def hook():
        import vllm_ascend
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"Patching vllm_ascend.func")
        
        original = vllm_ascend.func
        vllm_ascend.func = patched_func
        
        # Verify patch applied
        if vllm_ascend.func == patched_func:
            logger.info("Patch applied successfully")
        else:
            logger.error("Patch application failed")
    
    wrapt.register_post_import_hook(hook, 'vllm_ascend')
```

### 3. Dump Enabled Features

```python
# registry.py
def get_patches(engine_name, version, requested_features):
    # ... existing code ...
    
    # Debug: Print enabled features
    import logging
    logging.info(f"Requested features: {requested_features}")
    logging.info(f"Enabled features (after propagation): {enabled_features}")
    
    return patches
```
