const { installCommand } = require('./install');

async function addCommand(repo, options) {
  if (!options.skill) {
    console.error('Specify --skill <name>');
    console.error('   Example: npx good-skills add https://github.com/vercel-labs/skills --skill find-skills');
    process.exit(1);
  }

  await installCommand(repo, options);
}

module.exports = { addCommand };
