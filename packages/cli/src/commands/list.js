const { loadRegistry, filterSkills } = require('../registry');

async function listCommand(options) {
  const { installed, tag } = options;

  let registry;
  try {
    registry = await loadRegistry();
  } catch (err) {
    console.error('❌ Failed to load registry:', err.message);
    process.exit(1);
  }

  const skills = filterSkills(registry, { tag });

  console.log(`\n📚 Good Skills Registry${tag ? ` [tag: ${tag}]` : ''} (${skills.length} skills)\n`);
  console.log(`${'Skill'.padEnd(38)} ${'Version'.padEnd(10)} Tags`);
  console.log('─'.repeat(80));

  for (const skill of skills.sort((a, b) => a.name.localeCompare(b.name))) {
    const tags = (skill.tags || []).join(', ');
    console.log(`  ${skill.name.padEnd(36)} ${skill.version.padEnd(10)} ${tags}`);
  }

  console.log(`\nInstall: npx good-skills install <skill-name>`);
  console.log(`Filter:  npx good-skills list --tag <tag>\n`);
}

module.exports = { listCommand };
