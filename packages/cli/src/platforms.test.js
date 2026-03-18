const test = require('node:test');
const assert = require('node:assert/strict');
const os = require('os');
const path = require('path');

const { resolvePaths } = require('./platforms');

test('resolvePaths supports codex global installs', () => {
  assert.deepEqual(resolvePaths('codex'), [
    {
      name: 'codex',
      path: path.join(os.homedir(), '.codex', 'skills'),
    },
  ]);
});

test('resolvePaths supports codex project installs', () => {
  assert.deepEqual(resolvePaths('codex', true), [
    {
      name: 'codex',
      path: path.join('.codex', 'skills'),
    },
  ]);
});
