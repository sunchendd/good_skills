# Good Skills 安装指南 / Installation Guide

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English

### Quick Start

The easiest way to install all Good Skills to your AI coding assistants is using the remote installation script:

```bash
curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash
```

This single command will:
1. Clone the repository to `~/.good_skills`
2. Install all skills to all supported platforms using symbolic links

#### Remote Installation Options

```bash
# Install to specific platforms
curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash -s -- --github-copilot --claude

# Install to current project directory
curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash -s -- --all --project

# Install to custom directory
curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash -s -- --dir ~/my-skills --all

# View all options
curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash -s -- --help
```

### Local Installation

If you prefer to clone the repository manually:

```bash
git clone https://github.com/sunchendd/good_skills.git
cd good_skills
./install.sh --all
```

This will install all skills to all supported platforms using symbolic links.

### Installation Options

#### Install to All Platforms
```bash
./install.sh --all
```

#### Install to Specific Platforms
```bash
# GitHub Copilot only
./install.sh --github-copilot

# Claude Code only
./install.sh --claude

# Codex only
./install.sh --codex

# Multiple specific platforms
./install.sh --github-copilot --claude --codex --opencode
```

#### Project vs Global Installation

By default, skills are installed globally (in your home directory). You can also install them to a specific project:

```bash
# Global installation (default)
./install.sh --all --global

# Project installation
cd /path/to/your/project
/path/to/good_skills/install.sh --all --project
```

### Supported Platforms

| Platform | Global Path | Project Path |
|----------|-------------|--------------|
| **GitHub Copilot** | `~/.copilot/skills/` | `.github/skills/` |
| **Claude Code** | `~/.claude/skills/` | `.claude/skills/` |
| **OpenCode** | `~/.config/opencode/skill/` | `.opencode/skill/` |
| **Antigravity** | `~/.gemini/antigravity/skills/` | `.agent/skills/` |
| **Codex** | `~/.codex/skills/` | `.codex/skills/` |
| **Cursor** | `~/.cursor/skills/` | `.cursor/skills/` |
| **Windsurf** | `~/.codeium/windsurf/skills/` | `.windsurf/skills/` |
| **Trae** | Manual configuration required | `.trae/skills/` |

### Uninstallation

To remove installed skills:

```bash
# Uninstall from all platforms
./uninstall.sh --all

# Uninstall from specific platforms
./uninstall.sh --github-copilot --claude --codex
```

### Update

To update existing installations with new skills and fix broken links:

```bash
# Update all platforms
./update.sh --all

# Only add missing skills (don't modify existing links)
./update.sh --all --add-missing

# Update specific platform
./update.sh --openclaw

# Preview changes without making them
./update.sh --all --dry-run
```

