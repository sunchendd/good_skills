#!/bin/bash

# =============================================================================
# VLLM基准测试自动化脚本 (混合并行模式)
# 
# 功能说明:
# - 支持多模型并行测试，自动分配NPU资源
# - 推理服务容器化部署，独立端口管理
# - 测试完成后自动清理资源，释放NPU供后续任务使用
# - 完整的错误处理和日志记录
#
# 作者: AI Assistant
# 版本: v2.0
# 更新: 2025-01-20
# =============================================================================

# ======================== 配置常量 ========================
DEFAULT_HOST="127.0.0.1"
DEFAULT_PORT_RANGE_START="2800"
DEFAULT_PORT_RANGE_END="2899"
DEFAULT_TEMPERATURE="0.65"
DEFAULT_REQUEST_RATE="0"
DEFAULT_DOCKER_TAG="v0.12.0rc1"  # 根据测试的VLLM版本配置
DEFAULT_DIR=$(pwd)
echo "DEFAULT_DIR=${DEFAULT_DIR}"
# ======================== 全局变量 ========================
BASE_MODEL_PATH=""          # 模型文件基础路径
RESULT_DIR=""               # 测试结果输出目录
DOCKER_TAG=""               # Docker镜像标签
DEBUG_MODE=false            # 调试模式开关
SINGLE_MODE=""              # 单模型测试开关
SINGLE_NPU_COUNT=""         # 单模型测试NPU卡数
SINGLE_MODE=""              # 单模型测试模式
SINGLE_DATASETS=""          # 单模型测试数据集

# ======================== 测试配置矩阵 ========================
# 格式: "模型名称:NPU卡数:模式"
# 说明:
# - 1卡模型: 小型模型，快速测试
# - 2卡模型: 中型模型，平衡性能
# - 4卡模型: 大型模型，高性能需求
# - 8卡模型: 超大型模型，最高性能
# 模式: eager, aclgraph, torchair
declare -a TEST_CONFIGS=(
    "Qwen3-0.6B:1:aclgraph:mmlu"
    "Qwen3-0.6B-FP8:1:aclgraph:mmlu"
    "Qwen3-32B-NVFP4:1:eager:mmlu_pro"
    "Qwen3-32B-FP8:1:aclgraph:mmlu"
    "Qwen3-14B-FP8:1:aclgraph:mmlu"
    "Qwen3-8B-FP8:1:aclgraph:mmlu"
    "Qwen3-4B-FP8:1:aclgraph:mmlu"
    "Qwen3-1.7B-FP8:1:aclgraph:mmlu"
    "Qwen3-1.7B-FP8:1:aclgraph"
    "Qwen3-0.6B-FP8:1:aclgraph:mmlu"
    "Qwen3-32B-FP8:1:aclgraph:cmmlu"
    "Qwen3-30B-A3B-FP8:1:aclgraph:cmmlu"
    "Qwen3-8B-FP8:1:aclgraph:cmmlu"
    "Qwen3-4B-FP8:1:aclgraph:cmmlu"
    "Qwen3-1.7B-FP8:1:aclgraph:cmmlu"
    "Qwen3-0.6B-FP8:1:aclgraph:cmmlu"
    "Qwen3-32B:1:aclgraph"
    "Qwen3-14B:1:aclgraph"
    "Qwen3-8B:1:aclgraph"
    "Qwen3-4B:1:aclgraph"
    "Qwen3-1.7B:1:aclgraph"
    "Qwen3-30B-A3B-FP8:1:eager"
	"Qwen3-32B-FP8:1:eager"
    "Qwen3-14B-FP8:1:eager"
    "Qwen3-8B-FP8:1:eager"
    "Qwen3-4B-FP8:1:eager"
    "Qwen3-1.7B-FP8:1:eager"
    "Qwen3-0.6B-FP8:1:eager"
	"Qwen3-32B:1:eager"
    "Qwen3-14B:1:eager"
    "Qwen3-8B:1:eager"
    "Qwen3-4B:1:eager"
    "Qwen3-1.7B:1:eager"
    "Qwen3-0.6B:1:eager"
	"DeepSeek-V3-0324:16:torchair"
)

# ======================== 运行时状态管理 ========================
declare -a AVAILABLE_NPUS=()       # 系统中所有可用的NPU设备ID
declare -a RUNNING_BENCHMARKS=()   # 运行中的测试任务: "pid:model_name:container_name:port:allocated_npus"
declare -a ALLOCATED_PORTS=()      # 已分配的端口列表，避免冲突

