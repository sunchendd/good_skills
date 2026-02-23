# AI 编程工具规则文件支持说明

不同 AI 编程平台支持不同的规则文件名称和格式。本项目已配置支持主流平台。

## 平台支持矩阵

| 平台 | 识别文件 | 状态 | 备注 |
|------|---------|------|------|
| **Claude Code** | `CLAUDE.md`<br>`.claude/CLAUDE.md` | ✅ | 项目根目录和子目录都已配置 |
| **GitHub Copilot** | `.github/copilot-instructions.md` | ✅ | 不识别 CLAUDE.md，需要单独文件 |
| **OpenCode** | `CLAUDE.md`<br>`.opencode/instructions.md` | ✅ | 两个位置都已配置 |
| **Cursor** | `.cursor/rules` | ✅ | 已创建精简配置文件 |
| **Windsurf** | `.windsurfrules` | ✅ | 已创建配置文件 |
| **Zed** | `README.md` | ⚠️ | 可能自动识别 |
| **VS Code AI** | `.github/copilot-instructions.md` | ✅ | 复用 Copilot 配置 |
| **JetBrains AI** | `.github/copilot-instructions.md` | ✅ | 复用 Copilot 配置 |
| **Cline (VS Code)** | `.clinerules` | ⚠️ | 可选创建 |
| **Roo Code** | `.cursorrules` | ⚠️ | 类似 Cursor 格式 |
| **Continue.dev** | `README.md`<br>`docs/*` | ⚠️ | 自动识别 |
| **Codeium** | `README.md` | ⚠️ | 可能自动识别 |

## 当前项目已创建的文件

```
good_skills/
├── CLAUDE.md                          # Claude Code, OpenCode 主文档
├── .claude/CLAUDE.md                   # Claude Code 优先位置（符号链接）
├── .github/copilot-instructions.md     # GitHub Copilot, VS Code AI, JetBrains AI
├── .opencode/instructions.md          # OpenCode（符号链接）
├── .cursor/rules                       # Cursor
├── .windsurfrules                      # Windsurf
└── README.md                           # 通用文档（部分平台识别）
```

## 各平台的配置详情

### Claude Code
- 优先识别 `.claude/CLAUDE.md`
- 也会识别项目根目录的 `CLAUDE.md`
- 识别 `.clauderc.json`（可选）
- ✅ 完全支持

### GitHub Copilot
- **只识别** `.github/copilot-instructions.md`
- 不识别 `CLAUDE.md`
- 在 VS Code、GitHub.com、JetBrains IDEs 中使用
- ✅ 完全支持

### OpenCode
- 识别项目根目录的 `CLAUDE.md`
- 也识别 `.opencode/instructions.md`
- 可能识别 `.opencode/config.yaml`
- ✅ 完全支持

### Cursor
- 识别 `.cursor/rules`
- 可能识别项目根目录的 `CLAUDE.md`
- ⚠️ 不识别 `.github/copilot-instructions.md`
- ✅ 完全支持

### Windsurf (Codeium)
- 识别 `.windsurfrules`
- 可能识别项目根目录的规则文件
- ✅ 完全支持

### 其他平台

#### Zed
- 自动搜索项目文档
- 通常识别 `README.md`
- ⚠️ 可选支持

#### Cline (VS Code 扩展)
- 识别 `.clinerules`
- ✅ 可选创建

#### Roo Code
- 识别 `.cursorrules`
- ✅ 可选创建

#### Continue.dev
- 自动阅读 `README.md`
- 自动阅读 `docs/` 目录
- ⚠️ 自动支持

## 维护策略

### 主文档层次
1. **CLAUDE.md** - 最详细的项目说明（Claude, OpenCode, Continue.dev）
2. **.cursor/rules** - Cursor 特定配置（精简）
3. **.windsurfrules** - Windsurf 特定配置（精简）
4. **.github/copilot-instructions.md** - GitHub Copilot 特定配置（精简）

### 更新建议
- 当更新 `CLAUDE.md` 时，同步更新其他平台的精简版本
- 定期检查是否有新的 AI 工具需要支持
- 对于精简版本，保留最关键的信息即可

### 可选的额外配置

#### Cline 支持
```bash
# 创建 .clinerules 用于 Cline
cp .cursor/rules .clinerules  # 或定制化
```

#### Roo Code 支持
```bash
# 创建 .cursorrules 用于 Roo Code
cp .cursor/rules .cursorrules  # 或定制化
```

## 安装脚本支持

项目提供的安装脚本支持以下平台：
- ✅ Claude Code (`--claude`)
- ✅ GitHub Copilot (`--github-copilot`)
- ✅ OpenCode (`--opencode`)
- ✅ OpenClaw (`--openclaw`)
- ✅ Cursor (`--cursor`)
- ✅ Windsurf (`--windsurf`)
- ✅ Antigravity (`--antigravity`)

```bash
# 安装到所有支持的平台
./install.sh --all

# 更新现有安装
./update.sh --all
```

## 已知限制

1. **格式差异**：某些平台可能需要特定格式（如 JSON、YAML）
2. **文件大小**：部分平台对配置文件大小有限制
3. **缓存**：某些工具可能缓存配置，需要重启才能生效

## 参考

- [Claude Code Skills](https://github.com/anthropics/skills)
- [GitHub Copilot Docs](https://docs.github.com/copilot)
- [Cursor Rules](https://docs.cursor.com/ide/features/cursor-rules)
- [Windsurf Rules](https://docs.codeium.com/windsurf)

---

最后更新：2026-02-23
