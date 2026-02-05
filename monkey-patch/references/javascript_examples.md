# JavaScript/TypeScript Monkey Patch Examples

## Table of Contents
1. [Basic JavaScript Patterns](#basic-javascript-patterns)
2. [TypeScript-Specific Techniques](#typescript-specific-techniques)
3. [Framework-Specific Patterns](#framework-specific-patterns)
4. [Node.js Module Patching](#nodejs-module-patching)
5. [Browser Environment Patching](#browser-environment-patching)
6. [Testing and Mocking](#testing-and-mocking)

## Basic JavaScript Patterns

### Function Patching
```javascript
// Store original function
const originalFetch = window.fetch;

// Create patched version
window.fetch = function patchedFetch(url, options) {
  console.log(`Fetching: ${url}`);
  
  // Add custom headers
  const modifiedOptions = {
    ...options,
    headers: {
      ...options?.headers,
      'X-Custom-Header': 'monkey-patch'
    }
  };
  
  // Call original function
  return originalFetch.call(this, url, modifiedOptions);
};

// Usage remains the same
fetch('https://api.example.com/data')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Method Patching on Prototypes
```javascript
// Patch Array.prototype.map
const originalMap = Array.prototype.map;

Array.prototype.map = function patchedMap(callback, thisArg) {
  console.log(`Mapping array of length: ${this.length}`);
  
  // Call original map
  const result = originalMap.call(this, callback, thisArg);
  
  console.log(`Result length: ${result.length}`);
  return result;
};

// Usage
const numbers = [1, 2, 3];
const doubled = numbers.map(n => n * 2);
// Logs: Mapping array of length: 3
// Logs: Result length: 3
```

### Property Patching with Descriptors
```javascript
// Patch Date.prototype to add custom property
Object.defineProperty(Date.prototype, 'isWeekend', {
  get: function() {
    const day = this.getDay();
    return day === 0 || day === 6; // Sunday or Saturday
  },
  enumerable: false, // Don't show in for...in loops
  configurable: true // Allow redefinition
});

// Usage
const today = new Date();
console.log(today.isWeekend); // true/false based on day
```

## TypeScript-Specific Techniques

### Type-Safe Patching with Declaration Merging
```typescript
// types/patches.d.ts - Declaration file
declare global {
  interface Array<T> {
    /**
     * Custom method added via monkey patch
     */
    customMap<U>(callback: (value: T, index: number, array: T[]) => U): U[];
    
    /**
     * Check if all elements satisfy condition
     */
    all(predicate: (value: T, index: number, array: T[]) => boolean): boolean;
  }
  
  interface Date {
    /**
     * Check if date is weekend
     */
    isWeekend: boolean;
    
    /**
     * Add days to date
     */
    addDays(days: number): Date;
  }
}

// Implementation file
export function applyTypeSafePatches() {
  // Array.prototype.customMap
  if (!Array.prototype.customMap) {
    Array.prototype.customMap = function<T, U>(
      this: T[],
      callback: (value: T, index: number, array: T[]) => U
    ): U[] {
      const result: U[] = [];
      for (let i = 0; i < this.length; i++) {
        result.push(callback(this[i], i, this));
      }
      return result;
    };
  }
  
  // Array.prototype.all
  if (!Array.prototype.all) {
    Array.prototype.all = function<T>(
      this: T[],
      predicate: (value: T, index: number, array: T[]) => boolean
    ): boolean {
      for (let i = 0; i < this.length; i++) {
        if (!predicate(this[i], i, this)) {
          return false;
        }
      }
      return true;
    };
  }
  
  // Date.prototype.addDays
  if (!Date.prototype.addDays) {
    Date.prototype.addDays = function(days: number): Date {
      const date = new Date(this);
      date.setDate(date.getDate() + days);
      return date;
    };
  }
}

// Usage
applyTypeSafePatches();

const numbers = [1, 2, 3, 4, 5];
const allPositive = numbers.all(n => n > 0); // true
const doubled = numbers.customMap(n => n * 2); // [2, 4, 6, 8, 10]

const today = new Date();
const nextWeek = today.addDays(7);
```

### Generic Patch Function with Type Safety
```typescript
type PatchTarget<T> = T & Record<string, any>;

function monkeyPatch<T, K extends keyof T>(
  target: PatchTarget<T>,
  methodName: K,
  implementation: T[K]
): void {
  // Store original if it exists
  const original = target[methodName];
  
  // Apply patch
  target[methodName] = implementation;
  
  // Add restore method
  if (original && typeof original === 'function') {
    (target as any)[`restore_${String(methodName)}`] = () => {
      target[methodName] = original;
    };
  }
}

// Usage with interface
interface MathUtils {
  sum: (a: number, b: number) => number;
  multiply: (a: number, b: number) => number;
}

const mathUtils: MathUtils = {
  sum: (a, b) => a + b,
  multiply: (a, b) => a * b
};

// Patch sum method
monkeyPatch(mathUtils, 'sum', function(a: number, b: number): number {
  console.log(`Summing ${a} + ${b}`);
  return a + b + 1; // Add 1 for demonstration
});

console.log(mathUtils.sum(2, 3)); // Logs: Summing 2 + 3, Returns: 6
```

## Framework-Specific Patterns

### React Component Patching
```javascript
import React from 'react';

// Patch React.createElement to log component creation
const originalCreateElement = React.createElement;

React.createElement = function patchedCreateElement(type, props, ...children) {
  // Log component type
  const componentName = typeof type === 'string' 
    ? type 
    : type?.displayName || type?.name || 'Unknown';
  
  console.log(`Creating component: ${componentName}`);
  
  // Call original
  return originalCreateElement.call(this, type, props, ...children);
};

// Usage in component
function MyComponent() {
  return <div>Hello World</div>;
  // Logs: Creating component: div
  // Logs: Creating component: MyComponent
}
```

### Vue.js Plugin Patching
```javascript
import Vue from 'vue';

// Patch Vue.mixin to add logging
const originalMixin = Vue.mixin;

Vue.mixin = function patchedMixin(mixin) {
  console.log('Applying mixin:', mixin);
  
  // Add created hook if not present
  if (mixin.created) {
    const originalCreated = mixin.created;
    mixin.created = function() {
      console.log('Component created with mixin');
      return originalCreated.call(this);
    };
  } else {
    mixin.created = function() {
      console.log('Component created with mixin');
    };
  }
  
  return originalMixin.call(this, mixin);
};

// Usage
Vue.mixin({
  methods: {
    logMessage(message) {
      console.log(message);
    }
  }
});
```

### Angular Service Patching
```typescript
import { Injectable } from '@angular/core';

// Patch HttpClient to add logging
@Injectable({ providedIn: 'root' })
export class PatchedHttpClient {
  constructor(private http: HttpClient) {
    this.patchHttpMethods();
  }
  
  private patchHttpMethods() {
    const methods = ['get', 'post', 'put', 'delete', 'patch'];
    
    methods.forEach(method => {
      const original = this.http[method];
      
      this.http[method] = function patchedMethod(...args: any[]) {
        console.log(`HTTP ${method.toUpperCase()} request:`, args[0]);
        
        // Add authentication header
        const [url, ...restArgs] = args;
        const options = restArgs[0] || {};
        options.headers = new HttpHeaders({
          ...options.headers,
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        });
        
        return original.call(this, url, options);
      };
    });
  }
  
  // Proxy all methods
  get(url: string, options?: any): Observable<any> {
    return this.http.get(url, options);
  }
  
  post(url: string, body: any, options?: any): Observable<any> {
    return this.http.post(url, body, options);
  }
  
  // ... other methods
}
```

## Node.js Module Patching

### Module Interception with require.cache
```javascript
// intercept-requires.js
const Module = require('module');
const originalRequire = Module.prototype.require;

Module.prototype.require = function patchedRequire(id) {
  console.log(`Requiring module: ${id}`);
  
  // Intercept specific modules
  if (id === 'axios') {
    // Return mocked axios
    return createMockAxios();
  }
  
  // Call original require
  return originalRequire.call(this, id);
};

function createMockAxios() {
  return {
    get: async (url) => {
      console.log(`Mock axios GET: ${url}`);
      return { data: { mocked: true } };
    },
    post: async (url, data) => {
      console.log(`Mock axios POST: ${url}`);
      return { data: { success: true } };
    }
  };
}

// Later in your code
const axios = require('axios'); // Returns mocked version
```

### Patching Core Modules
```javascript
// Patch fs.readFile to add caching
const fs = require('fs');
const originalReadFile = fs.readFile;
const fileCache = new Map();

fs.readFile = function patchedReadFile(path, options, callback) {
  // Handle callback vs promise style
  if (typeof options === 'function') {
    callback = options;
    options = null;
  }
  
  // Check cache
  if (fileCache.has(path)) {
    console.log(`Cache hit for: ${path}`);
    const cached = fileCache.get(path);
    
    if (callback) {
      process.nextTick(() => callback(null, cached));
      return;
    } else {
      return Promise.resolve(cached);
    }
  }
  
  // Call original
  const result = originalReadFile.call(this, path, options, (err, data) => {
    if (!err && data) {
      fileCache.set(path, data);
    }
    
    if (callback) {
      callback(err, data);
    }
  });
  
  if (!callback) {
    return result.then(data => {
      if (data) fileCache.set(path, data);
      return data;
    });
  }
  
  return result;
};

// Usage
fs.readFile('package.json', 'utf8', (err, data) => {
  console.log('First read - from disk');
  fs.readFile('package.json', 'utf8', (err, data) => {
    console.log('Second read - from cache');
  });
});
```

## Browser Environment Patching

### XMLHttpRequest Patching
```javascript
// Patch XMLHttpRequest for all requests
const OriginalXHR = window.XMLHttpRequest;

class PatchedXHR extends OriginalXHR {
  open(method, url, async = true, user, password) {
    console.log(`XHR ${method}: ${url}`);
    
    // Add custom header
    this.setRequestHeader('X-Monkey-Patch', 'true');
    
    // Call original
    return super.open(method, url, async, user, password);
  }
  
  send(body) {
    // Measure request time
    const startTime = performance.now();
    
    this.addEventListener('load', () => {
      const duration = performance.now() - startTime;
      console.log(`Request completed in ${duration.toFixed(2)}ms`);
    });
    
    return super.send(body);
  }
}

// Replace global XMLHttpRequest
window.XMLHttpRequest = PatchedXHR;

// All XHR requests will now be logged
```

### Fetch API Patching with Request/Response Interception
```javascript
// Comprehensive fetch patching
const originalFetch = window.fetch;

window.fetch = async function patchedFetch(input, init = {}) {
  const request = new Request(input, init);
  const url = request.url;
  const method = request.method;
  
  // Request interceptor
  console.log(`[Fetch] ${method} ${url}`);
  
  // Add custom headers
  const modifiedInit = {
    ...init,
    headers: {
      ...init.headers,
      'X-Request-ID': generateRequestId(),
      'X-Timestamp': Date.now()
    }
  };
  
  try {
    // Call original fetch
    const response = await originalFetch.call(this, input, modifiedInit);
    
    // Response interceptor
    console.log(`[Fetch] ${method} ${url} - ${response.status}`);
    
    // Clone response to read body without consuming it
    const clonedResponse = response.clone();
    
    // Log response for debugging (optional)
    if (process.env.NODE_ENV === 'development') {
      const text = await clonedResponse.text();
      console.log(`[Fetch Response] ${text.substring(0, 200)}...`);
      
      // Return new response with same body
      return new Response(text, response);
    }
    
    return response;
  } catch (error) {
    console.error(`[Fetch Error] ${method} ${url}:`, error);
    throw error;
  }
};

function generateRequestId() {
  return 'req_' + Math.random().toString(36).substr(2, 9);
}
```

### Console Patching for Log Management
```javascript
// Patch console methods for log aggregation
const originalConsole = { ...console };
const logBuffer = [];

['log', 'warn', 'error', 'info'].forEach(method => {
  console[method] = function patchedConsole(...args) {
    // Store in buffer
    logBuffer.push({
      timestamp: new Date().toISOString(),
      level: method,
      args: args.map(arg => 
        typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
      )
    });
    
    // Keep buffer size manageable
    if (logBuffer.length > 1000) {
      logBuffer.shift();
    }
    
    // Call original
    originalConsole[method].apply(console, args);
  };
});

// Add method to get logs
console.getLogs = function(limit = 100) {
  return logBuffer.slice(-limit);
};

console.clearLogs = function() {
  logBuffer.length = 0;
};

// Usage
console.log('Test message');
console.warn('Warning message');
console.error('Error message');

const recentLogs = console.getLogs();
console.log('Recent logs:', recentLogs);
```

## Testing and Mocking

### Jest Mock Patching
```javascript
// Manual mocking without jest.mock()
const originalDateNow = Date.now;

beforeAll(() => {
  // Patch Date.now for all tests
  Date.now = jest.fn(() => 1625097600000); // Fixed timestamp
});

afterAll(() => {
  // Restore original
  Date.now = originalDateNow;
});

test('uses mocked Date.now', () => {
  expect(Date.now()).toBe(1625097600000);
});
```

### Sinon.js Integration
```javascript
import sinon from 'sinon';

// Patch and stub method
function patchWithSinon(target, methodName, stubImplementation) {
  const original = target[methodName];
  const stub = sinon.stub(target, methodName);
  
  if (stubImplementation) {
    stub.callsFake(stubImplementation);
  }
  
  return {
    stub,
    restore: () => {
      target[methodName] = original;
    }
  };
}

// Usage
const math = {
  add: (a, b) => a + b,
  multiply: (a, b) => a * b
};

const patch = patchWithSinon(math, 'add', (a, b) => a + b + 1);

console.log(math.add(2, 3)); // 6 (2 + 3 + 1)

patch.restore();
console.log(math.add(2, 3)); // 5 (original)
```

### Comprehensive Testing Utility
```javascript
class MonkeyPatchTester {
  constructor() {
    this.patches = new Map();
  }
  
  patch(target, property, implementation) {
    // Store original
    const original = target[property];
    this.patches.set(`${target.constructor.name}.${property}`, {
      target,
      property,
      original
    });
    
    // Apply patch
    target[property] = implementation;
    
    return {
      restore: () => this.restore(target, property)
    };
  }
  
  restore(target, property) {
    const key = `${target.constructor.name}.${property}`;
    const patch = this.patches.get(key);
    
    if (patch) {
      target[property] = patch.original;
      this.patches.delete(key);
    }
  }
  
  restoreAll() {
    for (const [key, patch] of this.patches) {
      patch.target[patch.property] = patch.original;
    }
    this.patches.clear();
  }
  
  getActivePatches() {
    return Array.from(this.patches.keys());
  }
}

// Usage in tests
describe('MonkeyPatchTester', () => {
  const tester = new MonkeyPatchTester();
  
  afterEach(() => {
    tester.restoreAll();
  });
  
  test('patches Math.random', () => {
    const patch = tester.patch(Math, 'random', () => 0.5);
    
    expect(Math.random()).toBe(0.5);
    expect(tester.getActivePatches()).toContain('Math.random');
    
    patch.restore();
    expect(Math.random()).not.toBe(0.5);
  });
});
```

### Async/Await Patching for Testing
```javascript
// Patch setTimeout for testing async code
const originalSetTimeout = global.setTimeout;

global.setTimeout = function patchedSetTimeout(callback, delay, ...args) {
  // In test environment, execute immediately
  if (process.env.NODE_ENV === 'test') {
    return originalSetTimeout(() => {
      callback(...args);
    }, 0);
  }
  
  // In production, use normal behavior
  return originalSetTimeout(callback, delay, ...args);
};

// Patch Promise for testing
const originalPromise = global.Promise;

global.Promise = class PatchedPromise extends originalPromise {
  static resolve(value) {
    // Add logging for test debugging
    if (process.env.NODE_ENV === 'test') {
      console.log('Promise.resolve called with:', value);
    }
    return super.resolve(value);
  }
  
  static reject(reason) {
    if (process.env.NODE_ENV === 'test') {
      console.log('Promise.reject called with:', reason);
    }
    return super.reject(reason);
  }
};

// Usage in tests
async function testAsyncFunction() {
  await new Promise(resolve => setTimeout(resolve, 1000));
  return 'done';
}

// In test environment, this will execute immediately
test('async function', async () => {
  const result = await testAsyncFunction();
  expect(result).toBe('done');
});
```