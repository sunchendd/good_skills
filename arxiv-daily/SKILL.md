---
name: arxiv-daily
description: 每日 arXiv AI 论文精选系统。自动从 arXiv 抓取最新 cs.AI/cs.LG/cs.CL/cs.CV/cs.RO 论文，用 DeepSeek 评分筛选，生成中文摘要，通过邮件和 Bark 推送。
---

# 🔬 arXiv 每日 AI 论文精选

从 arXiv 抓取 5 大 AI 领域最新论文，经 DeepSeek 智能评分筛选，生成中文摘要并推送。

## 工作流程

```
arXiv API (100篇) → DeepSeek 分批评分(≥0.6) → 按方向分类 → Markdown简报 → 邮件+Bark
```

## 覆盖领域

cs.AI · cs.LG · cs.CL · cs.CV · cs.RO

## 评分标准

- **创新性** (35%) · **实用性** (30%) · **影响力** (20%) · **完整性** (15%)

## 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `DEEPSEEK_API_KEY` | ✅ | DeepSeek API |
| `QQ_EMAIL_PASSWORD` | 发邮件 | QQ SMTP 授权码 |
| `BARK_TOKEN` | 可选 | Bark iOS 推送 |

## 用法

```bash
python run_arxiv_daily.py              # 完整流程
python run_arxiv_daily.py --no-send    # 只生成不发送
```

## 输出

`newsletters/arxiv_YYYYMMDD_HHMM.md`

## 文件结构

```
arxiv-daily/
├── SKILL.md              # 本文件
├── run_arxiv_daily.py    # 入口（调度+推送）
├── arxiv_fetcher.py      # 核心（抓取+评分+格式化）
├── bark_client.py        # Bark 推送
└── newsletters/          # 输出目录
```
