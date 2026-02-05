---
name: models-test
description: >-
  大模型测试自动化框架，用于在华为昇腾NPU上进行VLLM和MindIE推理性能及精度评估。
  支持自动化NPU资源管理、Docker容器化部署和并行测试。
  当用户提出以下请求时请使用此技能：测试大模型性能或精度、运行VLLM或MindIE基准测试、
  生成模型测试命令、或请求执行测试工作流。
  Agent需要逐步完整执行测试工作流程，确保资源管理和错误处理。
---

# 大模型性能和精度测试框架

此技能提供自动化测试脚本。**Agent**需要逐步协调执行测试工作流程。

## 🛠 工作流程定义

### 步骤 1：选择测试类型

向用户展示以下测试选项（1-10）：

1. **单模型性能测试** - 测试单个模型的VLLM和MindIE推理性能
2. **单模型VLLM性能测试** - 测试单个模型的VLLM性能
3. **单模型MindIE性能测试** - 测试单个模型的MindIE性能
4. **单模型精度测试** - 测试单个模型的精度
5. **全套模型性能测试** - 测试所有配置模型的VLLM和MindIE性能
6. **全套模型VLLM性能测试** - 测试所有模型的VLLM性能
7. **全套模型MindIE性能测试** - 测试所有模型的MindIE性能
8. **全套模型精度测试** - 测试所有模型的精度
9. **全套模型性能和精度测试** - 对所有模型进行完整的性能和精度测试
10. **单模型性能和精度测试** - 对单个模型进行完整的性能和精度测试

### 步骤 2：准备测试环境

进入测试目录(根据实际目录修改)：
```bash
cd /data/models-test/
```

### 步骤 3：收集必要参数

根据选择的测试类型，询问用户以下信息：

**必需参数：**
- `-b`：模型基础路径（存放所有模型的目录）
- `-r`：结果目录（测试结果的保存位置）

**可选参数（用于单模型测试）：**
- `-m`：模型名称（例如："Qwen3-0.6B"）
- `-n`：NPU数量（例如：1、2、4、8、16）
- `--mode`：图模式（eager、aclgraph、xlite、torchair、mindie）
- `--datasets`：精度测试数据集名称（例如：mmlu、cmmlu）
- `-e`：执行标志（1=自定义性能脚本，2=VLLM基准测试脚本）

### 步骤 4：执行测试命令

**重要原则：** 对于组合性能和精度测试，必须按以下顺序执行命令：
VLLM性能测试 → MindIE性能测试 → 精度测试（使用 `&&` 串联命令）。

**选项 A：VLLM性能测试（单模型）**
```bash
cd ./scripts/vllm_benchmark_auto
bash run_benchmark_all_models.sh \
  -b <模型路径> \
  -r results_vllm_single \
  -m "<模型名称>" \
  -n <NPU数量> \
  --mode "<图模式>" \
  -e 1
```

**选项 B：VLLM性能测试（全套模型）**
```bash
cd ./scripts/vllm_benchmark_auto
bash run_benchmark_all_models.sh \
  -b <模型路径> \
  -r results_vllm_all \
  -e 1
```

**选项 C：MindIE性能测试（单模型）**
```bash
cd ./scripts/mindie_benchmark_auto
bash mindie_auto_test.sh \
  -b <模型路径> \
  -r results_mindie_single \
  -m "<模型名称>" \
  -n <NPU数量>
```

**选项 D：MindIE性能测试（全套模型）**
```bash
cd ./scripts/mindie_benchmark_auto
bash mindie_auto_test.sh \
  -b <模型路径> \
  -r results_mindie_all
```

**选项 E：精度测试（单模型）**
```bash
cd ./scripts/evalscope_auto
bash run_accuracy_all_models.sh \
  -b <模型路径> \
  -r results_accuracy_single \
  -m "<模型名称>" \
  -n <NPU数量> \
  --mode "<图模式>" \
  --datasets "<数据集名称>"
```

**选项 F：精度测试（全套模型）**
```bash
cd ./scripts/evalscope_auto
bash run_accuracy_all_models.sh \
  -b <模型路径> \
  -r results_accuracy_all
```

**选项 G：性能和精度联合测试（单模型）**
```bash
cd ./scripts/vllm_benchmark_auto && \
bash run_benchmark_all_models.sh -b <模型路径> -r results_vllm_single -m "<模型名称>" -n <NPU数量> --mode "<图模式>" -e 1 && \
cd ../mindie_benchmark_auto && \
bash mindie_auto_test.sh -b <模型路径> -r results_mindie_single -m "<模型名称>" -n <NPU数量> && \
cd ../evalscope_auto && \
bash run_accuracy_all_models.sh -b <模型路径> -r results_accuracy_single -m "<模型名称>" -n <NPU数量> --mode "<图模式>" --datasets "<数据集名称>"
```

**选项 H：性能和精度联合测试（全套模型）**
```bash
cd ./scripts/vllm_benchmark_auto && \
bash run_benchmark_all_models.sh -b <模型路径> -r results_vllm_all -e 1 && \
cd ../mindie_benchmark_auto && \
bash mindie_auto_test.sh -b <模型路径> -r results_mindie_all && \
cd ../evalscope_auto && \
bash run_accuracy_all_models.sh -b <模型路径> -r results_accuracy_all
```

### 步骤 5：验证并生成测试报告

测试完成后，框架将显示：
- ✅ 成功的测试
- ❌ 失败的测试
- ⚠️ 跳过的测试（包含原因）

