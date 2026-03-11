#!/usr/bin/env python3
"""
思源笔记每日知识库维护
每天将所有信息汇聚写入思源，形成个人知识库
- 每日日志（GitHub/笔记/早报状态）
- arXiv 精选论文摘要
- 健身记录
- 天气穿搭
- 无语哥选题
- B站视频精选
"""
import urllib.request, json, os, sys, logging, datetime, re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SIYUAN_HOST = os.environ.get("SIYUAN_HOST", "http://192.168.3.32:6806")
SIYUAN_TOKEN = os.environ.get("SIYUAN_TOKEN", "")
TODAY = datetime.date.today().strftime("%Y-%m-%d")
TODAY_ZH = datetime.datetime.now().strftime("%Y年%m月%d日")
WEEKDAY = ["周一","周二","周三","周四","周五","周六","周日"][datetime.date.today().weekday()]


def siyuan_post(path: str, data: dict) -> dict:
    url = f"{SIYUAN_HOST}{path}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
        headers={"Authorization": f"Token {SIYUAN_TOKEN}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def get_notebooks() -> dict:
    r = siyuan_post("/api/notebook/lsNotebooks", {})
    return {nb["id"]: nb["name"] for nb in r.get("data", {}).get("notebooks", [])}


def get_today_notes() -> list:
    result = siyuan_post("/api/query/sql", {
        "stmt": "SELECT id, content, root_id, box, path, created FROM blocks WHERE type='d' AND created >= '" + datetime.date.today().strftime("%Y%m%d") + "000000' ORDER BY created DESC LIMIT 30"
    })
    return result.get("data", [])


def read_skill_output(skill_name: str, pattern: str) -> str:
    """读取某个skill今天的输出文件"""
    skill_dirs = {
        'arxiv': Path.home() / ".openclaw/skills/arxiv-daily/newsletters",
        'fitness': Path.home() / ".openclaw/skills/super-fitness/daily_tasks",
        'wardrobe': Path.home() / ".openclaw/skills/super-wardrobe/outfits",
        'video': Path.home() / ".openclaw/skills/bili-daily/newsletters",
        'wuyu': Path.home() / ".openclaw/skills/wuyu-xiaohongshu/notes",
        'newsletter': Path.home() / ".openclaw/skills/daily-newsletter-skill/newsletters",
    }
    folder = skill_dirs.get(skill_name)
    if not folder or not folder.exists():
        return ""
    date_str = datetime.date.today().strftime("%Y%m%d")
    matches = sorted(folder.glob(f"*{date_str}*"))
    if not matches:
        return ""
    try:
        return matches[-1].read_text(encoding='utf-8')
    except:
        return ""


def build_daily_knowledge_note(notebooks: dict, today_notes: list) -> str:
    """构建每日知识库笔记"""
    now = datetime.datetime.now().strftime("%H:%M")
    # 读取今日各 skill 输出
    arxiv_content = read_skill_output('arxiv', '')
    fitness_content = read_skill_output('fitness', '')
    wardrobe_content = read_skill_output('wardrobe', '')
    video_content = read_skill_output('video', '')
    wuyu_content = read_skill_output('wuyu', '')

    lines = [
        f"# 📚 {TODAY_ZH} {WEEKDAY} · 个人知识库日志",
        f"*自动生成 · {now}*",
        "", "---", "",

        "## 🗂️ 今日概览",
        f"| 模块 | 状态 |",
        f"|------|------|",
        f"| 💪 健身计划 | {'✅ 已生成' if fitness_content else '❌ 未生成'} |",
        f"| 👔 穿搭建议 | {'✅ 已生成' if wardrobe_content else '❌ 未生成'} |",
        f"| 🔬 arXiv 论文 | {'✅ 已生成' if arxiv_content else '❌ 未生成'} |",
        f"| 📺 B站视频 | {'✅ 已生成' if video_content else '❌ 未生成'} |",
        f"| 😤 无语哥选题 | {'✅ 已生成' if wuyu_content else '❌ 未生成'} |",
        f"| 📝 新建笔记 | {len(today_notes)} 条 |",
        "", "---", "",
    ]

    # 健身打卡
    if fitness_content:
        # 提取关键部分
        lines += ["## 💪 今日健身打卡", ""]
        for line in fitness_content.split('\n')[2:20]:
            lines.append(line)
        lines += ["", f"[查看完整计划](siyuan://blocks/)", "", "---", ""]

    # arXiv 论文精选（提取前3篇）
    if arxiv_content:
        lines += ["## 🔬 今日 arXiv 精选", ""]
        # 提取论文标题和摘要
        papers = re.findall(r'### .+?\n\*\*.+?\*\*.*?\n.*?🔗 .+', arxiv_content, re.DOTALL)
        for p in papers[:3]:
            # 清理，取前5行
            paper_lines = p.split('\n')[:5]
            for pl in paper_lines:
                lines.append(pl)
            lines.append("")
        if len(papers) > 3:
            lines.append(f"*...共 {len(papers)} 篇，查看完整版*")
        lines += ["", "---", ""]

    # 无语哥选题
    if wuyu_content:
        lines += ["## 😤 无语哥今日选题", ""]
        # 提取每条标题
        titles = re.findall(r'## \d+\. (.+)', wuyu_content)
        for t in titles:
            lines.append(f"- {t[:60]}")
        lines += ["", "---", ""]

    # B站视频精选
    if video_content:
        lines += ["## 📺 今日 B站精选", ""]
        bili_items = re.findall(r'### .+ \d+\. (.+?)\n\*\*(.+?)\*\*.*?\n.*?🔗 (.+)', video_content)
        for item in bili_items[:5]:
            lines.append(f"- {item[0].strip()[:50]} `{item[1].strip()[:20]}`")
            lines.append(f"  {item[2].strip()}")
        lines += ["", "---", ""]

    # 今日新建笔记
    lines += ["## 📝 今日新建笔记", ""]
    if today_notes:
        nb_map = notebooks
        for n in today_notes[:10]:
            nb_name = nb_map.get(n.get('box', ''), '未知笔记本')
            lines.append(f"- **{n.get('content','无标题')[:50]}** `{nb_name}`")
    else:
        lines.append("- （今日无新建笔记）")
    lines += ["", "---", ""]

    # 学习与成长记录（空模板，供手动填写）
    lines += [
        "## 🌱 今日学习与成长",
        "",
        "> 今天学到了什么？有什么收获或感悟？",
        "",
        "- [ ] 读书/文章：",
        "- [ ] 技术学习：",
        "- [ ] 健身完成：",
        "- [ ] 今日心情：",
        "",
        "---",
        "",
        f"*知识库由 OpenClaw 自动维护 · {TODAY_ZH} {now}*",
    ]
    return "\n".join(lines)


def create_or_update_siyuan(content: str, notebooks: dict) -> str:
    """创建思源知识库日志"""
    # 优先找 AI开发 笔记本
    target_nb = list(notebooks.keys())[0] if notebooks else ""
    for nb_id, nb_name in notebooks.items():
        if any(k in nb_name for k in ['AI开发', '知识库', '日志', '工具']):
            target_nb = nb_id; break

    path = f"/每日知识库/{TODAY}"
    try:
        result = siyuan_post("/api/filetree/createDocWithMd", {
            "notebook": target_nb, "path": path, "markdown": content
        })
        doc_id = result.get("data", "")
        logger.info(f"✅ 思源知识库日志创建: {path} ({doc_id})")
        return doc_id
    except Exception as e:
        logger.error(f"❌ 思源写入失败: {e}")
        return ""


def main():
    logger.info("=" * 50)
    logger.info("📚 思源每日知识库更新")
    logger.info("=" * 50)

    notebooks = get_notebooks()
    today_notes = get_today_notes()
    content = build_daily_knowledge_note(notebooks, today_notes)
    print(content[:2000])

    doc_id = create_or_update_siyuan(content, notebooks)

    # Bark 通知
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from bark_client import bark_notify
        bark_notify(
            title=f"📚 {TODAY_ZH} 知识库日志已更新",
            body=f"新笔记 {len(today_notes)} 条 · 已写入思源知识库",
            sound="minuet", group="siyuan"
        )
    except Exception as e:
        logger.warning(f"Bark 失败: {e}")

    logger.info("🎉 思源知识库更新完成")


if __name__ == "__main__":
    main()
