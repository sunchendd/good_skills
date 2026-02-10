# Good Skills 技能集合

本项目提供了一套模块化的 **Skills**（技能）工具包，能够扩展 AI 助手的能力，为其提供特定领域的知识、自动化工作流和工具集成。这些 Skills 覆盖了开发、测试、文档处理、AI/ML 推理等多个领域。

## Skills 安装与集成方法

您可以参照以下说明，将本项目中的 Skills 集成到主流的 AI 编程工具中：

### 1. 一键安装脚本 (推荐)
使用本仓库提供的安装脚本，可以一次性将所有 Skills 安装到多个 AI 编程工具平台。安装脚本使用**符号链接（symbolic links）**的方式，确保：
- ✅ 兼容已有的 Skills 安装
- ✅ 自动识别并跳过已存在的 Skills
- ✅ Skills 更新会自动同步到所有平台
- ✅ 支持全局安装或项目级安装

#### 安装到所有平台
```bash
git clone https://github.com/sunchendd/good_skills.git
cd good_skills
./install.sh --all
```

#### 安装到特定平台
```bash
# 安装到 GitHub Copilot
./install.sh --github-copilot

# 安装到 Claude Code
./install.sh --claude

# 安装到多个平台
./install.sh --github-copilot --claude --opencode --antigravity

# 安装到项目目录（而非全局）
./install.sh --all --project
```

#### 卸载
```bash
# 从所有平台卸载
./uninstall.sh --all

# 从特定平台卸载
./uninstall.sh --github-copilot --claude
```

#### 支持的平台
- **GitHub Copilot** - `~/.copilot/skills/`
- **Claude Code** - `~/.claude/skills/`
- **OpenCode** - `~/.config/opencode/skill/`
- **Antigravity** - `~/.gemini/antigravity/skills/`
- **Cursor** - `~/.cursor/skills/`
- **Windsurf** - `~/.codeium/windsurf/skills/`
- **Trae** - 需要通过设置界面手动配置

### 2. 使用 npx add-skill 工具
使用 **add-skill** 工具可以一键将单个 Skill 安装到多个平台，自动识别正确的路径。
```bash
npx add-skill sunchendd/good_skills/<skill-name>
```

### 3. 各平台手动安装路径

| 工具  | 项目安装路径 (Project)          | 个人安装路径 (Global)                                |
| :--- | :--- | :--- |
| **Claude Code** | `.claude/skills/<name>/SKILL.md` | `~/.claude/skills/<name>/SKILL.md`           |
| **GitHub Copilot** | `.github/skills/<name>/SKILL.md` | `~/.copilot/skills/<name>/SKILL.md`          |
| **Trae** | `.trae/skills/<name>/SKILL.md`     | 设置 > 规则和技能 > 全局技能                    |
| **Cursor** | `.cursor/skills/<name>/SKILL.md`   | `~/.cursor/skills/<name>/SKILL.md`           |
| **Windsurf** | `.windsurf/skills/<name>/SKILL.md` | `~/.codeium/windsurf/skills/<name>/SKILL.md` |
| **OpenCode** | `.opencode/skill/<name>/SKILL.md`  | `~/.config/opencode/skill/<name>/SKILL.md`   |
| **Antigravity** | `.agent/skills/<name>/SKILL.md`   | `~/.gemini/antigravity/skills/<name>/SKILL.md` |

---

## Skills 编写与维护规范

为确保 Skill 在不同模型（如 Claude 3.5 Sonnet/Opus）上都能保持高效和稳定，请遵循以下原则：

1. **简洁高效**：建议 `SKILL.md` 正文保持在 500 行以内，复杂逻辑拆分为子文件（如 `reference.md`）。
2. **描述清晰**：`description` 字段应包含"做什么"+"何时使用"，使用第三人称，方便智能体精准触发。
3. **渐进式披露**：将详细 API 规范或长示例放入独立文件，仅在智能体需要时加载。
4. **术语一致性**：在整个 Skill 中使用统一的术语定义，避免混淆（如统一使用"API 端点"而非混用"URL/路由"）。

### Skill 质量检查清单 (Quality Checklist)

在分享或发布一个 Skill 前，请确保通过以下检查：

#### 核心质量
- [ ] **描述准确**：包含"做什么"和"何时使用"，且包含自然语言关键词。
- [ ] **长度控制**：`SKILL.md` 正文不超过 500 行，细节已拆分。
- [ ] **无时效性**：避免使用"当前"、"最新"等词汇，改用具体的版本号。
- [ ] **一层引用**：子文件引用保持在主文件的一层深度内，避免深层嵌套。
- [ ] **工作流闭环**：关键操作包含明确的顺序步骤和验证手段。

#### 脚本与资源
- [ ] **路径通用**：始终使用正斜杠（`/`），确保跨平台兼容。
- [ ] **错误处理**：脚本失败时应返回有帮助的错误信息给智能体，而非直接崩溃。
- [ ] **依赖透明**：明确列出所需环境或依赖包，并包含安装验证逻辑。

