---
name: vllm-dev-workflow
description: >-
  vLLM 开发验证工作流，用于在 Ascend NPU 环境下进行 vLLM 推理服务的开发、测试和验证。
  适用于自适应投机解码、EARS、Eagle 等特性的开发调试，包含完整的需求对齐、代码检查、
  服务启动、性能测试和对比分析流程。当用户提到"vllm开发"、"投机解码测试"、"性能对比"、
  "启动服务验证"等需求时使用此工作流。
---

# vLLM 开发验证工作流

## 配置参数

在使用此工作流前，请先确认或自定义以下配置：

```yaml
# === 可配置参数 ===
config:
  # 实验组配置
  adaptive:
    port: 10000
    npu_devices: "14,15"
    enable_adaptive: true
  
  # 对照组配置
  baseline:
    port: 10001
    npu_devices: "12,13"
    enable_adaptive: false
  
  # 模型路径
  model:
    main: "/data2/weights/Qwen_Qwen3-32B"
    draft: "/data2/weights/scd/RedHatAI/Qwen3-32B-speculator.eagle3"
  
  # 服务参数
  service:
    tensor_parallel_size: 2
    max_num_seqs: 16
    num_speculative_tokens: 4
    method: "eagle3"
    draft_tensor_parallel_size: 1
```

> **提示**: 使用时可告诉 Claude 自定义参数，如"使用端口 9000 和 NPU 0,1 启动服务"

## 作用
- 标准化 vLLM 相关特性的开发验证流程
- 确保代码质量和 commit 规范
- 提供自适应投机解码与基线的对比测试框架
- 支持 Ascend NPU 环境下的服务部署和性能验证

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

### 3. 启动服务验证

#### 环境清理
启动服务前先清理 NPU 环境：
```bash
./scripts/kill_vllm.sh
```

#### 启动服务（使用配置参数）
```bash
# 自适应服务（实验组）
export ASCEND_RT_VISIBLE_DEVICES=${config.adaptive.npu_devices}
vllm serve ${config.model.main} \
     -tp ${config.service.tensor_parallel_size} \
     --port ${config.adaptive.port} \
     --served-model-name Qwen3-32B \
     --speculative-config '{    
       "model": "${config.model.draft}",
       "num_speculative_tokens": ${config.service.num_speculative_tokens},
       "method": "${config.service.method}",
       "draft_tensor_parallel_size": ${config.service.draft_tensor_parallel_size},
       "enable_adaptive": ${config.adaptive.enable_adaptive}
     }' \
     --max-num-seqs ${config.service.max_num_seqs}

# 基线服务（对照组）- 使用 baseline 配置，enable_adaptive=false
```

### 4. 测试验证

```bash
# 测试自适应服务
./scripts/run_perf_test.sh ${config.adaptive.port}

# 测试基线服务
./scripts/run_perf_test.sh ${config.baseline.port}
```

### 5. 结果分析
- 对比自适应组与基线组的性能指标
- 分析开发日志，验证功能是否按预期工作
- 评估性能提升效果（吞吐量、延迟等）

## 脚本资源

| 脚本 | 路径 | 说明 |
|------|------|------|
| 清理环境 | `scripts/kill_vllm.sh` | 清理所有 vLLM 进程 |
| 启动自适应 | `scripts/start_adaptive.sh` | 使用默认配置启动实验组 |
| 启动基线 | `scripts/start_baseline.sh` | 使用默认配置启动对照组 |
| 性能测试 | `scripts/run_perf_test.sh <port>` | 执行性能测试 |

## 典型用法举例

```
# 使用默认配置
"帮我启动 vLLM 自适应投机解码服务并进行性能测试"

# 自定义配置
"使用端口 9000、9001，NPU 卡 0,1 和 2,3 进行对比测试"
"修改 max_num_seqs 为 32 后重新测试"
```

---

- version: v1.1.0 (2026-01-20): 抽象配置参数，支持自定义输入
- version: v1.0.0 (2026-01-19): 初始发布
