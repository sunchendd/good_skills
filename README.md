# 🦞 OpenClaw 自建 Skill 合集

12 个个人定制 skill，覆盖日常生活、内容创作、学术追踪、开发监控全场景。

## 技能概览

### 📡 信息聚合（每日推送）

| Skill | 时间 | 功能 |
|-------|------|------|
| [daily-newsletter](./daily-newsletter/) | 08:30 | 27+ RSS源科技早报 |
| [arxiv-daily](./arxiv-daily/) | 09:00 | arXiv AI 论文精选 |
| [vibe-daily](./vibe-daily/) | 09:30 | AI 编程工具动态 |
| [bili-daily](./bili-daily/) | 10:00 | B站+小红书视频精选 |

### 🎯 内容创作

| Skill | 时间 | 功能 |
|-------|------|------|
| [wuyu-xiaohongshu](./wuyu-xiaohongshu/) | 11:00 | 无语哥小红书内容生成 |

### 💡 生活助手

| Skill | 时间 | 功能 |
|-------|------|------|
| [super-fitness](./super-fitness/) | 07:00 | 三个月减脂计划+每日任务 |
| [super-wardrobe](./super-wardrobe/) | 07:30 | 天气穿搭建议 |
| [chess-advisor](./chess-advisor/) | 按需 | 中国象棋局面分析 |

### 🔧 开发工具

| Skill | 时间 | 功能 |
|-------|------|------|
| [github-watcher](./github-watcher/) | 每2h | GitHub 仓库监控 |
| [tts-skill](./tts-skill/) | 按需 | 中文语音合成 |

### 📊 数据聚合

| Skill | 时间 | 功能 |
|-------|------|------|
| [daily-digest](./daily-digest/) | 23:00 | 每日全数据汇总→思源笔记 |
| [weekly-report](./weekly-report/) | 周六20:00 | AI 周报→思源笔记 |

## 通用依赖

```bash
pip install openai requests feedparser beautifulsoup4 markdown edge-tts
```

## 通用环境变量

```bash
export DEEPSEEK_API_KEY="sk-..."        # 大多数 skill 必需
export QQ_EMAIL_PASSWORD="..."           # 邮件推送
export GITHUB_TOKEN="ghp_..."           # GitHub 相关
export SIYUAN_HOST="http://..."         # 思源笔记
export SIYUAN_TOKEN="..."               # 思源笔记
export BARK_TOKEN="..."                 # iOS Bark 推送
```

## 推送渠道

所有 skill 支持多渠道推送：
- 📧 **QQ 邮箱** → HTML 格式邮件
- 📱 **Bark** → iOS 推送通知
- 📚 **思源笔记** → 知识库归档

---

*Built with OpenClaw + DeepSeek · 2026*
