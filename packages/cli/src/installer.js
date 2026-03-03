const fs = require('fs');
const path = require('path');
const https = require('https');
const { fetchText } = require('./registry');

const REPO_RAW_BASE = 'https://raw.githubusercontent.com/sunchendd/good_skills/main';

/**
 * Recursively create directories
 */
function mkdirp(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

/**
 * Download a file from URL to local path
 */
async function downloadFile(url, destPath) {
  const content = await fetchText(url);
  mkdirp(path.dirname(destPath));
  fs.writeFileSync(destPath, content, 'utf-8');
}

/**
 * Copy directory recursively (for local installs)
 */
function copyDirRecursive(src, dest) {
  if (!fs.existsSync(src)) return;
  mkdirp(dest);
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue;
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDirRecursive(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

/**
 * Create a symbolic link (preferred for local development)
 */
function createSymlink(src, dest) {
  mkdirp(path.dirname(dest));
  // Use lstatSync to check for symlink (sync, doesn't throw for symlinks)
  let exists = false;
  try { fs.lstatSync(dest); exists = true; } catch { /* not found */ }
  if (exists) {
    fs.rmSync(dest, { recursive: true, force: true });
  }
  fs.symlinkSync(src, dest);
}

/**
 * Parse third-party skill reference: "owner/repo@skill-name"
 * Returns { owner, repo, skill, rawBase }
 */
function parseThirdPartyRef(ref) {
  const atIdx = ref.lastIndexOf('@');
  if (atIdx === -1) throw new Error(`Invalid skill reference: "${ref}". Use format: owner/repo@skill-name`);
  const repoPath = ref.substring(0, atIdx);
  const skill = ref.substring(atIdx + 1);
  const parts = repoPath.split('/');
  if (parts.length !== 2) throw new Error(`Invalid repo path: "${repoPath}". Use format: owner/repo`);
  const [owner, repo] = parts;
  return {
    owner,
    repo,
    skill,
    rawBase: `https://raw.githubusercontent.com/${owner}/${repo}/main`,
  };
}

/**
 * Fetch text with exponential backoff retry
 */
async function fetchWithRetry(url, retries = 3, delayMs = 800) {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetchText(url);
    } catch (e) {
      if (i === retries - 1) throw e;
      await new Promise((r) => setTimeout(r, delayMs * (i + 1)));
    }
  }
}

/**
 * List skill files via GitHub Contents API (returns [{name, download_url, type, path}])
 * Falls back to just SKILL.md if API fails.
 */
async function listSkillFilesRemote(owner, repo, skillName, branch = 'main') {
  const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contents/${skillName}?ref=${branch}`;
  try {
    const data = await fetchWithRetry(apiUrl);
    return JSON.parse(data);
  } catch {
    return null;
  }
}

/**
 * Download all files in a skill directory from remote GitHub (recursive for subdirs)
 * @param {string} rawBase - e.g. https://raw.githubusercontent.com/owner/repo/main
 * @param {string} skillName
 * @param {string} skillTargetPath - local dir to write to
 * @param {string} [subPath=''] - relative subpath within skill dir (for recursion)
 * @param {object} [ghInfo] - { owner, repo, branch } for Contents API listing
 */
async function downloadSkillDir(rawBase, skillName, skillTargetPath, subPath = '', ghInfo = null) {
  const dirPath = subPath ? `${skillName}/${subPath}` : skillName;

  let entries = null;
  if (ghInfo) {
    try {
      const apiUrl = `https://api.github.com/repos/${ghInfo.owner}/${ghInfo.repo}/contents/${dirPath}?ref=${ghInfo.branch}`;
      const data = await fetchWithRetry(apiUrl);
      entries = JSON.parse(data);
    } catch { /* fall through */ }
  }

  if (entries && Array.isArray(entries)) {
    // Use Contents API listing: download each file
    for (const entry of entries) {
      if (entry.name.startsWith('.')) continue;
      const localPath = subPath ? path.join(skillTargetPath, subPath, entry.name) : path.join(skillTargetPath, entry.name);
      if (entry.type === 'dir') {
        mkdirp(localPath);
        const nextSub = subPath ? `${subPath}/${entry.name}` : entry.name;
        await downloadSkillDir(rawBase, skillName, skillTargetPath, nextSub, ghInfo);
      } else if (entry.type === 'file') {
        const fileUrl = entry.download_url || `${rawBase}/${dirPath}/${entry.name}`;
        const content = await fetchWithRetry(fileUrl);
        mkdirp(path.dirname(localPath));
        fs.writeFileSync(localPath, content, 'utf-8');
      }
    }
  } else {
    // Fallback: download known files — SKILL.md is required
    const skillMdContent = await fetchWithRetry(`${rawBase}/${skillName}/SKILL.md`);
    fs.writeFileSync(path.join(skillTargetPath, 'SKILL.md'), skillMdContent, 'utf-8');
    // manifest.json is optional
    try {
      const manifestContent = await fetchWithRetry(`${rawBase}/${skillName}/manifest.json`);
      fs.writeFileSync(path.join(skillTargetPath, 'manifest.json'), manifestContent, 'utf-8');
    } catch { /* optional */ }
  }
}

