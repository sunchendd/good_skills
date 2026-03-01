---
name: vibe-daily
description: 每日 AI 编程工具动态。搜索 B站/Reddit 最新 AI 编程工具评测、Cursor/Claude Code/Copilot 教程，DeepSeek 精选并推送。
---

# 🚀 Vibe Coding 每日精选

追踪 AI 编程工具动态，精选最有价值的教程和评测。

## 关注方向

Cursor · Claude Code · GitHub Copilot · Windsurf · AI IDE · MCP · Agent Coding

## 工作流程

```
B站搜索 + Reddit/HN 搜索 → DeepSeek 评分精选 → Markdown简报 → 邮件+Bark
```

## 环境变量

| 变量 | 必需 |
|------|------|
| `DEEPSEEK_API_KEY` | ✅ |
| `QQ_EMAIL_PASSWORD` | 发邮件 |

## 用法

```bash
python run_vibe_daily.py              # 完整流程
python run_vibe_daily.py --no-send    # 只生成
```

## 输出

`newsletters/vibe_YYYYMMDD.md`
