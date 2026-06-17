#!/bin/bash
# 执行性能测试

PORT=${1:-8000}
CONCURRENT=${2:-4}
INPUT_TOKENS=${3:-1024}
OUTPUT_TOKENS=${4:-1024}
ITERATIONS=${5:-10}

echo "执行性能测试..."
echo "  端口: ${PORT}"
echo "  并发: ${CONCURRENT}"
echo "  输入: ${INPUT_TOKENS}"
echo "  输出: ${OUTPUT_TOKENS}"

# 使用 vLLM benchmark 工具
python3 -m vllm.entrypoints.openai.api_server \
    --model ${MODEL_PATH} \
    --trust-remote-code

# 运行测试
vllm_benchmark \
    --model ${MODEL_PATH} \
    --tokenizer ${MODEL_PATH} \
    --num-prompts ${ITERATIONS} \
    --concurrent ${CONCURRENT} \
    --prompt-len ${INPUT_TOKENS} \
    --output-len ${OUTPUT_TOKENS} \
    --port ${PORT}

echo "性能测试完成"
