const { loadRegistry } = require('../registry');
const { resolvePaths } = require('../platforms');
const { installSkill, parseThirdPartyRef, buildThirdPartyInstallTarget } = require('../installer');

async function performInstall(skillsToInstall, options) {
  const { platform, project } = options;
  const platformPaths = resolvePaths(platform, project);
  const total = skillsToInstall.length * platformPaths.length;
  let done = 0;
  let successCount = 0;
  let failCount = 0;

  if (skillsToInstall.length > 1) {
    console.log(`\nInstalling ${skillsToInstall.length} skill(s) to ${platformPaths.length} platform(s)...\n`);
  }

  for (const { name, thirdParty, rawBase } of skillsToInstall) {
    for (const { name: platformName, path: platformPath } of platformPaths) {
      done++;
      const prefix = skillsToInstall.length > 1 ? `[${done}/${total}] ` : '  ';
      process.stdout.write(`${prefix}Installing ${name} -> ${platformName}... `);
      try {
        await installSkill(name, platformPath, { thirdParty, rawBase });
        console.log('OK');
        successCount++;
      } catch (err) {
        console.log(`ERROR ${err.message}`);
        if (err.message.includes('404') || err.message.includes('HTTP 404')) {
          console.error(`     Hint: Skill "${name}" not found. Run: npx good-skills list`);
        } else if (err.message.includes('Timeout') || err.message.includes('ENOTFOUND')) {
          console.error('     Hint: Network error. Check your connection and try again.');
        }
        failCount++;
      }
    }
  }

  console.log(`\nDone: ${successCount} installed, ${failCount} failed`);
  if (failCount > 0) process.exit(1);
}

async function installCommand(skill, options) {
  const { all, ref } = options;
  let skillsToInstall = [];

  if (all) {
    let registry;
    try {
      registry = await loadRegistry();
    } catch (err) {
      console.error('Failed to load registry:', err.message);
      process.exit(1);
    }
    skillsToInstall = Object.keys(registry.skills).map((name) => ({ name, thirdParty: false }));
  } else if (skill) {
    try {
      if (options.skill) {
        skillsToInstall = [buildThirdPartyInstallTarget(skill, options.skill, ref)];
      } else if (skill.includes('/') && skill.includes('@')) {
        const parsedRef = parseThirdPartyRef(skill);
        skillsToInstall = [{ name: parsedRef.skill, thirdParty: true, rawBase: parsedRef.rawBase }];
      } else {
        skillsToInstall = [{ name: skill, thirdParty: false }];
      }
    } catch (err) {
      console.error(err.message);
      process.exit(1);
    }
  } else {
    console.error('Specify a skill name or use --all');
    console.error('   Example: npx good-skills install git-commit');
    console.error('   Example: npx good-skills install vercel-labs/skills@find-skills');
    console.error('   Example: npx good-skills install https://github.com/vercel-labs/skills --skill find-skills');
    console.error('   Example: npx good-skills install --all --platform claude');
    process.exit(1);
  }

  await performInstall(skillsToInstall, options);
}

module.exports = { installCommand, performInstall };