The update function will:
- Add new skills from the repository that are missing in target platforms
- Fix broken links that point to `~/.good_skills/`
- Preserve external skills and real directories (won't overwrite them)

### Key Features

- **Symbolic Links**: Uses symbolic links instead of copying files, so updates to skills in the repository automatically reflect in all installations
- **Compatibility**: Detects existing skill installations and asks before overwriting
- **Multi-Platform**: Install to multiple platforms with a single command
- **Flexible**: Supports both global and project-level installations

### How It Works

1. The script scans the repository for directories containing `SKILL.md` files
2. For each platform selected, it creates the appropriate directory structure
3. It creates symbolic links from the platform's skill directory to the repository
4. Existing installations are detected and handled gracefully

### Troubleshooting

**Q: I see a warning about an existing directory**

A: The script detected that a skill already exists at the target location. You can choose to:
- Skip it (keep the existing installation)
- Replace it (remove existing and create a symbolic link)

**Q: Skills aren't showing up in my AI assistant**

A: Make sure:
1. The symbolic links were created correctly: `ls -la ~/.copilot/skills/` (or relevant path)
2. Your AI assistant supports the skills directory
3. Try restarting your AI assistant/IDE

**Q: Can I install individual skills?**

A: The script installs all skills together. To install individual skills, use manual installation or the `npx add-skill` command mentioned in the main README.

---

<a name="chinese"></a>
## 中文

### 快速开始

最简单的方式，使用远程安装脚本一键安装所有 Good Skills 到您的 AI 编程助手：

```bash
curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash
```

这条命令将：
1. 将仓库克隆到 `~/.good_skills`
2. 使用符号链接将所有技能安装到所有支持的平台

#### 远程安装选项

```bash
# 安装到特定平台
curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash -s -- --github-copilot --claude

# 安装到当前项目目录
curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash -s -- --all --project

# 安装到自定义目录
curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash -s -- --dir ~/my-skills --all

# 查看所有选项
curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash -s -- --help
```

### 本地安装

如果您希望手动克隆仓库：

```bash
git clone https://github.com/sunchendd/good_skills.git
cd good_skills
./install.sh --all
```

这将使用符号链接的方式将所有技能安装到所有支持的平台。

### 安装选项

#### 安装到所有平台
```bash
./install.sh --all
```

#### 安装到特定平台
```bash
# 仅 GitHub Copilot
./install.sh --github-copilot

# 仅 Claude Code
./install.sh --claude

# 多个特定平台
./install.sh --github-copilot --claude --opencode
```

#### 项目级 vs 全局安装

默认情况下，技能会安装到全局（您的用户主目录）。您也可以安装到特定项目：

```bash
# 全局安装（默认）
./install.sh --all --global

# 项目安装
cd /path/to/your/project
/path/to/good_skills/install.sh --all --project
```

### 支持的平台

| 平台 | 全局路径 | 项目路径 |
|------|---------|---------|
| **GitHub Copilot** | `~/.copilot/skills/` | `.github/skills/` |
| **Claude Code** | `~/.claude/skills/` | `.claude/skills/` |
| **OpenCode** | `~/.config/opencode/skill/` | `.opencode/skill/` |
| **Antigravity** | `~/.gemini/antigravity/skills/` | `.agent/skills/` |
| **Cursor** | `~/.cursor/skills/` | `.cursor/skills/` |
| **Windsurf** | `~/.codeium/windsurf/skills/` | `.windsurf/skills/` |
| **Trae** | 需要手动配置 | `.trae/skills/` |

### 卸载

移除已安装的技能：

```bash
# 从所有平台卸载
./uninstall.sh --all

# 从特定平台卸载
./uninstall.sh --github-copilot --claude
```

### 更新

更新现有安装，添加新技能并修复损坏的链接：

```bash
# 更新所有平台
./update.sh --all

# 仅添加缺失的技能（不修改现有链接）
./update.sh --all --add-missing

# 更新特定平台
./update.sh --openclaw

# 预览将要进行的更改（不实际执行）
./update.sh --all --dry-run
```

更新功能会：
- 添加当前仓库中存在但目标平台缺失的新技能
- 修复指向 `~/.good_skills/` 的损坏链接
- 保留用户自定义的外部技能和真实目录（不覆盖）

### 主要特性

- **符号链接**：使用符号链接而非复制文件，因此仓库中的技能更新会自动反映到所有安装位置
- **兼容性**：检测现有技能安装，询问后再覆盖
- **多平台**：单条命令安装到多个平台
- **灵活性**：支持全局和项目级安装

### 工作原理

1. 脚本扫描仓库中包含 `SKILL.md` 文件的目录
2. 对于每个选定的平台，创建相应的目录结构
3. 从平台的技能目录创建符号链接到仓库
4. 优雅地检测和处理现有安装

### 故障排除

**问：我看到关于现有目录的警告**

答：脚本检测到目标位置已存在技能。您可以选择：
- 跳过（保留现有安装）
- 替换（删除现有并创建符号链接）

**问：我的 AI 助手中没有显示技能**

答：请确保：
1. 符号链接创建正确：`ls -la ~/.copilot/skills/`（或相关路径）
2. 您的 AI 助手支持技能目录功能
3. 尝试重启您的 AI 助手/IDE

**问：可以只安装单个技能吗？**

答：本脚本会一起安装所有技能。要安装单个技能，请使用手动安装或主 README 中提到的 `npx add-skill` 命令。

### 更多信息

更多关于技能的详细信息，请查看主 [README.md](README.md)。
