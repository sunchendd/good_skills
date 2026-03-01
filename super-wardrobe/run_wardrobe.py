#!/usr/bin/env python3
"""Super 衣橱 - 主入口"""
import sys, os, logging, datetime, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))

from wardrobe_advisor import fetch_weather, generate_outfit, format_full_newsletter
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "daily-newsletter-skill"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_email(content, subject):
    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    import markdown as md_lib

    sender = "995943586@qq.com"
    recipients = ["2464076118@qq.com", "sunchend@outlook.com"]
    password = os.environ.get("QQ_EMAIL_PASSWORD")
    if not password:
        logger.error("未设置 QQ_EMAIL_PASSWORD"); return False

    extensions = ['markdown.extensions.tables','markdown.extensions.nl2br','markdown.extensions.fenced_code']
    html_body = md_lib.markdown(content, extensions=extensions)
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
body{{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;line-height:1.7;color:#333;max-width:700px;margin:0 auto;padding:20px;background:#f5f5f5}}
.c{{background:#fff;padding:28px;border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.1)}}
h1{{color:#2c3e50;border-bottom:3px solid #e67e22;padding-bottom:10px}}
h2{{color:#2c3e50;margin-top:24px;padding:6px 12px;background:#fff8f0;border-left:4px solid #e67e22;border-radius:4px}}
h3{{color:#34495e}}table{{border-collapse:collapse;width:100%;margin:12px 0}}
th,td{{border:1px solid #ddd;padding:8px 12px}}th{{background:#fff8f0}}
hr{{border:none;border-top:1px solid #eee;margin:20px 0}}
</style></head><body><div class="c">{html_body}</div></body></html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(content, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP("smtp.qq.com", 587) as s:
            s.ehlo(); s.starttls(context=ctx)
            s.login(sender, password)
            s.sendmail(sender, recipients, msg.as_bytes())
        logger.info(f"✅ 邮件已发送 → {recipients}"); return True
    except Exception as e:
        logger.error(f"❌ 邮件失败: {e}"); return False

def send_bark(title, body):
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    try:
        from bark_client import bark_notify
        bark_notify(title=title, body=body, sound="minuet", group="wardrobe")
        logger.info("✅ Bark 已发送")
    except Exception as e:
        logger.warning(f"⚠️ Bark 失败: {e}")

def main():
    logger.info("=" * 50)
    logger.info("👔 Super 衣橱启动")
    logger.info("=" * 50)
    weather = fetch_weather()
    logger.info(f"🌡️ 天气: {weather['weather_desc']} {weather['temp_min']}~{weather['temp_max']}°C 降雨{weather['rain_chance']}%")
    outfit = generate_outfit(weather)
    content = format_full_newsletter(weather, outfit)

    # 保存
    out_dir = pathlib.Path(__file__).parent / "outfits"
    out_dir.mkdir(exist_ok=True)
    fname = out_dir / f"outfit_{datetime.datetime.now().strftime('%Y%m%d')}.md"
    fname.write_text(content, encoding='utf-8')

    # 打印
    print(content)

    if "--no-send" in sys.argv:
        return

    today = datetime.datetime.now().strftime("%Y年%m月%d日")
    umbrella = "☂️ 今日带伞" if weather['rain_chance'] > 30 else "☀️ 今日无需带伞"
    temp_range = f"{weather['temp_min']}~{weather['temp_max']}°C"

    send_email(content, f"👔 今日穿搭建议 {today} | {weather['weather_desc']} {temp_range}")
    send_bark(
        title=f"👔 今日穿搭建议 {today}",
        body=f"{weather['weather_desc']} {temp_range} | 降雨{weather['rain_chance']}% | {umbrella}"
    )
    logger.info("🎉 Super 衣橱运行完成")

if __name__ == "__main__":
    main()
