# Good Skills CLI 包管理器 设计文档

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:writing-plans to create implementation plan from this design.

**Goal:** 构建 `@good-skills/cli` NPM 包，为 Good Skills 提供统一的技能生命周期管理能力，支持安装、更新、状态查询、技能搜索。

**架构:** Node.js CLI 包发布至 npm，通过 `npx @good-skills/cli` 使用；每个技能目录增加 `manifest.json` 存储版本元数据；根目录增加 `skills-registry.json` 作为统一注册表；CLAUDE.md 重写为结构化格式提升 AI 定位准确性。

**Tech Stack:** Node.js 18+, Commander.js, 原生 fetch（无重量级依赖）, npm publish

---

## 背景与动机

### 现状痛点

1. **安装体验差**：`curl -fsSL ... | bash` 是一次性操作，无管理能力
2. **无版本概念**：所有技能都是"最新版本"，无法固定或回滚
3. **无状态查询**：不知道哪些技能已安装、是否需要更新
4. **CLAUDE.md 效果差**：AI 无法精确定位应使用哪个技能
5. **开源技能无法便捷安装**：无法直接安装 skills.sh 生态的技能

### 设计目标

- `npx @good-skills/cli` 提供完整包管理体验
- 每个技能有独立版本号（SemVer）
- 支持从本仓库和第三方 GitHub 仓库安装
- 支持搜索 skills.sh 生态系统
- CLAUDE.md 结构化重写，AI 精确匹配

---

## 架构设计

### 目录结构

```
good_skills/
├── packages/
│   └── cli/                         # npm 包根目录
│       ├── src/
│       │   ├── index.js             # CLI 入口 (Commander)
│       │   ├── commands/
│       │   │   ├── install.js       # install 命令
│       │   │   ├── update.js        # update 命令
│       │   │   ├── status.js        # status 命令
│       │   │   ├── find.js          # find 命令 (集成 skills.sh)
│       │   │   └── list.js          # list 命令
│       │   ├── registry.js          # 读取 skills-registry.json
│       │   ├── installer.js         # 技能安装逻辑（符号链接 / 复制）
│       │   └── platforms.js         # 各平台路径配置
│       ├── bin/
│       │   └── good-skills.js       # #!/usr/bin/env node 入口
│       └── package.json             # name: "@good-skills/cli"
│
├── <skill-name>/
│   ├── SKILL.md                     # 技能主文件（不变）
│   └── manifest.json                # NEW: 版本 + 元数据
│
├── skills-registry.json             # NEW: 全局注册表
├── CLAUDE.md                        # 重写：结构化触发词表
└── docs/
    └── plans/                       # 设计文档目录
```

### 数据流

```
用户运行命令
    ↓
npx @good-skills/cli install git-commit --platform claude
    ↓
CLI → registry.js 查询 skills-registry.json
    ↓
从 GitHub raw 下载 git-commit/SKILL.md + manifest.json
    ↓
installer.js → 写入目标平台路径（~/.claude/skills/git-commit/）
    ↓
输出安装成功 + 版本信息
```

---

## 组件设计

### 1. manifest.json（每个技能）

```json
{
  "name": "git-commit",
  "version": "1.2.0",
  "description": "Creates git commits following Conventional Commits format with type/scope/subject",
  "author": "good-skills",
  "tags": ["git", "workflow", "conventional-commits"],
  "platforms": ["claude", "github-copilot", "opencode", "openclaw", "cursor", "windsurf"],
  "dependencies": [],
  "minAgentVersion": "1.0.0"
}
```

### 2. skills-registry.json（根目录）

```json
{
  "version": "1.0.0",
  "repository": "https://github.com/sunchendd/good_skills",
  "skills": {
    "git-commit": {
      "version": "1.2.0",
      "path": "git-commit",
      "tags": ["git", "workflow"]
    },
    "github-pr-creation": {
      "version": "1.1.0",
      "path": "github-pr-creation",
      "tags": ["git", "pr", "workflow"]
    }
  }
}
```

### 3. CLI 命令规范

#### `install`

```bash
npx @good-skills/cli install git-commit                    # 安装本仓库技能，所有平台
npx @good-skills/cli install git-commit --platform claude  # 指定平台
npx @good-skills/cli install owner/repo@skill-name         # 第三方 GitHub 仓库
npx @good-skills/cli install --all                         # 安装全部
```

#### `update`

```bash
npx @good-skills/cli update                    # 更新所有已安装技能
npx @good-skills/cli update git-commit         # 更新指定技能
npx @good-skills/cli update --check            # 仅检查可用更新，不执行
```

#### `status`

```bash
npx @good-skills/cli status
# 输出示例：
# ✅ git-commit          v1.2.0  (claude, github-copilot)
# ✅ github-pr-creation  v1.1.0  (claude)
# ⚠️  pdf                v0.9.0  → v1.0.0 available
```

#### `find`（集成 skills.sh 生态）

```bash
npx @good-skills/cli find "pr review"
# 搜索 skills.sh 生态 + 本仓库，合并展示结果
# 结果示例：
# [本仓库] github-pr-review v1.0.0  npx @good-skills/cli install github-pr-review
# [skills.sh] vercel-labs/agent-skills@vercel-react-best-practices
#             npx skills add vercel-labs/agent-skills@vercel-react-best-practices
```

#### `list`

```bash
npx @good-skills/cli list              # 列出本仓库所有技能
npx @good-skills/cli list --installed  # 仅列出已安装技能
npx @good-skills/cli list --tag git    # 按标签过滤
```

### 4. 平台路径配置（platforms.js）

| Platform | Global Path | Project Path |
|----------|-------------|--------------|
| claude | `~/.claude/skills/` | `.claude/skills/` |
| github-copilot | `~/.copilot/skills/` | `.github/skills/` |
| opencode | `~/.config/opencode/skill/` | `.opencode/skill/` |
| openclaw | `~/.openclaw/skills/` | `.openclaw/skills/` |
| cursor | `~/.cursor/skills/` | `.cursor/skills/` |
| windsurf | `~/.codeium/windsurf/skills/` | `.windsurf/skills/` |

### 5. CLAUDE.md 重写策略

现有 CLAUDE.md 使用宽泛分类描述，AI 难以精确匹配。新格式：

```markdown
## 技能触发词快速索引

| 技能名 | 触发场景（用这些词时调用）| 不适用场景 |
|--------|--------------------------|------------|
| git-commit | "帮我提交", "commit", "创建提交", "写 commit message" | 只是查看 git 状态 |
| github-pr-creation | "创建 PR", "open pull request", "提交 PR" | PR 已存在需要修改 |
| pdf | "处理 PDF", "读取 PDF", "生成 PDF", "填写表单" | 纯文本文件 |
```

---

## 错误处理

- 网络失败：提示用户检查网络，建议使用本地安装
- 版本冲突：显示当前版本与目标版本，让用户确认覆盖
- 平台路径不存在：自动创建目录
- 第三方仓库格式错误：提示正确格式 `owner/repo@skill-name`

---

## 发布策略

1. 初始版本：`0.1.0`（CLI 基础功能：install, status, list）
2. `0.2.0`：update + find（skills.sh 集成）
3. `1.0.0`：所有技能添加 manifest.json，CLAUDE.md 重写完成

---

## 非目标（此次不做）

- 私有技能注册表（企业版）
- 技能版本回滚
- GUI 界面
- 技能依赖自动安装