/**
 * Extract GitHub owner/repo from a rawBase URL
 */
function parseRawBase(rawBase) {
  const m = rawBase.match(/raw\.githubusercontent\.com\/([^/]+)\/([^/]+)\/([^/]+)/);
  if (!m) return null;
  return { owner: m[1], repo: m[2], branch: m[3] };
}

/**
 * Get files to install for a skill from remote GitHub
 */
async function getSkillFilesRemote(rawBase, skillName) {
  // Legacy: just confirm SKILL.md exists and return content
  const skillMdUrl = `${rawBase}/${skillName}/SKILL.md`;
  const content = await fetchWithRetry(skillMdUrl);
  return [{ url: skillMdUrl, name: 'SKILL.md', content }];
}

/**
 * Get local skill directory path
 */
function getLocalSkillDir(skillName) {
  // CLI is at packages/cli/, so skills are 2 levels up
  return path.join(__dirname, '..', '..', '..', skillName);
}

/**
 * Install a skill to a target directory
 * @param {string} skillName
 * @param {string} targetDir - full path to install into
 * @param {Object} options - { useSymlink, thirdParty, rawBase, onProgress }
 */
async function installSkill(skillName, targetDir, options = {}) {
  const skillTargetPath = path.join(targetDir, skillName);
  const { useSymlink = false, thirdParty = false, rawBase = REPO_RAW_BASE, onProgress } = options;

  const ghInfo = parseRawBase(rawBase);

  if (thirdParty || !fs.existsSync(getLocalSkillDir(skillName))) {
    // Download from remote using GitHub Contents API
    onProgress && onProgress('Downloading skill files...');
    mkdirp(skillTargetPath);
    await downloadSkillDir(rawBase, skillName, skillTargetPath, '', ghInfo);
    // Validate SKILL.md was successfully downloaded
    if (!fs.existsSync(path.join(skillTargetPath, 'SKILL.md'))) {
      fs.rmSync(skillTargetPath, { recursive: true, force: true });
      throw new Error(`Skill "${skillName}" not found in registry. Run: npx good-skills list`);
    }
    return;
  }

  const localSkillDir = getLocalSkillDir(skillName);

  if (useSymlink) {
    // Symlink for local dev — remove existing first
    if (fs.existsSync(skillTargetPath)) {
      fs.rmSync(skillTargetPath, { recursive: true, force: true });
    }
    fs.symlinkSync(path.resolve(localSkillDir), skillTargetPath);
  } else {
    copyDirRecursive(localSkillDir, skillTargetPath);
  }
}

/**
 * Read installed manifest from target dir
 */
function getInstalledManifest(skillName, targetDir) {
  const manifestPath = path.join(targetDir, skillName, 'manifest.json');
  if (!fs.existsSync(manifestPath)) return null;
  try {
    return JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
  } catch {
    return null;
  }
}

/**
 * Check if a skill is installed in any platform dir
 */
function isInstalled(skillName, platformPaths) {
  return platformPaths.some((p) => fs.existsSync(path.join(p, skillName, 'SKILL.md')));
}

module.exports = {
  installSkill,
  getInstalledManifest,
  isInstalled,
  parseThirdPartyRef,
  mkdirp,
  copyDirRecursive,
  fetchWithRetry,
};
