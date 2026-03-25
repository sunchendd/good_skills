#!/usr/bin/env python3
"""
Vibe Coding Daily - 每日 AI 编程工具动态
收集：Claude Code / OpenCode / GitHub Copilot 更新 + Vibe Coding 技巧 + 相关视频
"""
import urllib.request, urllib.parse, json, os, sys, re, logging, datetime, time
from pathlib import Path
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent / "newsletters"
TODAY = datetime.date.today().strftime("%Y-%m-%d")
TODAY_ZH = datetime.datetime.now().strftime("%Y年%m月%d日")
MAX_AGE_DAYS = 7
CUTOFF_DATE = (datetime.datetime.now() - datetime.timedelta(days=MAX_AGE_DAYS)).strftime('%Y-%m-%d')

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

WATCH_REPOS = [
    {"repo": "anthropics/claude-code",       "label": "Claude Code",     "npm": "@anthropic-ai/claude-code"},
    {"repo": "continuedev/continue",          "label": "Continue.dev",    "npm": None},
    {"repo": "microsoft/vscode-copilot-chat", "label": "Copilot Chat",    "npm": None},
    {"repo": "getcursor/cursor",              "label": "Cursor",          "npm": None},
    {"repo": "cline/cline",                   "label": "Cline",           "npm": None},
    {"repo": "opencode-ai/opencode",          "label": "OpenCode",        "npm": None},
    {"repo": "openai/codex",                  "label": "OpenAI Codex",    "npm": None},
    {"repo": "google-gemini/gemini-cli",      "label": "Gemini CLI",      "npm": None},
]

SEARCH_KEYWORDS = [
    "vibe coding tutorial 2026",
    "claude code tips tricks",
    "github copilot new features",
    "AI coding workflow 2026",
    "cursor IDE tutorial",
    "opencode AI editor",
]

# X/Twitter 创始人及官方账号（用于 Google/Brave 搜索）
CREATOR_ACCOUNTS = [
    {"handle": "AnthropicAI",  "label": "Anthropic 官方"},
    {"handle": "dario_amodei", "label": "Dario Amodei"},
    {"handle": "sama",         "label": "Sam Altman"},
    {"handle": "opencode_ai",  "label": "OpenCode"},
    {"handle": "cursor_ai",    "label": "Cursor"},
    {"handle": "github",       "label": "GitHub Copilot"},
]


