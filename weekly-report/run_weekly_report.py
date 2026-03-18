#!/usr/bin/env python3
"""
每周报告生成器 - 每周六自动运行
数据来源：macOS日历(icalBuddy) + 思源笔记 + GitHub动态 + 各skill输出
生成：结构化周报 + 时间分析 + 未完成任务 + 下周规划建议
"""
import subprocess, urllib.request, json, os, sys, re, logging, datetime
from pathlib import Path
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from shared.siyuan import save_named_automation_report
except Exception:
    save_named_automation_report = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SIYUAN_HOST = os.environ.get("SIYUAN_HOST", "http://127.0.0.1:6806")
SIYUAN_TOKEN = os.environ.get("SIYUAN_TOKEN", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT_DIR = Path(__file__).parent / "reports"

today = datetime.date.today()
# 本周一到本周日
week_start = today - datetime.timedelta(days=today.weekday())
week_end = week_start + datetime.timedelta(days=6)
WEEK_STR = f"{week_start.strftime('%Y.%m.%d')} - {week_end.strftime('%Y.%m.%d')}"
WEEK_NUM = today.isocalendar()[1]


def get_calendar_events() -> list[dict]:
    """用 icalBuddy 读取本周日历事件"""
    events = []
    try:
        cmd = ["icalBuddy", "-f", "-tf", "%H:%M",
               f"eventsFrom:{week_start.strftime('%Y-%m-%d')}",
               f"to:{week_end.strftime('%Y-%m-%d')}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        raw = result.stdout

        current_event = None
        for line in raw.split('\n'):
            line = line.strip()
            if line.startswith('•'):
                if current_event:
                    events.append(current_event)
                title = line[1:].strip()
                current_event = {'title': title, 'time': '', 'calendar': '', 'location': ''}
            elif line.startswith('at') or re.match(r'\d{1,2}:\d{2}', line):
                if current_event:
                    current_event['time'] = line
            elif line.startswith('location:'):
                if current_event:
                    current_event['location'] = line.replace('location:', '').strip()
            elif line and line.startswith('(') and line.endswith(')'):
                if current_event:
                    current_event['calendar'] = line.strip('()')

        if current_event:
            events.append(current_event)
        logger.info(f"✅ 日历事件: {len(events)} 个")
    except Exception as e:
        logger.warning(f"日历读取失败: {e}")
    return events


def get_reminders() -> list[dict]:
    """用 remindctl 读取提醒事项"""
    reminders = []
    try:
        result = subprocess.run(["remindctl", "list", "--json"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for item in data:
                reminders.append({
                    'title': item.get('title', ''),
                    'completed': item.get('isCompleted', False),
                    'due': item.get('dueDate', ''),
                    'list': item.get('listName', ''),
                })
            logger.info(f"✅ 提醒事项: {len(reminders)} 个")
    except Exception as e:
        logger.warning(f"Reminders 读取失败: {e}")
    return reminders


def get_siyuan_week_notes() -> list[dict]:
    """读取本周在思源笔记创建的文档"""
    notes = []
    try:
        start_str = week_start.strftime("%Y%m%d") + "000000"
        end_str = week_end.strftime("%Y%m%d") + "235959"
        req = urllib.request.Request(
            f"{SIYUAN_HOST}/api/query/sql",
            data=json.dumps({"stmt": f"SELECT id, content, box, path, created FROM blocks WHERE type='d' AND created >= '{start_str}' AND created <= '{end_str}' ORDER BY created DESC LIMIT 50"}).encode(),
            headers={"Authorization": f"Token {SIYUAN_TOKEN}", "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            result = json.loads(r.read())
        notes = result.get("data", [])
        logger.info(f"✅ 思源本周笔记: {len(notes)} 条")
    except Exception as e:
        logger.warning(f"思源读取失败: {e}")
    return notes


def get_github_week_activity() -> dict:
    """本周 GitHub 动态汇总"""
    activity = {"vllm_releases": [], "deepseek_repos": [], "events": []}
    try:
        # vllm-ascend 本周 releases
        req = urllib.request.Request(
            "https://api.github.com/repos/vllm-project/vllm-ascend/releases?per_page=5",
            headers={"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "openclaw"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            releases = json.loads(r.read())
        for rel in releases:
            pub = rel.get("published_at", "")[:10]
            if pub >= str(week_start):
                activity["vllm_releases"].append(f"{rel['tag_name']} ({pub})")

        # PR 活动
        req2 = urllib.request.Request(
            "https://api.github.com/repos/vllm-project/vllm-ascend/events?per_page=30",
            headers={"Authorization": f"token {GITHUB_TOKEN}", "User-Agent": "openclaw"}
        )
        with urllib.request.urlopen(req2, timeout=10) as r:
            events = json.loads(r.read())
        week_events = [e for e in events if e.get("created_at", "")[:10] >= str(week_start)]
        pr_actors = set()
        for e in week_events:
            if e.get("type") == "PullRequestEvent":
                pr_actors.add(e.get("actor", {}).get("login", ""))
        activity["events"] = week_events[:10]
        activity["pr_count"] = len([e for e in week_events if e.get("type") == "PullRequestEvent"])
        activity["pr_actors"] = list(pr_actors)
        logger.info(f"✅ GitHub 本周活动: {len(week_events)} 条")
    except Exception as e:
        logger.warning(f"GitHub 活动获取失败: {e}")
    return activity


def collect_week_skill_outputs() -> dict:
    """收集本周各 skill 的输出文件"""
    outputs = {}
    skill_dirs = {
        'arxiv': (Path.home() / ".openclaw/skills/arxiv-daily/newsletters", "arXiv 精选"),
        'fitness': (Path.home() / ".openclaw/skills/super-fitness/daily_tasks", "健身记录"),
        'vibe': (Path.home() / ".openclaw/skills/vibe-daily/newsletters", "Vibe Coding"),
        'wuyu': (Path.home() / ".openclaw/skills/wuyu-xiaohongshu/notes", "无语哥选题"),
    }
    for key, (folder, label) in skill_dirs.items():
        if not folder.exists():
            continue
        week_files = []
        for date in [week_start + datetime.timedelta(days=i) for i in range(7)]:
            date_str = date.strftime("%Y%m%d")
            matches = list(folder.glob(f"*{date_str}*"))
            week_files.extend(matches)
        if week_files:
            outputs[key] = {"label": label, "count": len(week_files), "files": week_files}
    return outputs


def generate_weekly_report_ai(data: dict) -> str:
    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

    cal_text = "\n".join([f"- {e.get('time','')} {e['title']} {e.get('calendar','')}" for e in data['calendar'][:30]]) or "（无日历数据）"
    rem_text_done = "\n".join([f"- ✅ {r['title']}" for r in data['reminders'] if r['completed']][:20]) or "（无）"
    rem_text_todo = "\n".join([f"- ⬜ {r['title']} (到期:{r.get('due','')[:10]})" for r in data['reminders'] if not r['completed']][:20]) or "（无）"
    notes_text = "\n".join([f"- {n.get('content','无标题')[:50]}" for n in data['notes'][:20]]) or "（无）"
    github_text = f"vLLM-Ascend: {data['github'].get('vllm_releases', [])} | PR数: {data['github'].get('pr_count',0)}"
    skill_text = "\n".join([f"- {v['label']}: {v['count']}天有记录" for v in data['skills'].values()])

    prompt = f"""你是一位专业的个人效能顾问。请根据以下信息生成本周工作总结报告。

## 本周时间：{WEEK_STR}（第{WEEK_NUM}周）

## 日历事件（{len(data['calendar'])}个）
{cal_text}

## 已完成提醒事项
{rem_text_done}

## 未完成提醒事项
{rem_text_todo}

## 本周思源笔记（{len(data['notes'])}条新建）
{notes_text}

## GitHub 动态
{github_text}

## 各类日报执行情况
{skill_text}

请生成结构化周报（Markdown格式），包含以下章节：

### 📊 本周总览
（用一段话概括这周做了什么，主基调是什么）

### ✅ 本周完成事项
（结合日历+提醒事项，分类整理）

### 📝 本周学习与积累
（结合思源笔记数量、arXiv论文、vibe coding等）

### ⚠️ 未完成 & 遗留事项
（列出未完成的任务，评估紧急程度）

### ⏰ 时间分配分析
（基于日历分析时间用在哪里，是否合理，给出百分比估算）

### 📈 效率洞察
（这周效率如何？哪里可以改进？至少3条具体建议）

### 📅 下周规划建议
（基于未完成任务和规律，给出下周重点事项和时间分配建议）

### 💪 健身打卡情况
（结合健身记录）

语气专业但温和，建议要具体可执行，不要泛泛而谈。"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        timeout=120,
    )
    return resp.choices[0].message.content


def format_full_report(ai_content: str, data: dict) -> str:
    now = datetime.datetime.now().strftime("%H:%M")
    lines = [
        f"# 📋 第 {WEEK_NUM} 周工作周报",
        f"**{WEEK_STR}** | 生成于 {datetime.datetime.now().strftime('%Y年%m月%d日')} {now}",
        "",
        "---",
        "",
        ai_content,
        "",
        "---",
        "",
        "## 📎 数据附录",
        f"- 日历事件：{len(data['calendar'])} 个",
        f"- 提醒事项：完成 {len([r for r in data['reminders'] if r['completed']])} / 未完成 {len([r for r in data['reminders'] if not r['completed']])}",
        f"- 思源新笔记：{len(data['notes'])} 条",
        f"- GitHub 活动：{data['github'].get('pr_count',0)} 个PR",
        "",
        f"*由 OpenClaw Weekly Report 自动生成 · {WEEK_STR}*",
    ]
    return "\n".join(lines)


def save_to_siyuan(content: str):
    if not save_named_automation_report:
        logger.warning("共享思源模块不可用，跳过思源写入")
        return
    try:
        doc_name = f"{week_start.strftime('%Y-%m-%d')}_第{WEEK_NUM}周"
        result = save_named_automation_report(
            route_key="weekly_report",
            markdown=content,
            doc_name=doc_name,
            title=f"第{WEEK_NUM}周周报",
        )
        logger.info("✅ 思源周报已创建: /效率复盘/周报/%s (%s)", doc_name, result.get("doc_id", ""))
    except Exception as e:
        logger.error(f"❌ 思源失败: {e}")


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
body{{font-family:-apple-system,'PingFang SC',sans-serif;line-height:1.8;color:#333;max-width:860px;margin:0 auto;padding:20px;background:#f9f9f9}}
.c{{background:#fff;padding:32px;border-radius:12px;box-shadow:0 2px 16px rgba(0,0,0,.08)}}
h1{{color:#1a1a2e;border-bottom:3px solid #6c63ff;padding-bottom:12px}}
h2,h3{{color:#2c3e50;margin-top:24px}}
h3{{padding:6px 12px;background:#f0f0ff;border-left:3px solid #6c63ff;border-radius:4px}}
table{{border-collapse:collapse;width:100%;margin:12px 0}}th,td{{border:1px solid #ddd;padding:8px 12px}}
th{{background:#f0f0ff}}hr{{border:none;border-top:1px solid #eee;margin:24px 0}}
blockquote{{background:#fffbf0;border-left:4px solid #f0b429;padding:8px 16px;border-radius:4px}}
</style></head><body><div class="c">{html_body}</div></body></html>"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject; msg["From"] = sender; msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(content, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP("smtp.qq.com", 587) as s:
            s.ehlo(); s.starttls(context=ctx); s.login(sender, password)
            s.sendmail(sender, recipients, msg.as_bytes())
        logger.info("✅ 邮件发送成功"); return True
    except Exception as e:
        logger.error(f"❌ 邮件失败: {e}"); return False


def main():
    no_send = "--no-send" in sys.argv
    logger.info("=" * 50); logger.info(f"📋 周报生成 · 第{WEEK_NUM}周"); logger.info("=" * 50)

    data = {
        "calendar": get_calendar_events(),
        "reminders": get_reminders(),
        "notes": get_siyuan_week_notes(),
        "github": get_github_week_activity(),
        "skills": collect_week_skill_outputs(),
    }

    ai_content = generate_weekly_report_ai(data)
    report = format_full_report(ai_content, data)

    OUTPUT_DIR.mkdir(exist_ok=True)
    fname = OUTPUT_DIR / f"weekly_{week_start.strftime('%Y_W%W')}.md"
    fname.write_text(report, encoding='utf-8')
    print(report[:3000])

    if no_send: return

    save_to_siyuan(report)
    send_email(report, f"📋 第{WEEK_NUM}周工作周报 | {WEEK_STR}")

    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from bark_client import bark_notify
        bark_notify(
            title=f"📋 第{WEEK_NUM}周周报已生成",
            body=f"{WEEK_STR}\n日历{len(data['calendar'])}项 · 笔记{len(data['notes'])}条 · 已写入思源",
            sound="minuet", group="report"
        )
    except Exception as e:
        logger.warning(f"Bark 失败: {e}")

    logger.info("🎉 周报生成完成")


if __name__ == "__main__":
    main()
