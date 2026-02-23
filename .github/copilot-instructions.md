Good Skills 项目是 AI 助手技能的集合，支持多种 AI 编程平台（Claude Code、GitHub Copilot、OpenCode 等）。本项目包含了原始技能以及从 dev-agent-skills 项目集成的技能。

### 技能类别

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

### Git 提交规范

**优先使用 Conventional Commits 格式**: `type(scope): subject`

支持的类型包括：
- `feat` - 新功能
- `fix` - 修复
- `docs` - 文档
- `style` - 格式
- `refactor` - 重构
- `test` - 测试
- `chore` - 构建/工具
- `security` - 安全修复/加固

**规则**:
- scope 是必需的（kebab-case）
- subject 不超过 50 字符
- 使用现在时祈使语态
- 不以句号结尾

示例:
- `git-commit(auth): add conventional commits enforcement`
- `github-pr-creation(workflow): add task validation`
- `feat(git): add automated PR branch detection`

### 安装技能

```bash
# 安装到所有平台
./install.sh --all

# 安装到特定平台
./install.sh --claude --opencode --github-copilot

# 更新现有安装
./update.sh --all
```

### 更多信息

详细的文档请参阅项目根目录的 `CLAUDE.md` 文件。
