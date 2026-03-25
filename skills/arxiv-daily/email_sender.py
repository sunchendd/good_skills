#!/usr/bin/env python3
"""邮件发送模块（复用 daily-newsletter 逻辑）"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
import logging
import os
import markdown as markdown_lib
from pathlib import Path

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self):
        self.smtp_server = "smtp.qq.com"
        self.smtp_port = 587
        self.sender_email = os.environ.get("EMAIL_SENDER", "").strip()
        self.sender_password = os.environ.get("QQ_EMAIL_PASSWORD")
        self.recipients = [
            item.strip()
            for item in os.environ.get("EMAIL_RECIPIENTS", "").split(",")
            if item.strip()
        ]

    def markdown_to_html(self, md_content: str) -> str:
        extensions = [
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.nl2br',
        ]
        html_body = markdown_lib.markdown(md_content, extensions=extensions)
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>arXiv AI 论文精选</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif;
    line-height: 1.7; color: #333; max-width: 860px;
    margin: 0 auto; padding: 20px; background: #f5f5f5;
  }}
  .container {{ background: #fff; padding: 32px; border-radius: 12px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.1); }}
  h1 {{ color: #1a1a2e; border-bottom: 3px solid #6c63ff; padding-bottom: 12px; }}
  h2 {{ color: #2c3e50; margin-top: 32px; padding: 6px 12px;
    background: #f0f0ff; border-left: 4px solid #6c63ff; border-radius: 4px; }}
  h3 {{ color: #34495e; margin-top: 24px; }}
  blockquote {{ background: #fffbf0; border-left: 4px solid #f0b429;
    padding: 8px 16px; margin: 8px 0; border-radius: 4px; }}
  a {{ color: #6c63ff; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  code {{ background: #f0f0f0; padding: 1px 6px; border-radius: 3px; font-size: 0.9em; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
  th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
  th {{ background: #f8f8ff; }}
  hr {{ border: none; border-top: 1px solid #eee; margin: 24px 0; }}
</style>
</head>
<body><div class="container">{html_body}</div></body>
</html>"""

    def send(self, md_content: str, subject: str) -> bool:
        if not self.sender_email or not self.recipients or not self.sender_password:
            logger.error("❌ 未设置 EMAIL_SENDER / EMAIL_RECIPIENTS / QQ_EMAIL_PASSWORD")
            return False
        import time
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = ", ".join(self.recipients)
        html = self.markdown_to_html(md_content)
        msg.attach(MIMEText(md_content, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
        for attempt in range(3):
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_server, 465, context=context) as server:
                    server.login(self.sender_email, self.sender_password)
                    server.sendmail(self.sender_email, self.recipients, msg.as_bytes())
                logger.info(f"✅ 邮件发送成功 → {self.recipients}")
                return True
            except Exception as e:
                if attempt < 2:
                    logger.warning(f"⚠️ 邮件发送失败，重试 {attempt+1}/2: {e}"); time.sleep(3)
                else:
                    logger.error(f"❌ 邮件发送失败: {e}")
                    return False
