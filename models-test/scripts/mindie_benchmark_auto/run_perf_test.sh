#!/bin/bash
CSV_FILE="mindie_results_Qwen3-32B-FP8-1-NPU_acgraph_all.csv"
IP="127.0.0.1"
WARMUP_NUM=10
UNIFORM_INTERVAL=0
# Define the fixed combinations of P, I, O
declare -a combinations_test=(
    "1 2048 2048 0"
    "8 2048 2048 0"
    "16 2048 2048 0"
    "32 2048 2048 0"
    "64 2048 2048 0"
    "128 2048 2048 0"
    "256 2048 2048 0"
)

declare -a combinations=(
    "1 128 128 0"
    "1 256 256 0"
    "1 512 512 0"
    "1 128 1024 0"
    "1 1024 128 0"
    "1 128 2048 0"
    "1 1024 1024 0"
    "1 2048 2048 0"
    "1 4096 1024 0"
    "1 4096 4096 0"
#    "1 8192 8192 0"
#    "2 128 128 0"
#    "2 256 256 0"
#    "2 512 512 0"
#    "2 128 1024 0"
#    "2 1024 128 0"
#    "2 128 2048 0"
#    "2 1024 1024 0"
#    "2 2048 2048 0"
#    "2 4096 1024 0"
#    "2 4096 4096 0"
#    "2 8192 8192 0"
#    "4 128 128 0"
#    "4 256 256 0"
#    "4 512 512 0"
#    "4 128 1024 0"
#    "4 1024 128 0"
#    "4 128 2048 0"
#    "4 1024 1024 0"
#    "4 2048 2048 0"
#    "4 4096 1024 0"
#    "4 4096 4096 0"
#    "4 8192 8192 0"
    "8 128 128 0"
    "8 256 256 0"
    "8 512 512 0"
    "8 128 1024 0"
    "8 1024 128 0"
    "8 128 2048 0"
    "8 1024 1024 0"
    "8 2048 2048 0"
    "8 4096 1024 0"
    "8 4096 4096 0"
#    "8 8192 8192 0"
    "16 128 128 0"
    "16 256 256 0"
    "16 512 512 0"
    "16 128 1024 0"
    "16 1024 128 0"
    "16 128 2048 0"
    "16 1024 1024 0"
    "16 2048 2048 0"
    "16 4096 1024 0"
    "16 4096 4096 0"
#    "16 8192 8192 0"
    "24 128 128 0"
    "24 256 256 0"
    "24 512 512 0"
    "24 128 1024 0"
    "24 1024 128 0"
    "24 128 2048 0"
    "24 1024 1024 0"
    "24 2048 2048 0"
    "24 4096 1024 0"
    "24 4096 4096 0"
#    "24 8192 8192 0"
    "32 128 128 0"
    "32 256 256 0"
    "32 512 512 0"
    "32 128 1024 0"
    "32 1024 128 0"
    "32 128 2048 0"
    "32 1024 1024 0"
    "32 2048 2048 0"
    "32 4096 1024 0"
    "32 4096 4096 0"
#    "32 8192 8192 0"
    "48 128 128 0"
    "48 256 256 0"
    "48 512 512 0"
    "48 128 1024 0"
    "48 1024 128 0"
    "48 128 2048 0"
    "48 1024 1024 0"
    "48 2048 2048 0"
    "48 4096 1024 0"
    "48 4096 4096 0"
#    "48 8192 8192 0"
    "64 128 128 0"
    "64 256 256 0"
    "64 512 512 0"
    "64 128 1024 0"
    "64 1024 128 0"
    "64 128 2048 0"
    "64 1024 1024 0"
    "64 2048 2048 0"
    "64 4096 1024 0"
    "64 4096 4096 0"
#    "64 8192 8192 0"
    "128 128 128 0"
    "128 256 256 0"
    "128 512 512 0"
    "128 128 1024 0"
    "128 1024 128 0"
    "128 128 2048 0"
    "128 1024 1024 0"
    "128 2048 2048 0"
    "128 4096 1024 0"
    "128 4096 4096 0"
#    "128 8192 8192 0"
    "256 128 128 0"
    "256 256 256 0"
    "256 512 512 0"
    "256 128 1024 0"
    "256 1024 128 0"
    "256 128 2048 0"
    "256 1024 1024 0"
    "256 2048 2048 0"
    "256 4096 1024 0"
    "256 4096 4096 0"
#    "256 8192 8192 0"
)


show_help() {
    cat << 'EOF'
===========================================================================
        AI Model Benchmark Testing Script
===========================================================================

USAGE:
  ./run_perf_test.sh --model-path MODEL_PATH --port PORT [OPTIONS]

REQUIRED:
  --model-path PATH     Path to model directory (e.g. /data/models/Qwen/Qwen3-32B)
  --port NUMBER         API server port (e.g. 4567)

OPTIONS:
  --ip ADDRESS         API server IP (default: 127.0.0.1)
  --temperature FLOAT  Inference temperature (default: 0.65)
  --request-rate NUM   Request rate per second (optional, if not specified, no rate limit)

EXAMPLES:
  ./run_perf_test.sh --model-path /data/models/Qwen/Qwen3-32B --port 4567
  ./run_perf_test.sh --model-path /data/models/Qwen/Qwen3-32B --ip 192.168.1.100 --port 4567 --temperature 0.8 --request-rate 10

===========================================================================
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --ip)
            IP="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --model-path)
            MODEL_PATH="$2"
            MODEL_NAME=$(basename "$2")
            shift 2
            ;;
        --temperature)
            TEMPERATURE="$2"
            shift 2
            ;;
        -r|--result-dir)
            RESULTS_DIR="$2"
            shift 2
            ;;
        -M|--mode)
            MODE="$2"
            shift 2
            ;;
        -n|--npu-count)
            NPU_COUNT="$2"
            shift 2
            ;;
        --request-rate)
            REQUEST_RATE="$2"
            if [[ "$REQUEST_RATE" == "0" ]]; then
                REQUEST_RATE=""
            fi
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            show_help
            exit 1
            ;;
    esac
done

DEFAULT_RESULTS_DIR="./results"
RESULTS_DIR="${RESULTS_DIR:-$DEFAULT_RESULTS_DIR}"

# 获取当前架构
ARCH=$(uname -m)
CSV_FILE="$RESULTS_DIR/${ARCH}_mindie_results_${MODEL_NAME}_${NPU_COUNT}_npu_${MODE}.csv"


python3 performance_test.py -M $MODEL_NAME --warmup-num $WARMUP_NUM --ip $IP --port $PORT --model-path $MODEL_PATH

for combination in "${combinations[@]}"; do
    # Read P, I, O from the combination string
    read -r p i o u <<< "$combination"
    echo "Running test with P=$p, I=$i, O=$o"
    python3 performance_test.py -M $MODEL_NAME -P $p -I $i -O $o -C $CSV_FILE --uniform-interval $UNIFORM_INTERVAL --ip $IP --port $PORT --model-path $MODEL_PATH
done
