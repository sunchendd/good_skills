#!/bin/bash
set -euo pipefail

TEST_IP=127.0.0.1
TEMPERATURE=0.65
REQUEST_RATE=""
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

declare -a combinations=(
    "128 128 1 1"
    "256 256 1 1"
    "512 512 1 1"
    "128 1024 1 1"
    "1024 128 1 1"
    "128 2048 1 1"
    "1024 1024 1 1"
    "2048 2048 1 1"
    "4096 1024 1 1"
    "4096 4096 1 1"
    "8192 8192 1 1"
    "128 128 2 2"
    "256 256 2 2"
    "512 512 2 2"
    "128 1024 2 2"
    "1024 128 2 2"
    "128 2048 2 2"
    "1024 1024 2 2"
    "2048 2048 2 2"
    "4096 1024 2 2"
    "4096 4096 2 2"
    "8192 8192 2 2"
    "128 128 4 4"
    "256 256 4 4"
    "512 512 4 4"
    "128 1024 4 4"
    "1024 128 4 4"
    "128 2048 4 4"
    "1024 1024 4 4"
    "2048 2048 4 4"
    "4096 1024 4 4"
    "4096 4096 4 4"
    "8192 8192 4 4"
    "128 128 8 8"
    "256 256 8 8"
    "512 512 8 8"
    "128 1024 8 8"
    "1024 128 8 8"
    "128 2048 8 8"
    "1024 1024 8 8"
    "2048 2048 8 8"
    "4096 1024 8 8"
    "4096 4096 8 8"
    "8192 8192 8 8"
    "128 128 16 16"
    "256 256 16 16"
    "512 512 16 16"
    "128 1024 16 16"
    "1024 128 16 16"
    "128 2048 16 16"
    "1024 1024 16 16"
    "2048 2048 16 16"
    "4096 1024 16 16"
    "4096 4096 16 16"
    "8192 8192 16 16"
    "128 128 24 24"
    "256 256 24 24"
    "512 512 24 24"
    "128 1024 24 24"
    "1024 128 24 24"
    "128 2048 24 24"
    "1024 1024 24 24"
    "2048 2048 24 24"
    "4096 1024 24 24"
    "4096 4096 24 24"
    "8192 8192 24 24"
    "128 128 32 32"
    "256 256 32 32"
    "512 512 32 32"
    "128 1024 32 32"
    "1024 128 32 32"
    "128 2048 32 32"
    "1024 1024 32 32"
    "2048 2048 32 32"
    "4096 1024 32 32"
    "4096 4096 32 32"
    "8192 8192 32 32"
    "128 128 64 64"
    "256 256 64 64"
    "512 512 64 64"
    "128 1024 64 64"
    "1024 128 64 64"
    "128 2048 64 64"
    "1024 1024 64 64"
    "2048 2048 64 64"
    "4096 1024 64 64"
    "4096 4096 64 64"
    "8192 8192 64 64"
    "128 128 128 128"
    "256 256 128 128"
    "512 512 128 128"
    "128 1024 128 128"
    "1024 128 128 128"
    "128 2048 128 128"
    "1024 1024 128 128"
    "2048 2048 128 128"
    "4096 1024 128 128"
    "4096 4096 128 128"
    "8192 8192 128 128"
    "128 128 256 256"
    "256 256 256 256"
    "512 512 256 256"
    "128 1024 256 256"
    "1024 128 256 256"
    "128 2048 256 256"
    "1024 1024 256 256"
    "2048 2048 256 256"
    "4096 1024 256 256"
    "4096 4096 256 256"
    "8192 8192 256 256"
)

combinations_old=(
    "1024 1024 8 8"
    "2048 2048 8 8"
    "4096 1024 8 8"
    "1024 1024 16 16"
    "2048 2048 16 16"
    "4096 1024 16 16"
    "1024 1024 32 32"
    "2048 2048 32 32"
    "4096 1024 32 32"
    "1024 1024 64 64"
    "2048 2048 64 64"
    "4096 1024 64 64"
    "1024 1024 128 128"
    "2048 2048 128 128"
    "4096 1024 128 128"
    "1024 1024 256 256"
    "2048 2048 256 256"
    "4096 1024 256 256"
)
# combinations=(
#     "1024 1024 640 128"
#     "2048 2048 389 98"
#     "3500 1500 330 66"
#     "4096 1024 300 60"
#     "8192 1024 150 30"
#     "16384 1024 75 15"
#     "32768 1024 35 7"
#     "65536 1024 40 2"
#     "131072 1024 40 2"
# )

