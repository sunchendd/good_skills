"""Shared SiYuan helpers for automation notebooks and reports."""
from __future__ import annotations

from datetime import date
import json
import logging
import urllib.error
import urllib.request

from .config import cfg

logger = logging.getLogger(__name__)


def _clean_path_part(value: str) -> str:
    cleaned = (value or "").strip().strip("/")
    return cleaned or "未命名"


def _resolve_day(day: date | str | None) -> str:
    if day is None:
        return date.today().isoformat()
    if isinstance(day, date):
        return day.isoformat()
    return str(day).strip() or date.today().isoformat()


def build_automation_path(
    feature_name: str,
    report_name: str,
    doc_name: str | None = None,
    day: date | str | None = None,
) -> str:
    """Build a normalized automation path inside the AI notebook."""
    leaf = _clean_path_part(doc_name or _resolve_day(day))
    return (
        f"/{_clean_path_part(feature_name)}"
        f"/{_clean_path_part(report_name)}"
        f"/{leaf}"
    )


class SiyuanClient:
    """Tiny SiYuan API client focused on note automation."""

    def __init__(
        self,
        host: str | None = None,
        token: str | None = None,
        automation_notebook: str | None = None,
    ) -> None:
        self.host = (host or cfg.siyuan_host).rstrip("/")
        self.token = token or cfg.siyuan_token
        self.automation_notebook = (
            automation_notebook or cfg.siyuan_automation_notebook
        )

    def post(self, path: str, data: dict, timeout: float = 15) -> dict:
        url = f"{self.host}{path}"
        body = json.dumps(data).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Token {self.token}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def get_notebooks(self) -> list[dict]:
        result = self.post("/api/notebook/lsNotebooks", {})
        return result.get("data", {}).get("notebooks", [])

    def get_notebook_map(self) -> dict[str, str]:
        return {item["id"]: item["name"] for item in self.get_notebooks()}

    def find_notebook_id(self, keywords: list[str] | None = None) -> str | None:
        notebooks = self.get_notebooks()
        if not notebooks:
            return None

        if keywords:
            for notebook in notebooks:
                if any(keyword == notebook["name"] for keyword in keywords):
                    return notebook["id"]
            for notebook in notebooks:
                if any(keyword in notebook["name"] for keyword in keywords):
                    return notebook["id"]

        return notebooks[0]["id"]

    def ensure_notebook(self, notebook_name: str | None = None) -> str | None:
        target_name = notebook_name or self.automation_notebook
        notebook_id = self.find_notebook_id([target_name])
        if notebook_id:
            return notebook_id

        try:
            result = self.post(
                "/api/notebook/createNotebook",
                {"name": target_name},
            )
        except urllib.error.URLError as exc:
            logger.error("Failed to create notebook %s: %s", target_name, exc)
            return None

        data = result.get("data") or {}
        notebook = data.get("notebook") if isinstance(data, dict) else None
        if isinstance(notebook, dict) and notebook.get("id"):
            return notebook["id"]

        return self.find_notebook_id([target_name])

    def create_doc(self, notebook_id: str, path: str, markdown: str) -> str:
        result = self.post(
            "/api/filetree/createDocWithMd",
            {
                "notebook": notebook_id,
                "path": path,
                "markdown": markdown,
            },
        )
        return result.get("data", "")

    def create_or_update_doc(
        self,
        path: str,
        title: str | None = None,
        content: str = "",
        notebook_name: str | None = None,
    ) -> dict:
        notebook_id = self.ensure_notebook(notebook_name)
        if not notebook_id:
            return {"ok": False, "path": path, "doc_id": ""}

        markdown = content
        if title and not content.lstrip().startswith("#"):
            markdown = f"# {title}\n\n{content}"

        doc_id = self.create_doc(notebook_id, path, markdown)
        return {"ok": bool(doc_id), "path": path, "doc_id": doc_id}

    def create_automation_doc(
        self,
        *,
        feature_name: str,
        report_name: str,
        markdown: str,
        doc_name: str | None = None,
        day: date | str | None = None,
        title: str | None = None,
    ) -> dict:
        path = build_automation_path(
            feature_name,
            report_name,
            doc_name=doc_name,
            day=day,
        )
        return self.create_or_update_doc(path=path, title=title, content=markdown)


def siyuan_post(path: str, data: dict) -> dict:
    return SiyuanClient().post(path, data)


def get_notebooks() -> dict[str, str]:
    try:
        return SiyuanClient().get_notebook_map()
    except Exception as exc:
        logger.error("Failed to load notebooks: %s", exc)
        return {}


def create_doc(notebook_id: str, path: str, markdown: str) -> str:
    try:
        return SiyuanClient().create_doc(notebook_id, path, markdown)
    except Exception as exc:
        logger.error("Failed to create document %s: %s", path, exc)
        return ""


def find_notebook(keywords: list[str] | None = None) -> str | None:
    try:
        return SiyuanClient().find_notebook_id(keywords)
    except Exception as exc:
        logger.error("Failed to find notebook: %s", exc)
        return None


def query_sql(stmt: str) -> list[dict]:
    try:
        result = SiyuanClient().post("/api/query/sql", {"stmt": stmt})
        return result.get("data", [])
    except Exception as exc:
        logger.error("Failed to query SiYuan SQL: %s", exc)
        return []


def save_automation_report(
    *,
    markdown: str,
    feature_name: str,
    report_name: str,
    doc_name: str | None = None,
    day: date | str | None = None,
    title: str | None = None,
) -> dict:
    client = SiyuanClient()
    return client.create_automation_doc(
        feature_name=feature_name,
        report_name=report_name,
        markdown=markdown,
        doc_name=doc_name,
        day=day,
        title=title,
    )
