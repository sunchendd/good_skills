---
name: tts-skill
description: 文字转语音。基于免费 edge-tts，支持 14 个中文音色（普通话/方言）、20+ 情感风格、语速调节，输出 MP3。
---

# 🎙️ TTS 文字转语音

基于微软 edge-tts 的免费高质量中文语音合成。

## 音色列表

| 名称 | 说明 | 适用场景 |
|------|------|---------|
| xiaoxiao | 温柔亲切女声 | 播报/故事 |
| yunyang | 专业播音男声 | 正式/新闻 |
| yunxi | 自然流畅男声 | 读文章 |
| xiaobei | 东北方言女声 | 搞笑日常 |
| yunjian | 运动激情男声 | 体育/励志 |

## 情感风格

`neutral` · `chat` · `news` · `excited` · `friendly` · `sad` · `angry` · `serious` · `poetry` · `gentle` · `affectionate`...

## 用法

```bash
python tts.py "今天天气不错" -v yunyang -s news --play
python tts.py "太离谱了！" -v xiaobei -s excited -r +20%
python tts.py --file input.txt -o output.mp3
python tts.py --list    # 列出所有音色
```

## 依赖

```bash
pip install edge-tts
```
