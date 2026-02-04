#!/usr/bin/env python3
"""
调试专利数据格式
"""

import requests
import json
from urllib.parse import quote


def debug_patent_data():
    """调试专利数据结构"""
    keyword = "artificial intelligence"

    base_url = "https://patents.google.com/xhr/query"
    params = {"url": f"q={quote(keyword)}&num=2", "exp": ""}

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

            # 保存原始数据用于分析
            with open("debug_patent_raw.json", "w") as f:
                json.dump(data, f, indent=2)
            print("原始数据已保存到 debug_patent_raw.json")

            # 分析数据结构
            print("\n数据结构分析:")
            print("=" * 50)

            if "results" in data and "cluster" in data["results"]:
                clusters = data["results"]["cluster"]
                print(f"找到 {len(clusters)} 个cluster")

                for i, cluster in enumerate(clusters):
                    print(f"\nCluster {i}:")
                    if "result" in cluster:
                        results = cluster["result"]
                        print(f"  包含 {len(results)} 个result")

                        for j, result in enumerate(results):
                            print(f"\n  Result {j}:")
                            print(f"    ID: {result.get('id', 'N/A')}")
                            print(f"    Rank: {result.get('rank', 'N/A')}")

                            if "patent" in result:
                                patent = result["patent"]
                                print(f"    Patent 类型: {type(patent)}")

                                if isinstance(patent, dict):
                                    print(f"    Patent 键: {list(patent.keys())}")
                                    print(
                                        f"    Title: {patent.get('title', 'N/A')[:50]}..."
                                    )
                                else:
                                    print(f"    Patent 值: {patent}")
                            else:
                                print("    没有patent字段")

            # 检查第一个result的详细结构
            print("\n\n第一个result的详细结构:")
            print("=" * 50)

            if clusters and "result" in clusters[0]:
                first_result = clusters[0]["result"][0]
                print(json.dumps(first_result, indent=2)[:1000])

    except Exception as e:
        print(f"调试异常: {e}")


if __name__ == "__main__":
    debug_patent_data()
