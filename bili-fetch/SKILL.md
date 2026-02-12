---
name: bili-fetch
description: Programmatic workflow to find B站 videos by keyword, fetch metadata and thumbnails, and optionally capture page screenshots using the OpenClaw browser relay. Use when the user asks to fetch B站 video lists, thumbnails, or screenshots (search -> download thumbnails -> try page screenshot via browser relay -> fallback to thumbnails).
---

# bili-fetch

Quick start

1. Use the `scripts/search_and_fetch.py` script to search B站 (public endpoints) and fetch metadata for matching videos.
2. The script downloads thumbnails to a workspace folder and writes a JSON results file with title, link, thumbnail path, and short description.
3. If the browser relay is available and attached, use `scripts/screenshot_pages.py` to capture rendered screenshots of individual video pages.
4. Results can be sent to the user via Telegram or saved to the workspace.

When to use

- Use this skill when the user requests a list of B站 videos (by keyword, channel, or category), thumbnails, or screenshots.
- Prefer the skill over ad-hoc scraping because it encapsulates retries, fallbacks, and consistent output formatting.

Bundled resources

- scripts/search_and_fetch.py — search and download metadata + thumbnails
- scripts/screenshot_pages.py — (optional) use browser relay to screenshot pages when a tab is attached

Examples

- "Find 10 popular B站 videos about '翻跳 舞蹈' and send thumbnails."
- "Grab today's top 10 B站 popular videos, download thumbnails and send them."