generate_combo_dirs() {
    local combo_dirs=()
    for combo in "${combinations[@]}"; do
        read input_len output_len num_prompts max_concurrency <<< "$combo"
        combo_dirs+=("$(get_combo_dir_name "$input_len" "$output_len" "$num_prompts" "$max_concurrency")")
    done
    echo "${combo_dirs[@]}"
}

log() {
    local message="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message"
}

get_combo_dir_name() {
    local input_len="$1"
    local output_len="$2"
    local num_prompts="$3"
    local max_concurrency="$4"
    echo "in${input_len}_out${output_len}_prompts${num_prompts}_conc${max_concurrency}"
}

show_help() {
    cat << 'EOF'
===========================================================================
        AI Model Benchmark Testing Script
===========================================================================

USAGE:
  ./run_test.sh --model-path MODEL_PATH --port PORT [OPTIONS]

REQUIRED:
  --model-path PATH     Path to model directory (e.g. /data/models/Qwen/Qwen3-32B)
  --port NUMBER         API server port (e.g. 4567)

OPTIONS:
  --ip ADDRESS         API server IP (default: 127.0.0.1)
  --temperature FLOAT  Inference temperature (default: 0.65)
  --request-rate NUM   Request rate per second (optional, if not specified, no rate limit)

EXAMPLES:
  ./run_test.sh --model-path /data/models/Qwen/Qwen3-32B --port 4567
  ./run_test.sh --model-path /data/models/Qwen/Qwen3-32B --ip 192.168.1.100 --port 4567 --temperature 0.8 --request-rate 10

===========================================================================
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --ip)
            TEST_IP="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --model-path)
            TOKENIZER_PATH="$2"
            MODEL_NAME=$(basename "$2")
            shift 2
            ;;
        --temperature)
            TEMPERATURE="$2"
            shift 2
            ;;
        --request-rate)
            REQUEST_RATE="$2"
            if [[ "$REQUEST_RATE" == "0" ]]; then
                REQUEST_RATE=""
            fi
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
        *)
            echo "Unknown parameter: $1"
            show_help
            exit 1
            ;;
    esac
done

if [[ -z "${MODEL_NAME:-}" ]]; then
    echo "Error: --model-path argument is required"
    show_help
    exit 1
fi
if [[ -z "${PORT:-}" ]]; then
    echo "Error: --port argument is required"
    show_help
    exit 1
fi

# 获取当前架构
ARCH=$(uname -m)

#vllm版本为0.11.0以上时，采用命令方式执行性能测试
VLLM_VERSION=$(pip list | grep vllm | awk '{print $2}')

if [ -z "$VLLM_VERSION" ]; then 
    echo "Error:not install vllm" >> "$EXEC_LOG"
    exit 1
fi

CLENA_VERSION=$(echo "$VLLM_VERSION" | sed 's/\+[a-zA-Z0-9]*$//')

if [[ "$CLENA_VERSION" < "0.11.0" ]]; then
    RESULTS_DIR="./results/${ARCH}_${MODEL_NAME}_${TEST_IP}_${PORT}_${TIMESTAMP}_${MODE}"
else
    DEFAULT_RESULTS_DIR="./results"
    RESULTS_DIR="${RESULTS_DIR:-$DEFAULT_RESULTS_DIR}"
    RESULTS_DIR="$RESULTS_DIR/${ARCH}_${MODEL_NAME}_${TEST_IP}_${PORT}_${TIMESTAMP}_${MODE}"
fi

#RESULTS_DIR="./results/${MODEL_NAME}_${TEST_IP}_${PORT}_${TIMESTAMP}_${MODE}"
mkdir -p "$RESULTS_DIR"

GLOBAL_START_TIME=$(date +%s)

{
    echo "==== Benchmark Configuration ===="
    echo "Model:       $MODEL_NAME"
    echo "Tokenizer:   $TOKENIZER_PATH"
    echo "API IP:      $TEST_IP"
    echo "API Port:    $PORT"
    echo "Temperature: $TEMPERATURE"
    if [[ -n "$REQUEST_RATE" ]]; then
        echo "Request Rate: $REQUEST_RATE"
    else
        echo "Request Rate: unlimited"
    fi
    echo "Start Time:  $(date)"
    echo "Result Dir:  $RESULTS_DIR"
    echo ""
} > "${RESULTS_DIR}/summary.log"

