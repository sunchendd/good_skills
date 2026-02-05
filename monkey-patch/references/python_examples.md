# Python Monkey Patch Examples

## Table of Contents
1. [Basic Examples](#basic-examples)
2. [Advanced Techniques](#advanced-techniques)
3. [Library-Specific Patterns](#library-specific-patterns)
4. [Testing Patterns](#testing-patterns)
5. [Troubleshooting](#troubleshooting)

## Basic Examples

### Simple Variable Patching
```python
# Patch a constant value
import math
original_pi = math.pi
math.pi = 3.14  # Educational purposes only!

# Patch configuration
import requests
requests.DEFAULT_TIMEOUT = 30  # Increase default timeout
```

### Function Patching
```python
import datetime

# Store original
original_now = datetime.datetime.now

def patched_now():
    """Always return a specific time for testing"""
    return datetime.datetime(2024, 1, 1, 12, 0, 0)

# Apply patch
datetime.datetime.now = patched_now

# Usage
print(datetime.datetime.now())  # Always returns 2024-01-01 12:00:00
```

### Class Method Patching
```python
import json

# Patch JSON encoder to handle custom objects
original_default = json.JSONEncoder.default

def patched_default(self, obj):
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    return original_default(self, obj)

json.JSONEncoder.default = patched_default

# Now JSON encoder can serialize custom objects with to_json() method
```

## Advanced Techniques

### Context Manager for Temporary Patches
```python
import contextlib
import some_library

class temporary_patch:
    """Context manager for temporary monkey patches"""
    
    def __init__(self, target, replacement):
        self.target = target
        self.replacement = replacement
        self.original = None
    
    def __enter__(self):
        # Store original
        module_name, attr_name = self.target.rsplit('.', 1)
        module = __import__(module_name)
        for part in module_name.split('.')[1:]:
            module = getattr(module, part)
        self.original = getattr(module, attr_name)
        
        # Apply patch
        setattr(module, attr_name, self.replacement)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original
        module_name, attr_name = self.target.rsplit('.', 1)
        module = __import__(module_name)
        for part in module_name.split('.')[1:]:
            module = getattr(module, part)
        setattr(module, attr_name, self.original)

# Usage
def mock_response():
    return "Mocked response"

with temporary_patch('requests.get', mock_response):
    import requests
    response = requests.get('https://example.com')
    print(response)  # "Mocked response"
```

### Decorator-Based Patching
```python
import functools

def monkey_patch(target_path):
    """Decorator to apply monkey patches"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Parse target path
            module_path, attr_name = target_path.rsplit('.', 1)
            
            # Import module
            module = __import__(module_path)
            for part in module_path.split('.')[1:]:
                module = getattr(module, part)
            
            # Store original
            original = getattr(module, attr_name)
            
            try:
                # Apply patch
                setattr(module, attr_name, func)
                return func(*args, **kwargs)
            finally:
                # Restore original
                setattr(module, attr_name, original)
        
        return wrapper
    return decorator

# Usage
@monkey_patch('datetime.datetime.now')
def fixed_time():
    return datetime.datetime(2024, 1, 1)
```

### Patch Registry Pattern
```python
class PatchRegistry:
    """Manage multiple monkey patches"""
    
    def __init__(self):
        self.patches = {}
        self.applied = set()
    
    def register(self, name, target, patch_func, revert_func=None):
        """Register a patch"""
        self.patches[name] = {
            'target': target,
            'patch': patch_func,
            'revert': revert_func,
            'original': None
        }
    
    def apply(self, name):
        """Apply a specific patch"""
        if name not in self.patches:
            raise ValueError(f"Patch '{name}' not registered")
        
        patch_info = self.patches[name]
        
        # Get target
        module_path, attr_name = patch_info['target'].rsplit('.', 1)
        module = __import__(module_path)
        for part in module_path.split('.')[1:]:
            module = getattr(module, part)
        
        # Store original
        patch_info['original'] = getattr(module, attr_name)
        
        # Apply patch
        setattr(module, attr_name, patch_info['patch'])
        self.applied.add(name)
    
    def revert(self, name):
        """Revert a specific patch"""
        if name not in self.applied:
            return
        
        patch_info = self.patches[name]
        if patch_info['original'] is None:
            return
        
        # Get target
        module_path, attr_name = patch_info['target'].rsplit('.', 1)
        module = __import__(module_path)
        for part in module_path.split('.')[1:]:
            module = getattr(module, part)
        
        # Revert to original
        setattr(module, attr_name, patch_info['original'])
        self.applied.remove(name)
    
    def apply_all(self):
        """Apply all registered patches"""
        for name in self.patches:
            self.apply(name)
    
    def revert_all(self):
        """Revert all applied patches"""
        for name in list(self.applied):
            self.revert(name)

# Usage
registry = PatchRegistry()

def patched_open(file, mode='r', *args, **kwargs):
    print(f"Opening {file} with mode {mode}")
    return open(file, mode, *args, **kwargs)

registry.register(
    name='verbose_open',
    target='builtins.open',
    patch_func=patched_open
)

registry.apply_all()  # Apply all patches
# ... use patched functionality ...
registry.revert_all()  # Revert all patches
```

## Library-Specific Patterns

### Patching Requests Library
```python
import requests
from unittest.mock import Mock

# Patch requests.get to return mock data
def mock_requests_get():
    original_get = requests.get
    
    def patched_get(url, *args, **kwargs):
        if 'example.com' in url:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'mocked': True}
            return mock_response
        return original_get(url, *args, **kwargs)
    
    requests.get = patched_get
    return original_get

# Usage
original = mock_requests_get()
response = requests.get('https://example.com/api')
print(response.json())  # {'mocked': True}
requests.get = original  # Restore
```

### Patching Django Models
```python
# Example: Add custom method to Django User model
from django.contrib.auth.models import User

def get_display_name(self):
    """Get user's display name (first name + last initial)"""
    if self.first_name and self.last_name:
        return f"{self.first_name} {self.last_name[0]}."
    return self.username

# Apply patch
User.add_to_class('get_display_name', get_display_name)

# Now all User instances have this method
user = User.objects.get(username='test')
print(user.get_display_name())
```

### Patching SQLAlchemy
```python
from sqlalchemy import event
from sqlalchemy.orm import Session

# Patch session to add automatic timestamp
def add_timestamps_before_flush(session, flush_context, instances):
    for obj in session.new:
        if hasattr(obj, 'created_at'):
            obj.created_at = datetime.datetime.utcnow()
    for obj in session.dirty:
        if hasattr(obj, 'updated_at'):
            obj.updated_at = datetime.datetime.utcnow()

# Apply the event listener
event.listen(Session, 'before_flush', add_timestamps_before_flush)
```

## Testing Patterns

### Pytest Fixtures for Monkey Patching
```python
import pytest
import some_library

@pytest.fixture
def patched_library():
    """Fixture that applies and cleans up patches"""
    original_func = some_library.some_function
    
    def mock_function(*args, **kwargs):
        return "mocked"
    
    some_library.some_function = mock_function
    
    yield  # Test runs here
    
    # Cleanup
    some_library.some_function = original_func

def test_with_patched_library(patched_library):
    result = some_library.some_function()
    assert result == "mocked"
```

### unittest.mock Integration
```python
from unittest.mock import patch, MagicMock
import some_library

# Using unittest.mock's patch decorator
@patch('some_library.expensive_function')
def test_with_mock(mock_function):
    mock_function.return_value = 42
    
    result = some_library.some_function_that_calls_expensive()
    assert result == 42
    mock_function.assert_called_once()

# Manual integration with monkey patching
def create_mock_patch(target, return_value=None):
    mock = MagicMock(return_value=return_value)
    
    # Store original
    module_path, attr_name = target.rsplit('.', 1)
    module = __import__(module_path)
    for part in module_path.split('.')[1:]:
        module = getattr(module, part)
    original = getattr(module, attr_name)
    
    # Apply mock
    setattr(module, attr_name, mock)
    
    return mock, original

# Usage
mock_func, original_func = create_mock_patch(
    'some_library.some_function',
    return_value='mocked'
)
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Patch doesn't work after import
**Problem**: Module was cached before patch was applied.
**Solution**: Patch before import or clear module cache.

```python
import sys

def apply_patch_before_import():
    # Mock module before it's imported
    mock_module = type(sys)('some_library')
    mock_module.some_function = lambda: 'mocked'
    sys.modules['some_library'] = mock_module
    
    # Now import will use mocked module
    import some_library
    print(some_library.some_function())  # 'mocked'
```

#### Issue: Multiple patches conflict
**Problem**: Different parts of code patch the same function.
**Solution**: Use patch coordination or registry.

```python
class CoordinatedPatch:
    def __init__(self, target):
        self.target = target
        self.patches = []
        self.original = None
    
    def add_patch(self, patch_func):
        self.patches.append(patch_func)
    
    def apply(self):
        # Get original
        module_path, attr_name = self.target.rsplit('.', 1)
        module = __import__(module_path)
        for part in module_path.split('.')[1:]:
            module = getattr(module, part)
        self.original = getattr(module, attr_name)
        
        # Create chained patch
        def chained_patch(*args, **kwargs):
            result = self.original(*args, **kwargs)
            for patch in self.patches:
                result = patch(result, *args, **kwargs)
            return result
        
        setattr(module, attr_name, chained_patch)
```

#### Issue: Patch breaks with library updates
**Problem**: Library interface changed.
**Solution**: Version checking and graceful degradation.

```python
import some_library

def safe_patch():
    try:
        # Try to patch new interface
        if hasattr(some_library, 'new_function'):
            original = some_library.new_function
            # ... patch new function
        else:
            # Fall back to old interface
            original = some_library.old_function
            # ... patch old function
    except AttributeError:
        # Library doesn't have expected interface
        warnings.warn(
            "Could not apply patch - library interface changed",
            DeprecationWarning
        )
```

### Debugging Tips

1. **Log patch application**:
```python
import logging

logger = logging.getLogger(__name__)

def logged_patch(target, patch_func):
    module_path, attr_name = target.rsplit('.', 1)
    logger.info(f"Patching {target}")
    
    # ... apply patch ...
    
    logger.info(f"Successfully patched {target}")
```

2. **Verify patch is active**:
```python
def verify_patch(target, expected_value):
    module_path, attr_name = target.rsplit('.', 1)
    module = __import__(module_path)
    for part in module_path.split('.')[1:]:
        module = getattr(module, part)
    
    actual = getattr(module, attr_name)
    if actual != expected_value:
        raise RuntimeError(
            f"Patch verification failed for {target}. "
            f"Expected {expected_value}, got {actual}"
        )
```

3. **Create patch diagnostics**:
```python
class PatchDiagnostics:
    def __init__(self):
        self.applied_patches = []
        self.failed_patches = []
    
    def record_apply(self, target, success=True, error=None):
        record = {
            'target': target,
            'timestamp': datetime.datetime.utcnow(),
            'success': success,
            'error': str(error) if error else None
        }
        
        if success:
            self.applied_patches.append(record)
        else:
            self.failed_patches.append(record)
    
    def get_report(self):
        return {
            'total_applied': len(self.applied_patches),
            'total_failed': len(self.failed_patches),
            'applied': self.applied_patches,
            'failed': self.failed_patches
        }
```