# ======================== 清理和退出处理 ========================
# 脚本退出时的资源清理函数
# 功能: 
# - 终止所有运行中的测试进程
# - 清理所有VLLM容器
# - 删除临时文件
# - 重置全局状态
cleanup_on_exit() {
    local exit_code=$?
    log "warning" "收到退出信号，开始清理资源..."
    
    # 终止所有运行中的精度测试进程
    if [ ${#RUNNING_BENCHMARKS[@]} -gt 0 ]; then
        log "info" "终止运行中的性能测试进程..."
        for benchmark_info in "${RUNNING_BENCHMARKS[@]}"; do
            IFS=':' read -r pid model_name container_name port allocated_npus <<< "$benchmark_info"
            if kill -0 "$pid" 2>/dev/null; then
                log "debug" "终止性能测试进程: $model_name (PID: $pid)"
                # 优雅终止，然后强制终止
                kill -TERM "$pid" 2>/dev/null || true
                sleep 2
                if kill -0 "$pid" 2>/dev/null; then
                    kill -KILL "$pid" 2>/dev/null || true
                fi
            fi
        done
    fi
    
    # 清理所有VLLM容器
    log "info" "清理VLLM容器..."
    local containers=$(docker ps -aq --filter "name=vllm_accuracy_" 2>/dev/null || true)
    if [ -n "$containers" ]; then
        docker rm -f $containers > /dev/null 2>&1 &
    fi
    
    # 清理临时文件
    rm -f /tmp/test_result_*.tmp 2>/dev/null || true
    rm -f /tmp/benchmark_*.log 2>/dev/null || true
    
    # 重置全局状态
    RUNNING_BENCHMARKS=()
    ALLOCATED_PORTS=()

    log "success" "资源清理完成"

    if [ $exit_code -ne 0 ]; then
        log "error" "脚本异常退出 (退出码: $exit_code)"
    fi

    exit $exit_code
}
# 注册信号处理器
trap cleanup_on_exit SIGINT SIGTERM EXIT

# ======================== 工具函数 ========================
# 生成模型名称的标准化标识符
# 用途: 生成安全的文件名和容器名
# 参数: $1 - 模型名称
# 返回: 小写字母和数字组成的标识符
get_model_identifier() {
    local model_name="$1"
    echo "$model_name" | tr '[:upper:]' '[:lower:]' | tr -d '.-'
}

# 显示帮助信息
show_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -b, --base-model-path <path>  Base path where all models are stored (required)"
    echo "  -r, --result-dir <dir>        Results directory (required)"
    echo "  -t, --temperature <temp>      Temperature setting (default: $DEFAULT_TEMPERATURE)"
    echo "  -R, --request-rate <rate>     Request rate (default: $DEFAULT_REQUEST_RATE)"
    echo "  -d, --docker-tag <version>    VLLM version (default: $DEFAULT_DOCKER_TAG)"
    echo "  -m, --model <name>            Sigle Model name (default: $SIGLE_MODEL_NAME)"
    echo "  -n, --npu-count <num>         Npu count for single model test (default: $DEFAULT_NUM_WORKERS)"
    echo "  --mode <mode>                 Exectution mode: eager, aclgraph, xlite (default: aclgraph)"
    echo "  --datasets <datasets>         Datasets for single model test (default: mmlu)"
    echo "  --debug                       Enable debug mode"
    echo "  -h, --help                    Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 -b /path/to/models -r /path/to/results"
    echo ""
    echo "注意: 使用 Ctrl+C 中断脚本时会自动清理所有容器和进程"
    exit 1
}

# ======================== 日志系统 ========================

# 统一日志输出函数
# 参数: 
#   $1 - 日志级别 (info|success|warning|error|debug)
#   $2 - 日志消息
#   $3 - 任务前缀 (可选)
log() {
    local level="$1"
    local message="$2"
    local task_prefix=""
    if [ -n "$3" ]; then
        task_prefix="[$3] "
    fi

    case "$level" in
        info)
            echo -e "🔷 ${task_prefix}$message"
            ;;
        success)
            echo -e "✅ ${task_prefix}$message"
            ;;
        warning)
            echo -e "⚠️  ${task_prefix}$message"
            ;;
        error)
            echo -e "❌ ${task_prefix}$message" >&2
            ;;
        debug)
            if [ "$DEBUG_MODE" = true ]; then
                echo -e "🔍 DEBUG: ${task_prefix}$message" >&2
            fi
            ;;
        *)
            echo -e "${task_prefix}$message"
            ;;
    esac
}

# ======================== 容器管理 ========================

