---
name: chess-advisor
description: 中国象棋顾问。使用时机：当用户说"分析这个棋局"、"象棋走法"、"下一步怎么走"、"chess"，或上传棋盘截图时。分析棋盘识别局面，给出最佳走法、战术分析和学习要点。支持图片路径/URL/base64。
---

# ♟️ 中国象棋顾问

AI 视觉分析棋盘截图，给出专业级走法建议。

## 功能

- 🔍 棋盘识别（红方/黑方棋子分布）
- ⚖️ 局势评估（优势/均势/劣势）
- 🎯 最佳走法推荐 + 备选走法
- ⚠️ 战术识别（将军/捉子/牵制）
- 💡 学习要点

## 用法

```bash
python chess_advisor.py screenshot.png 红方
python chess_advisor.py https://example.com/board.jpg 黑方 "怎么破解这个局面？"
```

在 OpenClaw 中：直接发送棋盘截图 + "怎么走" 即可。

## 环境变量

| 变量 | 必需 |
|------|------|
| `DEEPSEEK_API_KEY` | ✅（需视觉能力） |
