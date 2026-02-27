const fs = require('fs');
const path = require('path');
const { loadRegistry } = require('../registry');
const { resolvePaths } = require('../platforms');
const { getInstalledManifest } = require('../installer');

async function statusCommand(options) {
  const { platform = 'all' } = options;

  let registry;
  try {
    registry = await loadRegistry();
  } catch (err) {
    console.error('❌ Failed to load registry:', err.message);
    process.exit(1);
  }

  const platformPaths = resolvePaths(platform);
  const allSkills = Object.keys(registry.skills);

  console.log('\n📦 Good Skills Status\n');
  console.log(`${'Skill'.padEnd(38)} ${'Installed'.padEnd(10)} ${'Version'.padEnd(10)} Platforms`);
  console.log('─'.repeat(80));

  for (const skillName of allSkills.sort()) {
    const registryInfo = registry.skills[skillName];
    const installedPlatforms = [];

    for (const { name: platformName, path: platformPath } of platformPaths) {
      const skillPath = path.join(platformPath, skillName);
      if (fs.existsSync(path.join(skillPath, 'SKILL.md'))) {
        installedPlatforms.push(platformName);
      }
    }

    if (installedPlatforms.length === 0) continue; // Skip not-installed

    // Check version from first found platform
    let installedVersion = '?';
    for (const { path: platformPath } of platformPaths) {
      const manifest = getInstalledManifest(skillName, platformPath);
      if (manifest) {
        installedVersion = manifest.version;
        break;
      }
    }

    const latestVersion = registryInfo.version;
    const hasUpdate = installedVersion !== '?' && installedVersion !== latestVersion;
    const versionStr = hasUpdate ? `${installedVersion} → ${latestVersion}` : installedVersion;
    const icon = hasUpdate ? '⚠️ ' : '✅ ';

    console.log(
      `${icon}${skillName.padEnd(36)} ${'yes'.padEnd(10)} ${versionStr.padEnd(18)} ${installedPlatforms.join(', ')}`
    );
  }

  console.log('');
}

module.exports = { statusCommand };
