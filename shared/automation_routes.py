"""Centralized SiYuan automation routes."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AutomationRoute:
    feature_name: str
    report_name: str


AUTOMATION_ROUTES: dict[str, AutomationRoute] = {
    "wuyu_daily": AutomationRoute("内容创作", "无语哥日报"),
    "daily_digest": AutomationRoute("效率复盘", "每日汇总"),
    "weekly_report": AutomationRoute("效率复盘", "周报"),
    "knowledge_daily": AutomationRoute("知识库维护", "知识日报"),
}


def get_automation_route(route_key: str) -> AutomationRoute:
    try:
        return AUTOMATION_ROUTES[route_key]
    except KeyError as exc:
        known = ", ".join(sorted(AUTOMATION_ROUTES))
        raise KeyError(f"Unknown automation route: {route_key}. Expected one of: {known}") from exc
