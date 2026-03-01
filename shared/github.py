"""GitHub API 封装"""
from __future__ import annotations
import urllib.request
import json
import logging
from .config import cfg

logger = logging.getLogger(__name__)


def gh_get(path: str) -> dict | list:
    """GitHub API GET 请求"""
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {cfg.github_token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "openclaw",
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())
