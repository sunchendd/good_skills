const test = require('node:test');
const assert = require('node:assert/strict');

const { parseGitHubRepoInput, getCandidateRemoteSkillPaths } = require('./installer');

test('parseGitHubRepoInput supports full GitHub URLs', () => {
  assert.deepEqual(
    parseGitHubRepoInput('https://github.com/vercel-labs/skills'),
    {
      owner: 'vercel-labs',
      repo: 'skills',
      branch: 'main',
      rawBase: 'https://raw.githubusercontent.com/vercel-labs/skills/main',
    }
  );
});

test('parseGitHubRepoInput supports owner/repo shorthand', () => {
  assert.deepEqual(
    parseGitHubRepoInput('vercel-labs/skills'),
    {
      owner: 'vercel-labs',
      repo: 'skills',
      branch: 'main',
      rawBase: 'https://raw.githubusercontent.com/vercel-labs/skills/main',
    }
  );
});

test('parseGitHubRepoInput accepts explicit branch override', () => {
  assert.deepEqual(
    parseGitHubRepoInput('https://github.com/vercel-labs/skills', 'develop'),
    {
      owner: 'vercel-labs',
      repo: 'skills',
      branch: 'develop',
      rawBase: 'https://raw.githubusercontent.com/vercel-labs/skills/develop',
    }
  );
});

test('parseGitHubRepoInput rejects invalid repo inputs', () => {
  assert.throws(
    () => parseGitHubRepoInput('https://example.com/vercel-labs/skills'),
    /GitHub repository/
  );
});

test('getCandidateRemoteSkillPaths includes common skills.sh layouts', () => {
  assert.deepEqual(
    getCandidateRemoteSkillPaths('find-skills').slice(0, 4),
    [
      'find-skills',
      'skills/find-skills',
      '.skills/find-skills',
      '.skills/registry/find-skills',
    ]
  );
});
