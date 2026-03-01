#!/usr/bin/env python3
"""
邮件发送模块
通过SMTP发送每日早报到指定邮箱
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import datetime
import markdown
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        """初始化邮件发送器"""
        # QQ邮箱SMTP配置
        self.smtp_server = "smtp.qq.com"
        self.smtp_port = 587  # 使用TLS
        self.sender_email = "995943586@qq.com"  # 发送方邮箱
        self.sender_password = None  # 需要设置授权码
        
    def set_credentials(self, password: str):
        """设置邮箱授权码"""
        self.sender_password = password
        
    def markdown_to_html(self, markdown_content: str) -> str:
        """将Markdown转换为HTML"""
        try:
            # 配置markdown扩展
            extensions = [
                'markdown.extensions.tables',
                'markdown.extensions.fenced_code',
                'markdown.extensions.toc',
                'markdown.extensions.nl2br'
            ]
            
            html_content = markdown.markdown(markdown_content, extensions=extensions)
            
            # 添加CSS样式
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>每日科技早报</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f8f9fa;
                    }}
                    .container {{
                        background-color: white;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    h1 {{
                        color: #2c3e50;
                        border-bottom: 3px solid #3498db;
                        padding-bottom: 10px;
                        margin-bottom: 30px;
                    }}
                    h2 {{
                        color: #34495e;
                        margin-top: 30px;
                        margin-bottom: 15px;
                        padding-left: 10px;
                        border-left: 4px solid #3498db;
                    }}
                    h3 {{
                        color: #2c3e50;
                        margin-top: 20px;
                        margin-bottom: 10px;
                    }}
                    a {{
                        color: #3498db;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    .news-item {{
                        background-color: #f8f9fa;
                        padding: 15px;
                        margin: 10px 0;
                        border-radius: 5px;
                        border-left: 3px solid #3498db;
                    }}
                    .source {{
                        font-weight: bold;
                        color: #7f8c8d;
                    }}
                    .summary {{
                        margin-top: 8px;
                        color: #2c3e50;
                    }}
                    .stats {{
                        background-color: #ecf0f1;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #bdc3c7;
                        color: #7f8c8d;
                        font-size: 0.9em;
                    }}
                    .emoji {{
                        font-size: 1.2em;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    {html_content}
                </div>
            </body>
            </html>
            """
            
            return styled_html
            
        except Exception as e:
            logger.error(f"Markdown转HTML失败: {e}")
            return f"<html><body><pre>{markdown_content}</pre></body></html>"
    
    def send_newsletter(self, newsletter_path: Path, subject_prefix: str = "") -> bool:
        """发送早报邮件"""
        # 定义收件人列表
        to_emails = ["2464076118@qq.com", "sunchend@outlook.com"]
        
        try:
            if not self.sender_password:
                logger.error("未设置邮箱授权码")
                return False
                
            # 读取早报内容
            if not newsletter_path.exists():
                logger.error(f"早报文件不存在: {newsletter_path}")
                return False
                
            with open(newsletter_path, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # 转换为HTML
            html_content = self.markdown_to_html(markdown_content)
            
            # 创建邮件
            msg = MIMEMultipart('alternative')
            
            # 设置邮件头
            date_str = datetime.datetime.now().strftime('%Y年%m月%d日')
            subject = f"{subject_prefix}每日科技早报 - {date_str}"
            
            from email.header import Header
            msg['Subject'] = str(Header(subject, 'utf-8'))
            msg['From'] = self.sender_email
            msg['To'] = ", ".join(to_emails)
            msg['Date'] = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # 添加纯文本和HTML版本
            msg.attach(MIMEText(markdown_content, 'plain', 'utf-8'))
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))
            
            # 发送邮件
            logger.info(f"正在发送邮件到 {', '.join(to_emails)}...")
            
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg, to_addrs=to_emails)
            
            logger.info("✅ 邮件发送成功！")
            return True
            
        except smtplib.SMTPException as e:
            # 特殊处理QQ邮箱的 "(-1, b'')" 错误，它实际上表示成功
            if e.args and len(e.args) > 1 and e.args[0] == -1 and e.args[1] == b'\x00\x00\x00':
                logger.info("✅ 邮件发送成功！(忽略QQ邮箱特殊返回码)")
                return True
            logger.error(f"❌ 邮件发送失败: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ 邮件发送时发生未知错误: {e}")
            return False
    
    def test_connection(self) -> bool:
        """测试邮箱连接"""
        try:
            if not self.sender_password:
                logger.error("未设置邮箱授权码")
                return False
                
            logger.info("测试邮箱连接...")
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
            
            logger.info("✅ 邮箱连接测试成功！")
            return True
            
        except Exception as e:
            logger.error(f"❌ 邮箱连接测试失败: {e}")
            return False

def main():
    """测试邮件发送功能"""
    sender = EmailSender()
    
    # 这里需要设置QQ邮箱的授权码
    # 获取方式：QQ邮箱设置 -> 账户 -> POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务 -> 生成授权码
    password = input("请输入QQ邮箱授权码: ").strip()
    sender.set_credentials(password)
    
    # 测试连接
    if not sender.test_connection():
        return
    
    # 查找最新的早报文件
    newsletters_dir = Path("newsletters")
    if not newsletters_dir.exists():
        logger.error("newsletters目录不存在")
        return
    
    newsletter_files = list(newsletters_dir.glob("daily_newsletter_*.md"))
    if not newsletter_files:
        logger.error("未找到早报文件")
        return
    
    # 发送最新的早报
    latest_newsletter = max(newsletter_files, key=lambda x: x.stat().st_mtime)
    logger.info(f"发送早报: {latest_newsletter.name}")
    
    success = sender.send_newsletter(latest_newsletter, "[测试] ")
    if success:
        print("🎉 测试邮件发送成功！")
    else:
        print("❌ 测试邮件发送失败！")

if __name__ == "__main__":
    main()