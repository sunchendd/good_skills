#!/bin/bash

DEFAULT_API_URL="http://127.0.0.1:8000"
DEFAULT_EVAL_TYPE="server"
DEFAULT_DATASETS="mmlu"

show_help() {
    echo "Usage: $0 [options]"
    echo "Options (order-independent):"
    echo "  -a, --api_url                 API url (default: $DEFAULT_API_URL)"
    echo "  -m, --model <model name>       Model name (required)"
    echo "  -dir, --dataset_dir <dir>        Dataset directory (required)"
    echo "  -e, --eval_type <type>         Evaluation type (default: $DEFAULT_EVAL_TYPE)"
    echo "  -d, --datasets <datasets>      Datasets to evaluate (default: $DEFAULT_DATASETS)"
    echo "  -n, --npu_count <count>       NPU count (required)"
    echo "  --mode <mode>                 Execution mode (required)"
    echo "  -r, --result-dir <dir>        Result directory (required)"
    echo "  -h, --help                    Show this help message"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -a|--api_url)
            if [ -z "$2" ]; then
                echo "ERROR: --api_url requires a value" >&2
                show_help
            fi
            API_URL="$2"
            shift 2
            ;;
        -m|--model)
            if [ -z "$2" ]; then
                echo "ERROR: --model-path requires a value" >&2
                show_help
            fi
            MODEL="$2"
            shift 2
            ;;
        -dir|--dataset_dir)
            if [ -z "$2" ]; then
                echo "ERROR: --result-dir requires a value" >&2
                show_help
            fi
            if [[ "$2" = /* ]]; then
                DATASET_DIR="$2"
            else
                DATASET_DIR="$(cd "$(pwd)" && cd "$2" 2>/dev/null && pwd || echo "$2")"
            fi
            shift 2
            ;;
        -r|--result-dir)
            if [ -z "$2" ]; then
                echo "ERROR: --result-dir requires a value" >&2
                show_help
            fi
            if [[ "$2" = /* ]]; then
                RESULT_DIR="$2"
            else
                RESULT_DIR="$(cd "$(pwd)" && cd "$2" 2>/dev/null && pwd || echo "$2")"
            fi
            shift 2
            ;;
        -e|--eval_type)
            if [ -z "$2" ]; then
                echo "ERROR: --eval_type requires a value" >&2
                show_help
            fi
            EVAL_TYPE="$2"
            shift 2
            ;;
        -d|--datasets)
            if [ -z "$2" ]; then
                echo "ERROR: --datasets requires a value" >&2
                show_help
            fi
            DATASETS="$2"
            shift 2
            ;;
        -n|--npu_count)
            if [ -z "$2" ]; then
                echo "ERROR: --npu_count requires a value" >&2
                show_help
            fi
            NPU_COUNT="$2"
            shift 2
            ;;
        --mode)
            if [ -z "$2" ]; then
                echo "ERROR: --mode requires a value" >&2
                show_help
            fi
            MODE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo "Unknown option: $1" >&2
            show_help
            ;;
    esac
done

# 获取当前架构
ARCH=$(uname -m)

# 修改 evalscope 源码以设置 timeout 为 None
PYTHON_FILE=$(ls /usr/local/python3.*/lib/python3.*/site-packages/evalscope/models/openai_compatible.py 2>/dev/null | head -n 1)
if [ -n "$PYTHON_FILE" ] && [ -f "$PYTHON_FILE" ]; then
    if ! grep -q "model_args\['timeout'\] = None" "$PYTHON_FILE"; then
        sed -i "/self.base_url = self.base_url.rstrip('\/').removesuffix('\/chat\/completions')/a \        model_args['timeout'] = None" "$PYTHON_FILE"
        echo "Modified $PYTHON_FILE to set timeout to None"
    fi
fi

# 执行精度测试
evalscope eval \
 --model $MODEL \
 --eval-type $EVAL_TYPE \
 --api-url $API_URL \
 --api-key EMPTY \
 --datasets $DATASETS \
 --eval-batch-size 128 \
 --work-dir ./outputs/$MODEL 


# 寻找最新的 JSON 报告文件
REPORT_JSON=$(find ./outputs/$MODEL -name "${DATASETS}.json" 2>/dev/null | grep "reports/${MODEL}" | xargs ls -t 2>/dev/null | head -n 1)

# 记录结果到文件
RESULT_FILE="${RESULT_DIR}/${ARCH}_${MODEL}_$(date +%Y%m%d_%H%M%S)_${NPU_COUNT}_npu_${MODE}_${DATASETS}.csv"

if [ -n "$REPORT_JSON" ]; then
    echo "name,score,num" > "$RESULT_FILE"
    # 第一行：metrics 中的信息 (name, score, num)
    jq -r '.metrics[0] | [.name, .score, .num] | @csv' "$REPORT_JSON" >> "$RESULT_FILE"
    # 后续行：subsets 中的信息 (name, score, num)
    jq -r '.metrics[0].categories[].subsets[] | [.name, .score, .num] | @csv' "$REPORT_JSON" >> "$RESULT_FILE"
    echo "Results saved to: $RESULT_FILE"
else
    echo "ERROR: No evaluation report found for model $MODEL and dataset $DATASETS in ./outputs"
fi
