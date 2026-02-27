const fs = require('fs');
const path = require('path');
const https = require('https');

const LOCAL_REGISTRY_PATH = path.join(__dirname, '..', '..', '..', 'skills-registry.json');
const REMOTE_REGISTRY_URL = 'https://raw.githubusercontent.com/sunchendd/good_skills/main/skills-registry.json';

/**
 * Fetch a URL and return its text content (with timeout)
 */
function fetchText(url, timeoutMs = 8000) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, (res) => {
      if (res.statusCode === 302 || res.statusCode === 301) {
        return fetchText(res.headers.location, timeoutMs).then(resolve).catch(reject);
      }
      if (res.statusCode !== 200) {
        return reject(new Error(`HTTP ${res.statusCode}: ${url}`));
      }
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => resolve(data));
    }).on('error', reject);

    req.setTimeout(timeoutMs, () => {
      req.destroy();
      reject(new Error(`Timeout fetching: ${url}`));
    });
  });
}

/**
 * Load registry from local file (for development) or remote GitHub
 */
async function loadRegistry(useRemote = false) {
  if (!useRemote && fs.existsSync(LOCAL_REGISTRY_PATH)) {
    const content = fs.readFileSync(LOCAL_REGISTRY_PATH, 'utf-8');
    return JSON.parse(content);
  }

  const content = await fetchText(REMOTE_REGISTRY_URL);
  return JSON.parse(content);
}

/**
 * Load manifest.json for a specific skill
 */
async function loadManifest(skillName, registryData) {
  const skill = registryData.skills[skillName];
  if (!skill) return null;

  const rawBase = registryData.rawBase || 'https://raw.githubusercontent.com/sunchendd/good_skills/main';
  const localManifestPath = path.join(__dirname, '..', '..', '..', skillName, 'manifest.json');

  if (fs.existsSync(localManifestPath)) {
    return JSON.parse(fs.readFileSync(localManifestPath, 'utf-8'));
  }

  try {
    const content = await fetchText(`${rawBase}/${skillName}/manifest.json`);
    return JSON.parse(content);
  } catch {
    // Fallback to registry data if no manifest.json yet
    return { name: skillName, version: skill.version, ...skill };
  }
}

/**
 * List all skills matching optional tag filter
 */
function filterSkills(registry, { tag, query } = {}) {
  const skills = Object.entries(registry.skills).map(([name, info]) => ({
    name,
    ...info,
  }));

  if (tag) {
    return skills.filter((s) => s.tags && s.tags.includes(tag));
  }

  if (query) {
    const q = query.toLowerCase();
    return skills.filter(
      (s) =>
        s.name.toLowerCase().includes(q) ||
        (s.description && s.description.toLowerCase().includes(q)) ||
        (s.tags && s.tags.some((t) => t.includes(q)))
    );
  }

  return skills;
}

module.exports = { loadRegistry, loadManifest, filterSkills, fetchText };
