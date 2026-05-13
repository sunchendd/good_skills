#!/usr/bin/env python3
"""
Google Patents搜索 - 通过 Serper.dev API
"""

import json
import os
import sys
import argparse
import subprocess
from typing import List, Dict, Optional
from urllib.parse import quote

API_KEY = os.environ.get("SERPER_API_KEY", "")
API_URL = "https://google.serper.dev/patents"


def _api_get(keyword: str, page: int = 1, api_key: str = API_KEY) -> Optional[Dict]:
    """通过 curl 调用 Serper.dev API（绕过 Python TLS 指纹检测）"""
    url = f"{API_URL}?q={quote(keyword)}&page={page}&apiKey={api_key}"
    try:
        result = subprocess.run(
            ["curl", "-s", "--connect-timeout", "15", "--max-time", "20", url],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        else:
            print(f"API错误: {result.stderr[:200]}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"请求异常: {e}", file=sys.stderr)
        return None


class GooglePatentsSearch:
    """Google Patents搜索类 (Serper.dev API)"""

    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key

    def search(self, keyword: str, limit: int = 10, page: int = 1) -> List[Dict]:
        """搜索专利"""
        results = []
        num_pages = 1
        if limit > 10:
            num_pages = (limit + 9) // 10

        for p in range(num_pages):
            data = _api_get(keyword, page + p, self.api_key)
            if data is None:
                break
            page_results = self._parse_results(data)
            results.extend(page_results)
            if not page_results:
                break

        return results[:limit]

    def _parse_results(self, data: Dict) -> List[Dict]:
        """解析 Serper.dev API 响应"""
        results = []
        organic = data.get("organic", [])
        for patent_data in organic:
            patent = self._parse_patent(patent_data)
            if patent:
                results.append(patent)
        return results

    def _parse_patent(self, patent_data: Dict) -> Optional[Dict]:
        """解析单个专利数据"""
        try:
            patent_id = patent_data.get("publicationNumber", "")
            inventor = patent_data.get("inventor", "")
            assignee = patent_data.get("assignee", "")

            patent = {
                "patent_id": patent_id,
                "title": patent_data.get("title", ""),
                "inventors": [i.strip() for i in inventor.split(",") if i.strip()] if inventor else [],
                "assignees": [a.strip() for a in assignee.split(",") if a.strip()] if assignee else [],
                "filing_date": patent_data.get("filingDate", ""),
                "publication_date": patent_data.get("publicationDate", ""),
                "priority_date": patent_data.get("priorityDate", ""),
                "grant_date": patent_data.get("grantDate", ""),
                "abstract": patent_data.get("snippet", ""),
                "ipc_classes": [],
                "url": patent_data.get("link", f"https://patents.google.com/patent/{patent_id}" if patent_id else ""),
                "database": "Google Patents",
                "language": patent_data.get("language", ""),
                "pdf_url": patent_data.get("pdfUrl", ""),
                "thumbnail_url": patent_data.get("thumbnailUrl", ""),
            }
            return patent
        except Exception as e:
            print(f"解析专利数据异常: {e}", file=sys.stderr)
            return None

    def search_by_patent_number(self, patent_number: str) -> Optional[Dict]:
        """按专利号搜索"""
        data = _api_get(patent_number, page=1, api_key=self.api_key)
        if data:
            results = self._parse_results(data)
            return results[0] if results else None
        return None


def main():
    parser = argparse.ArgumentParser(description="Google Patents搜索工具 (Serper.dev API)")
    parser.add_argument("--keyword", "-k", help="搜索关键词")
    parser.add_argument("--patent", "-p", help="专利号")
    parser.add_argument("--limit", "-l", type=int, default=10, help="结果数量限制")
    parser.add_argument("--page", "-pg", type=int, default=1, help="起始页码")
    parser.add_argument(
        "--export",
        "-e",
        default="console",
        choices=["console", "json"],
        help="输出格式",
    )

    args = parser.parse_args()

    if not args.keyword and not args.patent:
        print("错误：需要提供 --keyword 或 --patent 参数")
        parser.print_help()
        return

    searcher = GooglePatentsSearch()

    if args.patent:
        patent = searcher.search_by_patent_number(args.patent)
        if patent:
            if args.export == "json":
                print(json.dumps(patent, indent=2, ensure_ascii=False))
            else:
                print(f"\n专利号: {patent['patent_id']}")
                print(f"标题: {patent['title']}")
                print(f"发明人: {', '.join(patent['inventors'])}")
                print(f"权利人: {', '.join(patent['assignees'])}")
                print(f"申请日: {patent['filing_date']}")
                print(f"公开日: {patent['publication_date']}")
                print(f"IPC分类: {', '.join(patent['ipc_classes'])}")
                print(f"摘要: {patent['abstract'][:200]}")
                print(f"URL: {patent['url']}")
        else:
            print("未找到专利")
    else:
        results = searcher.search(args.keyword, args.limit, args.page)
        if results:
            if args.export == "json":
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                print(f"\n找到 {len(results)} 个结果:")
                for i, patent in enumerate(results, 1):
                    print(f"\n{i}. {patent['patent_id']}")
                    print(f"   标题: {patent['title'][:80]}")
                    print(f"   发明人: {', '.join(patent['inventors'])[:50]}")
                    print(f"   权利人: {', '.join(patent['assignees'])[:50]}")
                    print(f"   申请日: {patent['filing_date']}")
        else:
            print("未找到结果")


if __name__ == "__main__":
    main()
