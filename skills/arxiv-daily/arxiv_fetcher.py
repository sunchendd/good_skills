#!/usr/bin/env python3
"""arXiv AI 论文每日精选 - 核心抓取和精选模块"""

import urllib.request
import xml.etree.ElementTree as ET
import json
import os
import logging
import datetime
import time
from pathlib import Path
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.RO"]
MAX_FETCH = 15
MAX_OUTPUT = 3
BATCH_SIZE = 15
MIN_SCORE = 0.6
DEEPSEEK_MODEL = "deepseek-chat"
OUTPUT_DIR = Path(__file__).parent / "newsletters"
HISTORY_FILE = Path(__file__).parent / "newsletters" / ".history.json"

def load_history():
    try:
        if HISTORY_FILE.exists():
            return set(json.loads(HISTORY_FILE.read_text()))
    except Exception:
        pass
    return set()

def save_history(ids):
    try:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        HISTORY_FILE.write_text(json.dumps(list(ids), ensure_ascii=False))
    except Exception:
        pass


def _parse_rss_date(pub_date_text):
    """Parse RSS pubDate like 'Thu, 21 May 2026 00:00:00 -0400' to '2026-05-21'"""
    from email.utils import parsedate_to_datetime
    try:
        dt = parsedate_to_datetime(pub_date_text)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return ''


def fetch_arxiv_papers(max_results=MAX_FETCH):
    import re
    keywords_list = ["speculative decoding", "draft model", "speculative inference",
                     "parallel decoding", "lookahead decoding", "multi-token prediction"]
    seen_links = set()
    all_papers = []
    # First pass: collect all papers with dates, find most recent date
    raw_papers = []

    logger.info(f"📡 通过 RSS 抓取 arXiv 论文 (投机推理)...")
    for cat_idx, cat in enumerate(CATEGORIES):
        rss_url = f"https://rss.arxiv.org/rss/{cat}"
        logger.info(f"   → [{cat_idx+1}/{len(CATEGORIES)}] {cat}...")
        for attempt in range(3):
            try:
                req = urllib.request.Request(rss_url, headers={"User-Agent": "arxiv-daily-bot/1.0"})
                data = urllib.request.urlopen(req, timeout=60).read()
                break
            except Exception as e:
                if attempt < 2:
                    logger.warning(f"  RSS {cat} 失败 (尝试 {attempt+1}/3): {e}")
                    time.sleep(10)
                else:
                    logger.error(f"  RSS {cat} 失败: {e}")
                    data = None
        if data is None:
            continue
        root = ET.fromstring(data)
        for item in root.findall('.//item'):
            title = (item.find('title').text or '').strip().replace('\n', ' ').replace('  ', ' ')
            link = (item.find('link').text or '').strip()
            desc = (item.find('description').text or '').strip()
            desc = re.sub(r'<[^>]+>', ' ', desc).replace('\n', ' ').strip()
            pub_date_el = item.find('pubDate')
            published = _parse_rss_date(pub_date_el.text) if pub_date_el is not None else ''
            if not published:
                continue
            creators = item.findall('creator') or item.findall('{http://purl.org/dc/elements/1.1/}creator')
            authors = [c.text for c in creators[:3] if c.text]
            ann = item.find('announce_type')
            cats = [cat]
            if ann is not None and ann.text == 'cross':
                cats.append('cross-list')
            raw_papers.append({'title': title, 'summary': desc[:2000], 'link': link,
                               'published': published, 'categories': cats, 'authors': authors})
        time.sleep(3 if cat_idx < len(CATEGORIES) - 1 else 0)

    if not raw_papers:
        logger.warning("⚠️ RSS 未获取到任何论文")
        return []

    # Find the most recent date with papers
    all_dates = sorted(set(p['published'] for p in raw_papers), reverse=True)
    latest_date = all_dates[0] if all_dates else ''
    logger.info(f"📅 RSS 最新发布日期: {latest_date} (共 {len(all_dates)} 个日期)")

    # Filter: only papers from the most recent date + keyword match
    for p in raw_papers:
        if p['published'] != latest_date:
            continue
        text_lower = (p['title'] + ' ' + p['summary']).lower()
        if not any(kw in text_lower for kw in keywords_list):
            continue
        if p['link'] in seen_links:
            continue
        seen_links.add(p['link'])
        all_papers.append(p)
        if len(all_papers) >= max_results:
            break

    logger.info(f"✅ 共获取 {len(all_papers)} 篇论文 ({latest_date})")
    return all_papers


