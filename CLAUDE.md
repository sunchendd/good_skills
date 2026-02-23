# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Good Skills is a comprehensive collection of AI agent skills for various platforms (Claude Code, GitHub Copilot, OpenCode, OpenClaw, Cursor, Windsurf, etc.). It includes both original skills and integrated skills from the dev-agent-skills project.

### Skill Categories

The repository contains 40+ skills organized into the following categories:

- **AI/ML推理与测试**: models-test, vllm-dev-workflow, vllm-ascend-profiler-diff, monkey-patch
- **开发工具与工作流**: dev-workflow, brainstorming, writing-plans, skill-creator, find-skills, git-advanced-workflows
- **Git & GitHub工作流**: git-commit, github-pr-creation, github-pr-review, github-pr-merge (conventional commits, PR workflows)
- **文档处理**: docx, pptx, pdf, xlsx
- **知识管理与对话**: archive-conversation, remembering-conversations, session-logger, diary-assistant, journal-prompter
- **Web与浏览器自动化**: agent-browser, browser-use, clawdirect-dev, web-design-guidelines
- **前端框架最佳实践**: next-best-practices, vercel-react-best-practices, remotion-best-practices, supabase-postgres-best-practices
- **内容创作与营销**: copywriting, research
- **专利与检索**: patent-search, patent-specialist
- **音频处理**: edge-tts, faster-whisper

### Skills from dev-agent-skills

Integrated from [fvadicamo/dev-agent-skills](https://github.com/fvadicamo/dev-agent-skills):

- **github-workflow plugin**:
  - `git-commit` - Creates commits following Conventional Commits format
  - `github-pr-creation` - Creates PRs with validation and task tracking
  - `github-pr-review` - Handles PR review comments and feedback
  - `github-pr-merge` - Merges PRs after validation
- **skill-authoring plugin**:
  - `creating-skills` - Guide for creating Claude Code skills

## Architecture

```
.claude-plugin/
  marketplace.json        # Plugin registry from dev-agent-skills
<skill-name>/
  SKILL.md              # Main skill file (YAML frontmatter + markdown body)
  references/           # Optional deep-dive docs loaded on demand
  scripts/              # Optional helper scripts
  assets/               # Optional resource files
```

## Conventions

### Development practices

- **Commits**: Prefer Conventional Commits format when appropriate - `type(scope): subject` (see `git-commit/SKILL.md`)
- **Naming**: lowercase, hyphens between words, no spaces (e.g., `github-pr-review`)
- **Merge strategy**: depends on project, generally use project convention
- **Structure**: Keep SKILL.md under 500 lines; move detailed content to `references/`

### Skill writing guidelines

When creating or editing skills, follow these patterns:

- **Description formula**: `<What it does>. Use when <trigger phrases>. <Key capabilities>.`
- **SKILL.md body**: Keep under 500 lines; move detailed content to `references/`
- **Trigger phrases**: Include relevant keywords in descriptions for model invocation
- **Critical constraints**: Mark with bold **ALWAYS**/**NEVER** in "Important Rules" sections
- **Progressive disclosure**: Reference files should only be loaded when needed

### Platform-specific paths

- **Claude Code**: `~/.claude/skills/` or `.claude/skills/`
- **GitHub Copilot**: `~/.copilot/skills/` or `.github/skills/`
- **OpenCode**: `~/.config/opencode/skill/` or `.opencode/skill/`
- **OpenClaw**: `~/.openclaw/skills/` or `.openclaw/skills/`
- **Cursor**: `~/.cursor/skills/` or `.cursor/skills/`
- **Windsurf**: `~/.codeium/windsurf/skills/` or `.windsurf/skills/`
- **Antigravity**: `~/.agent/skills/` or `.agent/skills/` (default base directory)

## Installation

Use the installation scripts to add skills to your AI agent platforms:

```bash
# Install to all platforms
./install.sh --all

# Install to specific platforms
./install.sh --claude --opencode --github-copilot

# Update existing installations
./update.sh --all

# Uninstall
./uninstall.sh --all
```

## License

Individual skills may have different licenses. Check the LICENSE file in each skill directory for details.
