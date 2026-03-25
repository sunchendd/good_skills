#!/usr/bin/env python3
"""Super 健身 - 主入口"""
import sys, os, logging, datetime, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fitness_plan import get_three_month_plan, get_day_number, generate_daily_task, format_newsletter, USER_PROFILE
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_email(content, subject):
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import markdown as md_lib

    sender = os.environ.get("EMAIL_SENDER", "").strip()
    recipients = [item.strip() for item in os.environ.get("EMAIL_RECIPIENTS", "").split(",") if item.strip()]
    password = os.environ.get("QQ_EMAIL_PASSWORD")
    if not sender or not recipients or not password: return False

    html_body = md_lib.markdown(content, extensions=['markdown.extensions.tables','markdown.extensions.nl2br'])
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
body{{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;line-height:1.7;color:#333;max-width:700px;margin:0 auto;padding:20px;background:#f0f8f0}}
.c{{background:#fff;padding:28px;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.1)}}
h1{{color:#1a5c2a;border-bottom:3px solid #27ae60;padding-bottom:10px}}
h2,h3{{color:#1a5c2a}}
h4{{color:#27ae60;margin:16px 0 8px}}
blockquote{{background:#f0fff4;border-left:4px solid #27ae60;padding:8px 16px;margin:8px 0;border-radius:4px}}
table{{border-collapse:collapse;width:100%;margin:12px 0}}th,td{{border:1px solid #ddd;padding:8px 12px}}
th{{background:#f0fff4}}hr{{border:none;border-top:1px solid #eee;margin:20px 0}}
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
            logger.info(f"✅ 邮件发送成功"); return True
        except Exception as e:
            if attempt < 2:
                logger.warning(f"⚠️ 邮件发送失败，重试 {attempt+1}/2: {e}"); time.sleep(3)
            else:
                logger.error(f"❌ 邮件失败: {e}"); return False

def send_bark(title, body):
    try:
        sys.path.insert(0, str(pathlib.Path(__file__).parent))
        from bark_client import bark_notify
        bark_notify(title=title, body=body, sound="minuet", group="fitness")
        logger.info("✅ Bark 已发送")
    except Exception as e:
        logger.warning(f"⚠️ Bark 失败: {e}")

def main():
    logger.info("=" * 50)
    logger.info("💪 Super 健身启动")
    generate_plan_only = "--plan" in sys.argv
    no_send = "--no-send" in sys.argv

    client = OpenAI(api_key=os.environ["DEEPSEEK_API_KEY"], base_url="https://api.deepseek.com")

    # 如果是 --plan 模式，只生成三个月计划
    if generate_plan_only:
        plan = get_three_month_plan(client)
        print(plan)
        return

    plan = get_three_month_plan(client)
    day_num, week_num = get_day_number()
    daily = generate_daily_task(client, day_num, week_num, plan)
    content = format_newsletter(daily, day_num, week_num)

    out_dir = pathlib.Path(__file__).parent / "daily_tasks"
    out_dir.mkdir(exist_ok=True)
    fname = out_dir / f"fitness_{datetime.datetime.now().strftime('%Y%m%d')}.md"
    fname.write_text(content, encoding='utf-8')
    print(content)

    if no_send: return

    today = datetime.datetime.now().strftime("%Y年%m月%d日")
    send_email(content, f"💪 今日健身任务 {today} · 第{day_num}天")
    # 从生成内容里提取关键摘要
    import re as _re
    goal_m = _re.search(r'\*\*今日目标[：:]\*\*\s*(.+)', content)
    cal_m = _re.search(r'今日总热量[：:].*?约\s*([\d,，]+)\s*kcal', content)
    type_m = _re.search(r'###\s*(.+?日)\s*·', content)
    goal_line = goal_m.group(1).strip()[:60] if goal_m else ""
    cal_line = f"🔥 {cal_m.group(1)} kcal" if cal_m else ""
    type_line = type_m.group(1).strip() if type_m else f"第{week_num}周训练"
    bark_lines = [f"第{day_num}天 · {type_line}"]
    if goal_line:
        bark_lines.append(f"🎯 {goal_line}")
    if cal_line:
        bark_lines.append(cal_line)
    send_bark(
        title=f"💪 今日健身任务 · 第{day_num}天",
        body="\n".join(bark_lines)
    )
    logger.info("🎉 Super 健身运行完成")

if __name__ == "__main__":
    main()