def select_papers_with_deepseek(papers):
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    selected = []
    if not papers:
        return selected
    batch = papers
    logger.info(f"🤖 DeepSeek 评分 {len(batch)} 篇论文...")
    papers_text = "\n\n".join([
        f"[{j+1}] Title: {p['title']}\nPublished: {p['published']}\n"
        f"Categories: {', '.join(p['categories'][:3])}\nAbstract: {p['summary'][:800]}\nLink: {p['link']}"
        for j, p in enumerate(batch)
    ])
    prompt = f"""你是 LLM 推理加速领域的论文评审专家。请对以下「投机推理/投机解码」相关论文逐篇评分。

评分标准（0.0-1.0）：
- 创新性：新方法/新架构/新发现（40%）
- 实用性：对大模型推理加速的直接价值（35%）
- 影响力潜力（15%）
- 完整性（10%）

研究方向归类（优先匹配）：投机解码 / 投机推理 / 草稿模型 / MTP / 前缀缓存 / 并行解码

输出 JSON：
{{
  "selected": [
    {{
      "original_index": 原始序号,
      "score": 0.85,
      "zh_title": "中文标题",
      "zh_abstract": "中文摘要150-200字，突出核心创新和实验结论",
      "zh_tags": ["标签1", "标签2"],
      "highlight": "一句话亮点（20字内）",
      "direction": "研究方向"
    }}
  ]
}}

论文列表：
{papers_text}"""
    try:
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            timeout=120,
        )
        result = json.loads(resp.choices[0].message.content)
        batch_selected = result.get("selected", [])
        for item in batch_selected:
            idx = item.get("original_index", 1) - 1
            if 0 <= idx < len(batch):
                orig = batch[idx]
                item.update({'en_title': orig['title'], 'link': orig['link'],
                             'published': orig['published'], 'authors': orig['authors'],
                             'categories': orig['categories']})
                selected.append(item)
        logger.info(f"   → 入选 {len(batch_selected)} 篇")
    except Exception as e:
        logger.error(f"   ❌ DeepSeek 处理失败: {e}")
    selected.sort(key=lambda x: x.get('score', 0), reverse=True)
    logger.info(f"✅ 共精选 {len(selected)} 篇论文")
    return selected


def format_newsletter(papers):
    today = datetime.datetime.now().strftime("%Y年%m月%d日")
    now = datetime.datetime.now().strftime("%H:%M")
    by_direction = {}
    for p in papers:
        d = p.get('direction', '其他')
        by_direction.setdefault(d, []).append(p)

    direction_icons = {
        'LLM推理': '🧠', '推理': '🧠', '多模态': '👁️', '视觉语言': '👁️',
        'Agent': '🤖', '智能体': '🤖', '训练优化': '⚡', '训练效率': '⚡',
        '安全对齐': '🛡️', '对齐': '🛡️', '具身智能': '🦾', '机器人': '🦾',
        '代码生成': '💻', '编程': '💻', '知识图谱': '🕸️', '医疗AI': '🏥', '其他': '📄',
    }

    def get_icon(d):
        for k, v in direction_icons.items():
            if k in d:
                return v
        return '📄'

    def score_label(s):
        if s >= 0.9: return '🔥 顶级'
        elif s >= 0.8: return '⭐⭐⭐ 强烈推荐'
        elif s >= 0.7: return '⭐⭐ 推荐'
        else: return '⭐ 值得一看'

    lines = [
        f"# 🔬 arXiv AI 论文每日精选",
        f"**{today}** | 共精选 **{len(papers)}** 篇 | 生成于 {now}",
        "", "---", "",
        "## 📊 今日概览", "",
        "| 研究方向 | 篇数 |", "|---------|------|",
    ]
    for d, ps in sorted(by_direction.items(), key=lambda x: -len(x[1])):
        lines.append(f"| {get_icon(d)} {d} | {len(ps)} |")
    lines += ["", "---", ""]

    for d, dir_papers in sorted(by_direction.items(), key=lambda x: -len(x[1])):
        lines.append(f"## {get_icon(d)} {d}")
        lines.append("")
        for p in dir_papers:
            tags = " ".join([f"`{t}`" for t in p.get('zh_tags', [])])
            authors = "、".join(p.get('authors', []))
            if len(p.get('authors', [])) >= 3:
                authors += " 等"
            lines += [
                f"### {p.get('zh_title', p.get('en_title', ''))}",
                f"**{p.get('en_title', '')}**  ",
                f"📅 {p.get('published', '')} | {score_label(p.get('score', 0))} | 评分 `{p.get('score', 0):.2f}`  ",
            ]
            if authors:
                lines.append(f"👤 {authors}  ")
            if tags:
                lines.append(f"🏷️ {tags}  ")
            lines += [
                f"> 💡 **{p.get('highlight', '')}**",
                "",
                p.get('zh_abstract', ''),
                "",
                f"🔗 {p.get('link', '')}",
                "", "---", "",
            ]

    lines.append(f"*由 arXiv-Daily Skill 自动生成 · {today} {now}*")
    return "\n".join(lines)


def save_newsletter(content):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = OUTPUT_DIR / f"arxiv_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md"
    fname.write_text(content, encoding='utf-8')
    logger.info(f"💾 已保存到: {fname}")
    return fname
