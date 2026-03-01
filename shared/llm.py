"""DeepSeek LLM 封装"""
from __future__ import annotations
from openai import OpenAI
from .config import cfg


def get_client() -> OpenAI:
    return OpenAI(api_key=cfg.deepseek_api_key, base_url="https://api.deepseek.com")


def chat(
    prompt: str,
    system: str | None = None,
    model: str = "deepseek-chat",
    json_mode: bool = False,
    timeout: int = 90,
    max_tokens: int | None = None,
) -> str:
    """单次对话，返回文本内容"""
    client = get_client()
    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    kwargs: dict = {"model": model, "messages": messages, "timeout": timeout}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    if max_tokens:
        kwargs["max_tokens"] = max_tokens
    return client.chat.completions.create(**kwargs).choices[0].message.content
