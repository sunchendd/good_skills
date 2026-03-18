from __future__ import annotations

import os
import unittest
from datetime import date
from unittest.mock import patch

from shared.automation_routes import get_automation_route
from shared.config import Config
from shared.siyuan import (
    SiyuanClient,
    build_automation_path,
    save_named_automation_report,
)


class ConfigTests(unittest.TestCase):
    def test_from_env_uses_safe_defaults(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = Config.from_env()

        self.assertEqual(config.siyuan_host, "http://127.0.0.1:6806")
        self.assertEqual(config.siyuan_automation_notebook, "AI自动化")
        self.assertEqual(config.bark_token, "")
        self.assertEqual(config.email_sender, "")
        self.assertEqual(config.email_recipients, [])

    def test_from_env_parses_recipients(self) -> None:
        with patch.dict(
            os.environ,
            {
                "EMAIL_RECIPIENTS": "a@example.com, b@example.com ,,c@example.com ",
                "EMAIL_SENDER": "sender@example.com",
            },
            clear=True,
        ):
            config = Config.from_env()

        self.assertEqual(config.email_sender, "sender@example.com")
        self.assertEqual(
            config.email_recipients,
            ["a@example.com", "b@example.com", "c@example.com"],
        )


class SiyuanPathTests(unittest.TestCase):
    def test_get_automation_route_returns_expected_chinese_structure(self) -> None:
        route = get_automation_route("wuyu_daily")

        self.assertEqual(route.feature_name, "内容创作")
        self.assertEqual(route.report_name, "无语哥日报")

    def test_build_automation_path_uses_chinese_structure(self) -> None:
        path = build_automation_path(
            "效率复盘",
            "每日汇总",
            day=date(2026, 3, 18),
        )
        self.assertEqual(path, "/效率复盘/每日汇总/2026-03-18")

    def test_create_automation_doc_uses_built_path(self) -> None:
        client = SiyuanClient(host="http://127.0.0.1:6806", token="token")
        with patch.object(client, "ensure_notebook", return_value="nb-1") as ensure:
            with patch.object(client, "create_doc", return_value="doc-1") as create_doc:
                result = client.create_automation_doc(
                    feature_name="内容创作",
                    report_name="无语哥日报",
                    doc_name="2026-03-18",
                    markdown="# 内容",
                )

        ensure.assert_called_once()
        create_doc.assert_called_once_with(
            "nb-1",
            "/内容创作/无语哥日报/2026-03-18",
            "# 内容",
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["doc_id"], "doc-1")

    def test_save_named_automation_report_uses_route_mapping(self) -> None:
        with patch("shared.siyuan.SiyuanClient") as client_cls:
            client = client_cls.return_value
            client.create_automation_doc.return_value = {
                "ok": True,
                "path": "/内容创作/无语哥日报/2026-03-18",
                "doc_id": "doc-2",
            }

            result = save_named_automation_report(
                route_key="wuyu_daily",
                markdown="# 内容",
                day=date(2026, 3, 18),
                title="无语哥日报 2026-03-18",
            )

        client.create_automation_doc.assert_called_once_with(
            feature_name="内容创作",
            report_name="无语哥日报",
            markdown="# 内容",
            doc_name=None,
            day=date(2026, 3, 18),
            title="无语哥日报 2026-03-18",
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["doc_id"], "doc-2")


if __name__ == "__main__":
    unittest.main()
