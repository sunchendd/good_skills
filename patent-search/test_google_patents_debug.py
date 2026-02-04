#!/usr/bin/env python3
"""
调试Google Patents API
"""

import requests
import json
from urllib.parse import quote


def debug_google_patents(keyword):
    """调试Google Patents API响应"""
    print(f"调试搜索: {keyword}")

    # Google Patents搜索URL
    base_url = "https://patents.google.com/xhr/query"

    # 构建查询参数
    params = {"url": f"q={quote(keyword)}&num=5", "exp": ""}

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://patents.google.com/",
        "Origin": "https://patents.google.com",
    }

    try:
        print(f"请求URL: {base_url}")
        print(f"参数: {params}")

        response = requests.get(base_url, params=params, headers=headers, timeout=30)

        print(f"状态码: {response.status_code}")
        print(f"响应类型: {response.headers.get('content-type')}")

        # 尝试解析JSON
        try:
            data = response.json()
            print("\nJSON响应结构:")
            print(json.dumps(data, indent=2)[:500] + "...")

            # 检查响应结构
            if isinstance(data, dict):
                print("\n响应键:")
                for key in data.keys():
                    print(f"  - {key}")

                if "results" in data:
                    print("\nresults结构:")
                    print(json.dumps(data["results"], indent=2)[:300] + "...")

        except json.JSONDecodeError:
            print("\n响应不是有效的JSON:")
            print(response.text[:500])

    except Exception as e:
        print(f"请求异常: {e}")


if __name__ == "__main__":
    print("Google Patents API调试")
    print("=" * 50)

    debug_google_patents("artificial intelligence")
