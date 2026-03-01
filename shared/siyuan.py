"""思源笔记 API 封装"""
from __future__ import annotations
import urllib.request
import json
import logging
from .config import cfg

logger = logging.getLogger(__name__)


def siyuan_post(path: str, data: dict) -> dict:
    """调用思源 API"""
    url = f"{cfg.siyuan_host}{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Token {cfg.siyuan_token}",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def get_notebooks() -> dict[str, str]:
    """获取笔记本 id→name 映射"""
    try:
        r = siyuan_post("/api/notebook/lsNotebooks", {})
        return {nb["id"]: nb["name"] for nb in r.get("data", {}).get("notebooks", [])}
    except Exception:
        return {}


def create_doc(notebook_id: str, path: str, markdown: str) -> str:
    """在笔记本中创建文档，返回 doc_id"""
    try:
        result = siyuan_post("/api/filetree/createDocWithMd", {
            "notebook": notebook_id,
            "path": path,
            "markdown": markdown,
        })
        doc_id = result.get("data", "")
        logger.info(f"✅ 思源笔记创建: {path} ({doc_id})")
        return doc_id
    except Exception as e:
        logger.error(f"❌ 思源写入失败: {e}")
        return ""


def find_notebook(keywords: list[str] | None = None) -> str | None:
    """根据关键词找笔记本 ID，找不到则返回第一个"""
    notebooks = get_notebooks()
    if not notebooks:
        return None
    if keywords:
        for nb_id, nb_name in notebooks.items():
            if any(k in nb_name for k in keywords):
                return nb_id
    return list(notebooks.keys())[0]


def query_sql(stmt: str) -> list[dict]:
    """执行思源 SQL 查询"""
    try:
        result = siyuan_post("/api/query/sql", {"stmt": stmt})
        return result.get("data", [])
    except Exception as e:
        logger.error(f"❌ 思源SQL查询失败: {e}")
        return []
