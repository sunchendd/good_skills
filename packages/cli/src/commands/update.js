const fs = require('fs');
const path = require('path');
const { loadRegistry } = require('../registry');
const { resolvePaths } = require('../platforms');
const { installSkill, getInstalledManifest } = require('../installer');

async function updateCommand(skill, options) {
  const { all, check } = options;

  let registry;
  try {
    registry = await loadRegistry(true); // fetch remote for latest versions
  } catch (err) {
    console.error('❌ Failed to load registry:', err.message);
    process.exit(1);
  }

  const platformPaths = resolvePaths('all');

  // Find skills that are installed across any platform
  const installedSkills = [];

  for (const skillName of Object.keys(registry.skills)) {
    const installedOnPlatforms = [];
    let currentVersion = null;

    for (const { name: platformName, path: platformPath } of platformPaths) {
      const skillPath = path.join(platformPath, skillName);
      if (fs.existsSync(path.join(skillPath, 'SKILL.md'))) {
        installedOnPlatforms.push({ name: platformName, path: platformPath });
        if (!currentVersion) {
          const manifest = getInstalledManifest(skillName, platformPath);
          if (manifest) currentVersion = manifest.version;
        }
      }
    }

    if (installedOnPlatforms.length === 0) continue;

    const latestVersion = registry.skills[skillName].version;
    const needsUpdate = !currentVersion || currentVersion !== latestVersion;

    if (!skill || skill === skillName) {
      installedSkills.push({
        name: skillName,
        currentVersion: currentVersion || 'unknown',
        latestVersion,
        needsUpdate,
        platforms: installedOnPlatforms,
      });
    }
  }

  if (installedSkills.length === 0) {
    console.log('No installed skills found.');
    return;
  }

  const toUpdate = installedSkills.filter((s) => s.needsUpdate);

  if (check) {
    // Only show what would be updated
    console.log('\n🔍 Update check results:\n');
    if (toUpdate.length === 0) {
      console.log('✅ All skills are up to date!');
    } else {
      for (const s of toUpdate) {
        console.log(`  ⚠️  ${s.name}: ${s.currentVersion} → ${s.latestVersion}`);
      }
      console.log(`\n${toUpdate.length} update(s) available. Run without --check to update.`);
    }
    return;
  }

  if (!all && !skill) {
    console.error('❌ Specify a skill name or use --all');
    process.exit(1);
  }

  const skillsToProcess = skill ? installedSkills : toUpdate;

  if (skillsToProcess.length === 0) {
    console.log('✅ All skills are up to date!');
    return;
  }

  console.log(`\n🔄 Updating ${skillsToProcess.length} skill(s)...\n`);

  let successCount = 0;
  let failCount = 0;

  for (const { name: skillName, platforms } of skillsToProcess) {
    for (const { name: platformName, path: platformPath } of platforms) {
      try {
        process.stdout.write(`  Updating ${skillName} → ${platformName}... `);
        await installSkill(skillName, platformPath, {});
        console.log('✅');
        successCount++;
      } catch (err) {
        console.log(`❌ ${err.message}`);
        failCount++;
      }
    }
  }

  console.log(`\nDone: ${successCount} updated, ${failCount} failed`);
}

module.exports = { updateCommand };
