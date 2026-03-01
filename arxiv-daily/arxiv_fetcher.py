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
MAX_FETCH = 100
BATCH_SIZE = 20
MIN_SCORE = 0.6
DEEPSEEK_MODEL = "deepseek-chat"
OUTPUT_DIR = Path(__file__).parent / "newsletters"


def fetch_arxiv_papers(max_results=MAX_FETCH):
    cat_query = "+OR+".join(f"cat:{c}" for c in CATEGORIES)
    url = (f"http://export.arxiv.org/api/query?search_query={cat_query}"
           f"&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending")
    logger.info(f"📡 抓取 arXiv 论文 (max={max_results})...")
    req = urllib.request.urlopen(url, timeout=60)
    data = req.read()
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    root = ET.fromstring(data)
    papers = []
    for entry in root.findall('atom:entry', ns):
        title = entry.find('atom:title', ns).text.strip().replace('\n', '').replace('  ', ' ')
        summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
        link = entry.find('atom:id', ns).text.strip()
        published = entry.find('atom:published', ns).text[:10]
        cats = [c.get('term') for c in entry.findall('atom:category', ns)]
        authors_el = entry.findall('atom:author', ns)
        authors = [a.find('atom:name', ns).text for a in authors_el[:3]]
        papers.append({'title': title, 'summary': summary, 'link': link,
                       'published': published, 'categories': cats, 'authors': authors})
    logger.info(f"✅ 获取 {len(papers)} 篇论文")
    return papers


def select_papers_with_deepseek(papers):
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")
    selected = []
    for i in range(0, len(papers), BATCH_SIZE):
        batch = papers[i:i + BATCH_SIZE]
        logger.info(f"🤖 DeepSeek 处理第 {i//BATCH_SIZE + 1} 批 ({len(batch)} 篇)...")
        papers_text = "\n\n".join([
            f"[{j+1}] Title: {p['title']}\nPublished: {p['published']}\n"
            f"Categories: {', '.join(p['categories'][:3])}\nAbstract: {p['summary'][:500]}\nLink: {p['link']}"
            for j, p in enumerate(batch)
        ])
        prompt = f"""你是 AI 科研论文评审专家。对以下 arXiv 论文逐篇评分筛选。

评分标准（0.0-1.0）：
- 创新性：新方法/新框架/新发现（35%）
- 实用性：对 LLM/Agent/推理/多模态等热门方向的直接价值（30%）
- 影响力潜力（20%）
- 完整性（15%）

**保留评分 >= {MIN_SCORE} 的所有论文**，数量不限，尽量全面。

输出 JSON：
{{
  "selected": [
    {{
      "original_index": 原始序号,
      "score": 0.85,
      "zh_title": "中文标题",
      "zh_abstract": "中文摘要150-200字，突出核心创新、方法和结论",
      "zh_tags": ["标签1", "标签2"],
      "highlight": "一句话亮点（20字内）",
      "direction": "研究方向（LLM推理/多模态/Agent/训练优化/安全对齐/具身智能/代码生成/其他）"
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
            logger.info(f"   → 本批入选 {len(batch_selected)} 篇")
            time.sleep(1)
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
