#!/bin/bash
# 性能测试脚本
# 用法: ./run_perf_test.sh <port>
# 示例: ./run_perf_test.sh 10000

PORT=${1:-10000}
MODEL_NAME="Qwen3-32B"
IP="127.0.0.1"
CSV_FILE="vllm-Qwen3-32B-$PORT.csv"
MODEL_PATH="/data2/weights/Qwen_Qwen3-32B"
WARMUP_NUM=2
UNIFORM_INTERVAL=0
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

rm -f $CSV_FILE

declare -a combinations=(
    "1 512 512 1"
    "4 512 512 1"
    "8 512 512 1"
    "16 512 512 1"
    "32 512 512 1"
    "64 512 512 1"
)

echo "========================================="
echo "Running performance test on port: $PORT"
echo "========================================="

# Warmup
python3 ${SCRIPT_DIR}/performance_test.py -M $MODEL_NAME --warmup-num $WARMUP_NUM --ip $IP --port $PORT --model-path $MODEL_PATH

# Main test
for combination in "${combinations[@]}"; do
    read -r p i o u <<< "$combination"
    echo "Running test with P=$p, I=$i, O=$o"
    python3 ${SCRIPT_DIR}/performance_test.py -M $MODEL_NAME -P $p -I $i -O $o -C $CSV_FILE --uniform-interval $UNIFORM_INTERVAL --ip $IP --port $PORT --model-path $MODEL_PATH
done

echo "Results saved to: $CSV_FILE"
