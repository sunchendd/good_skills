#!/usr/bin/env python3
"""
测试patent-search skill的完整功能
"""

import sys
import os
import json

# 添加scripts目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))

from patent_finder import PatentFinder


def test_complete_patent_search():
    """测试完整的专利搜索流程"""
    print("专利搜索skill测试")
    print("=" * 60)

    finder = PatentFinder()

    # 测试用例
    test_cases = [
        {
            "name": "人工智能专利",
            "keywords": "artificial intelligence",
            "database": "google",
            "limit": 3,
        },
        {
            "name": "机器学习专利",
            "keywords": "machine learning",
            "database": "google",
            "limit": 2,
        },
        {
            "name": "神经网络专利",
            "keywords": "neural network",
            "database": "google",
            "limit": 2,
        },
    ]

    all_results = []

    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"关键词: {test_case['keywords']}")
        print("-" * 40)

        if test_case["database"] == "google":
            results = finder.search_google_patents(
                test_case["keywords"], test_case["limit"]
            )
        elif test_case["database"] == "uspto":
            results = finder.search_uspto(
                test_case["keywords"], limit=test_case["limit"]
            )
        elif test_case["database"] == "cnipa":
            results = finder.search_cnipa(
                test_case["keywords"], limit=test_case["limit"]
            )
        elif test_case["database"] == "epo":
            results = finder.search_epo(test_case["keywords"], limit=test_case["limit"])
        else:
            results = []

        all_results.extend(results)

        # 显示结果
        if results:
            print(f"找到 {len(results)} 个结果:")
            for i, patent in enumerate(results, 1):
                print(f"\n{i}. {patent['patent_id']}")
                print(f"   标题: {patent['title'][:80]}...")
                print(f"   权利人: {patent['applicant'][:50]}")
                print(f"   申请日: {patent['filing_date']}")
        else:
            print("未找到结果")

    # 分析所有结果
    print("\n" + "=" * 60)
    print("综合分析")
    print("=" * 60)

    analysis = finder.analyze_patents(all_results)
    print(f"总共找到 {analysis['total']} 篇专利")

    if analysis["by_database"]:
        print("\n按数据库分布:")
        for db, count in analysis["by_database"].items():
            print(f"  {db}: {count}")

    # 保存结果到文件
    output_file = "patent_search_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n结果已保存到: {output_file}")

    # 生成简要报告
    report_file = "patent_search_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# 专利检索报告\n\n")
        f.write("## 检索概要\n\n")
        f.write(f"- 检索时间: {sys.argv[0]}\n")
        f.write(f"- 总专利数: {analysis['total']}\n")
        f.write("\n## 测试用例\n\n")

        for test_case in test_cases:
            f.write(f"### {test_case['name']}\n")
            f.write(f"- 关键词: {test_case['keywords']}\n")
            f.write(f"- 数据库: {test_case['database']}\n")
            f.write(f"- 限制数量: {test_case['limit']}\n\n")

        f.write("## 按数据库分布\n\n")
        for db, count in analysis["by_database"].items():
            f.write(f"- {db}: {count}\n")

        f.write("\n## 重点专利\n\n")
        for i, patent in enumerate(all_results[:5], 1):
            f.write(f"### {i}. {patent['patent_id']}\n")
            f.write(f"- **标题**: {patent['title']}\n")
            f.write(f"- **权利人**: {patent['applicant']}\n")
            f.write(f"- **申请日**: {patent['filing_date']}\n")
            f.write(f"- **数据库**: {patent['database']}\n")
            f.write(f"- **URL**: {patent['url']}\n\n")

    print(f"报告已生成: {report_file}")


if __name__ == "__main__":
    test_complete_patent_search()