**生成测试报告：**

1. 进入结果目录并分析输出
2. 对每个测试的模型，提供以下信息：
   - 模型名称（例如：Qwen3-0.6B）
   - 结果目录路径（可点击链接）
   - 结果文件（可点击链接到CSV/JSON文件）
   - 测试日志（可点击链接到日志文件）

3. CSV中可用的性能指标：
   - TTFT（首Token时延）单位：毫秒
   - TPS（每秒Token数）含/不含预填充
   - TPOT（每个输出Token时间）
   - 总推理时间
   - 请求吞吐量

4. JSON中可用的精度指标：
   - 数据集特定精度分数
   - 模型在基准数据集上的性能

**示例报告格式：**
```
=== Qwen3-0.6B 测试摘要 ===

📁 结果目录: [results_vllm_single](./results_vllm_single)
📊 结果文件: [results.csv](./results_vllm_single/results.csv)
📋 测试日志: [benchmark_Qwen3-0.6B_xxx.log和start_xxx_Qwen3-0.6B_XXX.log](./results_vllm_single/log/benchmark_Qwen3-0.6B_xxx.log)

性能指标:
- TTFT: XXX.XX ms
- TPS (含预填充): XXX.XX tokens/s
- TPS (不含预填充): XXX.XX tokens/s
- 平均输入Token数: XXX
- 平均输出Token数: XXX
```

---

## 使用场景示例

**用户请求：** "测试Qwen3-0.6B的VLLM推理性能"

**Agent响应：**
1. 展示测试选项（用户选择选项2：单模型VLLM性能测试）
2. 收集参数：
   - 模型路径: /data/models
   - 模型名称: Qwen3-0.6B
   - NPU数量: 1
   - 图模式: aclgraph
3. 执行命令：
   ```bash
   cd ./scripts/vllm_benchmark_auto
   bash run_benchmark_all_models.sh \
     -b /data/models \
     -r results_vllm_single \
     -m "Qwen3-0.6B" \
     -n 1 \
     --mode "aclgraph" \
     -e 1
   ```
4. 监控测试进度和日志
5. 验证完成情况并生成测试报告

## 目录结构

### 性能测试脚本
- `scripts/vllm_benchmark_auto/`: VLLM性能测试
  - `run_benchmark_all_models.sh`: 主测试协调器
  - `run_vllmbench.sh`: VLLM基准测试运行器
  - `start_vllm_sever.sh`: VLLM服务启动器
  - `performance_test.py`: 核心性能测试逻辑

- `scripts/mindie_benchmark_auto/`: MindIE性能测试
  - `mindie_auto_test.sh`: MindIE测试协调器
  - `run_mindiebench.sh`: MindIE基准测试运行器
  - `start_mindie.sh`: MindIE服务启动器
  - `performance_test.py`: 核心性能测试逻辑

### 精度测试脚本
- `scripts/evalscope_auto/`: 模型精度评估
  - `run_accuracy_all_models.sh`: 精度测试协调器
  - `run_accuracy_test.sh`: 精度测试运行器
  - `start_vllm_sever.sh`: 用于精度测试的VLLM服务启动器

## 参数参考表

| 参数 | 说明 | 示例 |
|-----------|-------------|---------|
| `-b, --base-model-path` | 存放所有模型的基础路径 | `/data/models` |
| `-r, --result-dir` | 保存测试输出的结果目录 | `/data/results` |
| `-m, --model` | 单模型测试的模型名称 | `Qwen3-32B` |
| `-n, --npu-count` | 要分配的NPU数量 | `4` |
| `--mode` | 图模式：eager、aclgraph、xlite、torchair、mindie | `aclgraph` |
| `--datasets` | 精度测试的数据集名称 | `mmlu` |
| `-e, --executable-module` | 执行标志：1=自定义脚本，2=VLLM基准测试 | `1` |
| `-t, --temperature` | 生成温度参数 | `0.65` |
| `-R, --request-rate` | 测试的请求速率 | `0` |
| `-d, --docker-tag` | Docker镜像标签 | `v0.12.0rc1` |

## 图模式说明

| 模式 | 说明 | 使用场景 |
|------|-------------|----------|
| `eager` | eager模式 |  |
| `aclgraph` | ACL图模式 | 生产环境，优化性能 |
| `xlite` | X-Lite模式 | 轻量级部署场景 |
| `torchair` | TorchAIR模式 | PyTorch生态集成 |
| `mindie` | MindIE模式 | 华为MindIE推理 |

## 重要注意事项

1. **顺序执行**：对于组合测试，必须始终按 VLLM → MindIE → 精度 的顺序使用 `&&` 执行
2. **资源管理**：框架自动管理NPU分配和清理
3. **端口管理**：自动在2800-2899范围内分配端口
4. **超时处理**：NPU资源最长等待时间为10小时
5. **容器清理**：所有容器在测试完成后自动清理
6. **错误处理**：失败的测试会记录详细的错误信息
7. **并行测试**：当NPU资源可用时，多个测试可以并行运行

## 性能指标

框架测量并报告以下指标：

- **TTFT（首Token时延）**：生成第一个Token的延迟
- **TPS（每秒Token数）**：含/不含预填充阶段的吞吐量
- **TPOT（每个输出Token时间）**：每个输出Token的平均时间
- **请求吞吐量**：每秒完成的请求数
- **成功率**：成功请求的百分比
- **总推理时间**：完整的推理持续时间