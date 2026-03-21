---
name: weekly-report
description: >-
  自动周报生成。Use when "周报", "本周工作总结", "weekly report", "自动生成周报".
  汇总本周日历、思源笔记、GitHub 活动，AI 生成工作总结+时间分析+下周规划，写入思源笔记。
---

# 📋 自动周报

汇总一周数据，AI 生成结构化工作周报。

## 数据源

- 📅 macOS 日历（本周事件）
- 📝 思源笔记（本周文档）
- 🐙 GitHub（代码活动）
- 📊 各 skill 产出统计

## 工作流程

```
日历API + 思源SQL + GitHub API → DeepSeek 分析总结 → 周报Markdown → 思源笔记
```

## 环境变量

| 变量 | 必需 |
|------|------|
| `DEEPSEEK_API_KEY` | ✅ |
| `GITHUB_TOKEN` | ✅ |
| `SIYUAN_HOST` | ✅ |
| `SIYUAN_TOKEN` | ✅ |

## 用法

```bash
python run_weekly_report.py    # 建议周六 20:00 cron
```

## 输出

- 思源笔记：`/周报/YYYY-WXX`