# 清理指定的Docker容器
# 参数: $1 - 容器名称
# 功能: 安全删除Docker容器，包含完整的错误处理和状态检查
# 设计: 强制删除模式，确保资源得到彻底清理
cleanup_container() {
    local container_name="$1"
    
    if [ -z "$container_name" ]; then
        log "warning" "容器名称为空，跳过清理操作"
        return 0
    fi
    
    # 去除可能的换行符和空格，但保留原始容器名称
    container_name=$(echo "$container_name" | tr -d '\n' | tr -s ' ')
    
    # 验证容器名称格式：应该以vllm_开头
    if [[ ! "$container_name" =~ ^vllm_accuracy_[a-z0-9_]+$ ]]; then
        log "warning" "容器名称格式无效: $container_name"
        return 0
    fi
    
    log "debug" "尝试清理容器: $container_name"
    
    # 检查容器是否存在
    if docker ps -a --format "{{.Names}}" | grep -qx "$container_name"; then
        log "debug" "正在删除容器: $container_name"
        # 使用强制删除模式（-f参数）同时停止和删除容器
        if docker rm -f "$container_name" >/dev/null 2>&1; then
            log "debug" "容器删除成功: $container_name"
            return 0
        else
            log "warning" "容器删除失败: $container_name"
            return 1
        fi
    else
        log "debug" "容器不存在或已删除: $container_name"
        return 0
    fi
}

# ======================== NPU资源管理 ========================
# 获取当前可用的NPU列表（实时检查）
# 原理: 通过npu-smi检查哪些NPU没有运行进程
# 返回: 可用NPU ID列表（空格分隔）
get_current_available_npus_old() {
    local available_npus=$(npu-smi info 2>/dev/null | grep "No running processes found in NPU" | grep -o "NPU [0-9]*" | grep -o "[0-9]*" | tr '\n' ' ')
    echo "$available_npus"
}

get_current_available_npus() {
    local available_npus=$(npu-smi info 2>/dev/null | grep "No running processes found in NPU" | grep -o "NPU [0-9]*" | grep -o "[0-9]*" | tr '\n' ' ')
    local filtered_npus=""
    for npu_id in $available_npus; do
        if [ "$npu_id" -ge 10 ] && [ "$npu_id" -le 15 ]; then
            filtered_npus="$filtered_npus $npu_id "
        fi
    done
    echo "$filtered_npus"
}


