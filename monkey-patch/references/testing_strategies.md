# Testing Monkey Patches

## Table of Contents
1. [Testing Philosophy](#testing-philosophy)
2. [Unit Testing Strategies](#unit-testing-strategies)
3. [Integration Testing](#integration-testing)
4. [Regression Testing](#regression-testing)
5. [Performance Testing](#performance-testing)
6. [Security Testing](#security-testing)
7. [Testing Tools and Frameworks](#testing-tools-and-frameworks)

## Testing Philosophy

### Why Test Monkey Patches?
Monkey patches are inherently risky because they modify behavior at runtime. Testing is crucial to ensure:
- **Correctness**: The patch works as intended
- **Safety**: The patch doesn't break existing functionality
- **Compatibility**: The patch works with different library versions
- **Performance**: The patch doesn't introduce significant overhead
- **Maintainability**: The patch can be safely removed or updated

### Testing Principles
1. **Isolation**: Test patches in isolation from other patches
2. **Reversibility**: Ensure patches can be cleanly reverted
3. **Idempotence**: Applying the same patch multiple times should be safe
4. **Documentation**: Tests should document expected behavior
5. **Version awareness**: Tests should account for library version differences

## Unit Testing Strategies

### Basic Patch Testing
```python
import unittest
import third_party_lib
from patches import apply_timeout_patch, revert_timeout_patch

class TestTimeoutPatch(unittest.TestCase):
    def setUp(self):
        """Apply patch before each test"""
        apply_timeout_patch()
    
    def tearDown(self):
        """Revert patch after each test"""
        revert_timeout_patch()
    
    def test_patch_applied(self):
        """Verify patch changes the expected value"""
        self.assertEqual(third_party_lib.DEFAULT_TIMEOUT, 30)
    
    def test_original_restored(self):
        """Verify original value is restored"""
        original_value = third_party_lib.DEFAULT_TIMEOUT
        revert_timeout_patch()
        self.assertNotEqual(third_party_lib.DEFAULT_TIMEOUT, original_value)
    
    def test_patch_idempotent(self):
        """Applying patch twice should not cause issues"""
        apply_timeout_patch()  # Already applied in setUp
        apply_timeout_patch()  # Apply again
        self.assertEqual(third_party_lib.DEFAULT_TIMEOUT, 30)
```

### Testing Patch Logic
```python
import unittest
from unittest.mock import Mock, patch
import third_party_lib
from patches import patch_api_call

class TestApiCallPatch(unittest.TestCase):
    def test_patch_wraps_correctly(self):
        """Test that patch correctly wraps the original function"""
        # Create mock original function
        mock_original = Mock(return_value="original_result")
        
        # Apply patch to mock
        patched = patch_api_call(mock_original)
        
        # Test patch behavior
        result = patched("test_arg", keyword="test")
        
        # Verify original was called with correct arguments
        mock_original.assert_called_once_with("test_arg", keyword="test")
        
        # Verify patch added expected behavior
        # (Assuming patch adds logging or modification)
        self.assertIsNotNone(result)
    
    def test_patch_error_handling(self):
        """Test patch handles errors from original function"""
        # Mock original that raises exception
        mock_original = Mock(side_effect=ValueError("Test error"))
        patched = patch_api_call(mock_original)
        
        # Test error is handled gracefully
        with self.assertLogs(level='ERROR') as log:
            result = patched()
            
            # Verify error was logged
            self.assertIn("Test error", log.output[0])
            
            # Verify fallback behavior
            self.assertEqual(result, {"error": "fallback"})
    
    def test_patch_performance(self):
        """Test patch doesn't add significant overhead"""
        import time
        
        # Time original function
        start = time.perf_counter()
        for _ in range(1000):
            third_party_lib.fast_function()
        original_time = time.perf_counter() - start
        
        # Apply patch
        apply_patch()
        
        # Time patched function
        start = time.perf_counter()
        for _ in range(1000):
            third_party_lib.fast_function()
        patched_time = time.perf_counter() - start
        
        # Verify overhead is less than 10%
        overhead = (patched_time - original_time) / original_time
        self.assertLess(overhead, 0.1, f"Overhead too high: {overhead:.1%}")
```

### Testing with Parameterized Tests
```python
import pytest
import third_party_lib
from patches import apply_calculation_patch, revert_calculation_patch

@pytest.fixture
def patched_calculator():
    """Fixture that applies and reverts patch"""
    apply_calculation_patch()
    yield
    revert_calculation_patch()

@pytest.mark.parametrize("input_val,expected", [
    (0, 0),
    (1, 2),
    (5, 10),
    (-3, -6),
    (100, 200),
])
def test_calculation_patch(patched_calculator, input_val, expected):
    """Test patch with various inputs"""
    result = third_party_lib.calculate(input_val)
    assert result == expected

@pytest.mark.parametrize("library_version", ["1.0.0", "1.1.0", "1.2.0", "2.0.0"])
def test_patch_version_compatibility(library_version):
    """Test patch works with different library versions"""
    # Mock version check
    with patch('third_party_lib.__version__', library_version):
        apply_calculation_patch()
        
        # Test basic functionality
        result = third_party_lib.calculate(5)
        
        # Version-specific assertions
        if library_version.startswith("1."):
            assert result == 10  # Old behavior
        else:
            assert result == 15  # New behavior in v2.0
```

## Integration Testing

### Testing Patch Interactions
```python
import unittest
from patches import PatchRegistry

class TestPatchInteractions(unittest.TestCase):
    def setUp(self):
        self.registry = PatchRegistry()
        self.registry.register_patches()
    
    def tearDown(self):
        self.registry.revert_all()
    
    def test_multiple_patches_independent(self):
        """Test that multiple patches don't interfere"""
        # Apply patch A
        self.registry.apply('patch_a')
        result_a = third_party_lib.function_a()
        self.assertEqual(result_a, "patched_a")
        
        # Apply patch B
        self.registry.apply('patch_b')
        result_b = third_party_lib.function_b()
        self.assertEqual(result_b, "patched_b")
        
        # Verify patch A still works
        result_a_again = third_party_lib.function_a()
        self.assertEqual(result_a_again, "patched_a")
    
    def test_patch_ordering(self):
        """Test patches applied in different orders"""
        # Apply in order A then B
        self.registry.apply('patch_a')
        self.registry.apply('patch_b')
        result_ab = third_party_lib.combined_function()
        
        # Revert and apply in opposite order
        self.registry.revert_all()
        self.registry.apply('patch_b')
        self.registry.apply('patch_a')
        result_ba = third_party_lib.combined_function()
        
        # Results should be the same regardless of order
        self.assertEqual(result_ab, result_ba)
    
    def test_patch_dependencies(self):
        """Test patches that depend on each other"""
        # Patch that depends on another patch
        self.registry.apply('base_patch')
        self.registry.apply('dependent_patch')
        
        # Verify both work together
        result = third_party_lib.complex_function()
        self.assertEqual(result, "expected_with_both_patches")
        
        # Verify dependent patch fails without base
        self.registry.revert('base_patch')
        with self.assertRaises(RuntimeError):
            third_party_lib.complex_function()
```

### Testing with Real Dependencies
```python
import unittest
import requests
from requests.exceptions import Timeout
from patches import patch_requests_timeout

class TestRequestsPatchIntegration(unittest.TestCase):
    def test_patch_with_real_network(self):
        """Test patch with actual network calls"""
        # Apply timeout patch
        patch_requests_timeout(timeout=1)  # 1 second timeout
        
        # Test with a site that should respond quickly
        response = requests.get('https://httpbin.org/delay/0.5')
        self.assertEqual(response.status_code, 200)
        
        # Test with a site that should timeout
        with self.assertRaises(Timeout):
            requests.get('https://httpbin.org/delay/2')
    
    def test_patch_preserves_original_behavior(self):
        """Test that patch doesn't break normal requests"""
        # Store original behavior
        original_get = requests.get
        
        # Apply patch
        patch_requests_timeout(timeout=5)
        
        # Test normal request still works
        response = requests.get('https://httpbin.org/get')
        self.assertEqual(response.status_code, 200)
        
        # Verify it's still the patched version
        self.assertNotEqual(requests.get, original_get)
    
    def test_patch_with_session(self):
        """Test patch works with requests.Session"""
        patch_requests_timeout(timeout=2)
        
        session = requests.Session()
        
        # Session should use patched timeout
        response = session.get('https://httpbin.org/delay/1')
        self.assertEqual(response.status_code, 200)
        
        with self.assertRaises(Timeout):
            session.get('https://httpbin.org/delay/3')
```

## Regression Testing

### Version Compatibility Matrix
```python
import pytest
import third_party_lib
from packaging import version

# Define supported versions
SUPPORTED_VERSIONS = [
    "1.0.0", "1.0.1", "1.1.0", "1.2.0",
    "2.0.0", "2.0.1", "2.1.0"
]

@pytest.fixture(params=SUPPORTED_VERSIONS)
def library_version(request):
    """Fixture to test with different library versions"""
    original_version = getattr(third_party_lib, '__version__', None)
    
    # Mock version
    third_party_lib.__version__ = request.param
    
    yield request.param
    
    # Restore original version
    if original_version is None:
        delattr(third_party_lib, '__version__')
    else:
        third_party_lib.__version__ = original_version

def test_patch_all_versions(library_version):
    """Regression test: patch should work with all supported versions"""
    from patches import apply_compatibility_patch
    
    try:
        apply_compatibility_patch()
        
        # Test basic functionality
        result = third_party_lib.basic_function()
        assert result is not None
        
        # Version-specific tests
        if version.parse(library_version) >= version.parse("2.0.0"):
            # New feature in v2.0
            result = third_party_lib.new_function()
            assert result == "expected_v2"
        else:
            # Old behavior
            result = third_party_lib.old_function()
            assert result == "expected_v1"
            
    except Exception as e:
        pytest.fail(f"Patch failed with version {library_version}: {e}")
```

### Backward Compatibility Testing
```python
import unittest
import json
from patches import patch_json_encoder

class TestBackwardCompatibility(unittest.TestCase):
    def test_original_serialization_preserved(self):
        """Test that patch doesn't break original JSON serialization"""
        patch_json_encoder()
        
        # Test standard types still work
        test_cases = [
            {"key": "value"},
            [1, 2, 3],
            "string",
            123,
            45.67,
            True,
            None
        ]
        
        for obj in test_cases:
            # Serialize with patched encoder
            json_str = json.dumps(obj)
            
            # Deserialize to verify
            decoded = json.loads(json_str)
            
            # Should match original
            if isinstance(obj, dict):
                self.assertDictEqual(decoded, obj)
            elif isinstance(obj, list):
                self.assertListEqual(decoded, obj)
            else:
                self.assertEqual(decoded, obj)
    
    def test_custom_object_serialization(self):
        """Test new functionality added by patch"""
        patch_json_encoder()
        
        class CustomObject:
            def __init__(self, value):
                self.value = value
            
            def to_json(self):
                return {"custom": self.value}
        
        obj = CustomObject("test")
        
        # Should serialize using to_json method
        json_str = json.dumps(obj)
        decoded = json.loads(json_str)
        
        self.assertEqual(decoded, {"custom": "test"})
    
    def test_mixed_objects(self):
        """Test patch handles mixed standard and custom objects"""
        patch_json_encoder()
        
        class CustomObject:
            def to_json(self):
                return {"type": "custom"}
        
        mixed_obj = {
            "standard": [1, 2, 3],
            "custom": CustomObject(),
            "nested": {
                "inner": CustomObject()
            }
        }
        
        json_str = json.dumps(mixed_obj)
        decoded = json.loads(json_str)
        
        self.assertEqual(decoded["standard"], [1, 2, 3])
        self.assertEqual(decoded["custom"], {"type": "custom"})
        self.assertEqual(decoded["nested"]["inner"], {"type": "custom"})
```

## Performance Testing

### Benchmarking Patch Overhead
```python
import timeit
import statistics
from patches import apply_performance_patch, revert_performance_patch

class TestPatchPerformance(unittest.TestCase):
    def setUp(self):
        self.iterations = 10000
        self.setup_code = "from __main__ import third_party_lib"
    
    def test_patch_overhead(self):
        """Measure performance overhead of patch"""
        # Benchmark original function
        original_time = timeit.timeit(
            "third_party_lib.fast_function()",
            setup=self.setup_code,
            number=self.iterations
        )
        
        # Apply patch
        apply_performance_patch()
        
        # Benchmark patched function
        patched_time = timeit.timeit(
            "third_party_lib.fast_function()",
            setup=self.setup_code,
            number=self.iterations
        )
        
        # Calculate overhead
        overhead = (patched_time - original_time) / original_time
        
        print(f"Original: {original_time:.4f}s")
        print(f"Patched: {patched_time:.4f}s")
        print(f"Overhead: {overhead:.1%}")
        
        # Assert overhead is acceptable
        self.assertLess(overhead, 0.05, "Overhead exceeds 5%")
        
        # Revert patch
        revert_performance_patch()
    
    def test_patch_memory_usage(self):
        """Test patch doesn't cause memory leaks"""
        import gc
        import tracemalloc
        
        # Start tracking memory
        tracemalloc.start()
        
        # Apply and revert patch multiple times
        for i in range(100):
            apply_performance_patch()
            # Use patched function
            result = third_party_lib.memory_intensive_function()
            revert_performance_patch()
            
            # Force garbage collection
            gc.collect()
        
        # Get memory statistics
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"Current memory: {current / 1024:.1f} KB")
        print(f"Peak memory: {peak / 1024:.1f} KB")
        
        # Assert no significant memory leak
        self.assertLess(current, 10 * 1024 * 1024, "Memory leak detected")
    
    def test_concurrent_patch_usage(self):
        """Test patch performance under concurrent access"""
        import threading
        import queue
        
        apply_performance_patch()
        
        results = queue.Queue()
        errors = queue.Queue()
        
        def worker(worker_id):
            try:
                start = time.perf_counter()
                for _ in range(1000):
                    third_party_lib.thread_safe_function()
                elapsed = time.perf_counter() - start
                results.put((worker_id, elapsed))
            except Exception as e:
                errors.put((worker_id, str(e)))
        
        # Create multiple threads
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Check for errors
        self.assertTrue(errors.empty(), f"Errors in concurrent execution: {list(errors.queue)}")
        
        # Analyze performance
        worker_times = []
        while not results.empty():
            worker_id, elapsed = results.get()
            worker_times.append(elapsed)
        
        avg_time = statistics.mean(worker_times)
        std_dev = statistics.stdev(worker_times) if len(worker_times) > 1 else 0
        
        print(f"Average time per worker: {avg_time:.3f}s")
        print(f"Standard deviation: {std_dev:.3f}s")
        
        # Assert reasonable consistency
        self.assertLess(std_dev / avg_time, 0.5, "High variance in concurrent execution")
        
        revert_performance_patch()
```

## Security Testing

### Testing Patch Safety
```python
import unittest
import tempfile
import os
from patches import apply_file_operation_patch

class TestPatchSecurity(unittest.TestCase):
    def test_patch_path_traversal_prevention(self):
        """Test patch prevents path traversal attacks"""
        apply_file_operation_patch()
        
        # Attempt path traversal
        malicious_path = "../../../etc/passwd"
        
        with self.assertRaises(ValueError) as context:
            third_party_lib.read_file(malicious_path)
        
        self.assertIn("path traversal", str(context.exception).lower())
    
    def test_patch_input_validation(self):
        """Test patch validates input properly"""
        apply_file_operation_patch()
        
        # Test with various malicious inputs
        test_cases = [
            (None, "None input"),
            ("", "Empty string"),
            ("   ", "Whitespace only"),
            ("file\nwith\nnewlines", "Newlines in filename"),
            ("file\0with\0nulls", "Null bytes in filename"),
        ]
        
        for input_val, description in test_cases:
            with self.subTest(description=description):
                with self.assertRaises(ValueError):
                    third_party_lib.read_file(input_val)
    
    def test_patch_permission_handling(self):
        """Test patch handles permissions correctly"""
        apply_file_operation_patch()
        
        # Create a file with restricted permissions
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            # Make file unreadable
            os.chmod(temp_file, 0o000)
            
            # Should handle permission error gracefully
            with self.assertRaises(PermissionError):
                third_party_lib.read_file(temp_file)
                
        finally:
            # Cleanup
            os.chmod(temp_file, 0o644)
            os.unlink(temp_file)
    
    def test_patch_resource_cleanup(self):
        """Test patch properly cleans up resources"""
        apply_file_operation_patch()
        
        # Monitor file descriptors
        import resource
        initial_fds = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
        
        # Perform many file operations
        for i in range(100):
            with tempfile.NamedTemporaryFile(mode='w') as f:
                f.write(f"test {i}")
                f.flush()
                third_party_lib.process_file(f.name)
        
        # Check for file descriptor leaks
        # (This is simplified - in reality would need OS-specific checks)
        final_fds = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
        self.assertEqual(initial_fds, final_fds, "File descriptor leak detected")
```

## Testing Tools and Frameworks

### Custom Testing Framework for Patches
```python
class PatchTestRunner:
    """Custom test runner for monkey patches"""
    
    def __init__(self):
        self.tests = []
        self.results = []
    
    def add_test(self, name, test_func, setup=None, teardown=None):
        """Add a test to the runner"""
        self.tests.append({
            'name': name,
            'test': test_func,
            'setup': setup,
            'teardown': teardown
        })
    
    def run_all(self):
        """Run all tests"""
        for test_info in self.tests:
            print(f"\nRunning: {test_info['name']}")
            
            try:
                # Setup
                if test_info['setup']:
                    test_info['setup']()
                
                # Run test
                test_info['test']()
                
                # Teardown
                if test_info['teardown']:
                    test_info['teardown']()
                
                print(f"  ✓ PASS")
                self.results.append((test_info['name'], True, None))
                
            except Exception as e:
                print(f"  ✗ FAIL: {e}")
                self.results.append((test_info['name'], False, str(e)))
    
    def generate_report(self):
        """Generate test report"""
        passed = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)
        
        report = f"\n{'='*50}\n"
        report += f"Patch Test Report\n"
        report += f"{'='*50}\n"
        report += f"Total Tests: {total}\n"
        report += f"Passed: {passed}\n"
        report += f"Failed: {total - passed}\n"
        report += f"Success Rate: {passed/total*100:.1f}%\n"
        
        if total - passed > 0:
            report += f"\nFailed Tests:\n"
            for name, success, error in self.results:
                if not success:
                    report += f"  - {name}: {error}\n"
        
        return report

# Usage
def test_patch_basic():
    runner = PatchTestRunner()
    
    # Add tests
    runner.add_test(
        "Timeout patch applied",
        lambda: assert_equal(third_party_lib.DEFAULT_TIMEOUT, 30),
        setup=apply_timeout_patch,
        teardown=revert_timeout_patch
    )
    
    runner.add_test(
        "Patch idempotent",
        lambda: apply_timeout_patch(),  # Apply twice
        setup=apply_timeout_patch,
        teardown=revert_timeout_patch
    )
    
    # Run tests
    runner.run_all()
    print(runner.generate_report())
```

### Integration with Existing Test Frameworks
```python
# conftest.py for pytest integration
import pytest
from patches import PatchRegistry

@pytest.fixture(scope="session")
def patch_registry():
    """Session-scoped patch registry"""
    registry = PatchRegistry()
    registry.register_all_patches()
    return registry

@pytest.fixture(autouse=True)
def auto_apply_patches(patch_registry, request):
    """Automatically apply and revert patches for each test"""
    # Check if test is marked to skip patching
    if request.node.get_closest_marker("no_patch"):
        yield
        return
    
    # Apply patches
    patch_registry.apply_all()
    
    yield
    
    # Revert patches
    patch_registry.revert_all()

# Custom markers
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "no_patch: skip automatic patch application for this test"
    )
    config.addinivalue_line(
        "markers",
        "patch_version(version): test with specific library version"
    )

# Usage in tests
@pytest.mark.no_patch
def test_without_patches():
    """Test original behavior"""
    assert third_party_lib.DEFAULT_TIMEOUT == 10

def test_with_patches():
    """Test with patches automatically applied"""
    assert third_party_lib.DEFAULT_TIMEOUT == 30

@pytest.mark.patch_version("1.0.0")
def test_specific_version():
    """Test patch with specific library version"""
    # Version-specific test logic
    pass
```

### Continuous Integration Setup
```yaml
# .github/workflows/test-patches.yml
name: Test Monkey Patches

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test-patches:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']
        library-version: ['1.0.0', '1.1.0', '2.0.0']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
        pip install "third-party-lib==${{ matrix.library-version }}"
    
    - name: Run patch tests
      run: |
        python -m pytest tests/test_patches.py \
          --cov=patches \
          --cov-report=xml \
          --tb=short
    
    - name: Run performance tests
      run: |
        python tests/test_patch_performance.py
    
    - name: Run security tests
      run: |
        python tests/test_patch_security.py
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
```

### Test Data Generation
```python
import hypothesis
from hypothesis import given, strategies as st
from patches import apply_validation_patch

class TestPatchWithPropertyBasedTesting:
    """Property-based testing for patches"""
    
    @given(st.text(min_size=1, max_size=100))
    def test_patch_handles_all_strings(self, input_string):
        """Test patch handles all possible strings"""
        apply_validation_patch()
        
        try:
            result = third_party_lib.validate_input(input_string)
            # Property: result should be boolean
            assert isinstance(result, bool)
            
            # Property: identical strings should give same result
            result2 = third_party_lib.validate_input(input_string)
            assert result == result2
            
        finally:
            revert_validation_patch()
    
    @given(st.integers(min_value=-1000, max_value=1000))
    def test_patch_preserves_arithmetic(self, number):
        """Test patch doesn't break arithmetic operations"""
        apply_calculation_patch()
        
        try:
            result = third_party_lib.calculate(number)
            
            # Property: result should be number * 2 ± small tolerance
            expected = number * 2
            tolerance = abs(expected * 0.01)  # 1% tolerance
            
            assert abs(result - expected) <= tolerance
            
        finally:
            revert_calculation_patch()
    
    @given(
        st.lists(st.text(min_size=1, max_size=10), min_size=0, max_size=100)
    )
    def test_patch_list_processing(self, string_list):
        """Test patch handles lists of various sizes"""
        apply_list_patch()
        
        try:
            result = third_party_lib.process_list(string_list)
            
            # Property: result length equals input length
            assert len(result) == len(string_list)
            
            # Property: processing is idempotent
            result2 = third_party_lib.process_list(string_list)
            assert result == result2
            
        finally:
            revert_list_patch()
```