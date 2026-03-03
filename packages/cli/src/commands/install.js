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
    console.error('   Example: npx good-skills install git-commit');
    console.error('   Example: npx good-skills install --all --platform claude');
    process.exit(1);
  }

  const total = skillsToInstall.length * platformPaths.length;
  let done = 0;
  let successCount = 0;
  let failCount = 0;

  if (skillsToInstall.length > 1) {
    console.log(`\n📦 Installing ${skillsToInstall.length} skill(s) to ${platformPaths.length} platform(s)...\n`);
  }

  for (const { name, thirdParty, rawBase } of skillsToInstall) {
    for (const { name: platformName, path: platformPath } of platformPaths) {
      done++;
      const prefix = skillsToInstall.length > 1 ? `[${done}/${total}] ` : '  ';
      process.stdout.write(`${prefix}Installing ${name} → ${platformName}... `);
      try {
        await installSkill(name, platformPath, { thirdParty, rawBase });
        console.log('✅');
        successCount++;
      } catch (err) {
        console.log(`❌ ${err.message}`);
        // Provide actionable hint for common errors
        if (err.message.includes('404') || err.message.includes('HTTP 404')) {
          console.error(`     ℹ  Skill "${name}" not found. Run: npx good-skills list`);
        } else if (err.message.includes('Timeout') || err.message.includes('ENOTFOUND')) {
          console.error(`     ℹ  Network error. Check your connection and try again.`);
        }
        failCount++;
      }
    }
  }

  console.log(`\nDone: ${successCount} installed, ${failCount} failed`);
  if (failCount > 0) process.exit(1);
}

module.exports = { installCommand };