# 等待并获取足够的NPU资源
# 参数: 
#   $1 - 需要的NPU数量
#   $2 - 模型名称（用于日志）
# 返回: 分配的NPU ID列表（逗号分隔）
wait_for_available_npus() {
    local required_count="$1"
    local model_name="$2"
    local max_wait_minutes=300  # 最大等待5小时
    local wait_minutes=0

    while true; do
        local available_npus_str=$(get_current_available_npus)
        [ $? -eq 0 ] || return 1
        
        read -ra available_npus <<< "$available_npus_str"
        if [ ${#available_npus[@]} -ge $required_count ]; then
            # 选择前N个可用的NPU
            local selected_npus=("${available_npus[@]:0:$required_count}")
            local npu_list=$(IFS=,; echo "${selected_npus[*]}")
            echo "$npu_list"
            return 0
        fi
        
        # 检查超时
        [ $wait_minutes -le $max_wait_minutes ] || return 1
        ((wait_minutes++))
        sleep 60  # 每分钟检查一次
    done
}

# 检查推理服务是否就绪
# 参数:
#   $1 - 主机地址
#   $2 - 端口号
#   $3 - 模型名称（用于日志标识）
# 功能: 通过HTTP健康检查确认VLLM服务完全就绪
# 返回: 0表示服务就绪，1表示超时失败
wait_for_service_ready() {
    local host="$1"
    local port="$2"
    local model_name="$3"
    local max_wait_seconds=600  # 最大等待10分钟
    local wait_time=0
    local check_interval=10     # 每10秒检查一次
    
    log "info" "正在等待推理服务启动 (最大等待: ${max_wait_seconds}s)" "$model_name"
    
    while [ $wait_time -lt $max_wait_seconds ]; do
        # 检查models端点的响应状态码
        models_response=$(curl -s -w "%{http_code}" -o /dev/null --max-time 10 "http://$host:$port/v1/models" 2>/dev/null)
        if [ "$models_response" = "200" ]; then
            log "success" "推理服务已就绪 (耗时: ${wait_time}秒)" "$model_name"
            return 0
        fi
        
        sleep $check_interval
        wait_time=$((wait_time + check_interval))
    done
    
    log "error" "推理服务启动超时 (等待时间: ${max_wait_seconds}s)" "$model_name"
    return 1
}

# ======================== NPU 设备管理 ========================

# 初始化NPU设备列表
# 功能: 扫描系统中所有可用的Ascend 910B3 NPU设备
# 设计: 使用npu-smi工具获取设备状态，只选择健康可用的设备
# 返回: 0表示成功检测到设备，1表示无可用设备
init_npu_devices() {
    local npu_info
    npu_info=$(npu-smi info 2>/dev/null) || {
        log "error" "无法获取NPU设备信息，请检查驱动安装"
        return 1
    }

    AVAILABLE_NPUS=()
    # 解析npu-smi输出，提取状态为OK的910B3设备ID
    # 输出格式示例: |  0    910B3     |   OK     |
    while IFS= read -r line; do
        if [[ $line =~ ^\|[[:space:]]*([0-9]+)[[:space:]]+910B2C[[:space:]]*\|[[:space:]]*OK ]]; then
            AVAILABLE_NPUS+=("${BASH_REMATCH[1]}")
        fi
    done <<< "$npu_info"
    
    if [ ${#AVAILABLE_NPUS[@]} -eq 0 ]; then
        log "error" "未检测到可用的910B3 NPU设备"
        return 1
    fi
    
    log "info" "检测到NPU设备: ${AVAILABLE_NPUS[*]} (共 ${#AVAILABLE_NPUS[@]} 张)"
    return 0
}

# ======================== 端口管理 ========================
# 获取可用端口
# 功能: 在指定端口范围内查找未被占用的端口
# 机制: 双重检查netstat和ss命令，避免内部端口冲突
# 返回: 输出可用端口号，成功返回0，失败返回1
get_available_port() {
    local port
    for ((port=DEFAULT_PORT_RANGE_START; port<=DEFAULT_PORT_RANGE_END; port++)); do
        # 检查端口是否被系统占用或内部分配
        if ! netstat -tuln 2>/dev/null | grep -q ":$port " && \
           ! ss -tuln 2>/dev/null | grep -q ":$port " && \
           [[ ! " ${ALLOCATED_PORTS[*]} " =~ " $port " ]]; then
            # 记录分配的端口，避免重复分配
            ALLOCATED_PORTS+=("$port")
            echo "$port"
            return 0
        fi
    done
    
    log "error" "无可用端口 (范围: $DEFAULT_PORT_RANGE_START-$DEFAULT_PORT_RANGE_END)"
    return 1
}
# 释放已分配的端口
# 参数: $1 - 要释放的端口号
# 功能: 从内部端口分配列表中移除指定端口，释放资源供后续使用
release_port() {
    local port="$1"
    local new_allocated_ports=()
    
    # 重建分配列表，排除要释放的端口
    for allocated_port in "${ALLOCATED_PORTS[@]}"; do
        if [ "$allocated_port" != "$port" ]; then
            new_allocated_ports+=("$allocated_port")
        fi
    done
    
    ALLOCATED_PORTS=("${new_allocated_ports[@]}")
    log "debug" "已释放端口: $port"
}

# ======================== 推理服务管理 ========================

# 启动推理服务容器
# 参数:
#   $1 - 模型名称
#   $2 - NPU数量
#   $3 - 分配的NPU ID列表（逗号分隔）
#   $4 - 服务端口
# 返回: 容器名称（成功时）
start_inference_service() {
    local model_name="$1"
    local npu_count="$2"
    local allocated_npus="$3"
    local port="$4"
    local mode="$5"
    local datasets="$6"
    
    local model_path="$BASE_MODEL_PATH/$model_name"
    # 生成安全的容器名称（避免特殊字符冲突）
    local safe_model_name=$(echo "$model_name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g')
    local container_name="vllm_accuracy_${safe_model_name}_$(date +%s)"
    # 根据架构选择正确的Docker镜像
    local docker_image="quay.io/ascend/vllm-ascend:$DOCKER_TAG"
    local log_file="$RESULT_LOG_DIR/${ARCH}_start_vllm_acc_${model_name}_$(date +%s)_${npu_count}_npu_${mode}_${datasets}.log"

    log "debug" "容器: $container_name | NPU: $allocated_npus | 端口: $port" "$model_name"

    # 构建Docker运行命令
    local container_id=$(docker run -itd --privileged --net=host --name $container_name \
        --device /dev/davinci_manager \
        --device /dev/devmm_svm \
        --device /dev/hisi_hdc \
        -v /usr/local/dcmi:/usr/local/dcmi \
        -v /usr/local/bin/npu-smi:/usr/local/bin/npu-smi \
        -v /usr/local/Ascend/driver/lib64/:/usr/local/Ascend/driver/lib64/ \
        -v /usr/local/Ascend/driver:/usr/local/Ascend/driver \
        -v /etc/ascend_install.info:/etc/ascend_install.info \
        -v /root/.cache:/root/.cache \
        -v /root/.pip:/root/.pip \
        -v $model_path:$model_path \
        -v /workspace:/workspace \
        -v /home:/home \
        -v /data:/data \
	    -v /data2:/data2 \
        -v /nfs:/nfs \
        -e PIP_CONFIG_FILE=/root/.pip/pip.conf \
        -e VLLM_USE_V1=1 \
        -e ASCEND_RT_VISIBLE_DEVICES=$allocated_npus \
	    -e code_path=$DEFAULT_DIR \
        -e model_path=$model_path  \
        -e model_name=$model_name \
        -e npu_count=$npu_count \
        -e port=$port \
        -e mode=$mode \
        -e result_dir=$RESULT_DIR \
        $docker_image \
        bash -c "bash $DEFAULT_DIR/start_vllm_sever.sh 2>&1 | tee -a $log_file")

    # 启动容器
    if [ $? -eq 0 ] && [ -n "$container_id" ]; then
        # 等待服务就绪（日志输出到stderr，避免影响返回值）
        if wait_for_service_ready "$DEFAULT_HOST" "$port" "$model_name" >&2; then
            log "success" "推理服务启动成功 (容器: $container_name)" "$model_name" >&2
            echo "$container_name"  # 只输出容器名称到stdout
            return 0
        else
            log "error" "服务就绪检查失败，清理容器: $container_name" "$model_name" >&2
            cleanup_container "$container_name"
            return 1
        fi
    else
        log "error" "容器启动失败: $container_id" "$model_name" >&2
        # 尝试清理可能残留的容器
        cleanup_container "$container_name"
        return 1
    fi
}

# ======================== 精度测试管理 ========================

# 异步启动精度测试
# 参数:
#   $1 - 模型名称
#   $2 - 服务端口
#   $3 - 容器名称
#   $4 - 分配的NPU列表
# 功能: 在后台启动VLLM精度测试，测试完成后立即清理推理服务容器
# 设计: 使用子进程避免阻塞主流程，实现真正的并行测试
run_accuracy_async() {
    local model_name="$1"
    local port="$2"
    local container_name="$3"
    local allocated_npus="$4"
    local mode="$5"
    local npu_count="$6"
    local datasets="$7"
    local model_path="$BASE_MODEL_PATH/$model_name"
    local benchmark_script="./run_accuracy_test.sh"
    
    # 验证测试脚本存在性s
    if [ ! -f "$benchmark_script" ]; then
        log "error" "基准测试脚本不存在: $benchmark_script" "$model_name"
        return 1
    fi
    
    # 在子进程中执行测试（并行执行）
    (
        local log_file="$RESULT_LOG_DIR/${ARCH}_accuracy_${model_name}_$(date +%s)_${npu_count}_npu_${mode}_${datasets}.log"
        log "debug" "测试日志保存到: $log_file" "$model_name"
        echo "Result_dir:$RESULT_DIR"
        # 执行精度测试脚本
        bash "$benchmark_script" \
            --ip "$DEFAULT_HOST" \
            --port "$port" \
            --model-path "$model_path" \
            --result-dir "$RESULT_DIR" \
            --temperature "$TEMPERATURE" \
            --mode "$mode" \
            --npu-count "$npu_count" \
            --datasets "$datasets" \
            --request-rate "$REQUEST_RATE" 2>&1 > "$log_file"
        local test_result=${PIPESTATUS[0]}
        # 测试完成后立即清理推理服务容器
        log "info" "测试完成，清理推理服务容器: $container_name" "$model_name"
        cleanup_container "$container_name"
        # 记录测试结果到临时文件
        local result_file="/tmp/test_result_$(get_model_identifier "$model_name").tmp"
        log "debug" "测试脚本执行完成，返回码: $test_result,日志: $log_file" "$model_name"
        if [ $test_result -eq 0 ]; then
            echo "SUCCESS:$model_name:$log_file" > "$result_file"
        else
            echo "FAILED:$model_name:$log_file" > "$result_file"
        fi
    ) &
    
    # 记录后台进程信息，用于后续监控
    local pid=$!
    RUNNING_BENCHMARKS+=("$pid:$model_name:$container_name:$port:$allocated_npus")
    log "success" "精度测试已启动 (PID: $pid)" "$model_name"
    return 0
}

# 检查并处理完成的精度测试
# 功能: 监控后台测试进程状态，处理测试结果，释放相关资源
# 设计: 定期调用检查进程状态，解析测试结果文件，维护成功/失败统计
check_completed_accuracys() {
    local new_running_benchmarks=()
    
    # 遍历所有运行中的测试进程
    for benchmark_info in "${RUNNING_BENCHMARKS[@]}"; do
        IFS=':' read -r pid model_name container_name port _ <<< "$benchmark_info"
        
        # 检查进程是否仍在运行
        if kill -0 "$pid" 2>/dev/null; then
            # 进程仍在运行，保留在监控列表中
            new_running_benchmarks+=("$benchmark_info")
        else
            # 进程已完成，检查测试结果
            local result_file="/tmp/test_result_$(get_model_identifier "$model_name").tmp"
            if [ -f "$result_file" ]; then
                local result=$(cat "$result_file" 2>/dev/null)
                rm -f "$result_file"  # 清理临时结果文件
                
                # 解析结果格式: SUCCESS/FAILED:model_name:log_file
                IFS=':' read -r status result_model log_file <<< "$result"
                
                if [[ "$status" == "SUCCESS" ]]; then
                    log "success" "测试完成，日志: $log_file" "$model_name"
                    successful_tests+=("$model_name")
                else
                    log "error" "测试失败，查看日志: $log_file" "$model_name"
                    failed_tests+=("$model_name")
                fi
            else
                log "error" "测试异常退出 (无结果文件)" "$model_name"
                failed_tests+=("$model_name")
            fi
            
            # 释放端口资源（容器已在测试完成时清理）
            release_port "$port"
        fi
    done
    
    # 更新运行中的测试列表
    RUNNING_BENCHMARKS=("${new_running_benchmarks[@]}")
}

# ======================== 命令行参数处理 ========================

# 解析命令行参数
# 支持的参数：
#   -b, --base-model-path: 模型基础路径
#   -r, --result-dir: 测试结果保存目录
#   -t, --temperature: 生成温度参数
#   -R, --request-rate: 请求速率
#   -d, --docker-tag: Docker镜像标签
#   --debug: 启用调试模式
#   -h, --help: 显示帮助信息
while [[ $# -gt 0 ]]; do
    case "$1" in
        -b|--base-model-path)
            [ -z "$2" ] && { echo "ERROR: --base-model-path requires a value" >&2; show_help; }
            BASE_MODEL_PATH="$2"
            shift 2
            ;;
        -r|--result-dir)
            [ -z "$2" ] && { echo "ERROR: --result-dir requires a value" >&2; show_help; }
            # 规范化路径处理，确保绝对路径
            RESULT_DIR="$(cd "$(dirname "$2")" 2>/dev/null && cd "$(basename "$2")" 2>/dev/null && pwd || realpath "$2" 2>/dev/null || echo "$2")"
            shift 2
            ;;
        -t|--temperature)
            [ -z "$2" ] && { echo "ERROR: --temperature requires a value" >&2; show_help; }
            TEMPERATURE="$2"
            shift 2
            ;;
        -R|--request-rate)
            [ -z "$2" ] && { echo "ERROR: --request-rate requires a value" >&2; show_help; }
            REQUEST_RATE="$2"
            shift 2
            ;;
        -d|--docker-tag)
            [ -z "$2" ] && { echo "ERROR: --docker-tag requires a value" >&2; show_help; }
            DOCKER_TAG="$2"
            shift 2
            ;;
        -e|--executable-module)
            EXECUTABLE_MODULE="$2"
            shift 2
            ;;
        -m|--model)
            [ -z "$2" ] && { echo "ERROR: --model requires a value" >&2; show_help; }
            SINGLE_MODEL=("$2")
            shift 2
            ;;
        -n|--npu-count)
            [ -z "$2" ] && { echo "ERROR: --npu-count requires a value" >&2; show_help; }
            SINGLE_NPU_COUNT="$2"
            shift 2
            ;;
        --mode)
            [ -z "$2" ] && { echo "ERROR: --mode requires a value" >&2; show_help; }
            SINGLE_MODE="$2"
            shift 2
            ;;
        --datasets)
            [ -z "$2" ] && { echo "ERROR: --datasets requires a value" >&2; show_help; }
            SINGLE_DATASETS="$2"
            shift 2
            ;;
        --debug)
            DEBUG_MODE=true
            log "debug" "调试模式已启用"
            shift
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
# ======================== 参数验证和环境初始化 ========================

