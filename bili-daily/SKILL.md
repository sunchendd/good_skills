---
name: bili-daily
description: B站+小红书每日 AI 科技视频精选。多关键词搜索B站视频，Brave 搜索小红书内容，DeepSeek 评分精选，邮件+Bark 推送。
---

# 📺 每日 AI 视频精选

B站 + 小红书双平台 AI 科技内容精选。

## 搜索关键词

AI工具 · 人工智能 · 大模型 · ChatGPT · DeepSeek · AI编程

## 工作流程

```
B站API多关键词搜索 → 小红书(Brave搜索) → DeepSeek精选 → 分类简报 → 邮件+Bark
```

## 环境变量

| 变量 | 必需 |
|------|------|
| `DEEPSEEK_API_KEY` | ✅ |
| `QQ_EMAIL_PASSWORD` | 发邮件 |

## 用法

```bash
python run_bili_daily.py              # 完整流程
python run_bili_daily.py --no-send    # 只生成
```

## 输出

`newsletters/video_YYYYMMDD.md`
