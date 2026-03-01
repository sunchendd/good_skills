"""统一配置 - 从环境变量读取"""
from __future__ import annotations
from dataclasses import dataclass, field
import os


@dataclass
class Config:
    deepseek_api_key: str = ""
    qq_email_password: str = ""
    github_token: str = ""
    siyuan_host: str = "http://192.168.3.32:6806"
    siyuan_token: str = ""
    bark_token: str = "seYne8cq4c7MkzqWqF2JPJ"
    email_sender: str = "995943586@qq.com"
    email_recipients: list[str] = field(default_factory=lambda: [
        "2464076118@qq.com",
        "sunchend@outlook.com",
    ])

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            deepseek_api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
            qq_email_password=os.environ.get("QQ_EMAIL_PASSWORD", ""),
            github_token=os.environ.get("GITHUB_TOKEN", ""),
            siyuan_host=os.environ.get("SIYUAN_HOST", "http://192.168.3.32:6806"),
            siyuan_token=os.environ.get("SIYUAN_TOKEN", ""),
            bark_token=os.environ.get("BARK_TOKEN", "seYne8cq4c7MkzqWqF2JPJ"),
            email_sender=os.environ.get("EMAIL_SENDER", "995943586@qq.com"),
        )


cfg = Config.from_env()
