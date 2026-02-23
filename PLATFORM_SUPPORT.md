# 平台规则文件支持说明

不同 AI 编程平台支持不同的规则文件名称：

## Claude Code
- ✅ 识别 `CLAUDE.md` (项目根目录)
- ✅ 识别 `.claude/CLAUDE.md` (优先)
- ✅ 识别 `.clauderc.json`

## GitHub Copilot
- ✅ 识别 `.github/copilot-instructions.md`
- ⚠️ 不识别 `CLAUDE.md`

## OpenCode
- ✅ 识别 `.opencode/instructions.md`
- ✅ 可能识别 `CLAUDE.md`
- ✅ 可能识别 `.opencode/config.yaml`

## Cursor
- ✅ 识别 `.cursor/rules`
- ✅ 可能识别 `CLAUDE.md`
- ⚠️ 不识别 `.github/copilot-instructions.md`

## Windsurf
- ✅ 识别 `.windsurfrules`
- ✅ 可能识别项目根目录的规则文件

## 当前项目状态

✅ **Claude Code**: 支持 (CLAUDE.md 已存在，.claude/CLAUDE.md 已创建)
✅ **GitHub Copilot**: 支持 (.github/copilot-instructions.md 已创建)
✅ **OpenCode**: 支持 (.opencode/instructions.md 已创建)

## 建议的跨平台兼容方案

为了确保所有平台都能识别项目规则，建议：

1. **主文档**: `CLAUDE.md` - 完整的项目说明 (Claude, OpenCode 识别)
2. **GitHub Copilot**: `.github/copilot-instructions.md` - 精简版本
3. **Cursor**: `.cursor/rules` - 可选创建
4. **Windsurf**: `.windsurfrules` - 可选创建

## 维护策略

由于不同平台可能需要不同的格式：
- 主文档 `CLAUDE.md` 保持详细和完整
- `.github/copilot-instructions.md` 保持简洁，只包含关键信息
- 当更新 `CLAUDE.md` 时，注意同步更新其他平台相关的文件
