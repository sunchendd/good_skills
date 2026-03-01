"""统一邮件发送模块"""
from __future__ import annotations
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

import markdown as md_lib

from .config import cfg

logger = logging.getLogger(__name__)

# ── 通用 HTML 模板 ────────────────────────────────────────────────────────────
_HTML_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;
  line-height:1.7;color:{fg};max-width:860px;margin:0 auto;padding:20px;background:{bg}}}
.c{{background:{card};padding:28px;border-radius:12px;box-shadow:0 2px 16px {shadow}}}
h1{{color:{h1};border-bottom:3px solid {accent};padding-bottom:10px}}
h2{{color:{h2};margin-top:24px;padding:6px 12px;background:{h2bg};border-left:4px solid {accent};border-radius:4px}}
h3{{color:{h3}}}
a{{color:{accent};text-decoration:none}}a:hover{{text-decoration:underline}}
code{{background:{codebg};padding:1px 6px;border-radius:3px;font-size:0.9em}}
table{{border-collapse:collapse;width:100%;margin:12px 0}}
th,td{{border:1px solid {border};padding:8px 12px;text-align:left}}
th{{background:{thbg}}}
hr{{border:none;border-top:1px solid {border};margin:20px 0}}
blockquote{{background:{quotebg};border-left:4px solid {quoteaccent};padding:8px 16px;margin:8px 0;border-radius:4px}}
p,li{{color:{fg}}}
</style></head><body><div class="c">{body}</div></body></html>"""

# ── 预定义颜色主题 ─────────────────────────────────────────────────────────────
THEMES: dict[str, dict] = {
    "default": dict(
        fg="#333", bg="#f5f5f5", card="#fff", shadow="rgba(0,0,0,0.1)",
        h1="#1a1a2e", h2="#2c3e50", h2bg="#f0f0ff", h3="#34495e",
        accent="#6c63ff", border="#ddd", thbg="#f8f8ff", codebg="#f0f0f0",
        quotebg="#fffbf0", quoteaccent="#f0b429",
    ),
    "green": dict(
        fg="#333", bg="#f0f8f0", card="#fff", shadow="rgba(0,0,0,0.1)",
        h1="#1a5c2a", h2="#1a5c2a", h2bg="#f0fff4", h3="#27ae60",
        accent="#27ae60", border="#ddd", thbg="#f0fff4", codebg="#e8f5e9",
        quotebg="#f0fff4", quoteaccent="#27ae60",
    ),
    "orange": dict(
        fg="#333", bg="#f5f5f5", card="#fff", shadow="rgba(0,0,0,0.1)",
        h1="#2c3e50", h2="#2c3e50", h2bg="#fff8f0", h3="#34495e",
        accent="#e67e22", border="#ddd", thbg="#fff8f0", codebg="#fff3e0",
        quotebg="#fff8f0", quoteaccent="#e67e22",
    ),
    "pink": dict(
        fg="#333", bg="#fff0f5", card="#fff", shadow="rgba(255,71,87,0.15)",
        h1="#ff4757", h2="#333", h2bg="#fff0f5", h3="#555",
        accent="#ff4757", border="#ffd6e0", thbg="#fff0f5", codebg="#fff0f5",
        quotebg="#fff0f5", quoteaccent="#ff6b81",
    ),
    "bili": dict(
        fg="#333", bg="#f5f5f5", card="#fff", shadow="rgba(0,0,0,0.1)",
        h1="#fb7299", h2="#333", h2bg="#fff0f5", h3="#444",
        accent="#fb7299", border="#eee", thbg="#fff0f5", codebg="#f5f5f5",
        quotebg="#fff0f5", quoteaccent="#fb7299",
    ),
    "dark": dict(
        fg="#e6edf3", bg="#0d1117", card="#161b22", shadow="rgba(0,0,0,0.3)",
        h1="#58a6ff", h2="#58a6ff", h2bg="#21262d", h3="#58a6ff",
        accent="#58a6ff", border="#30363d", thbg="#21262d", codebg="#21262d",
        quotebg="#161b22", quoteaccent="#58a6ff",
    ),
    "weekly": dict(
        fg="#333", bg="#f9f9f9", card="#fff", shadow="rgba(0,0,0,0.08)",
        h1="#1a1a2e", h2="#2c3e50", h2bg="#f0f0ff", h3="#2c3e50",
        accent="#6c63ff", border="#ddd", thbg="#f0f0ff", codebg="#f0f0f0",
        quotebg="#fffbf0", quoteaccent="#f0b429",
    ),
}


def markdown_to_html(md_content: str, theme: str = "default") -> str:
    """将 Markdown 转换为带样式的 HTML 邮件"""
    extensions = [
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.nl2br',
    ]
    html_body = md_lib.markdown(md_content, extensions=extensions)
    colors = THEMES.get(theme, THEMES["default"])
    return _HTML_TEMPLATE.format(body=html_body, **colors)


def send_email(
    content: str,
    subject: str,
    theme: str = "default",
    *,
    recipients: list[str] | None = None,
) -> bool:
    """发送邮件（Markdown → HTML）"""
    password = cfg.qq_email_password
    if not password:
        logger.error("❌ 未设置 QQ_EMAIL_PASSWORD")
        return False

    to_list = recipients or cfg.email_recipients
    html = markdown_to_html(content, theme=theme)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = cfg.email_sender
    msg["To"] = ", ".join(to_list)
    msg.attach(MIMEText(content, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP("smtp.qq.com", 587) as s:
            s.ehlo()
            s.starttls(context=ctx)
            s.login(cfg.email_sender, password)
            s.sendmail(cfg.email_sender, to_list, msg.as_bytes())
        logger.info(f"✅ 邮件发送成功 → {to_list}")
        return True
    except Exception as e:
        logger.error(f"❌ 邮件发送失败: {e}")
        return False
