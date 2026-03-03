Good Skills 项目是 AI 助手技能的集合，支持多种 AI 编程平台（Claude Code、GitHub Copilot、OpenCode 等）。本项目包含了原始技能以及从 dev-agent-skills 项目集成的技能。

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
| `tts-skill` | "把这段文字转成语音", "TTS 生成", "朗读这段话", "语音合成 MP3" | 新闻播报推送（用 `news-tts`）|

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

### Daily & Personal

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `super-wardrobe` | "今天穿什么", "穿搭建议", "帮我搭配衣服", "wardrobe", "衣橱" | 只查询天气不需要穿搭 |
| `super-fitness` | "今天健身", "运动计划", "减脂建议", "每日健身打卡", "fitness plan" | 泛泛健康咨询 |
| `vibe-daily` | "AI 编程工具动态", "Claude Code 有什么更新", "vibe coding 资讯" | 泛科技新闻（用 daily-newsletter）|
| `daily-digest` | "每日日志汇总", "今日汇总", "daily digest" | 单个 skill 的输出 |
| `daily-newsletter` | "科技早报", "每日新闻", "RSS 聚合", "daily newsletter" | 单主题搜索 |
| `bili-daily` | "B站 AI 视频精选", "今日 B 站", "bili daily" | 搜索特定 B 站视频（用 `bili-fetch`）|
| `arxiv-daily` | "今日 arXiv 论文", "AI 论文精选", "每日论文推送" | 搜索特定论文 |
| `weekly-report` | "周报", "本周工作总结", "weekly report" | 每日汇报 |
| `github-watcher` | "GitHub 仓库监控", "版本更新通知" | 手动查看 PR/commits |
| `chess-advisor` | "象棋", "棋盘分析", "chess", "分析棋局" | 国际象棋（非中国象棋）|
| `wuyu-xiaohongshu` | "无语哥", "奇葩新闻文案", "小红书无语内容" | 普通小红书内容创作 |
| `xhs-skill` | "小红书检索", "发布小红书", "xhs MCP" | 生成小红书文案（用 `wuyu-xiaohongshu`）|

---

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
