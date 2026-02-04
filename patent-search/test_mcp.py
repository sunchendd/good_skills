#!/usr/bin/env python3
"""
测试MCP服务器连接
"""

import requests
import json

# MCP服务器配置
MCP_SERVER_URL = "https://www.modelscope.cn/mcp/servers/@KunihiroS/google-patents-mcp"
API_KEY = "ceac1888ee08e1e41d3ae9a2176c888ad05a85955c8e0580b95b7ae4262a824a"


def test_mcp_connection():
    """测试MCP服务器连接"""
    print("测试MCP服务器连接...")
    print(f"服务器地址: {MCP_SERVER_URL}")
    print(f"API密钥: {API_KEY[:10]}...")

    # 尝试连接服务器
    try:
        # 注意：MCP服务器通常使用特定的API端点
        # 这里需要查看MCP服务器的具体API文档
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

        # 尝试获取服务器信息
        response = requests.get(f"{MCP_SERVER_URL}/info", headers=headers, timeout=10)

        if response.status_code == 200:
            print("连接成功！")
            print(f"服务器响应: {response.text[:200]}")
            return True
        else:
            print(f"连接失败，状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False

    except Exception as e:
        print(f"连接异常: {e}")
        return False


def search_patents(keyword):
    """搜索专利"""
    print(f"\n搜索专利: {keyword}")

    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

        # 构建搜索请求
        payload = {"query": keyword, "limit": 5}

        # 注意：需要查看MCP服务器的具体API端点
        response = requests.post(
            f"{MCP_SERVER_URL}/search", headers=headers, json=payload, timeout=30
        )

        if response.status_code == 200:
            results = response.json()
            print(f"找到 {len(results.get('results', []))} 个结果")
            return results
        else:
            print(f"搜索失败，状态码: {response.status_code}")
            return None

    except Exception as e:
        print(f"搜索异常: {e}")
        return None


if __name__ == "__main__":
    print("Google Patents MCP测试")
    print("=" * 50)

    # 测试连接
    if test_mcp_connection():
        # 测试搜索
        results = search_patents("artificial intelligence")
        if results:
            print("\n搜索结果:")
            print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print("\n无法连接到MCP服务器，请检查配置。")
        print("\n建议:")
        print("1. 检查MCP服务器地址是否正确")
        print("2. 检查API密钥是否有效")
        print("3. 查看MCP服务器文档了解具体API端点")
