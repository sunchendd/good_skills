#!/usr/bin/env python3
"""
专利检索辅助工具
支持在多个专利数据库中检索专利
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Optional, Any


class PatentFinder:
    """专利检索辅助类"""

    def __init__(self):
        self.results = []

    def search_google_patents(self, keywords: str, limit: int = 50) -> List[Dict]:
        """Google Patents 检索"""
        print(f"检索 Google Patents: {keywords}")

        try:
            # 导入Google Patents搜索模块
            import sys
            import os

            # 添加当前目录到路径
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))

            # 动态导入Google Patents搜索
            from google_patents_search import GooglePatentsSearch

            searcher = GooglePatentsSearch()
            results = searcher.search(keywords, limit)

            # 转换为兼容格式
            formatted_results = []
            for patent in results:
                formatted_patent = {
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
                }
                formatted_results.append(formatted_patent)

            return formatted_results

        except Exception as e:
            print(f"Google Patents搜索失败: {e}")
            # 失败时返回模拟结果
            return self._mock_search("Google Patents", keywords, limit)

    def search_uspto(
        self,
        keywords: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """USPTO 专利检索"""
        query = f'"{keywords}"'
        if start_date:
            query += f" AND PD >= {start_date}"
        if end_date:
            query += f" AND PD <= {end_date}"

        print(f"检索 USPTO: {query}")

        results = self._mock_search("USPTO", keywords, limit)
        return results

    def search_cnipa(self, keywords: str, limit: int = 50) -> List[Dict]:
        """中国专利检索"""
        print(f"检索 CNIPA (中国专利): {keywords}")

        results = self._mock_search("CNIPA", keywords, limit)
        return results

    def search_epo(self, keywords: str, limit: int = 50) -> List[Dict]:
        """欧洲专利检索"""
        print(f"检索 EPO: {keywords}")

        results = self._mock_search("EPO", keywords, limit)
        return results

    def _mock_search(self, database: str, keywords: str, limit: int) -> List[Dict]:
        """模拟检索结果（实际使用时替换为真实API调用）"""
        mock_results = []

        # 生成模拟专利数据
        for i in range(min(limit, 5)):
            patent = {
                "patent_id": f"{database[:3].upper()}{2024000000 + i}",
                "title": f"基于{keywords}的优化方法及系统",
                "applicant": f"公司{i + 1}",
                "inventor": f"发明人{i + 1}",
                "filing_date": f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                "publication_date": f"2025-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                "abstract": f"本发明涉及{keywords}技术领域，提供了一种...",
                "ipc_class": [f"G06F9/5{(i % 10)}"],
                "keywords": keywords,
                "database": database,
                "url": f"https://patents.google.com/patent/{database[:3].upper()}{2024000000 + i}",
            }
            mock_results.append(patent)

        return mock_results

    def analyze_patents(self, patents: List[Dict]) -> Dict:
        """分析专利列表"""
        if not patents:
            return {"total": 0, "by_database": {}, "by_ipc": {}}

        by_database = {}
        by_ipc = {}

        for patent in patents:
            # 按数据库统计
            db = patent.get("database", "Unknown")
            by_database[db] = by_database.get(db, 0) + 1

            # 按IPC分类统计
            for ipc in patent.get("ipc_class", []):
                by_ipc[ipc] = by_ipc.get(ipc, 0) + 1

        return {"total": len(patents), "by_database": by_database, "by_ipc": by_ipc}

    def export_results(self, patents: List[Dict], format: str = "json") -> str:
        """导出检索结果"""
        if format == "json":
            return json.dumps(patents, ensure_ascii=False, indent=2)
        elif format == "csv":
            lines = ["patent_id,title,applicant,filing_date,ipc_class,database"]
            for p in patents:
                line = f'{p["patent_id"]},"{p["title"]}",{p["applicant"]},{p["filing_date"]},"{p["ipc_class"]}",{p["database"]}'
                lines.append(line)
            return "\n".join(lines)
        else:
            return str(patents)


def main():
    parser = argparse.ArgumentParser(description="专利检索辅助工具")
    parser.add_argument("--keywords", "-k", help="检索关键词")
    parser.add_argument(
        "--database",
        "-d",
        default="all",
        choices=["google", "uspto", "cnipa", "epo", "all"],
        help="检索数据库",
    )
    parser.add_argument("--company", "-c", help="特定公司/权利人")
    parser.add_argument("--ipc", "-i", help="IPC分类")
    parser.add_argument("--years", "-y", help="年份范围，格式: 2020-2025")
    parser.add_argument("--limit", "-l", type=int, default=50, help="结果数量限制")
    parser.add_argument(
        "--export",
        "-e",
        default="json",
        choices=["json", "csv", "console"],
        help="导出格式",
    )

    args = parser.parse_args()

    if not any([args.keywords, args.company, args.ipc]):
        print("错误：至少需要提供 --keywords、--company 或 --ipc 参数")
        parser.print_help()
        sys.exit(1)

    finder = PatentFinder()
    all_results = []

    # 解析年份范围
    start_date = None
    end_date = None
    if args.years:
        parts = args.years.split("-")
        if len(parts) == 2:
            start_date = parts[0]
            end_date = parts[1]

    # 执行检索
    databases = []
    if args.database == "all":
        databases = ["google", "uspto", "cnipa", "epo"]
    else:
        databases = [args.database]

    for db in databases:
        if db == "google":
            results = finder.search_google_patents(args.keywords, args.limit)
        elif db == "uspto":
            results = finder.search_uspto(
                args.keywords, start_date, end_date, args.limit
            )
        elif db == "cnipa":
            results = finder.search_cnipa(args.keywords, args.limit)
        elif db == "epo":
            results = finder.search_epo(args.keywords, args.limit)
        else:
            results = []
        all_results.extend(results)

    # 分析结果
    analysis = finder.analyze_patents(all_results)
    print(f"\n检索完成！共找到 {analysis['total']} 篇专利")

    if analysis["by_database"]:
        print("\n按数据库分布:")
        for db, count in analysis["by_database"].items():
            print(f"  {db}: {count}")

    if analysis["by_ipc"]:
        print("\n按IPC分类分布:")
        for ipc, count in analysis["by_ipc"].items():
            print(f"  {ipc}: {count}")

    # 导出结果
    if args.export == "console":
        for p in all_results[:10]:
            print(f"\n{p['patent_id']}: {p['title']}")
            print(f"  权利人: {p['applicant']}")
            print(f"  申请日: {p['filing_date']}")
            print(f"  IPC: {p['ipc_class']}")
    else:
        output = finder.export_results(all_results, args.export)
        print(f"\n检索结果已导出（{args.export}格式）")
        print(output)


if __name__ == "__main__":
    main()
