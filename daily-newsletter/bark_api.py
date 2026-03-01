from typing import Optional, Dict, Any

import os
import urllib.parse

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI(title="Bark Notification API", version="1.0.0")


class NotifyRequest(BaseModel):
    # Bark token: prefer body.token, fallback to env BARK_TOKEN
    token: Optional[str] = None

    # Basic content
    body: str = Field(..., description="推送内容（路径段会自动 URL 编码）")
    title: Optional[str] = Field(None, description="推送标题（可选）")

    # Options (all optional)
    sound: Optional[str] = Field(None, description="自定义铃声，如 minuet")
    call: Optional[int] = Field(None, ge=0, le=1, description="持续响铃：1 开启")
    isArchive: Optional[int] = Field(None, ge=0, le=1, description="自动保存通知消息：1 开启")
    icon: Optional[HttpUrl] = Field(None, description="自定义图标（iOS15+）")
    group: Optional[str] = Field(None, description="消息分组名")
    ciphertext: Optional[str] = Field(None, description="推送加密密文")
    level: Optional[str] = Field(
        None,
        pattern=r"^(active|timeSensitive|passive|critical)$",
        description="通知级别：active|timeSensitive|passive|critical",
    )
    volume: Optional[int] = Field(None, ge=0, le=10, description="critical 时的音量 0-10")
    url: Optional[HttpUrl] = Field(None, description="通知点击跳转 URL")
    image: Optional[HttpUrl] = Field(None, description="图片推送 URL")
    copy: Optional[str] = Field(None, description="手动复制内容")
    badge: Optional[int] = Field(None, ge=0, description="角标数")
    autoCopy: Optional[int] = Field(None, ge=0, le=1, description="自动复制到剪贴板：1 开启")


def _build_bark_url(payload: NotifyRequest) -> str:
    token = payload.token or os.getenv("BARK_TOKEN") or "seYne8cq4c7MkzqWqF2JPJ"

    # Path segments with URL encoding
    # Bark 允许 /{token}/{body} 或 /{token}/{title}/{body}
    title_seg = ""
    if payload.title:
        title_seg = urllib.parse.quote(payload.title, safe="")

    body_seg = urllib.parse.quote(payload.body, safe="")

    if title_seg:
        path = f"{token}/{title_seg}/{body_seg}"
    else:
        path = f"{token}/{body_seg}"

    # Query params
    params: Dict[str, Any] = {}

    if payload.sound is not None:
        params["sound"] = payload.sound
    if payload.call is not None:
        params["call"] = payload.call
    if payload.isArchive is not None:
        params["isArchive"] = payload.isArchive
    if payload.icon is not None:
        params["icon"] = str(payload.icon)
    if payload.group is not None:
        params["group"] = payload.group
    if payload.ciphertext is not None:
        params["ciphertext"] = payload.ciphertext
    if payload.level is not None:
        params["level"] = payload.level
    if payload.volume is not None:
        params["volume"] = payload.volume
    if payload.url is not None:
        params["url"] = str(payload.url)
    if payload.image is not None:
        params["image"] = str(payload.image)
    if payload.autoCopy is not None:
        params["autoCopy"] = payload.autoCopy
    if payload.copy is not None:
        params["copy"] = payload.copy
    if payload.badge is not None:
        params["badge"] = payload.badge

    query = urllib.parse.urlencode(params, safe="/:")
    return f"https://api.day.app/{path}" + (f"?{query}" if query else "")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/notify")
async def notify(payload: NotifyRequest):
    url = _build_bark_url(payload)
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url)
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"请求 Bark 失败：{e}") from e

    # Bark 通常返回 JSON：{"code":200,"message":"success","timestamp":...}
    # 也可能返回文本，尝试解析 JSON，否则回落为文本
    data: Any
    try:
        data = resp.json()
    except ValueError:
        data = {"status_code": resp.status_code, "text": resp.text}

    if resp.status_code >= 400:
        raise HTTPException(status_code=resp.status_code, detail=data)

    return {"ok": True, "url": url, "response": data}


# 启动提示：
# 1) 安装依赖：
#    pip install fastapi uvicorn httpx
# 2) 设置环境变量（可选，如果不在请求体提供 token）：
#    export BARK_TOKEN="seYne8cq4c7MkzqWqF2JPJ"
# 3) 启动服务：
#    uvicorn bark_api:app --reload
#
# 示例请求（选择其一）：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{
#     "token": "seYne8cq4c7MkzqWqF2JPJ",
#     "title": "推送标题",
#     "body": "这里改成你自己的推送内容"
#   }'
#
# 铃声：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{"token":"seYne8cq4c7MkzqWqF2JPJ","body":"推送铃声","sound":"minuet"}'
#
# 持续响铃：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{"token":"seYne8cq4c7MkzqWqF2JPJ","body":"持续响铃","call":1}'
#
# 自动保存：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{"token":"seYne8cq4c7MkzqWqF2JPJ","body":"自动保存通知消息","isArchive":1}'
#
# 自定义图标：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{"token":"seYne8cq4c7MkzqWqF2JPJ","title":"自定义推送图标","body":"内容","icon":"https://day.app/assets/images/avatar.jpg"}'
#
# 分组：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{"token":"seYne8cq4c7MkzqWqF2JPJ","title":"推送消息分组","body":"内容","group":"groupName"}'
#
# 加密（ciphertext）：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{"token":"seYne8cq4c7MkzqWqF2JPJ","title":"推送加密","body":"内容","ciphertext":"ciphertext"}'
#
# 重要警告：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{"token":"seYne8cq4c7MkzqWqF2JPJ","title":"重要警告","body":"内容","level":"critical","volume":5}'
#
# 时效性通知：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{"token":"seYne8cq4c7MkzqWqF2JPJ","title":"时效性通知","body":"内容","level":"timeSensitive"}'
#
# URL 跳转：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{"token":"seYne8cq4c7MkzqWqF2JPJ","title":"URL Test","body":"内容","url":"https://www.baidu.com"}'
#
# 图片推送：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{"token":"seYne8cq4c7MkzqWqF2JPJ","title":"图片推送通知","body":"内容","image":"https://day.app/assets/images/avatar.jpg"}'
#
# Copy：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{"token":"seYne8cq4c7MkzqWqF2JPJ","title":"Copy Test","body":"内容","copy":"test"}'
#
# 角标：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{"token":"seYne8cq4c7MkzqWqF2JPJ","title":"设置角标","body":"内容","badge":1}'
#
# 自动复制：
# curl -X POST http://127.0.0.1:8000/notify \
#   -H "Content-Type: application/json" \
#   -d '{"token":"seYne8cq4c7MkzqWqF2JPJ","title":"自动复制推送内容到剪切板","body":"内容","autoCopy":1,"copy":"optionalsaqwf rv c"}'