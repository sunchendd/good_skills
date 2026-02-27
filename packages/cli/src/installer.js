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
  if (fs.existsSync(dest) || fs.lstatSync(dest).isSymbolicLink().catch(() => false)) {
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
 * Get files to install for a skill from remote GitHub
 */
async function getSkillFilesRemote(rawBase, skillName) {
  // Try fetching SKILL.md first to confirm skill exists
  const skillMdUrl = `${rawBase}/${skillName}/SKILL.md`;
  const content = await fetchText(skillMdUrl);
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
 * @param {Object} options - { useSymlink, thirdParty, rawBase }
 */
async function installSkill(skillName, targetDir, options = {}) {
  const skillTargetPath = path.join(targetDir, skillName);
  const { useSymlink = false, thirdParty = false, rawBase = REPO_RAW_BASE } = options;

  if (thirdParty) {
    // Download SKILL.md from remote
    const files = await getSkillFilesRemote(rawBase, skillName);
    mkdirp(skillTargetPath);
    for (const file of files) {
      fs.writeFileSync(path.join(skillTargetPath, file.name), file.content, 'utf-8');
    }
    // Try to download manifest.json too
    try {
      const manifestContent = await fetchText(`${rawBase}/${skillName}/manifest.json`);
      fs.writeFileSync(path.join(skillTargetPath, 'manifest.json'), manifestContent, 'utf-8');
    } catch {
      // manifest.json optional for third-party skills
    }
    return;
  }

  const localSkillDir = getLocalSkillDir(skillName);

  if (!fs.existsSync(localSkillDir)) {
    // Skill not local, download from remote
    const files = await getSkillFilesRemote(rawBase, skillName);
    mkdirp(skillTargetPath);
    for (const file of files) {
      fs.writeFileSync(path.join(skillTargetPath, file.name), file.content, 'utf-8');
    }
    return;
  }

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
};
