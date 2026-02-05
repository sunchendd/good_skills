#!/bin/bash

DEFAULT_HOST="127.0.0.1"
DEFAULT_TEMPERATURE="0.65"
DEFAULT_REQUEST_RATE="0"
MODEL_PATH=""
RESULT_DIR=""
PORT=""
PROXY_IP="192.168.110.10"
PROXY_PORT="10082"
CODE_PATH=$(pwd)
echo "CODE_PATH=${CODE_PATH}"

show_help() {
    echo "Usage: $0 [options]"
    echo "Options (order-independent):"
    echo "  -i, --ip <host>               API host (default: $DEFAULT_HOST)"
    echo "  -p, --port <port>             API port (required)"
    echo "  -m, --model-path <path>       Model path (required)"
    echo "  -r, --result-dir <dir>        Results directory to map into container (required)"
    echo "  -t, --temperature <temp>      Temperature setting (default: $DEFAULT_TEMPERATURE)"
    echo "  -R, --request-rate <rate>     Request rate (default: $DEFAULT_REQUEST_RATE)"
    echo "  -h, --help                    Show this help message"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -i|--ip)
            if [ -z "$2" ]; then
                echo "ERROR: --ip requires a value" >&2
                show_help
            fi
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            if [ -z "$2" ]; then
                echo "ERROR: --port requires a value" >&2
                show_help
            fi
            PORT="$2"
            shift 2
            ;;
        -m|--model-path)
            if [ -z "$2" ]; then
                echo "ERROR: --model-path requires a value" >&2
                show_help
            fi
            MODEL_PATH="$2"
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
        -t|--temperature)
            if [ -z "$2" ]; then
                echo "ERROR: --temperature requires a value" >&2
                show_help
            fi
            TEMPERATURE="$2"
            shift 2
            ;;
        -R|--request-rate)
            if [ -z "$2" ]; then
                echo "ERROR: --request-rate requires a value" >&2
                show_help
            fi
            REQUEST_RATE="$2"
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
        -e|--executable-module)
            EXECUTABLE_MODULE="$2"
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

if [ -z "$MODEL_PATH" ]; then
    echo "ERROR: Model path is REQUIRED. Use -m or --model-path" >&2
    show_help
fi
if [ -z "$RESULT_DIR" ]; then
    echo "ERROR: Result directory is REQUIRED. Use -r or --result-dir" >&2
    show_help
fi
if [ -z "$PORT" ]; then
    echo "ERROR: API port is REQUIRED. Use -p or --port" >&2
    show_help
fi

HOST="${HOST:-$DEFAULT_HOST}"
TEMPERATURE="${TEMPERATURE:-$DEFAULT_TEMPERATURE}"
REQUEST_RATE="${REQUEST_RATE:-$DEFAULT_REQUEST_RATE}"

# 创建结果目录（如果不存在）
echo "🗂️  Preparing result directory..."
if [ ! -d "$RESULT_DIR" ]; then
    echo "   • Creating result directory: $RESULT_DIR"
    mkdir -p "$RESULT_DIR" || {
        echo "❌ ERROR: Failed to create result directory '$RESULT_DIR'" >&2
        echo "   Please check directory permissions and try again." >&2
        exit 1
    }
    echo "✅ Result directory created successfully"
else
    echo "✅ Result directory already exists: $RESULT_DIR"
fi

if [[ "$(uname -m)" == "aarch64" ]]; then
    echo "ℹ️  Detected ARM architecture"
    DOCKER_IMAGE="swr.cn-south-1.myhuaweicloud.com/ascendhub/mindie:2.1.RC1-800I-A2-py311-openeuler24.03-lts"
else
    echo "ℹ️  Detected x86_64 architecture"
    DOCKER_IMAGE="swr.cn-south-1.myhuaweicloud.com/ascendhub/mindie:2.1.RC1-800I-A2-py311-openeuler24.03-lts"
fi

MODEL_NAME=$(basename "$MODEL_PATH")

