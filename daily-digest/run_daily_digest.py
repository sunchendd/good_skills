#!/usr/bin/env python3
"""
每日日志聚合器 → 写入思源笔记
聚合：GitHub 动态、当日新建思源笔记、今日arXiv/早报/健身/穿搭内容
"""
import urllib.request, json, os, sys, logging, datetime
from pathlib import Path
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SIYUAN_HOST = os.environ.get("SIYUAN_HOST", "http://192.168.3.32:6806")
SIYUAN_TOKEN = os.environ.get("SIYUAN_TOKEN", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

TODAY = datetime.date.today().strftime("%Y-%m-%d")
TODAY_ZH = datetime.datetime.now().strftime("%Y年%m月%d日")


# ── 思源 API ──────────────────────────────────────────────────────────────────
def siyuan_post(path: str, data: dict) -> dict:
    url = f"{SIYUAN_HOST}{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Token {SIYUAN_TOKEN}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        logger.warning(f"思源 API 请求失败 {path}: {e}")
        return {}


def get_today_new_notes() -> list[dict]:
    """查询今天新建的思源笔记"""
    try:
        # 查询今天创建的块
        ts_start = int(datetime.datetime.combine(datetime.date.today(), datetime.time.min).timestamp())
        result = siyuan_post("/api/query/sql", {
            "stmt": "SELECT id, content, root_id, box, path, type, created FROM blocks WHERE type='d' AND created >= '" + datetime.date.today().strftime("%Y%m%d") + "000000' ORDER BY created DESC LIMIT 20" 
        })
        notes = []
        for row in result.get("data", []):
            notes.append({
                "id": row.get("id"),
                "title": row.get("content", "无标题")[:60],
                "notebook": row.get("box", ""),
                "path": row.get("path", ""),
                "created": row.get("created", ""),
            })
        logger.info(f"✅ 今日思源新笔记: {len(notes)} 条")
        return notes
    except Exception as e:
        logger.error(f"❌ 思源查询失败: {e}")
        return []


def get_notebooks() -> dict:
    """获取笔记本 id→name 映射"""
    try:
        r = siyuan_post("/api/notebook/lsNotebooks", {})
        return {nb["id"]: nb["name"] for nb in r.get("data", {}).get("notebooks", [])}
    except:
        return {}


# ── GitHub 动态 ───────────────────────────────────────────────────────────────
def get_github_events() -> list[dict]:
    events = []
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/vllm-project/vllm-ascend/events?per_page=10",
            headers={"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "openclaw"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        today_events = [e for e in data if e.get("created_at", "")[:10] == TODAY]
        for e in today_events[:5]:
            events.append({
                "repo": "vllm-ascend",
                "type": e.get("type", ""),
                "actor": e.get("actor", {}).get("login", ""),
                "created_at": e.get("created_at", "")[:16],
            })
    except Exception as e:
        logger.warning(f"GitHub 事件获取失败: {e}")

    # deepseek-ai 最新 repos
    try:
        req = urllib.request.Request(
            "https://api.github.com/orgs/deepseek-ai/repos?sort=created&per_page=3",
            headers={"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "openclaw"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            repos = json.loads(r.read())
        for repo in repos:
            if repo.get("created_at", "")[:10] == TODAY:
                events.append({
                    "repo": "deepseek-ai",
                    "type": "CreateEvent(new repo)",
                    "actor": repo.get("name", ""),
                    "created_at": repo.get("created_at", "")[:16],
                })
    except Exception as e:
        logger.warning(f"DeepSeek repos 获取失败: {e}")

    logger.info(f"✅ GitHub 今日事件: {len(events)} 条")
    return events


# ── 读取今日本地文件内容 ──────────────────────────────────────────────────────
def read_today_files() -> dict:
    date_str = datetime.date.today().strftime("%Y%m%d")
    files_info = {}
    candidates = {
        "arxiv": Path.home() / ".openclaw/skills/arxiv-daily/newsletters",
        "newsletter": Path.home() / ".openclaw/skills/daily-newsletter-skill/newsletters",
        "fitness": Path.home() / ".openclaw/skills/super-fitness/daily_tasks",
        "wardrobe": Path.home() / ".openclaw/skills/super-wardrobe/outfits",
        "video": Path.home() / ".openclaw/skills/bili-daily/newsletters",
        "wuyu": Path.home() / ".openclaw/skills/wuyu-xiaohongshu/notes",
    }
    for name, folder in candidates.items():
        if folder.exists():
            matches = sorted(folder.glob(f"*{date_str}*"))
            if matches:
                try:
                    content = matches[-1].read_text(encoding='utf-8')
                    files_info[name] = content[:800]  # 截取摘要
                    logger.info(f"✅ 读取 {name}: {matches[-1].name}")
                except:
                    pass
    return files_info


# ── 生成日志 Markdown ─────────────────────────────────────────────────────────
def generate_daily_log(notes: list, notebooks: dict, github_events: list, today_files: dict) -> str:
    now = datetime.datetime.now().strftime("%H:%M")
    weekday = ["周一","周二","周三","周四","周五","周六","周日"][datetime.date.today().weekday()]

    lines = [
        f"# 📅 {TODAY_ZH} {weekday} 每日日志",
        f"*生成于 {now}*",
        "", "---", "",
    ]

    # 今日概览
    lines += [
        "## 📊 今日概览",
        f"- 新建笔记：{len(notes)} 条",
        f"- GitHub 动态：{len(github_events)} 条",
        f"- 早报已发送：{'✅' if 'newsletter' in today_files else '❌'}",
        f"- arXiv 论文：{'✅' if 'arxiv' in today_files else '❌'}",
        f"- 健身计划：{'✅' if 'fitness' in today_files else '❌'}",
        f"- 穿搭建议：{'✅' if 'wardrobe' in today_files else '❌'}",
        f"- 视频精选：{'✅' if 'video' in today_files else '❌'}",
        f"- 无语哥选题：{'✅' if 'wuyu' in today_files else '❌'}",
        "", "---", "",
    ]

    # 思源新笔记
    lines += ["## 📝 今日新建笔记", ""]
    if notes:
        for n in notes:
            nb_name = notebooks.get(n['notebook'], n['notebook'])
            lines.append(f"- **{n['title']}** `{nb_name}` `siyuan://blocks/{n['id']}`")
    else:
        lines.append("- （今日无新建笔记）")
    lines += ["", "---", ""]

    # GitHub 动态
    lines += ["## 🐙 GitHub 动态", ""]
    if github_events:
        for e in github_events:
            lines.append(f"- `{e['repo']}` {e['type']} by **{e['actor']}** @ {e['created_at']}")
    else:
        lines.append("- （今日无新动态）")
    lines += ["", "---", ""]

    # 健身打卡
    if "fitness" in today_files:
        lines += ["## 💪 今日健身计划（摘要）", ""]
        # 提取运动计划部分
        fitness_lines = today_files["fitness"].split("\n")
        for fl in fitness_lines[3:15]:
            lines.append(fl)
        lines += ["", "---", ""]

    # 穿搭建议
    if "wardrobe" in today_files:
        lines += ["## 👔 今日穿搭（摘要）", ""]
        wardrobe_lines = today_files["wardrobe"].split("\n")
        for wl in wardrobe_lines[3:10]:
            lines.append(wl)
        lines += ["", "---", ""]

    lines.append(f"*由 OpenClaw Daily Digest 自动生成 · {TODAY_ZH} {now}*")
    return "\n".join(lines)


# ── 写入思源笔记 ──────────────────────────────────────────────────────────────
def write_to_siyuan(content: str, notebooks: dict) -> str:
    """在思源笔记中创建每日日志"""
    # 找到"日志"或第一个笔记本
    target_nb = None
    for nb_id, nb_name in notebooks.items():
        if any(k in nb_name for k in ["日志", "日记", "每日", "Daily", "记录"]):
            target_nb = nb_id
            break
    if not target_nb and notebooks:
        target_nb = list(notebooks.keys())[0]

    if not target_nb:
        logger.error("❌ 未找到可用笔记本")
        return ""

    path = f"/每日日志/{TODAY}"
    try:
        result = siyuan_post("/api/filetree/createDocWithMd", {
            "notebook": target_nb,
            "path": path,
            "markdown": content,
        })
        doc_id = result.get("data", "")
        logger.info(f"✅ 思源笔记创建成功: {path} (id: {doc_id})")
        return doc_id
    except Exception as e:
        logger.error(f"❌ 思源写入失败: {e}")
        return ""


def main():
    logger.info("=" * 50)
    logger.info("📅 每日日志聚合启动")
    logger.info("=" * 50)

    notebooks = get_notebooks()
    notes = get_today_new_notes()
    github_events = get_github_events()
    today_files = read_today_files()

    content = generate_daily_log(notes, notebooks, github_events, today_files)
    print(content[:2000])

    # 保存本地
    out_dir = Path(__file__).parent / "logs"
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"daily_{TODAY}.md").write_text(content, encoding='utf-8')

    # 写入思源
    doc_id = write_to_siyuan(content, notebooks)

    # Bark 通知
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from bark_client import bark_notify
        bark_notify(
            title=f"📅 {TODAY_ZH} 每日日志已生成",
            body=f"新笔记{len(notes)}条 · GitHub{len(github_events)}条 · 已写入思源",
            sound="minuet", group="digest"
        )
    except Exception as e:
        logger.warning(f"Bark 失败: {e}")

    logger.info("🎉 每日日志聚合完成")


if __name__ == "__main__":
    main()
