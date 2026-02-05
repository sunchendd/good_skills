#!/bin/bash
# vLLM 进程清理脚本
echo "查找vllm相关进程(包括大小写)..."
ps -ef | grep -iE "vllm|VLLM" | grep -v grep

echo ""
echo "正在Kill所有vllm进程..."
ps -ef | grep -iE "vllm|VLLM" | grep -v grep | awk '{print $2}' | xargs -r kill -9 2>/dev/null

sleep 2
echo ""
echo "检查是否还有残留进程:"
ps -ef | grep -iE "vllm|VLLM" | grep -v grep || echo "所有vllm进程已清理完毕"
