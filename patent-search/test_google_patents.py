#!/usr/bin/env python3
"""
测试Google Patents API
"""

import requests
import json
from urllib.parse import quote


def search_google_patents(keyword, limit=5):
    """使用Google Patents公共API搜索专利"""
    print(f"搜索Google Patents: {keyword}")

    # Google Patents搜索URL
    base_url = "https://patents.google.com/xhr/query"

    # 构建查询参数
    params = {"url": f"q={quote(keyword)}&num={limit}", "exp": ""}

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://patents.google.com/",
        "Origin": "https://patents.google.com",
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()

            # 解析结果
            results = []
            if "results" in data and "cluster" in data["results"]:
                for cluster in data["results"]["cluster"]:
                    for patent in cluster.get("result", []):
                        patent_info = {
                            "patent_id": patent.get("patent", {}).get(
                                "publicationNumber", ""
                            ),
                            "title": patent.get("patent", {}).get("title", ""),
                            "inventor": ", ".join(
                                [
                                    inv.get("name", "")
                                    for inv in patent.get("patent", {}).get(
                                        "inventor", []
                                    )
                                ]
                            ),
                            "assignee": ", ".join(
                                [
                                    ass.get("name", "")
                                    for ass in patent.get("patent", {}).get(
                                        "assignee", []
                                    )
                                ]
                            ),
                            "filing_date": patent.get("patent", {}).get(
                                "filingDate", ""
                            ),
                            "publication_date": patent.get("patent", {}).get(
                                "publicationDate", ""
                            ),
                            "abstract": patent.get("patent", {})
                            .get("abstract", [{}])[0]
                            .get("text", "")
                            if patent.get("patent", {}).get("abstract")
                            else "",
                            "url": f"https://patents.google.com/patent/{patent.get('patent', {}).get('publicationNumber', '')}",
                        }
                        results.append(patent_info)

            return results
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"响应: {response.text[:200]}")
            return []

    except Exception as e:
        print(f"搜索异常: {e}")
        return []


def test_patent_search():
    """测试专利搜索"""
    print("Google Patents搜索测试")
    print("=" * 50)

    # 测试搜索
    keywords = ["artificial intelligence", "machine learning", "neural network"]

    for keyword in keywords:
        print(f"\n搜索关键词: {keyword}")
        results = search_google_patents(keyword, limit=3)

        if results:
            print(f"找到 {len(results)} 个结果:")
            for i, patent in enumerate(results, 1):
                print(f"\n{i}. {patent['patent_id']}")
                print(f"   标题: {patent['title'][:80]}...")
                print(f"   发明人: {patent['inventor'][:50]}")
                print(f"   申请日: {patent['filing_date']}")
                print(f"   摘要: {patent['abstract'][:100]}...")
        else:
            print("未找到结果")

        print("-" * 50)


if __name__ == "__main__":
    test_patent_search()
