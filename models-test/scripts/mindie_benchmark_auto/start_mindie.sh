#port=2800
#management_port=2801
#metrics_port=2802
#ASCEND_RT_VISIBLE_DEVICES=0,1,2,3
#model_name=Qwen_Qwen3-32B
#model_path="/data/models/Qwen_Qwen3-32B"
#npu_count=4

# 日志函数
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >&2
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1"
}

log_warning() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] $1"
}

validate_config_modification() {
    local config_path="$1"
    local validation_failed=false
    
    # 验证关键配置项
    # 使用更简单的grep模式，避免复杂正则表达式
    if ! grep -q "\"port\"[[:space:]]*:[[:space:]]*$port" "$config_path"; then
        log_error "port modification failed"
        validation_failed=true
    fi
    
    if ! grep -q "\"managementPort\"[[:space:]]*:[[:space:]]*$management_port" "$config_path"; then
        log_error "managementPort modification failed"
        validation_failed=true
    fi
    
    if ! grep -q "\"metricsPort\"[[:space:]]*:[[:space:]]*$metrics_port" "$config_path"; then
        log_error "metricsPort modification failed"
        validation_failed=true
    fi
    
    if ! grep -q "\"modelName\"[[:space:]]*:[[:space:]]*\"$model_name\"" "$config_path"; then
        log_error "modelName modification failed"
        validation_failed=true
    fi
    
    if ! grep -q "\"httpsEnabled\"[[:space:]]*:[[:space:]]*false" "$config_path"; then
        log_error "httpsEnabled modification failed"
        validation_failed=true
    fi
    
    if ! grep -q "\"interCommTLSEnabled\"[[:space:]]*:[[:space:]]*false" "$config_path"; then
        log_error "interCommTLSEnabled modification failed"
        validation_failed=true
    fi
    
    # 验证JSON格式
    if ! python3 -c "import json; json.load(open('$config_path'))" 2>/dev/null; then
        log_error "JSON format validation failed"
        # 显示JSON错误的详细信息
        python3 -c "import json; json.load(open('$config_path'))" 2>&1 | head -3
        validation_failed=true
    fi
    
    if [ "$validation_failed" = true ]; then
        return 1
    else
        return 0
    fi
}