for combo in "${combinations[@]}"; do
    read input_len output_len num_prompts max_concurrency <<< $combo
    COMBO_DIR="${RESULTS_DIR}/$(get_combo_dir_name "$input_len" "$output_len" "$num_prompts" "$max_concurrency")"
    mkdir -p "$COMBO_DIR"
    EXEC_LOG="${COMBO_DIR}/execution.log"
    START_TIME=$(date +%s)
    
    # 根据模型名称选择数据集
    if [[ "$MODEL_NAME" == "Qwen3-VL-32B-Instruct" || "$MODEL_NAME" == "Qwen3-VL-30B-A3B-Instruct" || "$CLENA_VERSION" < "0.11.0" ]]; then
        dataset_name="random--mm"
    else
        dataset_name="random"
    fi

    benchmark_args=(
        --backend openai-chat
        --base-url "http://${TEST_IP}:${PORT}"
        --endpoint '/v1/chat/completions'
        --model "$MODEL_NAME"
        --tokenizer "$TOKENIZER_PATH"
        --trust-remote-code
        --temperature "$TEMPERATURE"
        --dataset-name "$dataset_name"
        --random-input-len "$input_len"
        --random-output-len "$output_len"
        --ignore-eos
        --num-prompts "$num_prompts"
        --max-concurrency "$max_concurrency"
        --save-result
        --result-dir "$COMBO_DIR"
    )
    if [[ -n "$REQUEST_RATE" ]]; then
        benchmark_args+=(--request-rate "$REQUEST_RATE")
    fi
    
    log "Testing: input=${input_len}, output=${output_len}, prompts=${num_prompts}, concurrency=${max_concurrency}, temp=${TEMPERATURE}$(if [[ -n "$REQUEST_RATE" ]]; then echo ", request_rate=${REQUEST_RATE}"; else echo ", request_rate=unlimited"; fi)" > "$EXEC_LOG"
    log "开始测试组合: input=${input_len}, output=${output_len}, prompts=${num_prompts}, concurrency=${max_concurrency} ..."
    set +e

    log "vllm version {$VLLM_VERSION} {$CLENA_VERSION}" >> "$EXEC_LOG"
    if [[ "$CLENA_VERSION" < "0.11.0" ]]; then
        log "执行命令: python3 benchmark_serving.py ${benchmark_args[*]}" >> "$EXEC_LOG"
        python3 benchmark_serving.py "${benchmark_args[@]}" >> "$EXEC_LOG" 2>&1
    else
        log "执行命令: vllm  bench serve ${benchmark_args[*]}" >> "$EXEC_LOG"
        vllm  bench serve "${benchmark_args[@]}" >> "$EXEC_LOG" 2>&1
    fi 

    EXIT_STATUS=$?
    set -e
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    DURATION_STR=$(printf "%02d:%02d:%02d" $((DURATION/3600)) $(( (DURATION%3600)/60 )) $((DURATION%60)))
    if [ $EXIT_STATUS -eq 0 ]; then
        STATUS="SUCCESS"
        STATUS_COLOR="\033[32m"
        log "完成测试组合: input=${input_len}, output=${output_len}, prompts=${num_prompts}, concurrency=${max_concurrency} [SUCCESS - ${DURATION_STR}]"
    else
        STATUS="FAILED"
        STATUS_COLOR="\033[31m"
        log "完成测试组合: input=${input_len}, output=${output_len}, prompts=${num_prompts}, concurrency=${max_concurrency} [FAILED - ${DURATION_STR}]"
    fi
    printf "%-10s | %-5s | %-5s | %-5s | %-5s | ${STATUS_COLOR}%-7s\033[0m | %-9s | %s\n" \
        "$(date +%T)" "$input_len" "$output_len" "$num_prompts" "$max_concurrency" "$STATUS" "$DURATION_STR" "$COMBO_DIR" \
        >> "${RESULTS_DIR}/summary.log"
    if [ $EXIT_STATUS -ne 0 ]; then
        echo ""
        log "测试组合失败 (input=${input_len}, output=${output_len}, prompts=${num_prompts}, concurrency=${max_concurrency})"
        log "根据配置，提前结束后续所有测试..."
        break
    fi
done
echo ""
log "开始提取核心指标..."
CORE_METRICS_CSV="$RESULTS_DIR/core_metrics.csv"
echo "Process Num,Input Length,Output Length,total input Tokens,total output Tokens,duration (s),output throughput (tok/s),Mean TTFT (ms),Mean TPOT (ms),Mean ITL (ms)" > "$CORE_METRICS_CSV"
success_count=0