echo -e "\n🚀 Starting MindIe performance test:"
echo "   • Model Path:     $MODEL_PATH (REQUIRED)"
echo "   • Model Name:     $MODEL_NAME"
echo "   • Result Dir:     $RESULT_DIR (REQUIRED)"
echo "   • API Host:       $HOST"
echo "   • API Port:       $PORT (REQUIRED)"
echo "   • Temperature:    $TEMPERATURE"
echo "   • Request Rate:   $REQUEST_RATE"
echo "   • Docker Image:   $DOCKER_IMAGE"

echo -e "\n🔍 Checking LLM service availability..."

# First check if the service is running by checking /v1/models endpoint
echo "   • Checking service status..."
models_response=$(curl -s -w "%{http_code}" -o /dev/null \
    --max-time 10 \
    "http://$HOST:$PORT/v1/models")

if [ "$models_response" != "200" ]; then
    echo "❌ ERROR: LLM service is not accessible at http://$HOST:$PORT"
    echo "   HTTP response code: $models_response"
    echo "   Please ensure the LLM service is running and accessible."
    exit 1
fi

# Check if the target model is available
echo "   • Checking model availability..."
model_check=$(curl -s --max-time 10 "http://$HOST:$PORT/v1/models" | grep -o "\"id\":\"[^\"]*\"" | grep -o "\"$MODEL_NAME\"" || echo "")

if [ -z "$model_check" ]; then
    echo "⚠️  WARNING: Model '$MODEL_NAME' not found in available models"
    echo "   Available models:"
    curl -s --max-time 10 "http://$HOST:$PORT/v1/models" | grep -o "\"id\":\"[^\"]*\"" | sed 's/"id":"/   • /' | sed 's/"//'
    echo "   Continuing with performance test (model name might be auto-detected)..."
else
    echo "✅ Model '$MODEL_NAME' is available"
fi

# Optional: Test chat completions endpoint (non-blocking)
echo "   • Testing chat completions endpoint..."
chat_response=$(curl -s -w "%{http_code}" -o /tmp/chat_test_response 2>/dev/null \
    --max-time 15 \
    -H "Content-Type: application/json" \
    -d '{
        "model": "'"$MODEL_NAME"'",
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 10
    }' \
    "http://$HOST:$PORT/v1/chat/completions")

if [ "$chat_response" = "200" ]; then
    echo "✅ Chat completions endpoint is working"
else
    echo "⚠️  WARNING: Chat completions test failed (HTTP: $chat_response)"
    echo "   This might be due to model loading or configuration issues"
    echo "   Performance test will continue anyway..."
    if [ -f /tmp/chat_test_response ]; then
        echo "   Response preview:"
        head -c 200 /tmp/chat_test_response | sed 's/^/   /'
        rm -f /tmp/chat_test_response
    fi
fi

echo "✅ Service accessibility check completed"

TASK_DIR="mindiebench_${MODEL_NAME}_$(date +%Y%m%d_%H%M%S)_${MODE}"

# 定义清理函数
cleanup() {
    echo -e "\n🛑 Received interrupt signal, cleaning up..."
    
    # 获取所有相关的容器ID（包括可能的子进程）
    local containers=$(docker ps -aq --filter "name=$TASK_DIR" 2>/dev/null)
    
    if [ ! -z "$containers" ]; then
        echo "   • Found container(s) to clean up: $containers"
        
        # 首先尝试发送SIGTERM信号到容器
        echo "   • Sending SIGTERM to container '$TASK_DIR'..."
        docker kill --signal=SIGTERM "$TASK_DIR" >/dev/null 2>&1
        
        # 等待3秒让容器优雅退出
        sleep 3
        
        # 如果容器仍在运行，强制杀死
        if docker ps -q --filter "name=$TASK_DIR" | grep -q .; then
            echo "   • Force killing container '$TASK_DIR'..."
            docker kill --signal=SIGKILL "$TASK_DIR" >/dev/null 2>&1
        fi
        
        # 等待一下让容器完全停止
        sleep 2
        
        # 强制删除容器
        echo "   • Removing container '$TASK_DIR'..."
        docker rm -f "$TASK_DIR" >/dev/null 2>&1
        
        # 再次检查是否有残留容器
        remaining=$(docker ps -aq --filter "name=$TASK_DIR" 2>/dev/null)
        if [ ! -z "$remaining" ]; then
            echo "   • Cleaning up remaining containers: $remaining"
            docker rm -f $remaining >/dev/null 2>&1
        fi
        
        echo "✅ Container cleanup completed"
    else
        echo "   • No running container found to clean up"
    fi
    
    # 清理可能的后台进程
    echo "   • Cleaning up background processes..."
    pkill -f "docker.*$TASK_DIR" 2>/dev/null || true
    
    echo "🔚 Script terminated by user"
    exit 130
}

