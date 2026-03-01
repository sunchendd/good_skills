#!/usr/bin/env python3
"""
无语哥 - 每日无语事小红书内容生成器
搜索最新奇葩/无语新闻 → AI生成小红书笔记（封面文案+正文卡片+标签）
→ 邮件+Bark+思源笔记
"""
import urllib.request, urllib.parse, json, os, sys, logging, datetime, re
from pathlib import Path
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent / "notes"
SIYUAN_HOST = os.environ.get("SIYUAN_HOST", "http://192.168.3.32:6806")
SIYUAN_TOKEN = os.environ.get("SIYUAN_TOKEN", "")
TODAY = datetime.date.today().strftime("%Y-%m-%d")
TODAY_ZH = datetime.datetime.now().strftime("%Y年%m月%d日")

# ── 抓取奇葩新闻 ──────────────────────────────────────────────────────────────
def fetch_wuyu_news() -> list[dict]:
    """多源抓取无语/奇葩/社会新闻"""
    news = []

    # 1. 今日头条热榜
    try:
        url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"})
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read())
        for item in d.get('data', [])[:20]:
            title = item.get('Title', '')
            if title:
                news.append({'source': '今日头条', 'title': title, 'url': item.get('Url', ''), 'hot': item.get('HotValue', 0)})
        logger.info(f"✅ 今日头条: {len([n for n in news if n['source']=='今日头条'])} 条")
    except Exception as e:
        logger.warning(f"头条失败: {e}")

    # 2. 36Kr 快讯
    try:
        req = urllib.request.Request('https://36kr.com/api/newsflash?per_page=20',
            headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://36kr.com'})
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read())
        for item in d.get('data', {}).get('items', [])[:15]:
            title = item.get('title', '') or item.get('itemTitle', '')
            if title:
                news.append({'source': '36Kr', 'title': title, 'url': item.get('itemUrl', ''), 'hot': 0})
        logger.info(f"✅ 36Kr: {len([n for n in news if n['source']=='36Kr'])} 条")
    except Exception as e:
        logger.warning(f"36Kr失败: {e}")

    # 3. IT之家 RSS
    try:
        req = urllib.request.Request('https://www.ithome.com/rss/', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as r:
            content = r.read().decode('utf-8', errors='ignore')
        titles = re.findall(r'<title><!\[CDATA\[([^\]]+)\]\]></title>', content)
        links = re.findall(r'<link>https://www\.ithome\.com/0/[^<]+</link>', content)
        for i, title in enumerate(titles[1:16]):
            url = links[i].replace('<link>', '').replace('</link>', '') if i < len(links) else ''
            news.append({'source': 'IT之家', 'title': title, 'url': url, 'hot': 0})
        logger.info(f"✅ IT之家: {len([n for n in news if n['source']=='IT之家'])} 条")
    except Exception as e:
        logger.warning(f"IT之家失败: {e}")

    logger.info(f"📰 共获取 {len(news)} 条新闻")
    return news


# ── DeepSeek 选题+生成 ────────────────────────────────────────────────────────
def generate_xiaohongshu_posts(news: list[dict]) -> list[dict]:
    """从新闻中选出3-5条最无语的，逐条生成小红书内容"""
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    news_text = "\n".join([f"[{i+1}] [{n['source']}] {n['title']}" for i, n in enumerate(news[:40])])

    # Step1: 选出最无语的5条
    select_resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": f"""从以下新闻中选出5条最无语/最奇葩/最有网络讨论价值的，只输出序号和标题，格式：
1. [序号] 标题
2. [序号] 标题
...

新闻列表：
{news_text}"""}],
        timeout=30,
    )
    selected_text = select_resp.choices[0].message.content
    import re as _re
    indices = [int(m)-1 for m in _re.findall(r'\[(\d+)\]', selected_text) if int(m)-1 < len(news)]
    if not indices:
        indices = list(range(min(5, len(news))))
    selected_news = [news[i] for i in indices[:5]]
    logger.info(f"✅ 选出 {len(selected_news)} 条新闻进行创作")

    posts = []
    for sn in selected_news:
        try:
            resp = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": f"""你是"无语哥"小红书博主，风格犀利幽默，敢说真话。
请为以下新闻生成完整的小红书内容：

新闻：{sn["title"]}
来源：{sn["source"]}

请按以下格式输出（每段用分隔线 === 隔开）：

===封面大字===
（10字以内，爆炸感，如：离谱！这也行？💀）

===封面副标===
（15字以内概括）

===封面Emoji===
（1-2个最能代表情绪的emoji）

===背景色===
（亮黄/纯黑/荧光橙/血红等）

===无语指数===
（💀 到 💀💀💀💀💀）

===卡片1标题===
（8字以内）

===卡片1内容===
（80-120字，口语化，有画面感，描述事件经过）

===卡片2标题===
无语哥点评

===卡片2内容===
（60-100字，犀利点评，说出大家心声）

===正文描述===
（150-200字，事件经过+无语点评+一个引发思考的问题）

===标签===
#无语哥 #无语了 #社会百态 （再加3-4个相关标签）

===互动引导===
（一句话引导评论，如：你遇到过更无语的吗？）"""}],
                timeout=60,
            )
            raw = resp.choices[0].message.content
            # 解析分段格式
            def extract(tag):
                m = _re.search(f'==={tag}===\s*\n([^=]+)', raw)
                return m.group(1).strip() if m else ""
            posts.append({
                "news_title": sn["title"],
                "wuyu_level": extract("无语指数"),
                "cover": {
                    "main_text": extract("封面大字"),
                    "sub_text": extract("封面副标"),
                    "emoji": extract("封面Emoji"),
                    "bg_color_suggestion": extract("背景色"),
                },
                "cards": [
                    {"card_no": 1, "title": extract("卡片1标题"), "content": extract("卡片1内容"), "emoji_accent": "📱"},
                    {"card_no": 2, "title": "无语哥点评", "content": extract("卡片2内容"), "emoji_accent": "💀"},
                ],
                "caption": extract("正文描述"),
                "hashtags": extract("标签").split(),
                "cta": extract("互动引导"),
            })
            logger.info(f"  ✅ 生成: {sn['title'][:30]}")
        except Exception as e:
            logger.warning(f"  ⚠️ 生成失败: {e}")

    logger.info(f"✅ 共生成 {len(posts)} 条小红书内容")
    return posts


# ── 格式化 ────────────────────────────────────────────────────────────────────
def format_for_email(posts: list[dict]) -> str:
    now = datetime.datetime.now().strftime("%H:%M")
    lines = [
        f"# 😤 无语哥 · 今日无语事",
        f"**{TODAY_ZH}** | 共 {len(posts)} 条内容 | {now}",
        "", "---", "",
    ]
    for i, p in enumerate(posts):
        cover = p.get('cover', {})
        lines += [
            f"## {i+1}. {p.get('news_title', '')[:50]}",
            f"**无语指数：** {p.get('wuyu_level', '')}",
            "",
            f"### 🖼️ 封面设计",
            f"| 元素 | 内容 |",
            f"|------|------|",
            f"| 大字 | **{cover.get('main_text', '')}** |",
            f"| 副标 | {cover.get('sub_text', '')} |",
            f"| Emoji | {cover.get('emoji', '')} |",
            f"| 背景色 | {cover.get('bg_color_suggestion', '')} |",
            "",
            f"### 📋 正文卡片",
        ]
        for card in p.get('cards', []):
            lines += [
                f"**卡片 {card.get('card_no', '')}：{card.get('title', '')}** {card.get('emoji_accent', '')}",
                "",
                card.get('content', ''),
                "",
            ]
        lines += [
            f"### 📝 正文描述",
            p.get('caption', ''),
            "",
            f"**标签：** {' '.join(p.get('hashtags', []))}",
            "",
            f"**互动引导：** {p.get('cta', '')}",
            "",
            "---",
            "",
        ]
    lines.append(f"*无语哥小红书助手 · {TODAY_ZH} {now}*")
    return "\n".join(lines)


def format_for_siyuan(posts: list[dict]) -> str:
    now = datetime.datetime.now().strftime("%H:%M")
    lines = [
        f"# 😤 无语哥 今日选题 {TODAY_ZH}",
        f"生成时间：{now} | 共 {len(posts)} 条",
        "",
    ]
    for i, p in enumerate(posts):
        cover = p.get('cover', {})
        lines += [
            f"## {i+1}. {p.get('news_title', '')[:60]}",
            f"无语指数：{p.get('wuyu_level', '')}",
            "",
            f"### 封面",
            f"- 大字：{cover.get('main_text', '')}",
            f"- 副标：{cover.get('sub_text', '')}",
            f"- Emoji：{cover.get('emoji', '')}",
            f"- 背景色：{cover.get('bg_color_suggestion', '')}",
            "",
            "### 卡片内容",
        ]
        for card in p.get('cards', []):
            lines += [f"**{card.get('title', '')}**", card.get('content', ''), ""]
        lines += [
            "### 正文",
            p.get('caption', ''),
            "",
            f"标签：{' '.join(p.get('hashtags', []))}",
            f"互动：{p.get('cta', '')}",
            "", "---", "",
        ]
    return "\n".join(lines)


# ── 发送 ──────────────────────────────────────────────────────────────────────
def send_email(content, subject):
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import markdown as md
    sender = "995943586@qq.com"
    recipients = ["2464076118@qq.com", "sunchend@outlook.com"]
    password = os.environ.get("QQ_EMAIL_PASSWORD")
    if not password: return False
    html_body = md.markdown(content, extensions=['markdown.extensions.tables','markdown.extensions.nl2br'])
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
body{{font-family:-apple-system,'PingFang SC',sans-serif;line-height:1.7;color:#333;max-width:800px;margin:0 auto;padding:20px;background:#fff0f5}}
.c{{background:#fff;padding:28px;border-radius:12px;box-shadow:0 2px 16px rgba(255,71,87,0.15)}}
h1{{color:#ff4757;border-bottom:3px solid #ff4757;padding-bottom:10px}}
h2{{color:#333;margin-top:28px;padding:8px 14px;background:#fff0f5;border-left:4px solid #ff6b81;border-radius:4px;font-size:1em}}
h3{{color:#555;font-size:0.95em}}
table{{border-collapse:collapse;width:100%;margin:10px 0}}th,td{{border:1px solid #ffd6e0;padding:7px 12px}}th{{background:#fff0f5}}
hr{{border:none;border-top:1px solid #ffd6e0;margin:20px 0}}
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
        bark_notify(title=title, body=body, sound="minuet", group="wuyu")
        logger.info("✅ Bark 已发送")
    except Exception as e:
        logger.warning(f"⚠️ Bark 失败: {e}")


def save_to_siyuan(content: str):
    try:
        # 找笔记本（优先找带"AI开发"或第一个）
        req = urllib.request.Request(f"{SIYUAN_HOST}/api/notebook/lsNotebooks",
            data=b'{}', headers={"Authorization": f"Token {SIYUAN_TOKEN}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            nbs = json.loads(r.read())['data']['notebooks']
        nb_id = nbs[0]['id']  # 用第一个笔记本
        for nb in nbs:
            if any(k in nb['name'] for k in ['AI开发','工具','日志','无语','创作']):
                nb_id = nb['id']; break

        path = f"/无语哥选题/{TODAY}"
        req2 = urllib.request.Request(f"{SIYUAN_HOST}/api/filetree/createDocWithMd",
            data=json.dumps({"notebook": nb_id, "path": path, "markdown": content}).encode(),
            headers={"Authorization": f"Token {SIYUAN_TOKEN}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req2, timeout=10) as r:
            result = json.loads(r.read())
        doc_id = result.get('data', '')
        logger.info(f"✅ 思源笔记创建: {path} ({doc_id})")
        return doc_id
    except Exception as e:
        logger.error(f"❌ 思源失败: {e}")
        return ""


def main():
    no_send = "--no-send" in sys.argv
    logger.info("=" * 50); logger.info("😤 无语哥内容生成启动"); logger.info("=" * 50)

    news = fetch_wuyu_news()
    posts = generate_xiaohongshu_posts(news)

    email_content = format_for_email(posts)
    siyuan_content = format_for_siyuan(posts)

    # 保存本地
    OUTPUT_DIR.mkdir(exist_ok=True)
    (OUTPUT_DIR / f"wuyu_{TODAY}.md").write_text(email_content, encoding='utf-8')

    print(email_content[:3000])

    if no_send: return

    today_str = datetime.datetime.now().strftime("%Y年%m月%d日")
    send_email(email_content, f"😤 无语哥今日内容 {today_str}（{len(posts)}条）")
    send_bark(
        title=f"😤 无语哥今日选题 {today_str}",
        body=f"今日 {len(posts)} 条无语内容已生成，查看封面+卡片+正文"
    )
    save_to_siyuan(siyuan_content)
    logger.info("🎉 无语哥内容生成完成")


if __name__ == "__main__":
    main()
