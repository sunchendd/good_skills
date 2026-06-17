#!/bin/bash
# 启动 vLLM 服务

# 默认配置
PORT=${1:-8000}
TP=${2:-2}
MODEL_PATH=${3:-"/data/models/Qwen3-8B"}
MAX_SEQS=${4:-16}

echo "启动 vLLM 服务..."
echo "  模型: ${MODEL_PATH}"
echo "  端口: ${PORT}"
echo "  TP: ${TP}"

export CUDA_VISIBLE_DEVICES=0,1

vllm serve ${MODEL_PATH} \
    --tp ${TP} \
    --port ${PORT} \
    --max-num-seqs ${MAX_SEQS} \
    --host 0.0.0.0

echo "vLLM 服务已停止"