# 设置信号处理器 - 捕获多种信号
trap cleanup SIGINT SIGTERM SIGHUP SIGQUIT

echo -e "\n🏃 Starting performance test container..."
echo "   • Container name: $TASK_DIR"
echo "   • Press Ctrl+C to stop the test and clean up the container"
echo "   • If the script hangs, try Ctrl+\\ (SIGQUIT) for force cleanup"


# 在后台启动容器，这样可以更好地控制信号处理
(
    # 在子shell中运行docker，这样可以传播信号
    # 先创建软链接，设置代理，安装datasets包，然后执行benchmark.sh
    exec docker run --rm --privileged --net=host --name "$TASK_DIR" \
        --device /dev/davinci_manager --device /dev/devmm_svm --device /dev/hisi_hdc \
        -v /usr/local/dcmi:/usr/local/dcmi \
        -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
        -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
        -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
        -v /etc/ascend_install.info:/etc/ascend_install.info \
        -v "$MODEL_PATH:$MODEL_PATH" \
        -v /root/.cache:/root/.cache \
        -v /root/.pip:/root/.pip \
        -v /data:/data \
        -v /data2:/data2 \
        -v /nfs:/nfs \
        -v "$CODE_PATH":"$CODE_PATH" \
        -e PIP_CONFIG_FILE=/root/.pip/pip.conf \
        "$DOCKER_IMAGE" \
        bash -c "
            echo '📦 Installing datasets package...' &&
            pip install datasets &&
            echo '✅ Datasets package installed successfully' &&
            echo '🏃 Running perf test...' &&
            cd $CODE_PATH &&
            bash ./run_perf_test.sh \
                --ip '$HOST' \
                --port '$PORT' \
                --mode '$MODE' \
                --npu-count '$NPU_COUNT' \
                --result-dir '$RESULT_DIR' \
                --model-path '$MODEL_PATH'
        "
) &

# 获取后台进程的PID
DOCKER_PID=$!

# 等待docker进程完成
wait $DOCKER_PID
DOCKER_EXIT_CODE=$?

# 最终清理检查 - 确保没有残留容器
echo "🧹 Final cleanup check..."
remaining_containers=$(docker ps -aq --filter "name=$TASK_DIR" 2>/dev/null)
if [ ! -z "$remaining_containers" ]; then
    echo "   • Cleaning up remaining containers: $remaining_containers"
    docker stop $remaining_containers >/dev/null 2>&1
    docker rm -f $remaining_containers >/dev/null 2>&1
fi

# 重置信号处理器
trap - SIGINT SIGTERM SIGHUP SIGQUIT

if [ $DOCKER_EXIT_CODE -eq 0 ]; then
    echo -e "\n✅ Performance test completed successfully. Results saved to: $RESULT_DIR"
elif [ $DOCKER_EXIT_CODE -eq 130 ] || [ $DOCKER_EXIT_CODE -eq 143 ]; then
    echo -e "\n🛑 Performance test was interrupted by user. Results (if any) saved to: $RESULT_DIR"
else
    echo -e "\n⚠️  Performance test exited with code: $DOCKER_EXIT_CODE"
    echo "   Results (if any) saved to: $RESULT_DIR"
fi


