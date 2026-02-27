# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Good Skills is a comprehensive collection of AI agent skills for various platforms (Claude Code, GitHub Copilot, OpenCode, OpenClaw, Cursor, Windsurf, etc.). It includes both original skills and integrated skills from the dev-agent-skills project.

The project also includes **`good-skills`** (`packages/cli/`) — an NPM CLI tool for managing skill installation, updates, and discovery.

## Skill Trigger Index

Use this table to precisely match user requests to skills. Invoke the skill when trigger keywords appear.

### Git & GitHub Workflow

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `git-commit` | "帮我提交", "commit", "创建提交", "写 commit message", "stage and commit" | Just viewing git status or diff |
| `github-pr-creation` | "创建 PR", "open pull request", "提交 PR", "create pull request" | PR already exists and needs modification |
| `github-pr-review` | "处理 PR 评论", "resolve review", "fix review comments", "回复 reviewer" | Creating a new PR from scratch |
| `github-pr-merge` | "合并 PR", "merge pull request", "close PR and merge" | Creating or reviewing PR |
| `git-advanced-workflows` | "rebase", "cherry-pick", "bisect", "worktree", "git reflog", "clean up history" | Simple commits or PRs |

### Document Processing

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `pdf` | "处理 PDF", "读取 PDF", "生成 PDF", "填写表单", "merge PDF", "split PDF" | Plain text files |
| `docx` | "Word 文档", ".docx", "创建文档", "tracked changes", "word file" | PDF or plain markdown |
| `pptx` | "PPT", "演示文稿", "PowerPoint", "slides", "presentation" | Non-presentation documents |
| `xlsx` | "Excel", "电子表格", "spreadsheet", ".xlsx", "表格数据" | CSV or plain text data |

### Web & Browser Automation

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `agent-browser` / `browser-use` | "打开网页", "点击按钮", "填写表单", "截图", "navigate to URL", "web automation" | Static file reading |
| `defuddle` | "读取网页内容", "提取文章", "fetch URL as markdown", "clean web content" | Local files |
| `web-design-guidelines` | "检查 UI 代码", "review web interface", "UI guidelines compliance" | Backend code review |
| `clawdirect-dev` | "OpenClaw", "ATXP authentication", "agent-facing web experience" | Standard web apps |

### Frontend Best Practices

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `next-best-practices` | "Next.js", "RSC", "server components", "Next.js routing", "App Router" | Non-Next.js React |
| `vercel-react-best-practices` | "React 性能", "Vercel deployment", "React optimization" | Vue or Angular |
| `remotion-best-practices` | "Remotion", "视频创作", "React video" | Non-Remotion video |
| `supabase-postgres-best-practices` | "Supabase", "Postgres 优化", "database performance" | MySQL or MongoDB |

### Knowledge Management

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `archive-conversation` | "保存对话", "归档会话", "archive this chat", "save session summary" | Quick notes |
| `remembering-conversations` | "上次我们做了什么", "past solution", "how did we do X before" | New topics with no history |
| `session-logger` | "保存对话信息", "记录会话", "save session", "save conversation" | Archiving with analysis |
| `diary-assistant` | "写日记", "记录今天", "daily log" (macOS only) | Non-macOS environments |
| `journal-prompter` | "写作提示", "journaling prompt", "reflection prompts" | Task-oriented work |

### Obsidian Integration

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `obsidian-markdown` | "Obsidian 笔记", "wikilinks", "callouts", "obsidian frontmatter" | Non-Obsidian markdown |
| `obsidian-cli` | "Obsidian vault", "管理笔记", "obsidian CLI commands" | Reading plain markdown |
| `obsidian-bases` | "Obsidian Bases", ".base file", "database view in obsidian" | Regular notes |
| `json-canvas` | ".canvas file", "JSON Canvas", "obsidian canvas" | Regular notes or diagrams |

### AI/ML & Inference

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `models-test` | "测试大模型", "vLLM benchmark", "MindIE 测试", "NPU 推理测试" | CPU-based model inference |
| `vllm-dev-workflow` | "vLLM 开发", "vllm-ascend", "修改 vLLM 代码" | Non-vLLM inference |
| `vllm-ascend-profiler-diff` | "性能分析对比", "profiler diff", "ascend profiling" | General profiling |
| `monkey-patch` | "runtime patch", "monkey patch", "wrapt hook", "inference engine patch" | Standard code modifications |
| `dev-workflow` | "AI/ML 推理服务开发", "Ascend NPU workflow", "vLLM 服务部署" | Standard web app development |

### Content & Research

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `copywriting` | "写文案", "landing page copy", "marketing copy", "改进文案", "CTA" | Technical documentation |
| `research` | "研究一下", "synthesize info about", "research with citations" | Simple factual questions |
| `serpapi-search` | "Google 搜索", "search Google for", "SerpAPI", "find current results" | Static knowledge questions |
| `websearch` | "Brave 搜索", "web search", "news search", "image search" | Searches requiring Google specifically |

### Patent & Legal

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `patent-search` | "专利搜索", "patent search", "novelty assessment", "prior art", "infringement" | General research |
| `patent-specialist` | "写专利", "patent disclosure", "patent claims", "写权利要求" | Patent search only |

### Audio & Notifications

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `news-tts` | "新闻播报", "语音新闻", "TTS news", "Telegram 语音" | Text-only news summaries |

### Development Workflow

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `find-skills` | "找技能", "is there a skill for", "find a skill that can", "how do I do X" | When you already know which skill to use |
| `skill-creator` / `creating-skills` | "创建新技能", "write a SKILL.md", "new skill for" | Modifying existing skills |
| `brainstorming` | "帮我规划", "想想这个功能", "brainstorm", "design this feature" | Simple 1-line changes |
| `writing-plans` | "写实现计划", "create implementation plan", "plan this feature" | Executing, not planning |
| `feishu-doc-skill` | "飞书文档", "保存到飞书", "Feishu cloud doc" | Non-Feishu documents |
| `siyuan-note` | "思源笔记", "SiYuan Note", "知识库管理" | Other note-taking apps |

### Platform-Specific

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `openclaw-config` | "OpenClaw 配置", "OpenClaw bot", "autopilot settings" | Non-OpenClaw platforms |
| `bili-fetch` / `bili-grabber` | "B站视频", "Bilibili", "fetch bili" | Non-Bilibili video |

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
packages/
  cli/                    # good-skills NPM package
    src/
      index.js            # CLI entry (Commander.js)
      commands/           # install, update, status, list, find
      registry.js         # Load skills-registry.json (local or remote)
      installer.js        # Skill install/copy/symlink logic
      platforms.js        # Platform path configuration
    bin/
      good-skills.js      # Executable entry point
skills-registry.json      # Global skills registry with versions
<skill-name>/
  SKILL.md              # Main skill file (YAML frontmatter + markdown body)
  manifest.json         # Skill version + metadata (name, version, tags, platforms)
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

### CLI (Recommended)

```bash
# Install a specific skill
npx good-skills install git-commit

# Install to specific platform
npx good-skills install git-commit --platform claude

# Install all skills
npx good-skills install --all

# Update all installed skills
npx good-skills update --all

# Check for updates
npx good-skills update --check

# See installed skills
npx good-skills status

# Search skills
npx good-skills find "pr review"

# List all available skills
npx good-skills list --tag git
```

### Shell Scripts (Legacy)

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
