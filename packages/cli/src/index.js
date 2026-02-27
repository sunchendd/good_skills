#!/usr/bin/env node

const { Command } = require('commander');
const { installCommand } = require('./commands/install');
const { updateCommand } = require('./commands/update');
const { statusCommand } = require('./commands/status');
const { listCommand } = require('./commands/list');
const { findCommand } = require('./commands/find');

const program = new Command();

program
  .name('good-skills')
  .description('CLI package manager for Good Skills - AI agent skills management')
  .version('0.1.0');

program
  .command('install [skill]')
  .description('Install a skill (e.g. git-commit, owner/repo@skill-name)')
  .option('--all', 'Install all skills from registry')
  .option('--platform <platform>', 'Target platform (claude/github-copilot/opencode/openclaw/cursor/windsurf/all)', 'all')
  .option('--project', 'Install to project directory instead of global')
  .action(installCommand);

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
