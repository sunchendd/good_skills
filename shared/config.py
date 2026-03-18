"""Shared configuration loaded from environment variables."""
from __future__ import annotations

from dataclasses import dataclass, field
import os


def parse_email_recipients(raw: str) -> list[str]:
    """Parse comma-separated recipient emails from an env var."""
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass
class Config:
    deepseek_api_key: str = ""
    qq_email_password: str = ""
    github_token: str = ""
    siyuan_host: str = "http://127.0.0.1:6806"
    siyuan_token: str = ""
    siyuan_automation_notebook: str = "AI自动化"
    bark_token: str = ""
    email_sender: str = ""
    email_recipients: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            deepseek_api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
            qq_email_password=os.environ.get("QQ_EMAIL_PASSWORD", ""),
            github_token=os.environ.get("GITHUB_TOKEN", ""),
            siyuan_host=os.environ.get("SIYUAN_HOST", "http://127.0.0.1:6806"),
            siyuan_token=os.environ.get("SIYUAN_TOKEN", ""),
            siyuan_automation_notebook=os.environ.get(
                "SIYUAN_AUTOMATION_NOTEBOOK",
                "AI自动化",
            ),
            bark_token=os.environ.get("BARK_TOKEN", ""),
            email_sender=os.environ.get("EMAIL_SENDER", "").strip(),
            email_recipients=parse_email_recipients(
                os.environ.get("EMAIL_RECIPIENTS", "")
            ),
        )


cfg = Config.from_env()
