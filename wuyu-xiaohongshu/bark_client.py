from __future__ import annotations

from typing import Optional, Dict, Any

import os
import urllib.parse

import httpx


__all__ = ["bark_notify", "abark_notify", "build_bark_url", "send_bark_url", "asend_bark_url"]
# 默认 Bark Token（当未传入且环境变量缺省时使用）
DEFAULT_BARK_TOKEN = "seYne8cq4c7MkzqWqF2JPJ"


def build_bark_url(
    *,
    token: Optional[str] = None,
    title: Optional[str] = None,
    body: str,
    sound: Optional[str] = None,
    call: Optional[int] = None,
    isArchive: Optional[int] = None,
    icon: Optional[str] = None,
    group: Optional[str] = None,
    ciphertext: Optional[str] = None,
    level: Optional[str] = None,     # active|timeSensitive|passive|critical
    volume: Optional[int] = None,    # 0-10 (critical 时可用)
    url: Optional[str] = None,
    image: Optional[str] = None,
    copy: Optional[str] = None,
    badge: Optional[int] = None,
    autoCopy: Optional[int] = None,
) -> str:
    """
    组装 Bark API URL。除 token、body 外其余参数均可选。
    优先使用入参 token，缺省则读取环境变量 BARK_TOKEN。
    """
    tk = token or os.getenv("BARK_TOKEN") or DEFAULT_BARK_TOKEN
    # 仍保留兜底校验（理论上不会触发）
    if not tk:
        raise ValueError("缺少 token：请传入 token 或设置环境变量 BARK_TOKEN")

    # Bark 支持 /{token}/{body} 或 /{token}/{title}/{body}
    title_seg = urllib.parse.quote(title, safe="") if title else ""
    body_seg = urllib.parse.quote(body, safe="")
    path = f"{tk}/{title_seg}/{body_seg}" if title_seg else f"{tk}/{body_seg}"

    params: Dict[str, Any] = {}
    if sound is not None:
        params["sound"] = sound
    if call is not None:
        params["call"] = call
    if isArchive is not None:
        params["isArchive"] = isArchive
    if icon is not None:
        params["icon"] = icon
    if group is not None:
        params["group"] = group
    if ciphertext is not None:
        params["ciphertext"] = ciphertext
    if level is not None:
        # 不强制校验枚举，直接透传，便于服务端兼容
        params["level"] = level
    if volume is not None:
        params["volume"] = volume
    if url is not None:
        params["url"] = url
    if image is not None:
        params["image"] = image
    if copy is not None:
        params["copy"] = copy
    if badge is not None:
        params["badge"] = badge
    if autoCopy is not None:
        params["autoCopy"] = autoCopy

    query = urllib.parse.urlencode(params, safe="/:")
    return f"https://api.day.app/{path}" + (f"?{query}" if query else "")


def bark_notify(
    *,
    token: Optional[str] = None,
    title: Optional[str] = None,
    body: str,
    sound: Optional[str] = None,
    call: Optional[int] = None,
    isArchive: Optional[int] = None,
    icon: Optional[str] = None,
    group: Optional[str] = None,
    ciphertext: Optional[str] = None,
    level: Optional[str] = None,
    volume: Optional[int] = None,
    url: Optional[str] = None,
    image: Optional[str] = None,
    copy: Optional[str] = None,
    badge: Optional[int] = None,
    autoCopy: Optional[int] = None,
    timeout: float = 10.0,
) -> Dict[str, Any]:
    """
    同步发送 Bark 通知。
    返回服务端 JSON 或 {status_code, text} 结构。
    """
    full_url = build_bark_url(
        token=token,
        title=title,
        body=body,
        sound=sound,
        call=call,
        isArchive=isArchive,
        icon=icon,
        group=group,
        ciphertext=ciphertext,
        level=level,
        volume=volume,
        url=url,
        image=image,
        copy=copy,
        badge=badge,
        autoCopy=autoCopy,
    )

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(full_url)
    except httpx.RequestError as e:
        return {"ok": False, "url": full_url, "response": {"error": str(e)}, "status_code": 0}

    try:
        data = resp.json()
    except ValueError:
        data = {"status_code": resp.status_code, "text": resp.text}

    # 不抛异常，交由调用方根据 code/status_code 自行处理
    return {"ok": resp.status_code < 400, "url": full_url, "response": data, "status_code": resp.status_code}


async def abark_notify(
    *,
    token: Optional[str] = None,
    title: Optional[str] = None,
    body: str,
    sound: Optional[str] = None,
    call: Optional[int] = None,
    isArchive: Optional[int] = None,
    icon: Optional[str] = None,
    group: Optional[str] = None,
    ciphertext: Optional[str] = None,
    level: Optional[str] = None,
    volume: Optional[int] = None,
    url: Optional[str] = None,
    image: Optional[str] = None,
    copy: Optional[str] = None,
    badge: Optional[int] = None,
    autoCopy: Optional[int] = None,
    timeout: float = 10.0,
) -> Dict[str, Any]:
    """
    异步发送 Bark 通知。
    返回服务端 JSON 或 {status_code, text} 结构。
    """
    full_url = build_bark_url(
        token=token,
        title=title,
        body=body,
        sound=sound,
        call=call,
        isArchive=isArchive,
        icon=icon,
        group=group,
        ciphertext=ciphertext,
        level=level,
        volume=volume,
        url=url,
        image=image,
        copy=copy,
        badge=badge,
        autoCopy=autoCopy,
    )

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(full_url)
    except httpx.RequestError as e:
        return {"ok": False, "url": full_url, "response": {"error": str(e)}, "status_code": 0}

    try:
        data = resp.json()
    except ValueError:
        data = {"status_code": resp.status_code, "text": resp.text}

    return {"ok": resp.status_code < 400, "url": full_url, "response": data, "status_code": resp.status_code}


def send_bark_url(url: str, timeout: float = 10.0) -> Dict[str, Any]:
    """
    直接使用完整 Bark URL 发送（同步）。
    """
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(url)
    except httpx.RequestError as e:
        return {"ok": False, "url": url, "response": {"error": str(e)}, "status_code": 0}

    try:
        data = resp.json()
    except ValueError:
        data = {"status_code": resp.status_code, "text": resp.text}

    return {"ok": resp.status_code < 400, "url": url, "response": data, "status_code": resp.status_code}


async def asend_bark_url(url: str, timeout: float = 10.0) -> Dict[str, Any]:
    """
    直接使用完整 Bark URL 发送（异步）。
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
    except httpx.RequestError as e:
        return {"ok": False, "url": url, "response": {"error": str(e)}, "status_code": 0}

    try:
        data = resp.json()
    except ValueError:
        data = {"status_code": resp.status_code, "text": resp.text}

    return {"ok": resp.status_code < 400, "url": url, "response": data, "status_code": resp.status_code}


# 简单示例：
# 1) 同步：
# from bark_client import bark_notify
# r = bark_notify(token="seYne8cq4c7MkzqWqF2JPJ", title="推送标题", body="这里改成你自己的推送内容")
# print(r)
#
# 2) 异步：
# import asyncio
# from bark_client import abark_notify
# asyncio.run(abark_notify(token="seYne8cq4c7MkzqWqF2JPJ", body="异步消息"))