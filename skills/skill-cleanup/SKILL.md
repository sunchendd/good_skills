---
name: skill-cleanup
description: >-
  清理所有 AI 代理配置目录中的断裂 skill 符号链接。Use when "清理skill",
  "cleanup skills", "移除无效skill", "删除失效链接", "skill链接清理".
  扫描 .agent/.agents/.claude/.opencode/.copilot/.codex/.cursor/.iflow/.openclaw 等目录。
---

# Skill Cleanup: 清理断裂的 Skill 符号链接

扫描所有 AI 代理配置目录，查找并删除断裂的 skill 符号链接，保持开发环境整洁。

## 扫描目录

| 代理 | 目录 |
|------|------|
| Agent | `~/.agent/skills/` |
| Agents | `~/.agents/skills/` |
| Claude Code | `~/.claude/skills/` |
| OpenCode | `~/.config/opencode/skill/`, `~/.config/opencode/skills/`, `~/.opencode/skills/` |
| Copilot | `~/.copilot/skills/` |
| Codex | `~/.codex/skills/`, `~/.codex/tmp/` |
| Cursor | `~/.cursor/skills/` |
| iFlow | `~/.iflow/skills/` |
| OpenClaw | `~/.openclaw/skills/`, `~/.openclaw/workspace/skills/` |
| Windsurf | `~/.windsurf/skills/` |
| Gemini CLI | `~/.gemini-cli/skills/` |
| Antigravity | `~/.antigravity/skills/` |

## 使用方式

```bash
# 预览将删除的链接（不实际删除）
python3 scripts/cleanup_skills.py --dry-run
python3 scripts/cleanup_skills.py -n

# 实际删除
python3 scripts/cleanup_skills.py

# 通过 npm
npm run cleanup
```

## 执行流程

1. 递归扫描所有代理配置目录
2. 检测每个符号链接的目标是否存在
3. 删除目标不存在的断裂链接
4. 清理删除后留下的空目录
5. 输出每个目录中处理的断裂链接数量

## 注意事项

- 仅删除断裂的符号链接，不影响有效文件和目录
- 操作不可逆，建议先使用 `--dry-run` 预览
- 并非所有目录都必须存在，脚本会跳过不存在的目录
