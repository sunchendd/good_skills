---
name: daily-digest
description: 每日日志聚合器。使用时机：当用户说"每日日志汇总"、"今日汇总"、"daily digest"、"汇总今天所有 skill 输出"。汇总 GitHub 动态、思源新笔记、当日所有 skill 输出（arXiv/早报/健身/穿搭/视频），生成日志写入思源笔记。
---

# 📅 每日日志聚合

一天结束时，自动汇总所有数据源生成综合日志。

## 数据源

| 来源 | 内容 |
|------|------|
| GitHub | vllm-ascend 事件 + DeepSeek 新仓库 |
| 思源笔记 | 今日新建文档列表 |
| arXiv | 今日论文精选摘要 |
| 科技早报 | 新闻概要 |
| 健身 | 运动计划摘要 |
| 穿搭 | 穿搭建议摘要 |
| B站精选 | 视频推荐 |
| 无语哥 | 选题概要 |

## 工作流程

```
读取各 skill 输出 + GitHub API + 思源 API → 聚合 Markdown → 写入思源笔记 → Bark
```

## 环境变量

| 变量 | 必需 |
|------|------|
| `GITHUB_TOKEN` | ✅ |
| `SIYUAN_HOST` | ✅ |
| `SIYUAN_TOKEN` | ✅ |
| `DEEPSEEK_API_KEY` | 可选 |

## 用法

```bash
python run_daily_digest.py    # 建议 23:00 cron
```

## 输出

- 本地：`logs/daily_YYYY-MM-DD.md`
- 思源笔记：`/每日日志/YYYY-MM-DD`