# 验证必需参数
if [ -z "$BASE_MODEL_PATH" ]; then
    echo "ERROR: 模型基础路径为必需参数。请使用 -b 或 --base-model-path" >&2
    show_help
fi

# 验证模型路径可访问性
if [ ! -e "$BASE_MODEL_PATH" ] || [ ! -r "$BASE_MODEL_PATH" ]; then
    log "error" "模型基础路径不存在或不可读: $BASE_MODEL_PATH"
    if [ -L "$BASE_MODEL_PATH" ]; then
        log "debug" "检测到符号链接，目标路径: $(readlink -f "$BASE_MODEL_PATH" 2>/dev/null || echo "无法解析")"
    fi
    exit 1
fi

# 验证结果目录参数
if [ -z "$RESULT_DIR" ]; then
    echo "ERROR: 结果保存目录为必需参数。请使用 -r 或 --result-dir" >&2
    show_help
fi

# 创建当前VLLM版本的子目录
RESULT_DIR="$RESULT_DIR/vllm_acc_$DOCKER_TAG"
if ! mkdir -p "$RESULT_DIR" 2>/dev/null; then
    log "error" "无法创建VLLM版本目录: '$RESULT_DIR'"
    exit 1
fi

# 创建log目录
RESULT_LOG_DIR="$RESULT_DIR/log"
if ! mkdir -p "$RESULT_LOG_DIR" 2>/dev/null; then
    log "error" "无法创建log目录: '$RESULT_LOG_DIR'"
    exit 1
