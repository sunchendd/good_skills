const { loadRegistry, filterSkills } = require('../registry');
const { resolvePaths } = require('../platforms');
const { installSkill, parseThirdPartyRef } = require('../installer');

async function installCommand(skill, options) {
  const { all, platform, project } = options;

  let registry;
  try {
    registry = await loadRegistry();
  } catch (err) {
    console.error('❌ Failed to load registry:', err.message);
    process.exit(1);
  }

  const platformPaths = resolvePaths(platform, project);

  // Determine which skills to install
  let skillsToInstall = [];

  if (all) {
    skillsToInstall = Object.keys(registry.skills).map((name) => ({ name, thirdParty: false }));
  } else if (skill) {
    // Check if it's a third-party reference (owner/repo@skill-name)
    if (skill.includes('/') && skill.includes('@')) {
      const ref = parseThirdPartyRef(skill);
      skillsToInstall = [{ name: ref.skill, thirdParty: true, rawBase: ref.rawBase }];
    } else {
      skillsToInstall = [{ name: skill, thirdParty: false }];
    }
  } else {
    console.error('❌ Specify a skill name or use --all');
    process.exit(1);
  }

  let successCount = 0;
  let failCount = 0;

  for (const { name, thirdParty, rawBase } of skillsToInstall) {
    for (const { name: platformName, path: platformPath } of platformPaths) {
      try {
        process.stdout.write(`  Installing ${name} → ${platformName}... `);
        await installSkill(name, platformPath, { thirdParty, rawBase });
        console.log('✅');
        successCount++;
      } catch (err) {
        console.log(`❌ ${err.message}`);
        failCount++;
      }
    }
  }

  console.log(`\nDone: ${successCount} installed, ${failCount} failed`);
}

module.exports = { installCommand };
