#!/usr/bin/env python3
"""
Google Patents搜索实现
"""

import requests
import json
import argparse
from urllib.parse import quote
from typing import List, Dict, Optional


class GooglePatentsSearch:
    """Google Patents搜索类"""

    def __init__(self):
        self.base_url = "https://patents.google.com/xhr/query"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://patents.google.com/",
            "Origin": "https://patents.google.com",
        }

    def search(self, keyword: str, limit: int = 10, page: int = 0) -> List[Dict]:
        """搜索专利"""
        print(f"搜索: {keyword} (限制: {limit}, 页码: {page})")

        params = {"url": f"q={quote(keyword)}&num={limit}&page={page}", "exp": ""}

        try:
            response = requests.get(
                self.base_url, params=params, headers=self.headers, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return self._parse_results(data)
            else:
                print(f"API请求失败，状态码: {response.status_code}")
                return []

        except Exception as e:
            print(f"搜索异常: {e}")
            return []

    def _parse_results(self, data: Dict) -> List[Dict]:
        """解析API响应"""
        results = []

        if "results" in data and "cluster" in data["results"]:
            total_results = data["results"].get("total_num_results", 0)
            print(f"找到 {total_results} 个总结果")

            for cluster in data["results"]["cluster"]:
                for patent_data in cluster.get("result", []):
                    patent = self._parse_patent(patent_data)
                    if patent:
                        results.append(patent)

        return results

    def _parse_patent(self, patent_data: Dict) -> Optional[Dict]:
        """解析单个专利数据"""
        try:
            patent_info = patent_data.get("patent", {})

            # 从ID或publication_number获取专利号
            patent_id = (
                patent_data.get("id", "").split("/")[1]
                if "/" in patent_data.get("id", "")
                else ""
            )
            if not patent_id and "publication_number" in patent_info:
                patent_id = patent_info["publication_number"]

            # 处理发明人字段（可能是字符串或列表）
            inventors = []
            inventor_field = patent_info.get("inventor", "")
            if isinstance(inventor_field, list):
                for inv in inventor_field:
                    if isinstance(inv, dict):
                        inventors.append(inv.get("name", ""))
                    else:
                        inventors.append(str(inv))
            elif inventor_field:
                inventors.append(str(inventor_field))

            # 处理权利人字段（可能是字符串或列表）
            assignees = []
            assignee_field = patent_info.get("assignee", "")
            if isinstance(assignee_field, list):
                for ass in assignee_field:
                    if isinstance(ass, dict):
                        assignees.append(ass.get("name", ""))
                    else:
                        assignees.append(str(ass))
            elif assignee_field:
                assignees.append(str(assignee_field))

            # 提取摘要（从snippet字段）
            abstract = patent_info.get("snippet", "")

            # 清理HTML标签
            title = patent_info.get("title", "")
            title = (
                title.replace("&hellip;", "...").replace("<b>", "").replace("</b>", "")
            )

            patent = {
                "patent_id": patent_id,
                "title": title,
                "inventors": inventors,
                "assignees": assignees,
                "filing_date": patent_info.get("filing_date", ""),
                "publication_date": patent_info.get("publication_date", ""),
                "priority_date": patent_info.get("priority_date", ""),
                "grant_date": patent_info.get("grant_date", ""),
                "abstract": abstract,
                "ipc_classes": [],  # 这个API版本没有IPC分类
                "url": f"https://patents.google.com/patent/{patent_id}"
                if patent_id
                else "",
                "database": "Google Patents",
            }

            return patent

        except Exception as e:
            print(f"解析专利数据异常: {e}")
            import traceback

            traceback.print_exc()
            return None

    def search_by_patent_number(self, patent_number: str) -> Optional[Dict]:
        """按专利号搜索"""
        print(f"搜索专利号: {patent_number}")

        params = {"url": f"q={quote(patent_number)}&num=1", "exp": ""}

        try:
            response = requests.get(
                self.base_url, params=params, headers=self.headers, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                results = self._parse_results(data)
                return results[0] if results else None
            else:
                print(f"API请求失败，状态码: {response.status_code}")
                return None

        except Exception as e:
            print(f"搜索异常: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description="Google Patents搜索工具")
    parser.add_argument("--keyword", "-k", help="搜索关键词")
    parser.add_argument("--patent", "-p", help="专利号")
    parser.add_argument("--limit", "-l", type=int, default=5, help="结果数量限制")
    parser.add_argument("--page", "-pg", type=int, default=0, help="页码")
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
        # 按专利号搜索
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
                print(f"摘要: {patent['abstract'][:200]}...")
                print(f"URL: {patent['url']}")
        else:
            print("未找到专利")

    else:
        # 按关键词搜索
        results = searcher.search(args.keyword, args.limit, args.page)

        if results:
            if args.export == "json":
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                print(f"\n找到 {len(results)} 个结果:")
                for i, patent in enumerate(results, 1):
                    print(f"\n{i}. {patent['patent_id']}")
                    print(f"   标题: {patent['title'][:80]}...")
                    print(f"   发明人: {', '.join(patent['inventors'])[:50]}")
                    print(f"   权利人: {', '.join(patent['assignees'])[:50]}")
                    print(f"   申请日: {patent['filing_date']}")
                    print(f"   IPC: {', '.join(patent['ipc_classes'])}")
        else:
            print("未找到结果")


if __name__ == "__main__":
    main()