combo_dirs=($(generate_combo_dirs))
for dir in "${combo_dirs[@]}"; do
    if [[ $dir =~ ^in([0-9]+)_out([0-9]+)_prompts([0-9]+)_conc([0-9]+)$ ]]; then
        input_len=${BASH_REMATCH[1]}
        output_len=${BASH_REMATCH[2]}
        process_num=${BASH_REMATCH[3]}
        max_concurrency=${BASH_REMATCH[4]}
        echo "input_len = $input_len"
        echo "output_len = $output_len"
        echo "process_num = $process_num"
        echo "max_concurrency = $max_concurrency"
    else
        echo "error:目录格式不对"
    fi
    full_dir="$RESULTS_DIR/$dir"
    if [ -d "$full_dir" ]; then
        for json_file in "$full_dir"/*.json; do
            if [ -f "$json_file" ]; then
                log "处理: $json_file"
                extract_json_value() {
                    local file="$1"
                    local key="$2"
                    sed -n 's/.*"'"$key"'"[[:space:]]*:[[:space:]]*\([0-9.]*\).*/\1/p' "$file" | head -1
                }
                total_input_tokens=$(extract_json_value "$json_file" "total_input_tokens" || echo "0")
                total_output_tokens=$(extract_json_value "$json_file" "total_output_tokens" || echo "0")
                duration=$(extract_json_value "$json_file" "duration" || echo "0")
                output_throughput=$(extract_json_value "$json_file" "output_throughput" || echo "0")
                mean_ttft_ms=$(extract_json_value "$json_file" "mean_ttft_ms" || echo "0")
                mean_tpot_ms=$(extract_json_value "$json_file" "mean_tpot_ms" || echo "0")
                mean_itl_ms=$(extract_json_value "$json_file" "mean_itl_ms" || echo "0")
                clean_number() {
                    echo "$1" | sed 's/[^0-9.]//g' | grep -E '^[0-9]+\.?[0-9]*$' || echo "0"
                }
                total_input_tokens=$(clean_number "$total_input_tokens")
                total_output_tokens=$(clean_number "$total_output_tokens")
                duration=$(clean_number "$duration")
                output_throughput=$(clean_number "$output_throughput")
                mean_ttft_ms=$(clean_number "$mean_ttft_ms")
                mean_tpot_ms=$(clean_number "$mean_tpot_ms")
                mean_itl_ms=$(clean_number "$mean_itl_ms")
                total_input_tokens=${total_input_tokens:-0}
                total_output_tokens=${total_output_tokens:-0}
                duration=${duration:-0}
                output_throughput=${output_throughput:-0}
                mean_ttft_ms=${mean_ttft_ms:-0}
                mean_tpot_ms=${mean_tpot_ms:-0}
                mean_itl_ms=${mean_itl_ms:-0}
                echo "$process_num,$input_len,$output_len,$total_input_tokens,$total_output_tokens,$duration,$output_throughput,$mean_ttft_ms,$mean_tpot_ms,$mean_itl_ms" >> "$CORE_METRICS_CSV"
                success_count=$((success_count + 1))
                log "  提取结果: $total_input_tokens,$total_output_tokens,$duration,$output_throughput,$mean_ttft_ms,$mean_tpot_ms,$mean_itl_ms"
            fi
        done
    fi
done


log "核心指标提取完成! 成功处理 $success_count 个文件"
log "结果保存到: $CORE_METRICS_CSV"

TEMP_SUMMARY="${RESULTS_DIR}/temp_summary.log"
GLOBAL_END_TIME=$(date +%s)

{
    echo ""
    echo "==== Benchmark Results Summary ===="
    echo "Start Time: $(date -d @$GLOBAL_START_TIME +'%Y-%m-%d %H:%M:%S' 2>/dev/null || date -r $GLOBAL_START_TIME 2>/dev/null || date)"
    echo "End Time:   $(date)"
    if [[ -n "${GLOBAL_END_TIME:-}" && -n "${GLOBAL_START_TIME:-}" ]]; then
        echo "Total Duration: $(( (GLOBAL_END_TIME - GLOBAL_START_TIME)/60 )) minutes"
    fi
    echo ""
    echo "Model: $MODEL_NAME | IP: $TEST_IP | Port: $PORT | Temperature: $TEMPERATURE$(if [[ -n "$REQUEST_RATE" ]]; then echo " | Request Rate: $REQUEST_RATE"; else echo " | Request Rate: unlimited"; fi)"
    echo ""
    echo "Column: Time | Input | Output | Prompts | Concurrency | Status | Duration | Result Directory"
    echo "----------------------------------------------------------------------------------------"
} > "$TEMP_SUMMARY"

grep -E "^[0-9]{2}:[0-9]{2}:[0-9]{2}" "${RESULTS_DIR}/summary.log" >> "$TEMP_SUMMARY" 2>/dev/null || true

{
    echo ""
    echo "==== Core Metrics Summary ===="
    echo "核心指标已提取到: $CORE_METRICS_CSV"
    echo "成功处理文件数: $success_count"
} >> "$TEMP_SUMMARY"

cat "$TEMP_SUMMARY" >> "${RESULTS_DIR}/summary.log"
rm -f "$TEMP_SUMMARY"

echo ""
log "Benchmark completed. All results saved to:"
echo "  $RESULTS_DIR"
