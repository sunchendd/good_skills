---
name: dev-workflow
description: >-
  通用开发验证工作流，用于 AI/ML 推理服务的开发、测试和验证。支持多种硬件后端（Ascend NPU、GPU）和推理引擎（vLLM、MindIE）。包含完整的需求对齐、代码检查、服务部署、性能测试和结果分析流程。当用户提到"开发"、"测试"、"性能对比"、"服务部署"、"推理验证"等需求时使用此工作流。
---

# 通用开发验证工作流

## 配置参数

在使用此工作流前，请先确认或自定义以下配置：

```yaml
# === 可配置参数 ===
config:
  # 硬件配置
  hardware:
    type: "npu"  # npu 或 gpu
    devices: "0,1"  # 设备ID列表

  # 模型配置
  model:
    main: "/data/models/Qwen3-32B"
    draft: null  # 投机解码的draft模型

  # 服务配置
  service:
    port: 8000
    tensor_parallel_size: 2
    max_num_seqs: 16
    speculative_config: null

  # 测试配置
  test:
    concurrent: 4
    input_tokens: 1024
    output_tokens: 1024
    warmup: 3
    iterations: 10
```

> **提示**: 使用时可告诉 Claude 自定义参数，如"使用端口 9000 和 GPU 0,1 启动服务"

## 作用

- 标准化 AI/ML 推理服务的开发验证流程
- 支持多种硬件后端（Ascend NPU、GPU）
- 支持多种推理引擎（vLLM、MindIE）
- 确保代码质量和 commit 规范
- 提供实验组与基线的对比测试框架

## 工作流步骤

### 1. Plan 模式 - 需求对齐

在开始开发前，执行以下流程：
- 根据用户需求主动提问，对齐目标
- 明确需求边界和预期结果
- 确认技术方案和实现路径

### 2. 代码质量检查

修改完成后执行：
- 自检代码质量（格式、逻辑、边界条件）
- 创建 commit，命名规范: `修改点+时间<YYYYMMDD>`

```bash
# 示例
git add <修改的文件>
git commit -m "feature: 添加自适应投机解码逻辑 20260120"
```

### 3. 环境准备

#### 资源检查

确认可用设备：
```bash
# NPU
python3 scripts/check_npu.py

# GPU
nvidia-smi
```

#### 环境清理

启动服务前先清理环境：
```bash
# 清理进程
./scripts/kill_server.sh

# 清理显存/NPU内存
./scripts/clear_memory.sh
```

### 4. 启动服务验证

#### 选择推理引擎

根据配置选择启动命令：

**vLLM 服务**：
```bash
export CUDA_VISIBLE_DEVICES=${config.hardware.devices}
vllm serve ${config.model.main} \
     --tp ${config.service.tensor_parallel_size} \
     --port ${config.service.port} \
     --max-num-seqs ${config.service.max_num_seqs}
```

**vLLM 投机解码服务**：
```bash
export ASCEND_RT_VISIBLE_DEVICES=${config.hardware.devices}
vllm serve ${config.model.main} \
     --tp ${config.service.tensor_parallel_size} \
     --port ${config.service.port} \
     --spectral-config '{
       "model": "${config.model.draft}",
       "num_speculative_tokens": 4,
       "method": "eagle3"
     }'
```

**MindIE 服务**：
```bash
./scripts/start_mindie.sh \
  --model ${config.model.main} \
  --port ${config.service.port} \
  --device ${config.hardware.type}
```

### 5. 健康检查

阻塞等待服务就绪：
```bash
./scripts/wait_for_service.sh \
  --port ${config.service.port} \
  --timeout 300
```

### 6. 测试验证

#### 性能测试
```bash
./scripts/run_perf_test.sh \
  --port ${config.service.port} \
  --concurrent ${config.test.concurrent} \
  --input ${config.test.input_tokens} \
  --output ${config.test.output_tokens}
```

#### 精度测试
```bash
./scripts/run_accuracy_test.sh \
  --port ${config.service.port} \
  --datasets "mmlu,cmmlu"
```

### 7. 结果分析

- 对比实验组与基线的性能指标
- 分析测试日志，验证功能是否按预期工作
- 评估性能提升效果（吞吐量、延迟等）
- 生成测试报告

## 脚本资源

| 脚本 | 路径 | 说明 |
|------|------|------|
| 资源检查 | `scripts/check_npu.py` / `scripts/check_gpu.py` | 检查可用设备 |
| 清理环境 | `scripts/kill_server.sh` | 清理所有服务进程 |
| 启动 vLLM | `scripts/start_vllm.sh` | 启动 vLLM 服务 |
| 启动 MindIE | `scripts/start_mindie.sh` | 启动 MindIE 服务 |
| 健康检查 | `scripts/wait_for_service.sh` | 等待服务就绪 |
| 性能测试 | `scripts/run_perf_test.sh` | 执行性能测试 |
| 精度测试 | `scripts/run_accuracy_test.sh` | 执行精度测试 |
| 结果分析 | `scripts/analyze_results.py` | 分析测试结果 |

## 硬件支持

### Ascend NPU

```yaml
config:
  hardware:
    type: "npu"
    devices: "14,15"
  model:
    main: "/data2/weights/Qwen_Qwen3-32B"
```

### NVIDIA GPU

```yaml
config:
  hardware:
    type: "gpu"
    devices: "0,1"
  model:
    main: "/data/models/Qwen3-32B"
```

## 典型用法举例

```
# 使用默认配置
"帮我启动 vLLM 服务并进行性能测试"

# 自定义配置
"使用端口 9000、GPU 0,1 进行对比测试"
"修改 max_num_seqs 为 32 后重新测试"
"测试 MindIE 推理性能"
```

---

## 版本

- v1.0.0 (2026-02-03): 初始发布，基于 vllm-dev-workflow 抽象