fi

# 设置默认参数值
TEMPERATURE="${TEMPERATURE:-$DEFAULT_TEMPERATURE}"
REQUEST_RATE="${REQUEST_RATE:-$DEFAULT_REQUEST_RATE}"
DOCKER_TAG="${DOCKER_TAG:-$DEFAULT_DOCKER_TAG}"

# 获取当前架构
ARCH=$(uname -m)

log "info" "配置参数 - 模型路径: $BASE_MODEL_PATH"
log "info" "配置参数 - 结果目录: $RESULT_DIR"
log "info" "配置参数 - 温度: $TEMPERATURE, 请求速率: $REQUEST_RATE"
log "info" "配置参数 - Docker标签: $DOCKER_TAG"

# 清理可能残留的VLLM容器和临时文件
log "info" "清理可能残留的VLLM容器和临时文件..."
old_containers=$(docker ps -aq --filter "name=vllm_accuracy" 2>/dev/null || true)
if [ -n "$old_containers" ]; then
    log "info" "发现残留的VLLM容器，正在清理..."
    docker rm -f $old_containers > /dev/null 2>&1 
    sleep 2
fi

# 清理临时文件
rm -f /tmp/test_result_*.tmp 2>/dev/null || true
rm -f /tmp/benchmark_*.log 2>/dev/null || true

