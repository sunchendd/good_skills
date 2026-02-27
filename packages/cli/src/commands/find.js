const { loadRegistry, filterSkills, fetchText } = require('../registry');

const SKILLS_SH_API = 'https://registry.skills.sh/api/skills';

/**
 * Search the skills.sh registry
 */
async function searchSkillsSh(query) {
  try {
    const url = `${SKILLS_SH_API}?q=${encodeURIComponent(query)}`;
    const content = await fetchText(url);
    const data = JSON.parse(content);
    return Array.isArray(data) ? data : data.skills || data.results || [];
  } catch {
    return []; // skills.sh may not be reachable, silently skip
  }
}

async function findCommand(query) {
  console.log(`\n🔍 Searching for: "${query}"\n`);

  // Search local registry in parallel with skills.sh
  let registry;
  try {
    registry = await loadRegistry();
  } catch (err) {
    console.error('❌ Failed to load local registry:', err.message);
    process.exit(1);
  }

  const [localResults, remoteResults] = await Promise.all([
    Promise.resolve(filterSkills(registry, { query })),
    searchSkillsSh(query),
  ]);

  let found = false;

  if (localResults.length > 0) {
    found = true;
    console.log(`📦 Good Skills repository (${localResults.length} match${localResults.length > 1 ? 'es' : ''}):\n`);
    for (const skill of localResults) {
      console.log(`  ${skill.name}`);
      if (skill.description) {
        console.log(`  └ ${skill.description.substring(0, 80)}`);
      }
      console.log(`  └ Install: npx @good-skills/cli install ${skill.name}\n`);
    }
  }

  if (remoteResults.length > 0) {
    found = true;
    console.log(`🌐 skills.sh ecosystem (${remoteResults.length} match${remoteResults.length > 1 ? 'es' : ''}):\n`);
    for (const skill of remoteResults.slice(0, 10)) {
      const ref = skill.package || skill.name || skill.ref;
      const desc = skill.description || '';
      const url = skill.url || `https://skills.sh/${ref}`;
      console.log(`  ${ref}`);
      if (desc) console.log(`  └ ${desc.substring(0, 80)}`);
      console.log(`  └ ${url}`);
      if (ref) console.log(`  └ Install: npx skills add ${ref}\n`);
    }
  }

  if (!found) {
    console.log(`No skills found for "${query}".`);
    console.log('\nTips:');
    console.log('  • Try different keywords (e.g., "react" instead of "reactjs")');
    console.log('  • Browse all skills: npx @good-skills/cli list');
    console.log('  • Browse skills.sh: https://skills.sh/\n');
  }
}

module.exports = { findCommand };
