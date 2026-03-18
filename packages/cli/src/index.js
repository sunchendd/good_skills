#!/usr/bin/env node

const { Command } = require('commander');
const { addCommand } = require('./commands/add');
const { installCommand } = require('./commands/install');
const { updateCommand } = require('./commands/update');
const { statusCommand } = require('./commands/status');
const { listCommand } = require('./commands/list');
const { findCommand } = require('./commands/find');
const pkg = require('../package.json');

const program = new Command();

program
  .name('good-skills')
  .description('CLI package manager for Good Skills - AI agent skills management')
  .version(pkg.version);

program
  .command('install [skill]')
  .description('Install a skill (e.g. git-commit, owner/repo@skill-name, or GitHub URL + --skill)')
  .option('--all', 'Install all skills from registry')
  .option('--skill <name>', 'Skill directory name when installing from a GitHub repo or URL')
  .option('--ref <branch>', 'Git branch to fetch from when installing from a GitHub repo')
  .option('--platform <platform>', 'Target platform (claude/github-copilot/opencode/openclaw/cursor/windsurf/antigravity/codex/all)', 'all')
  .option('--project', 'Install to project directory instead of global')
  .action(installCommand);

program
  .command('add <repo>')
  .description('Install a specific skill from a GitHub repo or URL')
  .requiredOption('--skill <name>', 'Skill directory name inside the GitHub repository')
  .option('--ref <branch>', 'Git branch to fetch from when installing from a GitHub repo')
  .option('--platform <platform>', 'Target platform (claude/github-copilot/opencode/openclaw/cursor/windsurf/antigravity/codex/all)', 'all')
  .option('--project', 'Install to project directory instead of global')
  .action(addCommand);

program
  .command('update [skill]')
  .description('Update installed skills')
  .option('--all', 'Update all installed skills')
  .option('--check', 'Check for updates without installing')
  .action(updateCommand);

program
  .command('status')
  .description('Show installed skills and their versions')
  .option('--platform <platform>', 'Show status for specific platform')
  .action(statusCommand);

program
  .command('list')
  .description('List available skills from registry')
  .option('--installed', 'Show only installed skills')
  .option('--tag <tag>', 'Filter by tag')
  .action(listCommand);

program
  .command('find <query>')
  .description('Search for skills in registry and skills.sh ecosystem')
  .action(findCommand);

program.parse(process.argv);
