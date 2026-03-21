---
name: daily-newsletter
description: 每日科技早报。27+ RSS源并发抓取，智能分类（AI/区块链/游戏/科技/金融），质量评分过滤，可选 DeepSeek 英译中，邮件+Bark 推送。
---

# 📰 每日科技早报

多源 RSS 聚合 → 智能分类 → 质量评分 → 邮件推送的完整新闻流水线。

## 工作流程

```
27+ RSS并发 → MD5去重 → 关键词分类 → 质量评分 → 可选翻译 → HTML邮件+Bark
```

## 新闻分类

| 分类 | 来源示例 |
|------|---------|
| 🤖 AI推理 | 量子位、机器之心、OpenAI Blog |
| 🔗 区块链 | CoinTelegraph、Decrypt |
| 🎮 游戏 | Polygon、GamesIndustry |
| 🚀 技术突破 | TechCrunch、Ars Technica |
| 🇨🇳 中国科技 | 36氪、IT之家、钛媒体 |
| 💰 投资金融 | 财经媒体 |

## 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `QQ_EMAIL_PASSWORD` | 发邮件 | QQ SMTP 授权码 |
| `DEEPSEEK_API_KEY` | 可选 | 英文新闻翻译 |
| `NEWS_START_DATE` | 可选 | 日期范围起始 |

## 用法

```bash
python run_daily_newsletter.py --now       # 立即生成
python run_daily_newsletter.py --schedule  # 每天定时
python run_daily_newsletter.py --test      # 测试模式
```

## 文件结构

```
daily-newsletter/
├── SKILL.md
├── daily_newsletter.py       # 主模块
├── newsletter_config.py      # 源+分类配置
├── email_sender.py           # SMTP 发送
├── run_daily_newsletter.py   # 调度入口
├── bark_client.py
└── newsletters/
```
