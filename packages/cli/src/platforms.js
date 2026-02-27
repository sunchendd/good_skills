const os = require('os');
const path = require('path');

const HOME = os.homedir();

// Platform path configurations
const PLATFORMS = {
  claude: {
    global: path.join(HOME, '.claude', 'skills'),
    project: path.join('.claude', 'skills'),
  },
  'github-copilot': {
    global: path.join(HOME, '.copilot', 'skills'),
    project: path.join('.github', 'skills'),
  },
  opencode: {
    global: path.join(HOME, '.config', 'opencode', 'skill'),
    project: path.join('.opencode', 'skill'),
  },
  openclaw: {
    global: path.join(HOME, '.openclaw', 'skills'),
    project: path.join('.openclaw', 'skills'),
  },
  cursor: {
    global: path.join(HOME, '.cursor', 'skills'),
    project: path.join('.cursor', 'skills'),
  },
  windsurf: {
    global: path.join(HOME, '.codeium', 'windsurf', 'skills'),
    project: path.join('.windsurf', 'skills'),
  },
  antigravity: {
    global: path.join(HOME, '.agent', 'skills'),
    project: path.join('.agent', 'skills'),
  },
};

/**
 * Resolve install paths for a given platform option
 * @param {string} platform - 'all' or specific platform name
 * @param {boolean} isProject - use project-level paths
 * @returns {Array<{name: string, path: string}>}
 */
function resolvePaths(platform, isProject = false) {
  const pathKey = isProject ? 'project' : 'global';

  if (platform === 'all') {
    return Object.entries(PLATFORMS).map(([name, paths]) => ({
      name,
      path: paths[pathKey],
    }));
  }

  if (!PLATFORMS[platform]) {
    throw new Error(`Unknown platform: "${platform}". Available: ${Object.keys(PLATFORMS).join(', ')}, all`);
  }

  return [{ name: platform, path: PLATFORMS[platform][pathKey] }];
}

/**
 * Get all platform names
 */
function getPlatformNames() {
  return Object.keys(PLATFORMS);
}

module.exports = { PLATFORMS, resolvePaths, getPlatformNames };