def gh_get(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "openclaw", "Accept": "application/vnd.github.v3+json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        logger.warning(f"GitHub API 请求失败 {path}: {e}")
        return None


def fetch_tool_updates() -> list[dict]:
    updates = []
    for w in WATCH_REPOS:
        try:
            releases = gh_get(f"/repos/{w['repo']}/releases?per_page=3")
            if not releases or not isinstance(releases, list) or len(releases) == 0:
                logger.info(f"  {w['label']}: 无公开 releases")
                continue
            latest = releases[0]
            if not latest or not isinstance(latest, dict):
                logger.info(f"  {w['label']}: release 数据异常，跳过")
                continue
            tag = latest.get("tag_name") or ""
            published = (latest.get("published_at") or "")[:10]
            body = (latest.get("body") or "")[:500]
            # 检查是否是近7天内发布的
            from datetime import timedelta
            pub_date = datetime.date.fromisoformat(published) if published else None
            is_recent = pub_date and (datetime.date.today() - pub_date).days <= 7
            updates.append({
                "tool": w["label"],
                "repo": w["repo"],
                "version": tag,
                "published": published,
                "changelog": body,
                "url": latest.get("html_url", ""),
                "is_recent": is_recent,
            })
            logger.info(f"✅ {w['label']}: {tag} ({published}) {'🆕' if is_recent else ''}")
        except Exception as e:
            logger.warning(f"  {w['label']} 获取失败: {e}")
    return updates


def search_vibe_content() -> list[dict]:
    """用 web_fetch 搜索 Vibe Coding 内容"""
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    results = []

    # HackerNews API 搜索
    hn_keywords = ["claude code", "vibe coding", "copilot", "cursor AI", "opencode"]
    for kw in hn_keywords[:3]:
        try:
            kw_enc = urllib.parse.quote(kw)
            url = f"https://hn.algolia.com/api/v1/search?query={kw_enc}&tags=story&hitsPerPage=5&numericFilters=created_at_i>{int((datetime.datetime.now() - datetime.timedelta(days=7)).timestamp())}"
            with urllib.request.urlopen(url, timeout=8) as r:
                d = json.loads(r.read())
            for hit in d.get("hits", []):
                results.append({
                    "source": "HackerNews",
                    "title": hit.get("title", ""),
                    "url": hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID')}"),
                    "points": hit.get("points", 0),
                    "keyword": kw,
                })
        except Exception as e:
            logger.warning(f"HN 搜索失败 [{kw}]: {e}")
        time.sleep(0.2)

    # B站搜索（按最新发布排序 + 7天时间过滤）
    bili_keywords = ["vibe coding", "claude code教程", "AI编程助手"]
    for kw in bili_keywords:
        try:
            kw_enc = urllib.parse.quote(kw)
            url = f"https://api.bilibili.com/x/web-interface/search/all/v2?keyword={kw_enc}&page=1&pagesize=8&order=pubdate"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com"})
            with urllib.request.urlopen(req, timeout=8) as r:
                d = json.loads(r.read())
            for block in d.get('data', {}).get('result', []):
                if block.get('result_type') == 'video':
                    for v in block.get('data', [])[:3]:
                        pub = datetime.datetime.fromtimestamp(v.get('pubdate', 0)).strftime('%Y-%m-%d') if v.get('pubdate') else ''
                        if pub < CUTOFF_DATE:
                            continue  # 跳过 7 天前的旧视频
                        title = re.sub(r'<[^>]+>', '', v.get('title', ''))
                        results.append({
                            "source": "B站",
                            "title": title,
                            "url": f"https://www.bilibili.com/video/{v.get('bvid','')}",
                            "points": v.get("play", 0),
                            "keyword": kw,
                            "pubdate": pub,
                        })
        except Exception as e:
            logger.warning(f"B站搜索失败 [{kw}]: {e}")
        time.sleep(0.3)

    logger.info(f"✅ 共找到 {len(results)} 条相关内容")
    return results


def fetch_creator_updates() -> list[dict]:
    """通过 DuckDuckGo 搜索 X/Twitter 上 AI 工具创始人和官方账号的近期动态"""
    logger.info("🐦 搜索 X/Twitter 创始人/官方账号近期动态...")

    def _ddg_search(query: str, num: int = 3) -> list[dict]:
        kw_enc = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={kw_enc}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
        links_raw = re.findall(r'uddg=(https[^&"]+)', html)
        seen_u = set(); links = []
        for l in links_raw:
            d = urllib.parse.unquote(l)
            if d not in seen_u: seen_u.add(d); links.append(d)
        titles_raw = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
        titles = [re.sub(r'<[^>]+>', '', t).strip() for t in titles_raw]
        return [{'title': titles[i] if i < len(titles) else '', 'url': links[i]} for i in range(min(num, len(links)))]

    results = []
    for acc in CREATOR_ACCOUNTS:
        try:
            # 搜索 x.com 账号的近期内容（不用 site: 因为 x.com 登录墙）
            query = f'{acc["handle"]} twitter AI coding vibe 2026'
            items = _ddg_search(query, num=2)
            for item in items:
                if item['title']:
                    results.append({
                        "source": f"X(@{acc['handle']})",
                        "label": acc["label"],
                        "title": item['title'][:120],
                        "url": item['url'],
                        "points": 0,
                        "keyword": acc["handle"],
                    })
            time.sleep(0.5)
        except Exception as e:
            logger.warning(f"X 搜索失败 [@{acc['handle']}]: {e}")
    logger.info(f"✅ X/Twitter 共找到 {len(results)} 条动态")
    return results


def fetch_xiaohongshu_vibe() -> list[dict]:
    """搜索小红书 Vibe Coding 相关内容（通过 DuckDuckGo 搜索）"""
    logger.info("📱 搜索小红书 Vibe Coding 内容...")

    def _ddg_search(query: str, num: int = 4) -> list[dict]:
        kw_enc = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={kw_enc}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode('utf-8', errors='ignore')
        links_raw = re.findall(r'uddg=(https[^&"]+)', html)
        seen_u = set(); links = []
        for l in links_raw:
            d = urllib.parse.unquote(l)
            if d not in seen_u: seen_u.add(d); links.append(d)
        titles_raw = re.findall(r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
        titles = [re.sub(r'<[^>]+>', '', t).strip() for t in titles_raw]
        return [{'title': titles[i] if i < len(titles) else '', 'url': links[i]} for i in range(min(num, len(links)))]

    results = []
    this_month = datetime.datetime.now().strftime("%Y年%m月")
    keywords = [
        f"小红书 vibe coding claude code {this_month}",
        f"小红书 AI编程工具推荐 2026",
    ]
    for kw in keywords:
        try:
            for item in _ddg_search(kw, num=3):
                if item['title']:
                    results.append({
                        "source": "小红书相关",
                        "title": item['title'][:100],
                        "url": item['url'],
                        "points": 0,
                        "keyword": kw,
                    })
            time.sleep(0.8)
        except Exception as e:
            logger.warning(f"小红书搜索失败 [{kw[:30]}...]: {e}")
    seen = set()
    unique = [r for r in results if r['url'] not in seen and not seen.add(r['url'])]
    logger.info(f"✅ 小红书相关内容共找到 {len(unique)} 条")
    return unique


def generate_summary(tool_updates, content_results, creator_results=None, xhs_results=None) -> str:
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

    updates_text = "\n".join([
        f"- {u['tool']} {u['version']} ({u['published']}) {'🆕近7天' if u['is_recent'] else ''}\n  更新内容: {u['changelog'][:200]}"
        for u in tool_updates
    ])

    content_text = "\n".join([
        f"[{c['source']}] {c['title']} | {c.get('points',0)} 热度 | {c['url']}"
        for c in content_results[:20]
    ])

    creator_text = ""
    if creator_results:
        creator_text = "\n## 创始人/官方账号近期动态（X/Twitter）\n" + "\n".join([
            f"[{c['label']}] {c['title']} | {c['url']}"
            for c in creator_results[:10]
        ])

    xhs_text = ""
    if xhs_results:
        xhs_text = "\n## 小红书 Vibe Coding 内容\n" + "\n".join([
            f"{x['title']} | {x['url']}"
            for x in xhs_results[:5]
        ])

    prompt = f"""你是 AI 编程工具领域的专家编辑。请为开发者生成今日 Vibe Coding & AI 工具动态简报。

## 工具版本更新
{updates_text}

## 相关内容/教程
{content_text}
{creator_text}
{xhs_text}

请生成 Markdown 格式简报，包含：

### 🆕 本周工具更新（精选近7天有更新的）
（每个工具：版本、关键更新点解读、对开发者的影响）

### 🐦 创始人/官方动态
（从 X/Twitter 动态中提炼最有价值的 2-3 条，加中文说明）

### 🎯 今日 Vibe Coding 精选
（从内容列表中精选3-5条最有价值的教程/文章/视频，加中文摘要）

### 📱 小红书热门内容
（小红书近期相关内容精选，有链接）

### 💡 AI 编程技巧 Today
（根据当前工具状态，给出1-2个实用 tip）

语气要有干货感，面向有经验的开发者，50-100字/条摘要。"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        timeout=90,
    )
    return resp.choices[0].message.content


def format_newsletter(tool_updates, ai_summary) -> str:
    now = datetime.datetime.now().strftime("%H:%M")
    recent_tools = [u for u in tool_updates if u.get('is_recent')]

    lines = [
        f"# 🚀 Vibe Coding & AI 工具日报",
        f"**{TODAY_ZH}** | 监控 {len(tool_updates)} 个工具 | {len(recent_tools)} 个近期更新 | {now}",
        "", "---", "",
        "## 📦 版本速览",
        "",
        "| 工具 | 最新版本 | 发布日期 | 状态 |",
        "|------|---------|---------|------|",
    ]
    for u in tool_updates:
        badge = "🆕" if u.get('is_recent') else "✅"
        lines.append(f"| {u['tool']} | `{u['version']}` | {u['published']} | {badge} |")
    lines += ["", "---", "", ai_summary, "", "---",
              f"*Vibe Coding Daily · {TODAY_ZH} {now}*"]
    return "\n".join(lines)


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
body{{font-family:-apple-system,'PingFang SC',monospace,sans-serif;line-height:1.7;color:#333;max-width:860px;margin:0 auto;padding:20px;background:#0d1117}}
.c{{background:#161b22;padding:28px;border-radius:12px;color:#e6edf3}}
h1{{color:#58a6ff;border-bottom:2px solid #21262d;padding-bottom:10px}}
h2,h3{{color:#58a6ff}}
code{{background:#21262d;padding:2px 6px;border-radius:4px;font-family:monospace;color:#e6edf3}}
table{{border-collapse:collapse;width:100%;margin:12px 0}}
th,td{{border:1px solid #30363d;padding:8px 12px;color:#e6edf3}}
th{{background:#21262d}}tr:hover{{background:#21262d}}
a{{color:#58a6ff}}hr{{border:none;border-top:1px solid #21262d;margin:20px 0}}
p,li{{color:#e6edf3}}
</style></head><body><div class="c">{html_body}</div></body></html>"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject; msg["From"] = sender; msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(content, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    import time
    for attempt in range(3):
        try:
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.qq.com", 465, context=ctx) as s:
                s.login(sender, password)
                s.sendmail(sender, recipients, msg.as_bytes())
            logger.info("✅ 邮件发送成功"); return True
        except Exception as e:
            if attempt < 2:
                logger.warning(f"⚠️ 邮件发送失败，重试 {attempt+1}/2: {e}"); time.sleep(3)
            else:
                logger.error(f"❌ 邮件失败: {e}"); return False


def send_bark(title, body):
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from bark_client import bark_notify
        bark_notify(title=title, body=body, sound="minuet", group="vibe")
        logger.info("✅ Bark 已发送")
    except Exception as e:
        logger.warning(f"Bark 失败: {e}")


def main():
    no_send = "--no-send" in sys.argv
    logger.info("=" * 50); logger.info("🚀 Vibe Coding Daily 启动"); logger.info("=" * 50)

    tool_updates = fetch_tool_updates()
    content_results = search_vibe_content()
    creator_results = fetch_creator_updates()
    xhs_results = fetch_xiaohongshu_vibe()
    ai_summary = generate_summary(tool_updates, content_results, creator_results, xhs_results)
    newsletter = format_newsletter(tool_updates, ai_summary)

    OUTPUT_DIR.mkdir(exist_ok=True)
    fname = OUTPUT_DIR / f"vibe_{datetime.datetime.now().strftime('%Y%m%d')}.md"
    fname.write_text(newsletter, encoding='utf-8')
    print(newsletter[:3000])

    if no_send: return

    recent_count = len([u for u in tool_updates if u.get('is_recent')])
    send_email(newsletter, f"🚀 Vibe Coding日报 {TODAY_ZH} | {recent_count}个工具更新")
    # 提取最新工具版本摘要
    recent = [u for u in tool_updates if u.get('is_recent')]
    bark_lines = [f"🆕 {len(recent)} 个工具近期更新"]
    for u in recent[:3]:
        ver = f" {u.get('version','')}" if u.get('version') else ""
        log = u.get('changelog', '')[:40].replace('\n', ' ')
        bark_lines.append(f"• {u['tool']}{ver}: {log}")
    send_bark(
        title=f"🚀 Vibe Coding日报 {TODAY_ZH}",
        body="\n".join(bark_lines)
    )
    logger.info("🎉 完成")


if __name__ == "__main__":
    main()
