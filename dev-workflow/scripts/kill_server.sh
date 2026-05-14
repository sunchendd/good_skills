#!/bin/bash
# 清理所有推理服务进程

echo "正在清理推理服务进程..."

# 查找并kill vLLM 进程
pkill -f "vllm serve" 2>/dev/null
pkill -f "vllm.serve" 2>/dev/null

# 查找并kill MindIE 进程
pkill -f "mindie" 2>/dev/null

# 查找并kill 相关 Python 进程
pkill -f "performance_test" 2>/dev/null
pkill -f "benchmark" 2>/dev/null

# 清理残留的端口占用
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti:8001 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti:10000 2>/dev/null | xargs kill -9 2>/dev/null
lsof -ti:10001 2>/dev/null | xargs kill -9 2>/dev/null

echo "清理完成"
