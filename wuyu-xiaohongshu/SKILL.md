---
name: wuyu-xiaohongshu
description: 无语哥小红书内容生成器。搜索奇葩/无语新闻，生成小红书封面文案+正文卡片+标签，邮件+Bark推送，保存思源笔记。
---

# 😤 无语哥小红书内容生成器

自动搜索奇葩新闻 → 生成小红书格式内容 → 多渠道推送。

## 工作流程

```
Brave搜索奇葩新闻 → DeepSeek 筛选+文案 → 封面标题+正文卡片+TTS → 邮件+Bark+思源
```

## 输出内容

- 📝 封面文案（标题+副标题）
- 📄 正文卡片（无语哥点评风格）
- 🏷️ 标签组合
- 🎙️ TTS 语音版本（可选）
- 📚 自动保存到思源笔记

## 环境变量

| 变量 | 必需 |
|------|------|
| `DEEPSEEK_API_KEY` | ✅ |
| `QQ_EMAIL_PASSWORD` | 发邮件 |
| `SIYUAN_HOST` | 保存笔记 |
| `SIYUAN_TOKEN` | 保存笔记 |

## 用法

```bash
python run_wuyu.py              # 完整流程
python run_wuyu.py --no-send    # 只生成
```
