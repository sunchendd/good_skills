#!/usr/bin/env python3
"""
B站 + 小红书每日 AI 科技视频精选
B站用公开API抓取，小红书用 agent-browser 搜索
"""
import urllib.request, urllib.parse, json, os, re, sys, logging, datetime, time
from openai import OpenAI
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KEYWORDS = ["AI工具", "人工智能", "大模型", "ChatGPT", "DeepSeek", "AI编程"]
BILI_MAX_PER_KW = 8
MAX_AGE_DAYS = 7  # 只保留最近 N 天内的内容
OUTPUT_DIR = Path(__file__).parent / "newsletters"
CUTOFF_DATE = (datetime.datetime.now() - datetime.timedelta(days=MAX_AGE_DAYS)).strftime('%Y-%m-%d')

# ── B站搜索 ───────────────────────────────────────────────────────────────────
def search_bili(keyword: str, page_size: int = 8) -> list[dict]:
    kw_enc = urllib.parse.quote(keyword)
    url = (f"https://api.bilibili.com/x/web-interface/search/all/v2"
           f"?keyword={kw_enc}&page=1&pagesize={page_size}&order=pubdate")
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Referer": "https://www.bilibili.com",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
    except Exception as e:
        logger.warning(f"B站搜索失败 [{keyword}]: {e}")
        return []

    videos = []
    for block in data.get('data', {}).get('result', []):
        if block.get('result_type') == 'video':
            for v in block.get('data', []):
                title = re.sub(r'<[^>]+>', '', v.get('title', ''))
                videos.append({
                    'platform': 'bilibili',
                    'title': title,
                    'bvid': v.get('bvid', ''),
                    'link': f"https://www.bilibili.com/video/{v.get('bvid', '')}",
                    'author': v.get('author', ''),
                    'play': v.get('play', 0),
                    'desc': re.sub(r'<[^>]+>', '', v.get('description', ''))[:200],
                    'duration': v.get('duration', ''),
                    'pubdate': datetime.datetime.fromtimestamp(v.get('pubdate', 0)).strftime('%Y-%m-%d') if v.get('pubdate') else '',
                    'keyword': keyword,
                })
    return videos


def fetch_bili_videos() -> list[dict]:
    seen_bvids = set()
    all_videos = []
    for kw in KEYWORDS:
        for v in search_bili(kw, BILI_MAX_PER_KW):
            if v['bvid'] not in seen_bvids:
                seen_bvids.add(v['bvid'])
                all_videos.append(v)
        time.sleep(0.3)
    # 过滤掉超过 MAX_AGE_DAYS 天的旧内容
    fresh_videos = [v for v in all_videos if v.get('pubdate', '') >= CUTOFF_DATE]
    logger.info(f"✅ B站共抓取 {len(all_videos)} 个视频，过滤后保留 {len(fresh_videos)} 个（{MAX_AGE_DAYS}天内）")
    return fresh_videos


# ── 小红书搜索（DuckDuckGo HTML 搜索）──────────────────────────────────────
def _ddg_search(query: str, num: int = 5) -> list[dict]:
    """用 DuckDuckGo HTML 接口搜索，返回去重后的结果列表"""
    kw_enc = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={kw_enc}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    })
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode('utf-8', errors='ignore')
    # DDG 每个结果块中同一链接会出现 4 次，需去重保序
    links_raw = re.findall(r'uddg=(https[^&"]+)', html)
    seen = set(); links = []
    for l in links_raw:
        d = urllib.parse.unquote(l)
        if d not in seen:
            seen.add(d); links.append(d)
    titles_raw = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
    titles = [re.sub(r'<[^>]+>', '', t).strip() for t in titles_raw]
    results = []
    for i in range(min(num, len(links))):
        results.append({'title': titles[i] if i < len(titles) else query, 'url': links[i]})
    return results


