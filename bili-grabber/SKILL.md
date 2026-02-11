---
name: bili-grabber
description: Grab Bilibili search results and video metadata (use when user asks to fetch video lists, download covers, and send results as chat messages).
---

# bili-grabber

Quick skill to fetch Bilibili search results and gather metadata.

When to use
- Use this skill when the user asks: "抓 N 条 <关键词> 的 B 站视频并把结果发给我" or similar.

What it provides
- scripts/grab_bili_search.py — a runnable script that fetches search results, downloads covers, and prints summary to stdout (no JSON/CSV by default).

Usage
- Run the script from the workspace root:
  python3 skills/bili-grabber/scripts/grab_bili_search.py --keyword "跳舞" --count 10

Notes
- This skill is intentionally conservative: by default it saves covers to result/bili_covers/ and prints entries to stdout instead of writing JSON/CSV files. Adjust script flags to change behavior.