# 初始化NPU设备列表
if ! init_npu_devices; then
    log "error" "无法初始化NPU设备列表，请检查Ascend驱动安装"
    exit 1
fi

# ======================== 主执行逻辑 ========================

# 混合并行执行模式：
# - 推理服务顺序启动，确保稳定性
# - 精度测试并行执行，提高效率
# - 资源动态分配，优化利用率

# 初始化测试结果统计
declare -a successful_tests=()  # 成功的测试
declare -a failed_tests=()     # 失败的测试  
declare -a skipped_tests=()    # 跳过的测试

#单模型测试模式
if [ -n "$SINGLE_MODEL" ]; then
    log "info" "🚀 开始单模型基准测试"
    log "info" "模型路径: $BASE_MODEL_PATH | 结果目录: $RESULT_DIR"
    log "info" "测试模型: ${SINGLE_MODEL} | NPU: ${SINGLE_NPU_COUNT} 张 | 模式: ${SINGLE_MODE}"
    TEST_CONFIGS=("$SINGLE_MODEL:$SINGLE_NPU_COUNT:$SINGLE_MODE:$SINGLE_DATASETS")
else
    log "info" "🚀 开始自动化VLLM基准测试 (混合并行模式)"
    log "info" "模型路径: $BASE_MODEL_PATH | 结果目录: $RESULT_DIR"
    log "info" "测试模型数: ${#TEST_CONFIGS[@]} | NPU总计: ${#AVAILABLE_NPUS[@]} 张"
fi

