#!/usr/bin/env python3
"""
每日日志聚合器
聚合：GitHub 动态、今日arXiv/早报/健身/穿搭内容
"""
import urllib.request, json, os, sys, logging, datetime
from pathlib import Path
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
DEEPSEEK_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

TODAY = datetime.date.today().strftime("%Y-%m-%d")
TODAY_ZH = datetime.datetime.now().strftime("%Y年%m月%d日")


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
def generate_daily_log(github_events: list, today_files: dict) -> str:
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
        f"- GitHub 动态：{len(github_events)} 条",
        f"- 早报已发送：{'✅' if 'newsletter' in today_files else '❌'}",
        f"- arXiv 论文：{'✅' if 'arxiv' in today_files else '❌'}",
        f"- 健身计划：{'✅' if 'fitness' in today_files else '❌'}",
        f"- 穿搭建议：{'✅' if 'wardrobe' in today_files else '❌'}",
        f"- 视频精选：{'✅' if 'video' in today_files else '❌'}",
        f"- 无语哥选题：{'✅' if 'wuyu' in today_files else '❌'}",
        "", "---", "",
    ]

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


def main():
    logger.info("=" * 50)
    logger.info("📅 每日日志聚合启动")
    logger.info("=" * 50)

    github_events = get_github_events()
    today_files = read_today_files()

    content = generate_daily_log(github_events, today_files)
    print(content[:2000])

    # 保存本地
    out_dir = Path(__file__).parent / "logs"
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"daily_{TODAY}.md").write_text(content, encoding='utf-8')

    # Bark 通知
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from bark_client import bark_notify
        bark_notify(
            title=f"📅 {TODAY_ZH} 每日日志已生成",
            body=f"🐙 GitHub{len(github_events)}条活动",
            sound="minuet", group="digest"
        )
    except Exception as e:
        logger.warning(f"Bark 失败: {e}")

    logger.info("🎉 每日日志聚合完成")


if __name__ == "__main__":
    main()