#### 测试验证
- [ ] **多场景测试**：至少创建并运行过 3 个以上的实际业务评估场景。
- [ ] **多模型兼容**：在 Sonnet、Opus 或其他目标模型上进行过基本的效果对比。

---

## 现有 Skills 概览

本仓库包含 35+ 个专业技能，涵盖多个领域：

### 🤖 AI/ML 推理与测试
- **[models-test](models-test/)**: 大模型的推理性能（vLLM、Mindie）和精度测试框架
- **[vllm-dev-workflow](vllm-dev-workflow/)**: vLLM 开发验证工作流
- **[vllm-ascend-profiler-diff](vllm-ascend-profiler-diff/)**: vLLM-Ascend 性能差异分析工具
- **[monkey-patch](monkey-patch/)**: 推理引擎（vLLM、vLLM-Ascend）运行时补丁生成与管理框架

### 💻 开发工具与工作流
- **[dev-workflow](dev-workflow/)**: 通用开发验证工作流
- **[brainstorming](brainstorming/)**: 在实现功能前探索用户需求和设计
- **[writing-plans](writing-plans/)**: 为多步骤任务编写全面的实施计划
- **[skill-creator](skill-creator/)**: 创建和优化新 Skill 的指导手册
- **[find-skills](find-skills/)**: 帮助用户发现和安装 Agent 技能
- **[git-advanced-workflows](git-advanced-workflows/)**: 高级 Git 工作流（rebase、cherry-pick、bisect、worktrees 等）

### 📝 文档处理
- **[docx](docx/)**: Word 文档创建、编辑和分析，支持修订跟踪和注释
- **[pptx](pptx/)**: PowerPoint 演示文稿创建、编辑和分析
- **[pdf](pdf/)**: PDF 操作工具包（文本/表格提取、创建、合并/拆分、表单处理）
- **[xlsx](xlsx/)**: Excel 电子表格创建、编辑和分析，支持公式、格式化和数据可视化

### 📚 知识管理与对话
- **[archive-conversation](archive-conversation/)**: 创建 AI 对话的分析归档摘要
- **[remembering-conversations](remembering-conversations/)**: 搜索对话历史以回忆过往工作
- **[session-logger](session-logger/)**: 保存对话历史到会话日志文件
- **[diary-assistant](diary-assistant/)**: (macOS) 日记写作助手，集成提醒事项
- **[journal-prompter](journal-prompter/)**: 日常日记提示和反思框架

### 🌐 Web 与浏览器自动化
- **[agent-browser](agent-browser/)**: 自动化浏览器交互（测试、表单填写、截图、数据提取）
- **[browser-use](browser-use/)**: 使用 browser-use CLI 进行浏览器自动化
- **[clawdirect-dev](clawdirect-dev/)**: 使用 ATXP 认证构建面向 Agent 的 Web 体验
- **[web-design-guidelines](web-design-guidelines/)**: 审查 UI 代码的 Web 界面指南合规性

### 🎯 前端框架最佳实践
- **[next-best-practices](next-best-practices/)**: Next.js 最佳实践（文件约定、RSC、数据模式等）
- **[vercel-react-best-practices](vercel-react-best-practices/)**: Vercel 的 React 和 Next.js 性能优化指南
- **[remotion-best-practices](remotion-best-practices/)**: Remotion 视频创建最佳实践
- **[supabase-postgres-best-practices](supabase-postgres-best-practices/)**: Supabase 的 Postgres 性能优化和最佳实践

### 🎨 内容创作与营销
- **[copywriting](copywriting/)**: 营销文案写作和优化（首页、落地页、定价页等）
- **[research](research/)**: 获取 AI 综合的研究报告，带引用支持

### 🔍 专利与检索
- **[patent-search](patent-search/)**: 专利检索专家
- **[patent-specialist](patent-specialist/)**: 专利专家 Agent

### 🎤 音频处理
- **[edge-tts](i3130002/edge-tts/)**: 使用 Microsoft Edge TTS 服务进行文本转语音（作者：i3130002）
- **[faster-whisper](theplasmak/faster-whisper/)**: 本地语音转文字，比 OpenAI Whisper 快 4-6 倍（作者：theplasmak）

---

## 贡献指南

欢迎贡献新的 Skills 或改进现有 Skills！

1. 遵循上述 Skills 编写与维护规范
2. 确保通过质量检查清单
3. 在 SKILL.md 中提供清晰的 `name` 和 `description`
4. 提交 Pull Request 前进行充分测试

## 许可证

各个 Skill 可能有不同的许可证，请查看各 Skill 目录中的 LICENSE 文件。

---

**维护者**: sunchendd  
**仓库**: https://github.com/sunchendd/good_skills
