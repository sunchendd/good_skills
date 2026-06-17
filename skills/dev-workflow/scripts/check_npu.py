#!/usr/bin/env python3
# 检查 Ascend NPU 可用性

import subprocess
import json

def check_npu():
    try:
        result = subprocess.run(
            ["npu-smi", "info", "-l"],
            capture_output=True,
            text=True
        )
        print("NPU 信息:")
        print(result.stdout)

        # 解析可用设备
        usable_cards = []
        for line in result.stdout.split('\n'):
            if '空闲' in line or 'free' in line.lower():
                # 提取设备ID
                print(f"可用 NPU: {line}")

        return True
    except Exception as e:
        print(f"检查 NPU 失败: {e}")
        return False

if __name__ == "__main__":
    check_npu()