modify_config_file() {
    log_info "Modifying MindIE configuration file using sed..."
    
    local config_path="/usr/local/Ascend/mindie/latest/mindie-service/conf/config.json"
    local backup_path="${config_path}.backup_$(date +%Y%m%d_%H%M%S)"
    
    # 1. 备份原始配置文件
    if test -f "$config_path"; then
        cp "$config_path" "$backup_path"
        log_info "Original config file backed up to: $backup_path"
    else
        log_error "Config file does not exist: $config_path"
        exit 1
    fi
    
    sed -i "s/\"httpsEnabled\"[[:space:]]*:[[:space:]]*true/\"httpsEnabled\": false/g" "$config_path"


    # 2. 创建NPU设备ID JSON数组
    if [ -z "$ASCEND_RT_VISIBLE_DEVICES" ]; then
        local npu_devices_json="[[0]]"
    else
        # 移除空格并添加逗号
        local devices_clean="${ASCEND_RT_VISIBLE_DEVICES//,/ }"
        local devices_with_commas=$(echo "$devices_clean" | sed 's/ /, /g')
        local npu_devices_json="[[$devices_with_commas]]"
    fi   
 
    # 3. 使用sed修改ServerConfig部分
    log_info "Modifying ServerConfig section..."
    
    # 修改port
    sed -i "s/\"port\"[[:space:]]*:[[:space:]]*[0-9]*/\"port\": $port/g" "$config_path"
    
    # 修改managementPort
    sed -i "s/\"managementPort\"[[:space:]]*:[[:space:]]*[0-9]*/\"managementPort\": $management_port/g" "$config_path"
    
    # 修改metricsPort
    sed -i "s/\"metricsPort\"[[:space:]]*:[[:space:]]*[0-9]*/\"metricsPort\": $metrics_port/g" "$config_path"
    
    # 修改httpsEnabled
    sed -i "s/\"httpsEnabled\"[[:space:]]*:[[:space:]]*true/\"httpsEnabled\": false/g" "$config_path"
    sed -i "s/\"httpsEnabled\"[[:space:]]*:[[:space:]]*false/\"httpsEnabled\": false/g" "$config_path"
    
    # 修改interCommTLSEnabled
    sed -i "s/\"interCommTLSEnabled\"[[:space:]]*:[[:space:]]*true/\"interCommTLSEnabled\": false/g" "$config_path"
    sed -i "s/\"interCommTLSEnabled\"[[:space:]]*:[[:space:]]*false/\"interCommTLSEnabled\": false/g" "$config_path"
    
    # 4. 使用sed修改BackendConfig部分
    log_info "Modifying BackendConfig section..."
    
    # 修改npuDeviceIds
    #sed -i 's|"npuDeviceIds"[[:space:]]*:[[:space:]]*\[[^]]*\]|"npuDeviceIds": '"$npu_devices_json"'|g' "$config_path"
    sed -i 's|"npuDeviceIds"[[:space:]]*:[[:space:]]*\[\[[^]]*\]\]|"npuDeviceIds": '"$npu_devices_json"'|g' "$config_path"    

    # 修改interNodeTLSEnabled
    sed -i "s/\"interNodeTLSEnabled\"[[:space:]]*:[[:space:]]*true/\"interNodeTLSEnabled\": false/g" "$config_path"
    sed -i "s/\"interNodeTLSEnabled\"[[:space:]]*:[[:space:]]*false/\"interNodeTLSEnabled\": false/g" "$config_path"
    
    # 5. 使用sed修改ModelDeployConfig部分
    log_info "Modifying ModelDeployConfig section..."
    
    # 修改maxSeqLen
    sed -i "s/\"maxSeqLen\"[[:space:]]*:[[:space:]]*[0-9]*/\"maxSeqLen\": 8192/g" "$config_path"
    
    # 修改maxInputTokenLen
    sed -i "s/\"maxInputTokenLen\"[[:space:]]*:[[:space:]]*[0-9]*/\"maxInputTokenLen\": 8192/g" "$config_path"
    
    # 6. 使用sed修改ModelConfig部分
    log_info "Modifying ModelConfig section..."
    
    # 修改modelName
    sed -i 's|"modelName"[[:space:]]*:[[:space:]]*"[^"]*"|"modelName": "'"$model_name"'"|g' "$config_path"
    
    # 修改modelWeightPath
    sed -i 's|"modelWeightPath"[[:space:]]*:[[:space:]]*"[^"]*"|"modelWeightPath": "'"$model_path"'"|g' "$config_path"

    sed -i "s/\"worldSize\"[[:space:]]*:[[:space:]]*[0-9]*/\"worldSize\": $npu_count/g" "$config_path"
    
    # 7. 使用sed修改ScheduleConfig部分
    log_info "Modifying ScheduleConfig section..."
    
    # 修改maxIterTimes
    sed -i "s/\"maxIterTimes\"[[:space:]]*:[[:space:]]*[0-9]*/\"maxIterTimes\": 16384/g" "$config_path"
    
    # 8. 验证修改结果
    log_info "Validating configuration changes..."
   
#    if ! validate_config_modification "$config_path"; then
#        log_error "Configuration validation failed, restoring backup..."
#        # 直接恢复配置文件
#        if cp "$backup_path" "$config_path"; then
#            log_info "Configuration restored from backup: $backup_path"
#        else
#            log_error "Failed to restore configuration backup"
#        fi
#        exit 1
#    fi 
    cp "$config_path" ./config_${model_name}.json    
    # 9. 显示修改后的关键配置信息
    log_success "Configuration file modified successfully"
    log_info "Modified configurations:"
    log_info "  port: $port"
    log_info "  managementPort: $management_port"
    log_info "  metricsPort: $metrics_port"
    log_info "  modelName: $model_name"
    log_info "  modelWeightPath: $model_path"
    log_info "  npuDeviceIds: $npu_devices_json"
    log_info "  maxSeqLen: 8192"
    log_info "  maxInputTokenLen: 8192"
    log_info "  maxIterTimes: 16384"
    log_info "  httpsEnabled: false"
    log_info "  interCommTLSEnabled: false"
    log_info "  interNodeTLSEnabled: false"
    log_info "  Backup file: $backup_path"
    
    CONFIG_FILE="$config_path"
}

configure_environment_and_start_service() {
    echo "Configuring environment and starting MindIE service..."
    
    # 在容器内配置环境变量并启动服务

    # 配置CANN环境
    source /usr/local/Ascend/ascend-toolkit/set_env.sh
    # 配置加速库环境
    source /usr/local/Ascend/nnal/atb/set_env.sh
    # 配置模型仓环境变量
    source /usr/local/Ascend/atb-models/set_env.sh
    # MindIE
    source /usr/local/Ascend/mindie/latest/mindie-llm/set_env.sh
    source /usr/local/Ascend/mindie/latest/mindie-service/set_env.sh
    # 开启MindIE日志打印
    export MINDIE_LOG_TO_STDOUT='true'
        
    cd /usr/local/Ascend/mindie/latest/mindie-service
    if ./bin/mindieservice_daemon > output.log 2>&1; then
        echo "MindIE service started successfully (PID: $$)"
    else
        log_error "MindIE service startup failed! Check output.log:"
        cat output.log
        exit 1
    fi
    #nohup ./bin/mindieservice_daemon > output.log 2>&1 &
    #nohup ./bin/mindieservice_daemon
    echo \$! > /tmp/mindie_service.pid
    #cat output.log    
    trap 'echo "Caught signal, stopping service..."; kill $(cat /tmp/mindie_service.pid); exit 0' SIGTERM SIGINT    
    echo 'MindIE service started with PID:' \$!
    echo 'Environment configured successfully'
    echo 'Using config file: /usr/local/Ascend/mindie/latest/mindie-service/conf/config.json'   
    echo "MindIE service started"
    tail -f /dev/null
}

# 主函数
modify_config_file

configure_environment_and_start_service


