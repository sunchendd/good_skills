#!/usr/bin/env python3
"""
专利检索工具 - 统一 Serper.dev API 接口
支持命令行和 Python API 两种使用方式
"""

import argparse
import json
import sys
from typing import List, Dict, Optional

from google_patents_search import GooglePatentsSearch


class PatentFinder:
    """专利检索类"""

    def __init__(self, api_key: Optional[str] = None):
        if api_key:
            self.searcher = GooglePatentsSearch(api_key=api_key)
        else:
            self.searcher = GooglePatentsSearch()
        self.results: List[Dict] = []

    def search(
        self,
        keywords: str,
        limit: int = 20,
        page: int = 1,
    ) -> List[Dict]:
        """执行专利检索，自动处理多页"""
        results = self.searcher.search(keywords, limit=limit, page=page)

        formatted = []
        for patent in results:
            formatted.append({
                "patent_id": patent.get("patent_id", ""),
                "title": patent.get("title", ""),
                "applicant": ", ".join(patent.get("assignees", [])),
                "inventor": ", ".join(patent.get("inventors", [])),
                "filing_date": patent.get("filing_date", ""),
                "publication_date": patent.get("publication_date", ""),
                "abstract": patent.get("abstract", ""),
                "ipc_class": patent.get("ipc_classes", []),
                "keywords": keywords,
                "database": "Google Patents",
                "url": patent.get("url", ""),
            })

        self.results = formatted
        return formatted

    def search_by_patent_number(self, patent_number: str) -> Optional[Dict]:
        """按专利号检索"""
        result = self.searcher.search_by_patent_number(patent_number)
        if result:
            return {
                "patent_id": result.get("patent_id", ""),
                "title": result.get("title", ""),
                "applicant": ", ".join(result.get("assignees", [])),
                "inventor": ", ".join(result.get("inventors", [])),
                "filing_date": result.get("filing_date", ""),
                "publication_date": result.get("publication_date", ""),
                "abstract": result.get("abstract", ""),
                "ipc_class": result.get("ipc_classes", []),
                "database": "Google Patents",
                "url": result.get("url", ""),
            }
        return None

    def analyze_patents(self, patents: List[Dict]) -> Dict:
        """分析专利列表"""
        if not patents:
            return {"total": 0, "by_applicant": {}, "by_year": {}}

        by_applicant = {}
        by_year = {}

        for patent in patents:
            applicant = patent.get("applicant", "Unknown")
            by_applicant[applicant] = by_applicant.get(applicant, 0) + 1

            year = patent.get("filing_date", "")[:4]
            if year:
                by_year[year] = by_year.get(year, 0) + 1

        return {
            "total": len(patents),
            "by_applicant": dict(sorted(by_applicant.items(), key=lambda x: -x[1])),
            "by_year": dict(sorted(by_year.items())),
        }

    def export_results(self, patents: List[Dict], format: str = "json") -> str:
        """导出检索结果"""
        if format == "json":
            return json.dumps(patents, ensure_ascii=False, indent=2)
        elif format == "csv":
            lines = ["patent_id,title,applicant,filing_date,database,url"]
            for p in patents:
                title = p["title"].replace('"', '""')
                line = f'{p["patent_id"]},"{title}",{p["applicant"]},{p["filing_date"]},{p["database"]},{p["url"]}'
                lines.append(line)
            return "\n".join(lines)
        else:
            return str(patents)


def main():
    parser = argparse.ArgumentParser(description="专利检索工具 (Serper.dev API)")
    parser.add_argument("--keywords", "-k", help="检索关键词")
    parser.add_argument("--patent", "-p", help="按专利号检索")
    parser.add_argument("--limit", "-l", type=int, default=20, help="结果数量限制")
    parser.add_argument("--page", "-pg", type=int, default=1, help="起始页码")
    parser.add_argument(
        "--export",
        "-e",
        default="console",
        choices=["json", "csv", "console"],
        help="输出格式",
    )

    args = parser.parse_args()

    if not args.keywords and not args.patent:
        print("错误：需要提供 --keywords 或 --patent 参数")
        parser.print_help()
        sys.exit(1)

    finder = PatentFinder()

    if args.patent:
        patent = finder.search_by_patent_number(args.patent)
        if patent:
            if args.export == "json":
                print(json.dumps(patent, ensure_ascii=False, indent=2))
            else:
                print(f"\n专利号: {patent['patent_id']}")
                print(f"标题: {patent['title']}")
                print(f"发明人: {patent['inventor']}")
                print(f"权利人: {patent['applicant']}")
                print(f"申请日: {patent['filing_date']}")
                print(f"公开日: {patent['publication_date']}")
                print(f"摘要: {patent['abstract'][:200]}")
                print(f"链接: {patent['url']}")
        else:
            print("未找到专利")
    else:
        results = finder.search(args.keywords, limit=args.limit, page=args.page)
        analysis = finder.analyze_patents(results)

        if args.export == "json":
            print(finder.export_results(results, "json"))
        elif args.export == "csv":
            print(finder.export_results(results, "csv"))
        else:
            print(f"\n检索完成！共找到 {analysis['total']} 篇专利（本页）")

            if analysis["by_applicant"]:
                print("\n按权利人分布:")
                for applicant, count in analysis["by_applicant"].items():
                    print(f"  {applicant}: {count}")

            if analysis["by_year"]:
                print("\n按年份分布:")
                for year, count in analysis["by_year"].items():
                    print(f"  {year}: {count}")

            print(f"\n--- 前10篇专利 ---")
            for i, p in enumerate(results[:10], 1):
                print(f"\n{i}. {p['patent_id']}")
                print(f"   标题: {p['title'][:80]}")
                print(f"   权利人: {p['applicant']}")
                print(f"   发明人: {p['inventor']}")
                print(f"   申请日: {p['filing_date']}")
                print(f"   链接: {p['url']}")


if __name__ == "__main__":
    main()
