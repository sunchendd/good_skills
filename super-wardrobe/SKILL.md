---
name: super-wardrobe
description: 每日穿搭建议推送。使用时机：当用户说"今天穿什么"、"帮我搭配衣服"、"穿搭建议"、"wardrobe"。自动获取杭州实时天气，AI 生成上衣/裤子/鞋/帽/手表/配色/是否带伞，邮件+Bark 推送。
---

# 👔 Super 衣橱

杭州实时天气 + AI 穿搭建议，每日推送完整穿搭方案。

## 工作流程

```
wttr.in 天气API → 解析温度/降雨/UV → DeepSeek 生成穿搭 → 邮件+Bark
```

## 输出内容

- 🌤️ 天气总结 · 👔 上衣 · 👖 裤子 · 👟 鞋子 · 🧢 配件
- 🎨 配色方案（2-3套）· ☂️ 是否带伞 · 💡 穿搭贴士

## 环境变量

| 变量 | 必需 |
|------|------|
| `DEEPSEEK_API_KEY` | ✅ |
| `QQ_EMAIL_PASSWORD` | 发邮件 |

## 用法

```bash
python run_wardrobe.py              # 正常运行
python run_wardrobe.py --no-send    # 只生成不发送
```

## 文件结构

```
super-wardrobe/
├── SKILL.md
├── run_wardrobe.py         # 入口
├── wardrobe_advisor.py     # 天气+穿搭核心
├── bark_client.py
└── outfits/                # 每日穿搭输出
```