# 遍历所有测试配置
for config in "${TEST_CONFIGS[@]}"; do
    # 解析配置，支持可选的mode参数
    IFS=':' read -r model_name npu_count mode datasets<<< "$config"
    # 如果没有指定mode，则默认为eager
    mode="${mode:-eager}"
    log "info" "处理测试配置: $model_name (需要 $npu_count 卡, 模式: $mode, 数据集：$datasets)" "$model_name"

    # 显示当前NPU状态信息
    read -ra current_available_npus <<< "$(get_current_available_npus)"
    log "info" "NPU状态: 总计${#AVAILABLE_NPUS[@]}张 | 可用${#current_available_npus[@]}张 | 占用$((${#AVAILABLE_NPUS[@]} - ${#current_available_npus[@]}))张 | 需要${npu_count}张" "$model_name"
    
    # 验证模型路径存在性（支持软连接）
    model_path="$BASE_MODEL_PATH/$model_name"
    if [ ! -e "$model_path" ] || [ ! -r "$model_path" ]; then
        log "warning" "跳过测试: $model_name (模型路径不存在或不可读: $model_path)" "$model_name"
        if [ -L "$model_path" ]; then
            log "debug" "检测到软连接，目标路径: $(readlink -f "$model_path" 2>/dev/null || echo "无法解析")" "$model_name"
        fi
        skipped_tests+=("$model_name:模型路径不存在或不可读")
        continue
    fi
    
    # 验证NPU资源充足性
    if [ $npu_count -gt ${#AVAILABLE_NPUS[@]} ]; then
        log "warning" "跳过测试: $model_name (需要 $npu_count 卡，系统总共只有 ${#AVAILABLE_NPUS[@]} 卡)" "$model_name"
        skipped_tests+=("$model_name:需要${npu_count}卡, 系统总共只有${#AVAILABLE_NPUS[@]}卡")
        continue
    fi
    
    # 等待NPU资源分配
    log "info" "等待NPU资源分配 (需要 $npu_count 卡)..." "$model_name"
    allocated_npus=$(wait_for_available_npus "$npu_count" "$model_name")
    if [ $? -ne 0 ] || [ -z "$allocated_npus" ]; then
        log "warning" "跳过测试: $model_name (等待NPU资源超时，当前NPU被占用)" "$model_name"
        skipped_tests+=("$model_name:等待NPU资源超时")
        continue
    fi
    
    # 分配可用端口
    port=$(get_available_port)
    if [ $? -ne 0 ] || [ -z "$port" ]; then
        log "error" "无法分配可用端口" "$model_name"
        skipped_tests+=("$model_name:端口分配失败")
        continue
    fi
    
    # 启动推理服务（顺序启动，确保稳定性）
    log "info" "启动推理服务 (端口: $port, NPU: $allocated_npus)..." "$model_name"
    container_name=$(start_inference_service "$model_name" "$npu_count" "$allocated_npus" "$port" "$mode" "$datasets")
    
    if [ $? -eq 0 ] && [ -n "$container_name" ]; then
        # 启动精度测试（并行执行，提高效率）
        log "info" "启动精度测试..." "$model_name"
        run_accuracy_async "$model_name" "$port" "$container_name" "$allocated_npus" "$mode" "$npu_count" "$datasets"
    else
        log "error" "推理服务启动失败" "$model_name"
        release_port "$port"
        failed_tests+=("$model_name:推理服务启动失败")
    fi
done

# ======================== 等待测试完成 ========================

# 监控所有运行中的精度测试，直至全部完成
log "info" "⏳ 等待所有精度测试完成..."
while [ ${#RUNNING_BENCHMARKS[@]} -gt 0 ]; do
    check_completed_accuracys
    
    # 如果还有测试在运行，等待一段时间后再次检查
    if [ ${#RUNNING_BENCHMARKS[@]} -gt 0 ]; then
        log "debug" "当前运行中的测试: ${#RUNNING_BENCHMARKS[@]} 个"
        sleep 10
    fi
done

# ======================== 测试结果汇总 ========================

log "info" "📊 测试完成: 成功 ${#successful_tests[@]} | 失败 ${#failed_tests[@]} | 跳过 ${#skipped_tests[@]} (共 ${#TEST_CONFIGS[@]} 个)"

# 输出成功的测试详情
if [ ${#successful_tests[@]} -gt 0 ]; then
    log "success" "✅ 成功的测试:"
    for test in "${successful_tests[@]}"; do
        log "success" "  • $test"
    done
fi
# 输出失败的测试详情
if [ ${#failed_tests[@]} -gt 0 ]; then
    log "error" "❌ 失败的测试:"
    for test in "${failed_tests[@]}"; do
        log "error" "  • $test"
    done
fi

# 输出跳过的测试详情
if [ ${#skipped_tests[@]} -gt 0 ]; then
    log "warning" "⚠️  跳过的测试:"
    for test in "${skipped_tests[@]}"; do
        IFS=':' read -r model_name reason <<< "$test"
        log "warning" "  • $model_name ($reason)"
    done
fi

# 最终状态汇总
log "info" "🎯 测试会话完成"
log "info" "结果保存到: $RESULT_DIR"

# 显示测试日志文件位置
local log_files=($(ls /tmp/benchmark_*.log 2>/dev/null || true))
if [ ${#log_files[@]} -gt 0 ]; then
    log "info" "📋 测试日志文件:"
    for log_file in "${log_files[@]}"; do
        local file_size=$(du -h "$log_file" 2>/dev/null | cut -f1)
        log "info" "  • $log_file ($file_size)"
    done
fi

# 根据测试结果设置退出码
if [ ${#failed_tests[@]} -gt 0 ]; then
    log "warning" "存在测试失败，请检查相关日志"
    exit 1
else
    log "success" "所有可执行的测试均已成功完成"
    exit 0
fi

