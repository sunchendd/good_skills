"""Centralized SiYuan automation routes."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AutomationRoute:
    feature_name: str
    report_name: str


AUTOMATION_ROUTES: dict[str, AutomationRoute] = {
    "wuyu_daily": AutomationRoute("Content Creation", "Wuyu Daily Report"),
    "daily_digest": AutomationRoute("Efficiency Review", "Daily Summary"),
    "weekly_report": AutomationRoute("Efficiency Review", "Weekly Report"),
    "knowledge_daily": AutomationRoute(
        "Knowledge Base Maintenance",
        "Knowledge Daily Report",
    ),
    "arxiv_daily": AutomationRoute("Research Feeds", "arXiv Daily"),
    "daily_newsletter": AutomationRoute("Research Feeds", "Daily Newsletter"),
    "vibe_daily": AutomationRoute("Engineering Logs", "Vibe Daily"),
    "fitness_daily": AutomationRoute("Personal Ops", "Fitness Daily"),
    "wardrobe_daily": AutomationRoute("Personal Ops", "Wardrobe Daily"),
}


def get_automation_route(route_key: str) -> AutomationRoute:
    try:
        return AUTOMATION_ROUTES[route_key]
    except KeyError as exc:
        known = ", ".join(sorted(AUTOMATION_ROUTES))
        raise KeyError(
            f"Unknown automation route: {route_key}. Expected one of: {known}"
        ) from exc
