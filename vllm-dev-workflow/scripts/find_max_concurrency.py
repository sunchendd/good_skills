# openai_api_test.py
# -*- coding: utf-8 -*-
import argparse 

from performance_test import performance_test, save_to_csv

def find_max_concurrency(args):
    """
    找出满足单用户吞吐大于目标值的最大并发数
    """
    base_concurrency = args.thread_num
    target_tokens_per_second = args.target_tps

    report_result_list = []
    
    # 首先检查是否至少1个并发能达标
    initial_concurrency = 1
    args.thread_num = initial_concurrency
    report_result = performance_test(args=args, print_result=False, save_file=False)
    initial_throughput = report_result["avg TPS (without prefill)"]
    report_result_list.append(report_result)
    if initial_throughput < target_tokens_per_second:
        print(f"单用户吞吐小于目标值，无法找到满足条件的并发数")
        return 0  # 即使1个并发都不够，返回0
    
    # 确定高边界
    low = 1
    high = base_concurrency
    print(f"开始寻找边界并发数")
    while True:
        print(f"当前测试并发数为：{high}")
        args.thread_num = high
        report_result = performance_test(args=args, print_result=False, save_file=False)
        report_result_list.append(report_result)
        current_throughput = report_result["avg TPS (without prefill)"]
        if current_throughput >= target_tokens_per_second:
            low =high
        else:
            break
        high *= 2  # 不断扩大高边界直到找到合适的范围
    print(f"边界并发数为：{high}")
    
    # 二分查找
    max_concurrency = 0
    print(f"开始寻找最大并发数")
    while low <= high:
        mid = (low + high) // 2
        print(f"当前测试并发数为：{mid}")
        args.thread_num = mid
        report_result = performance_test(args=args, print_result=False, save_file=False)
        report_result_list.append(report_result)
        current = report_result["avg TPS (without prefill)"]
        
        if current >= target_tokens_per_second:
            max_concurrency = mid
            low = mid + 1
        else:
            high = mid - 1
    print(f"最终最大并发数为：{max_concurrency}")
    if max_concurrency > 0:
        # 找到最大并发数后，更新对应的 report_result 的 if_max 字段
        for result in report_result_list:
            if result["Process Num"] == max_concurrency:
                result["is_max_concurrency"] = 'yes'
            else:
                result["is_max_concurrency"] = 'no'
    save_to_csv(report_result_list, args.csv_file)

    return max_concurrency


if __name__ == "__main__":
    # 添加argparse参数解析
    parser = argparse.ArgumentParser(description="Performance benchmark for a language model.")
    parser.add_argument("-P", '--thread-num', type=int, default=1, help='并发数')
    parser.add_argument("-I", '--input-tokens-num', type=int, default=128, help='输入Token数')
    parser.add_argument("-O", '--output-tokens-num', type=int, default=2048, help='输出Token数')
    parser.add_argument("-M", '--model-name', type=str, default="qwen", help='模型服务化部署时的模型名称')
    parser.add_argument("-C", "--csv-file", type=str, default="results.csv", help="csv file to store results")
    parser.add_argument('--ip', type=str, default="127.0.0.1", help='Service IP Address')
    parser.add_argument('--port', type=int, default=1025, help='Service 端口')
    parser.add_argument('--model-path', type=str, default="", help='模型路径')
    parser.add_argument('--dataset-path', type=str, default="./sonnet_20x.txt", help='数据集路径')
    parser.add_argument('--uniform-interval', type=float, default=0, help='均匀发起请求的时间间隔（秒），默认为0表示不启用均匀模式')
    parser.add_argument('--target-tps', type=int, default=9, help='tps阈值')

    args = parser.parse_args()

    max_concurrency = find_max_concurrency(args=args)
