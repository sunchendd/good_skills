# Security Considerations for Monkey Patches

## Table of Contents
1. [Security Risks Overview](#security-risks-overview)
2. [Injection Vulnerabilities](#injection-vulnerabilities)
3. [Privilege Escalation](#privilege-escalation)
4. [Data Integrity Risks](#data-integrity-risks)
5. [Authentication Bypass](#authentication-bypass)
6. [Secure Patch Design](#secure-patch-design)
7. [Security Testing](#security-testing)
8. [Incident Response](#incident-response)

## Security Risks Overview

### Why Monkey Patches Are Security-Sensitive
Monkey patches modify runtime behavior, which can introduce security vulnerabilities:

1. **Trust Boundary Violation**: Patches execute with the same privileges as the patched code
2. **Supply Chain Risk**: Patches can be injected by malicious dependencies
3. **Audit Trail Obfuscation**: Patches hide behavior from static analysis
4. **Version Confusion**: Different versions may have different security properties

### Common Attack Vectors
- **Code Injection**: Malicious patches modifying critical functions
- **Data Tampering**: Patches that alter input validation or output encoding
- **Privilege Bypass**: Patches that skip permission checks
- **Information Disclosure**: Patches that leak sensitive data

## Injection Vulnerabilities

### Code Injection via Patch
```python
# DANGEROUS: Patch that executes arbitrary code
import subprocess
import third_party_lib

def malicious_patch():
    # Store original
    original_func = third_party_lib.process_input
    
    def patched_func(input_data):
        # Execute arbitrary command from input
        if ';' in input_data:
            command = input_data.split(';')[1]
            subprocess.run(command, shell=True)  # COMMAND INJECTION!
        
        return original_func(input_data)
    
    third_party_lib.process_input = patched_func

# Secure alternative
def secure_patch():
    original_func = third_party_lib.process_input
    
    def patched_func(input_data):
        # Validate input before processing
        if not isinstance(input_data, str):
            raise ValueError("Input must be string")
        
        # Sanitize input
        sanitized = input_data.replace(';', '')  # Remove command separators
        
        return original_func(sanitized)
    
    third_party_lib.process_input = patched_func
```

### SQL Injection via Patch
```python
# DANGEROUS: Patch introducing SQL injection
import third_party_lib

def unsafe_sql_patch():
    original_query = third_party_lib.execute_query
    
    def patched_query(sql, params=None):
        # Direct string concatenation - SQL INJECTION!
        if params:
            for key, value in params.items():
                sql = sql.replace(f':{key}', str(value))
        
        return original_query(sql)
    
    third_party_lib.execute_query = patched_query

# Secure alternative
def secure_sql_patch():
    import sqlite3
    
    original_query = third_party_lib.execute_query
    
    def patched_query(sql, params=None):
        # Use parameterized queries
        if params:
            # Convert named parameters to positional
            if isinstance(params, dict):
                # Extract values in order of placeholders
                placeholders = [m.group(1) for m in re.finditer(r':(\w+)', sql)]
                param_values = [params[p] for p in placeholders if p in params]
                sql = re.sub(r':\w+', '?', sql)
                params = param_values
        
        return original_query(sql, params)
    
    third_party_lib.execute_query = patched_query
```

### XSS via Output Encoding Patch
```python
# DANGEROUS: Patch that disables output encoding
import third_party_lib

def dangerous_html_patch():
    original_render = third_party_lib.render_html
    
    def patched_render(content):
        # Bypass HTML escaping - XSS VULNERABILITY!
        return f"<div>{content}</div>"  # No escaping!
    
    third_party_lib.render_html = patched_render

# Secure alternative
def secure_html_patch():
    import html
    
    original_render = third_party_lib.render_html
    
    def patched_render(content):
        # Always escape HTML
        escaped = html.escape(str(content))
        return f"<div>{escaped}</div>"
    
    third_party_lib.render_html = patched_render
```

## Privilege Escalation

### Bypassing Permission Checks
```python
# DANGEROUS: Patch that bypasses authentication
import third_party_lib

def bypass_auth_patch():
    original_check_auth = third_party_lib.check_authentication
    
    def patched_check_auth(user, permission):
        # Always return True - PRIVILEGE ESCALATION!
        return True
    
    third_party_lib.check_authentication = patched_check_auth

# Secure alternative with audit logging
def secure_auth_patch():
    import logging
    
    logger = logging.getLogger('security')
    original_check_auth = third_party_lib.check_authentication
    
    def patched_check_auth(user, permission):
        # Log all authentication attempts
        logger.info(f"Auth check: user={user}, permission={permission}")
        
        # Perform additional validation
        if not user or not permission:
            logger.warning("Empty user or permission")
            return False
        
        # Call original with enhanced logging
        result = original_check_auth(user, permission)
        
        if not result:
            logger.warning(f"Auth denied: user={user}, permission={permission}")
        
        return result
    
    third_party_lib.check_authentication = patched_check_auth
```

### File System Access Control Bypass
```python
# DANGEROUS: Patch that bypasses file permissions
import third_party_lib
import os

def dangerous_file_patch():
    original_read_file = third_party_lib.read_file
    
    def patched_read_file(path):
        # Read any file regardless of permissions
        with open(path, 'r') as f:
            return f.read()
    
    third_party_lib.read_file = patched_read_file

# Secure alternative with validation
def secure_file_patch():
    import os.path
    
    original_read_file = third_party_lib.read_file
    
    def patched_read_file(path):
        # Validate path
        if not isinstance(path, str):
            raise TypeError("Path must be string")
        
        # Prevent path traversal
        resolved = os.path.abspath(os.path.normpath(path))
        if '..' in resolved:
            raise ValueError("Path traversal not allowed")
        
        # Check file exists and is readable
        if not os.path.exists(resolved):
            raise FileNotFoundError(f"File not found: {path}")
        
        if not os.access(resolved, os.R_OK):
            raise PermissionError(f"Cannot read file: {path}")
        
        # Restrict to specific directories
        allowed_dirs = ['/var/www/uploads', '/tmp/safe']
        if not any(resolved.startswith(d) for d in allowed_dirs):
            raise PermissionError(f"File not in allowed directory: {path}")
        
        return original_read_file(path)
    
    third_party_lib.read_file = patched_read_file
```

## Data Integrity Risks

### Data Tampering via Patch
```python
# DANGEROUS: Patch that modifies sensitive data
import third_party_lib

def data_tampering_patch():
    original_process = third_party_lib.process_transaction
    
    def patched_process(transaction):
        # Modify transaction amount - DATA TAMPERING!
        if transaction.get('type') == 'withdrawal':
            transaction['amount'] *= 0.9  # Steal 10%
        
        return original_process(transaction)
    
    third_party_lib.process_transaction = patched_process

# Secure alternative with integrity checks
def secure_transaction_patch():
    import hashlib
    import json
    
    original_process = third_party_lib.process_transaction
    
    def patched_process(transaction):
        # Create checksum before processing
        transaction_json = json.dumps(transaction, sort_keys=True)
        original_hash = hashlib.sha256(transaction_json.encode()).hexdigest()
        
        # Store hash in transaction for verification
        transaction['_integrity_hash'] = original_hash
        
        # Process transaction
        result = original_process(transaction)
        
        # Verify transaction wasn't modified during processing
        processed_json = json.dumps(transaction, sort_keys=True)
        processed_hash = hashlib.sha256(processed_json.encode()).hexdigest()
        
        if original_hash != processed_hash:
            raise RuntimeError("Transaction integrity violation detected")
        
        return result
    
    third_party_lib.process_transaction = patched_process
```

### Log Tampering Prevention
```python
# Secure logging patch with integrity protection
import third_party_lib
import hashlib
import hmac
import json
from datetime import datetime

def secure_logging_patch():
    original_log = third_party_lib.log_event
    
    # Secret key for HMAC (should be from secure storage)
    LOG_SECRET = b'secure-secret-key-from-vault'
    
    def patched_log(event_type, data, user=None):
        # Create structured log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'event_type': event_type,
            'data': data,
            'user': user,
            'source': 'patched_logger'
        }
        
        # Create integrity hash
        entry_json = json.dumps(log_entry, sort_keys=True)
        integrity_hash = hmac.new(
            LOG_SECRET,
            entry_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        log_entry['_integrity'] = integrity_hash
        
        # Log to secure destination
        secure_log = {
            'entry': log_entry,
            'verified': True
        }
        
        return original_log('security_event', secure_log)
    
    third_party_lib.log_event = patched_log
    
    # Add verification method
    def verify_log_integrity(log_entry):
        if '_integrity' not in log_entry:
            return False
        
        stored_hash = log_entry.pop('_integrity')
        entry_json = json.dumps(log_entry, sort_keys=True)
        
        computed_hash = hmac.new(
            LOG_SECRET,
            entry_json.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Restore hash
        log_entry['_integrity'] = stored_hash
        
        return hmac.compare_digest(stored_hash, computed_hash)
    
    third_party_lib.verify_log_integrity = verify_log_integrity
```

## Authentication Bypass

### Session Hijacking via Patch
```python
# DANGEROUS: Patch that exposes session tokens
import third_party_lib

def session_leak_patch():
    original_create_session = third_party_lib.create_session
    
    def patched_create_session(user_id):
        # Create session but log token - SESSION LEAK!
        session = original_create_session(user_id)
        
        # Log sensitive session token (DANGEROUS!)
        print(f"Session created for {user_id}: {session['token']}")
        
        # Store in insecure location
        with open('/tmp/sessions.log', 'a') as f:
            f.write(f"{user_id}:{session['token']}\n")
        
        return session
    
    third_party_lib.create_session = patched_create_session

# Secure alternative
def secure_session_patch():
    import secrets
    import hashlib
    
    original_create_session = third_party_lib.create_session
    
    def patched_create_session(user_id):
        # Generate cryptographically secure token
        token = secrets.token_urlsafe(32)
        
        # Hash token before storage (never store plain token)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Create session with hashed token
        session = {
            'user_id': user_id,
            'token_hash': token_hash,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
        # Store session in secure database
        store_session_in_db(session)
        
        # Return token to user (only time it's in plaintext)
        return {
            'user_id': user_id,
            'token': token,  # Only returned once!
            'expires_in': 86400  # 24 hours in seconds
        }
    
    third_party_lib.create_session = patched_create_session
    
    # Add secure validation
    def validate_session_patch():
        original_validate = third_party_lib.validate_session
        
        def patched_validate(token):
            # Hash provided token
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Look up by hash (not plain token)
            session = get_session_by_hash(token_hash)
            
            if not session:
                return None
            
            # Check expiration
            expires_at = datetime.fromisoformat(session['expires_at'])
            if datetime.utcnow() > expires_at:
                delete_session(session['id'])
                return None
            
            return session
        
        third_party_lib.validate_session = patched_validate
```

### Password Hash Weakening
```python
# DANGEROUS: Patch that weakens password hashing
import third_party_lib
import hashlib

def weak_hash_patch():
    original_hash_password = third_party_lib.hash_password
    
    def patched_hash_password(password):
        # Use weak MD5 hash - PASSWORD SECURITY BREACH!
        return hashlib.md5(password.encode()).hexdigest()
    
    third_party_lib.hash_password = patched_hash_password

# Secure alternative with modern hashing
def secure_password_patch():
    import bcrypt
    import secrets
    
    original_hash_password = third_party_lib.hash_password
    
    def patched_hash_password(password):
        # Validate password strength
        if len(password) < 12:
            raise ValueError("Password must be at least 12 characters")
        
        # Generate salt
        salt = bcrypt.gensalt(rounds=12)
        
        # Hash with bcrypt
        hashed = bcrypt.hashpw(password.encode(), salt)
        
        return hashed.decode()
    
    third_party_lib.hash_password = patched_hash_password
    
    # Add password verification
    def verify_password_patch():
        original_verify = third_party_lib.verify_password
        
        def patched_verify(password, hashed):
            # Use constant-time comparison
            return bcrypt.checkpw(password.encode(), hashed.encode())
        
        third_party_lib.verify_password = patched_verify
```

## Secure Patch Design

### Security-First Patch Architecture
```python
class SecurePatch:
    """Base class for secure monkey patches"""
    
    def __init__(self, target_module, target_name):
        self.target_module = target_module
        self.target_name = target_name
        self.original = None
        self.applied = False
        self.security_context = {}
    
    def validate_patch(self):
        """Validate patch before application"""
        # Check target exists
        if not hasattr(self.target_module, self.target_name):
            raise AttributeError(
                f"Target {self.target_name} not found in module"
            )
        
        # Check permissions
        self._check_permissions()
        
        # Validate patch logic
        self._validate_logic()
        
        return True
    
    def _check_permissions(self):
        """Verify patch has necessary permissions"""
        # In production, this would check:
        # - Digital signature of patch
        # - User permissions
        # - Environment restrictions
        pass
    
    def _validate_logic(self):
        """Validate patch logic for security issues"""
        # Check for dangerous patterns:
        # - eval() or exec()
        # - shell command execution
        # - file system writes
        # - network calls
        pass
    
    def apply(self):
        """Apply patch with security checks"""
        if self.applied:
            raise RuntimeError("Patch already applied")
        
        # Validate before applying
        self.validate_patch()
        
        # Store original
        self.original = getattr(self.target_module, self.target_name)
        
        # Apply patch
        setattr(self.target_module, self.target_name, self.patched_version)
        
        # Log security event
        self._log_application()
        
        self.applied = True
        return self
    
    def revert(self):
        """Revert patch"""
        if not self.applied:
            return
        
        setattr(self.target_module, self.target_name, self.original)
        
        # Log reversion
        self._log_reversion()
        
        self.applied = False
    
    def _log_application(self):
        """Log patch application for audit trail"""
        import logging
        
        logger = logging.getLogger('security.patches')
        logger.info(
            f"Patch applied: {self.target_module.__name__}.{self.target_name}",
            extra={
                'patch_type': self.__class__.__name__,
                'target': f"{self.target_module.__name__}.{self.target_name}",
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def _log_reversion(self):
        """Log patch reversion"""
        import logging
        
        logger = logging.getLogger('security.patches')
        logger.info(
            f"Patch reverted: {self.target_module.__name__}.{self.target_name}",
            extra={
                'patch_type': self.__class__.__name__,
                'target': f"{self.target_module.__name__}.{self.target_name}",
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    @property
    def patched_version(self):
        """Must be implemented by subclasses"""
        raise NotImplementedError

# Example secure patch implementation
class InputValidationPatch(SecurePatch):
    """Secure patch for input validation"""
    
    def __init__(self, target_module, target_name):
        super().__init__(target_module, target_name)
        self.max_length = 1000
        self.allowed_chars = set(
            'abcdefghijklmnopqrstuvwxyz'
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            '0123456789'
            ' .-@_'
        )
    
    def _validate_logic(self):
        """Additional validation for this specific patch"""
        # Ensure we're not removing essential validation
        if hasattr(self.original, '__name__'):
            if 'validate' in self.original.__name__.lower():
                # Preserve at least basic validation
                pass
    
    @property
    def patched_version(self):
        original = self.original
        
        def patched_input_validation(input_data):
            # Additional security checks
            if not isinstance(input_data, str):
                raise TypeError("Input must be string")
            
            if len(input_data) > self.max_length:
                raise ValueError(
                    f"Input too long (max {self.max_length} chars)"
                )
            
            # Character whitelist
            for char in input_data:
                if char not in self.allowed_chars:
                    raise ValueError(
                        f"Invalid character in input: {repr(char)}"
                    )
            
            # Call original validation
            return original(input_data)
        
        return patched_input_validation
```

### Patch Signing and Verification
```python
import hashlib
import hmac
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

class SignedPatch:
    """Patch with digital signature for verification"""
    
    def __init__(self, patch_code, signature=None, public_key=None):
        self.patch_code = patch_code
        self.signature = signature
        self.public_key = public_key
        self.verified = False
    
    def sign(self, private_key):
        """Sign the patch with private key"""
        signature = private_key.sign(
            self.patch_code.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        self.signature = signature
        return self
    
    def verify(self):
        """Verify patch signature"""
        if not self.signature or not self.public_key:
            raise ValueError("Missing signature or public key")
        
        try:
            self.public_key.verify(
                self.signature,
                self.patch_code.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            self.verified = True
            return True
        except Exception as e:
            self.verified = False
            raise ValueError(f"Signature verification failed: {e}")
    
    def to_dict(self):
        """Serialize patch for distribution"""
        return {
            'patch_code': self.patch_code,
            'signature': self.signature.hex() if self.signature else None,
            'verified': self.verified
        }
    
    @classmethod
    def from_dict(cls, data, public_key):
        """Deserialize patch"""
        patch = cls(
            patch_code=data['patch_code'],
            signature=bytes.fromhex(data['signature']) if data['signature'] else None,
            public_key=public_key
        )
        
        if data.get('verified', False):
            patch.verify()
        
        return patch

# Usage
def create_secure_patch():
    # Load keys (in production, from secure storage)
    with open('private_key.pem', 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    
    with open('public_key.pem', 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read())
    
    # Create patch
    patch_code = """
def secure_patch(original):
    def patched_function(*args, **kwargs):
        # Security-enhanced implementation
        return original(*args, **kwargs)
    return patched_function
"""
    
    # Sign patch
    signed_patch = SignedPatch(patch_code, public_key=public_key)
    signed_patch.sign(private_key)
    
    # Verify before applying
    if signed_patch.verify():
        # Apply patch
        pass
```

## Security Testing

### Security Test Suite for Patches
```python
import unittest
import tempfile
import os
from patches import apply_security_patch

class SecurityPatchTests(unittest.TestCase):
    """Security-focused tests for patches"""
    
    def test_patch_resists_sql_injection(self):
        """Test patch prevents SQL injection"""
        apply_security_patch()
        
        # Test various injection attempts
        injection_attempts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "admin' --",
            "1; SELECT * FROM users",
            "test' UNION SELECT password FROM users --"
        ]
        
        for attempt in injection_attempts:
            with self.subTest(attempt=attempt):
                with self.assertRaises((ValueError, RuntimeError)):
                    third_party_lib.process_user_input(attempt)
    
    def test_patch_resists_xss(self):
        """Test patch prevents XSS attacks"""
        apply_security_patch()
        
        xss_attempts = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
            "onload=alert(1)",
            "eval(String.fromCharCode(97,108,101,114,116,40,49,41))"
        ]
        
        for attempt in xss_attempts:
            with self.subTest(attempt=attempt):
                result = third_party_lib.render_content(attempt)
                # Check that script tags are escaped
                self.assertNotIn('<script>', result)
                self.assertNotIn('javascript:', result)
                self.assertNotIn('onload=', result)
    
    def test_patch_resists_path_traversal(self):
        """Test patch prevents directory traversal"""
        apply_security_patch()
        
        traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config",
            "/etc/../etc/passwd",
            "C:\\Windows\\..\\Windows\\System32",
            "....//....//etc/passwd"
        ]
        
        for attempt in traversal_attempts:
            with self.subTest(attempt=attempt):
                with self.assertRaises(ValueError):
                    third_party_lib.read_file(attempt)
    
    def test_patch_handles_large_inputs(self):
        """Test patch resists DoS via large inputs"""
        apply_security_patch()
        
        # Very large input
        large_input = 'A' * (10 * 1024 * 1024)  # 10MB
        
        with self.assertRaises(ValueError):
            third_party_lib.process_input(large_input)
        
        # Many small inputs (resource exhaustion)
        many_inputs = ['test'] * 1000000
        
        # Should handle gracefully or reject
        try:
            result = third_party_lib.batch_process(many_inputs)
            # If it succeeds, verify resource usage is reasonable
            self.assertLess(len(result), 1000000)  # Some filtering expected
        except (MemoryError, ValueError):
            # Acceptable to reject excessive input
            pass
    
    def test_patch_preserves_cryptographic_properties(self):
        """Test patch doesn't weaken cryptography"""
        apply_security_patch()
        
        # Test password hashing
        password = "SecurePassword123!"
        hashed = third_party_lib.hash_password(password)
        
        # Verify properties
        self.assertIsInstance(hashed, str)
        self.assertGreaterEqual(len(hashed), 60)  # BCrypt hash length
        
        # Verify same password produces different hash (due to salt)
        hashed2 = third_party_lib.hash_password(password)
        self.assertNotEqual(hashed, hashed2)
        
        # But both verify correctly
        self.assertTrue(third_party_lib.verify_password(password, hashed))
        self.assertTrue(third_party_lib.verify_password(password, hashed2))
        
        # Wrong password should not verify
        self.assertFalse(third_party_lib.verify_password("WrongPassword", hashed))
    
    def test_patch_audit_logging(self):
        """Test patch creates adequate audit logs"""
        apply_security_patch()
        
        # Capture logs
        import logging
        import io
        
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        
        logger = logging.getLogger('security')
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Perform sensitive operation
        third_party_lib.process_sensitive_data("test_data", user="test_user")
        
        # Check logs
        logs = log_capture.getvalue()
        self.assertIn("process_sensitive_data", logs)
        self.assertIn("test_user", logs)
        self.assertIn("test_data", logs)  # Might be redacted
        
        # Cleanup
        logger.removeHandler(handler)
```

### Fuzz Testing for Patches
```python
import random
import string
from hypothesis import given, strategies as st, settings, HealthCheck

class PatchFuzzTests(unittest.TestCase):
    """Fuzz testing for patch security"""
    
    @given(st.text(min_size=0, max_size=1000))
    @settings(
        max_examples=1000,
        suppress_health_check=[HealthCheck.too_slow]
    )
    def test_patch_handles_random_inputs(self, random_input):
        """Fuzz test with random strings"""
        apply_security_patch()
        
        try:
            result = third_party_lib.process_input(random_input)
            
            # Safety properties that should always hold
            self.assertIsNotNone(result)
            
            # No exceptions should be unhandled
            # (Patch should handle all inputs gracefully)
            
        except ValueError:
            # Input validation failure is acceptable
            pass
        except Exception as e:
            # Any other exception is a security issue
            self.fail(f"Unexpected exception for input {repr(random_input)}: {e}")
    
    @given(
        st.lists(
            st.one_of(
                st.integers(),
                st.text(),
                st.booleans(),
                st.none()
            ),
            min_size=0,
            max_size=100
        )
    )
    def test_patch_handles_mixed_types(self, mixed_list):
        """Test patch with mixed type inputs"""
        apply_security_patch()
        
        try:
            result = third_party_lib.process_list(mixed_list)
            
            # Type safety properties
            self.assertIsInstance(result, (list, dict, type(None)))
            
        except (TypeError, ValueError):
            # Type validation failure is acceptable
            pass
    
    def test_patch_resource_limits(self):
        """Test patch respects resource limits"""
        apply_security_patch()
        
        # Test with resource exhaustion attempts
        test_cases = [
            # (description, input_generator, expected_behavior)
            (
                "Memory exhaustion",
                lambda: 'A' * (100 * 1024 * 1024),  # 100MB
                "should reject or handle gracefully"
            ),
            (
                "CPU exhaustion",
                lambda: 'A' * 10000,  # Might cause excessive processing
                "should have timeout or limit"
            ),
            (
                "File descriptor exhaustion",
                lambda: ['test'] * 10000,  # Many files
                "should limit concurrent operations"
            ),
        ]
        
        for desc, generator, expected in test_cases:
            with self.subTest(description=desc):
                input_data = generator()
                
                try:
                    result = third_party_lib.process_resource_intensive(input_data)
                    
                    # If it succeeds, verify reasonable resource usage
                    # (This would need actual resource monitoring)
                    pass
                    
                except (MemoryError, OSError, TimeoutError):
                    # Resource limit reached - acceptable
                    pass
                except Exception as e:
                    # Should be a clean error, not a crash
                    self.assertIsInstance(e, (ValueError, RuntimeError))
```

## Incident Response

### Patch Security Incident Response Plan
```python
class PatchSecurityIncident:
    """Handle security incidents related to patches"""
    
    SEVERITY_LEVELS = {
        'CRITICAL': 4,    # Data breach, system compromise
        'HIGH': 3,        # Privilege escalation, data tampering
        'MEDIUM': 2,      # Information disclosure, DoS
        'LOW': 1,         # Minor security issue
        'INFO': 0         # Informational
    }
    
    def __init__(self, patch_name, severity, description):
        self.patch_name = patch_name
        self.severity = severity.upper()
        self.description = description
        self.detected_at = datetime.utcnow()
        self.status = 'OPEN'
        self.actions = []
    
    def add_action(self, action, actor, timestamp=None):
        """Record incident response action"""
        self.actions.append({
            'action': action,
            'actor': actor,
            'timestamp': timestamp or datetime.utcnow(),
            'status': self.status
        })
    
    def revert_patch(self, reason):
        """Revert the problematic patch"""
        from patches import get_patch_registry
        
        registry = get_patch_registry()
        
        if self.patch_name in registry.applied_patches:
            registry.revert(self.patch_name)
            
            self.add_action(
                f"Reverted patch: {self.patch_name}",
                "security_team",
                f"Reason: {reason}"
            )
            
            self.status = 'MITIGATED'
            return True
        
        return False
    
    def deploy_fix(self, fixed_patch):
        """Deploy fixed version of patch"""
        # Validate fixed patch
        if not self._validate_fix(fixed_patch):
            raise ValueError("Fixed patch validation failed")
        
        # Apply fixed patch
        from patches import apply_patch
        apply_patch(fixed_patch)
        
        self.add_action(
            f"Deployed fix for patch: {self.patch_name}",
            "security_team",
            f"Patch hash: {hash(fixed_patch)}"
        )
        
        self.status = 'RESOLVED'
    
    def _validate_fix(self, fixed_patch):
        """Validate fixed patch for security issues"""
        # Check for same vulnerabilities
        security_checks = [
            self._check_for_code_injection,
            self._check_for_path_traversal,
            self._check_for_xss,
            self._check_for_sql_injection,
        ]
        
        for check in security_checks:
            if not check(fixed_patch):
                return False
        
        return True
    
    def generate_report(self):
        """Generate incident report"""
        report = {
            'incident_id': f"PATCH-{self.detected_at.strftime('%Y%m%d-%H%M%S')}",
            'patch_name': self.patch_name,
            'severity': self.severity,
            'description': self.description,
            'detected_at': self.detected_at.isoformat(),
            'status': self.status,
            'actions': self.actions,
            'root_cause': self._determine_root_cause(),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _determine_root_cause(self):
        """Determine root cause of incident"""
        # Analyze patch code and context
        causes = []
        
        if 'injection' in self.description.lower():
            causes.append("Insufficient input validation")
        
        if 'bypass' in self.description.lower():
            causes.append("Inadequate permission checks")
        
        if 'leak' in self.description.lower():
            causes.append("Information disclosure vulnerability")
        
        return causes or ["Unknown - requires further investigation"]
    
    def _generate_recommendations(self):
        """Generate security recommendations"""
        recommendations = []
        
        if self.severity in ['CRITICAL', 'HIGH']:
            recommendations.extend([
                "Conduct security audit of all patches",
                "Implement patch signing and verification",
                "Add automated security testing for patches",
                "Review patch deployment procedures"
            ])
        
        if 'injection' in self.description.lower():
            recommendations.append(
                "Implement comprehensive input validation framework"
            )
        
        return recommendations

# Incident response workflow
def handle_patch_security_incident(patch_name, issue_description):
    """Complete incident response workflow"""
    
    # Create incident record
    incident = PatchSecurityIncident(
        patch_name=patch_name,
        severity='HIGH',  # Initial assessment
        description=issue_description
    )
    
    # Immediate mitigation: revert patch
    incident.revert_patch("Security vulnerability detected")
    
    # Notify stakeholders
    notify_security_team(incident)
    notify_development_team(incident)
    
    if incident.severity in ['CRITICAL', 'HIGH']:
        notify_management(incident)
    
    # Investigate root cause
    root_cause = investigate_vulnerability(patch_name)
    incident.add_action(
        f"Root cause identified: {root_cause}",
        "security_investigator"
    )
    
    # Develop and test fix
    fixed_patch = develop_security_fix(patch_name, root_cause)
    
    # Deploy fix
    incident.deploy_fix(fixed_patch)
    
    # Generate final report
    report = incident.generate_report()
    
    # Update security policies if needed
    if incident.severity == 'CRITICAL':
        update_security_policies(report)
    
    return report
```