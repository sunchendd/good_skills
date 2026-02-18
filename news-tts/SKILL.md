---
name: news-tts
description: Generate a short spoken news summary (TTS) and send as Telegram voice message. Use when the user asks for a brief audio news bulletin. Supports scheduling and customizable topics/regions.
---

# news-tts

Quick start

1. Run the script `scripts/generate_news_tts.py` with options like `--region cn --topic general --out /path/to/output.mp3`.
2. The script will fetch headlines (using web-search if configured), synthesize TTS audio, and save the file. When run inside OpenClaw it can send the audio to Telegram using the configured channel.

When to use

- Use when the user asks for a short audio news summary.
- Works best when the gateway has a web-search API key configured for live headlines; otherwise it will use an offline summary template.

Bundled resources

- scripts/generate_news_tts.py — script to fetch headlines, generate TTS, and (optionally) send via Telegram.

Examples

- "Give me a 60-second news voice summary for China"
- "Send today's morning news voice to my Telegram"