def fetch_xiaohongshu_videos() -> list[dict]:
    """小红书因登录墙无法直接抓取，改用 DuckDuckGo 搜索相关内容"""
    logger.info("📱 搜索小红书AI内容（via DuckDuckGo）...")
    results = []
    this_month = datetime.datetime.now().strftime("%Y年%m月")
    keywords = [
        f"小红书 AI工具推荐 {this_month}",
        f"小红书 DeepSeek Claude {this_month}",
        "小红书 AI编程 vibe coding 2026",
    ]
    for kw in keywords:
        try:
            for item in _ddg_search(kw, num=3):
                results.append({
                    'platform': 'xiaohongshu',
                    'title': item['title'][:80],
                    'link': item['url'],
                    'author': '', 'desc': '', 'keyword': kw,
                })
            time.sleep(0.8)
        except Exception as e:
            logger.warning(f"小红书搜索失败 [{kw}]: {e}")

    seen = set()
    unique = [r for r in results if r['link'] not in seen and not seen.add(r['link'])]
    logger.info(f"✅ 小红书共找到 {len(unique)} 条")
    return unique


# ── DeepSeek 精选 ─────────────────────────────────────────────────────────────
def select_with_deepseek(bili_videos: list, xhs_videos: list) -> dict:
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

    bili_text = "\n".join([
        f"[B{i+1}] {v['title']} | 作者:{v['author']} | 播放:{v['play']} | {v['link']}\n  {v['desc'][:100]}"
        for i, v in enumerate(bili_videos[:30])
    ])
    xhs_text = "\n".join([
        f"[X{i+1}] {v['title']} | {v['link']}"
        for i, v in enumerate(xhs_videos[:20])
    ])

    prompt = f"""你是 AI/科技内容筛选专家。从以下 B站视频和"AI社交内容"（来自搜索到的中文博客/知乎/微信等关于小红书AI趋势的文章）中，分别精选最有价值的内容。

筛选标准：
1. 内容具体，有实际工具推荐或技术干货
2. 不是营销广告或标题党
3. B站优先选播放量高的
4. 覆盖不同类型（工具使用/技术解析/行业动态）
5. AI社交内容：接受任何提到小红书AI趋势或AI工具的中文文章/帖子，无需必须是xiaohongshu.com域名

输出 JSON：
{{
  "bilibili": [
    {{
      "rank": 1,
      "title": "视频标题",
      "zh_summary": "50字以内摘要，说明视频核心内容",
      "highlight": "一句话亮点",
      "link": "链接",
      "author": "作者",
      "play": 播放量数字,
      "category": "分类（AI工具/技术解析/行业动态/实战教程）"
    }}
  ],
  "xiaohongshu": [
    {{
      "rank": 1,
      "title": "标题",
      "zh_summary": "摘要",
      "highlight": "亮点",
      "link": "链接",
      "category": "分类"
    }}
  ]
}}

B站视频列表：
{bili_text}

AI社交/小红书相关内容列表（包含中文博客/知乎/微信等讨论小红书AI趋势的文章，如为空则输出空数组）：
{xhs_text if xhs_text.strip() else "（暂无数据）"}"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        timeout=90,
    )
    return json.loads(resp.choices[0].message.content)


# ── 格式化 ────────────────────────────────────────────────────────────────────
def format_newsletter(selected: dict) -> str:
    today = datetime.datetime.now().strftime("%Y年%m月%d日")
    now = datetime.datetime.now().strftime("%H:%M")
    bili_list = selected.get("bilibili", [])
    xhs_list = selected.get("xiaohongshu", [])

    cat_icons = {"AI工具": "🛠️", "技术解析": "🔬", "行业动态": "📡", "实战教程": "🎯"}

    lines = [
        f"# 📺 每日 AI 科技视频精选",
        f"**{today}** | B站 {len(bili_list)} 个 · 小红书 {len(xhs_list)} 条 | {now}",
        "", "---", "",
        f"## 📺 B站精选（{len(bili_list)} 个）", "",
    ]
    for v in bili_list:
        icon = cat_icons.get(v.get('category', ''), '🎬')
        lines += [
            f"### {icon} {v['rank']}. {v['title']}",
            f"**{v.get('highlight', '')}**  ",
            f"👤 {v.get('author','')} | 👀 {v.get('play',0):,} 播放 | 📂 {v.get('category','')}",
            "",
            v.get('zh_summary', ''),
            "",
            f"🔗 {v['link']}",
            "", "---", "",
        ]

    if xhs_list:
        lines += [f"## 📱 AI社交精选（{len(xhs_list)} 条）", ""]
        for v in xhs_list:
            icon = cat_icons.get(v.get('category', ''), '📌')
            lines += [
                f"### {icon} {v['rank']}. {v['title']}",
                f"**{v.get('highlight', '')}**",
                "",
                v.get('zh_summary', ''),
                "",
                f"🔗 {v['link']}",
                "", "---", "",
            ]
    else:
        lines += ["## 📱 AI社交", "", "（今日暂无相关内容）", "", "---", ""]

    lines.append(f"*每日 AI 视频精选 · {today} {now}*")
    return "\n".join(lines)


# ── 发送 ──────────────────────────────────────────────────────────────────────
def send_email(content, subject):
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import markdown as md
    sender = os.environ.get("EMAIL_SENDER", "").strip()
    recipients = [item.strip() for item in os.environ.get("EMAIL_RECIPIENTS", "").split(",") if item.strip()]
    password = os.environ.get("QQ_EMAIL_PASSWORD")
    if not sender or not recipients or not password: return False
    html_body = md.markdown(content, extensions=['markdown.extensions.tables','markdown.extensions.nl2br'])
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
body{{font-family:-apple-system,'PingFang SC',sans-serif;line-height:1.7;color:#333;max-width:800px;margin:0 auto;padding:20px;background:#f5f5f5}}
.c{{background:#fff;padding:28px;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.1)}}
h1{{color:#fb7299;border-bottom:3px solid #fb7299;padding-bottom:10px}}
h2{{color:#333;margin-top:28px;padding:6px 12px;background:#fff0f5;border-left:4px solid #fb7299;border-radius:4px}}
h3{{color:#444}}a{{color:#fb7299;text-decoration:none}}hr{{border:none;border-top:1px solid #eee;margin:20px 0}}
</style></head><body><div class="c">{html_body}</div></body></html>"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject; msg["From"] = sender; msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(content, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP("smtp.qq.com", 587) as s:
            s.ehlo(); s.starttls(context=ctx); s.login(sender, password); s.sendmail(sender, recipients, msg.as_bytes())
        logger.info("✅ 邮件发送成功"); return True
    except Exception as e:
        logger.error(f"❌ 邮件失败: {e}"); return False


def send_bark(title, body):
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from bark_client import bark_notify
        bark_notify(title=title, body=body, sound="minuet", group="video")
        logger.info("✅ Bark 已发送")
    except Exception as e:
        logger.warning(f"⚠️ Bark 失败: {e}")


def main():
    no_send = "--no-send" in sys.argv
    logger.info("=" * 50); logger.info("📺 每日 AI 视频精选启动"); logger.info("=" * 50)

    bili_videos = fetch_bili_videos()
    xhs_videos = fetch_xiaohongshu_videos()
    selected = select_with_deepseek(bili_videos, xhs_videos)
    content = format_newsletter(selected)

    OUTPUT_DIR.mkdir(exist_ok=True)
    fname = OUTPUT_DIR / f"video_{datetime.datetime.now().strftime('%Y%m%d')}.md"
    fname.write_text(content, encoding='utf-8')
    print(content[:3000])
    logger.info(f"💾 已保存: {fname}")

    if no_send: return

    today = datetime.datetime.now().strftime("%Y年%m月%d日")
    bili_count = len(selected.get("bilibili", []))
    xhs_count = len(selected.get("xiaohongshu", []))
    send_email(content, f"📺 每日 AI 视频精选 {today}（B站{bili_count}+小红书{xhs_count}）")
    send_bark(title=f"📺 今日 AI 视频精选 {today}", body=f"B站精选{bili_count}个 · 小红书{xhs_count}条 · 已发送邮件")
    logger.info("🎉 完成")

if __name__ == "__main__":
    main()
