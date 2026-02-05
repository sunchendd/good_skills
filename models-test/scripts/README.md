# 大模型测试自动化框架

本项目是一个专门用于大语言模型(LLM)性能和精度测试的自动化框架，支持多种推理引擎(VLLM、MindIE)和多种执行模式的自动化测试。

## 目录

- [项目概述](#项目概述)
- [功能特性](#功能特性)
- [项目结构](#项目结构)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [详细使用说明](#详细使用说明)
- [配置参数说明](#配置参数说明)
- [测试类型](#测试类型)
- [执行模式](#执行模式)
- [结果分析](#结果分析)
- [常见问题](#常见问题)

## 项目概述

本项目旨在提供一套完整的大模型测试解决方案，通过自动化脚本实现：

- **性能测试**: 评估模型在推理过程中的吞吐量、时延等关键指标
- **精度测试**: 使用标准数据集评估模型的生成质量
- **资源管理**: 自动化NPU(神经网络处理器)资源的分配和回收
- **容器化部署**: 使用Docker容器隔离测试环境
- **并行测试**: 支持多模型并行测试，提高测试效率

## 功能特性

### 核心功能

1. **多引擎支持**
   - VLLM推理引擎性能测试
   - MindIE推理引擎性能测试
   - 基于EvalScope的精度评估

2. **自动化测试流程**
   - 自动检测和管理NPU资源
   - 自动分配和释放端口
   - 容器化部署和清理
   - 完整的错误处理和日志记录

3. **灵活的配置**
   - 支持单模型和批量模型测试
   - 可配置的NPU数量和执行模式
   - 自定义温度、请求速率等参数
   - 支持多种数据集

4. **详细的测试报告**
   - 性能指标(TTFT、TPS、TPOT等)
   - 精度评估结果
   - 完整的日志记录

### 性能指标

框架支持以下性能指标的测量：

- **TTFT (Time To First Token)**: 首个token生成时延
- **TPS (Tokens Per Second)**: 每秒生成的token数
- **TPOT (Time Per Output Token)**: 输出token平均时延
- **吞吐量**: 整体推理吞吐量
- **请求成功率**: 成功响应的请求比例

## 项目结构

```
models_test/
├── skills/
│   ├── SKILL.md                          # 技能说明文档
│   └── scripts/
│       ├── evalscope_auto/                # 精度测试脚本
│       │   ├── eval_accuracy.sh          # 启动精度测试
│       │   ├── run_accuracy_all_models.sh # 批量精度测试
│       │   ├── run_accuracy_test.sh      # 精度测试执行脚本
│       │   └── start_vllm_sever.sh      # VLLM服务启动脚本
│       ├── mindie_benchmark_auto/         # MindIE性能测试脚本
│       │   ├── docker_mindie.sh          # MindIE容器启动
│       │   ├── mindie_auto_test.sh      # 批量MindIE测试
│       │   ├── performance_test.py      # 性能测试核心脚本
│       │   ├── run_mindiebench.sh       # MindIE基准测试
│       │   ├── run_perf_test.sh         # 单模型性能测试
│       │   ├── sonnet_20x.txt          # 测试数据集
│       │   └── start_mindie.sh         # MindIE服务启动
│       └── vllm_benchmark_auto/          # VLLM性能测试脚本
│           ├── benchmark.sh             # VLLM基准测试
│           ├── performance_test.py      # 性能测试核心脚本
│           ├── run_benchmark_all_models.sh # 批量VLLM测试
│           ├── run_perf_test.sh         # 单模型性能测试
│           ├── run_vllmbench.sh         # VLLM基准测试执行
│           ├── sonnet_20x.txt          # 测试数据集
│           └── start_vllm_sever.sh      # VLLM服务启动
```

## 环境要求

### 硬件要求

- **NPU设备**: 昇腾910B系列处理器(推荐910B2C)
- **内存**: 建议至少64GB可用内存
- **存储**: 根据模型大小，建议至少500GB可用空间
- **网络**: 支持Docker网络功能

### 软件要求

- **操作系统**: Linux (支持Ubuntu、EulerOS等)
- **Docker**: 版本20.10或以上
- **Python**: 3.8+
- **依赖库**:
  - transformers
  - requests
  - pandas
  - numpy

### 驱动要求

- 昇腾NPU驱动(CANN)
- npu-smi工具

## 快速开始

### 1. 准备环境

确保已安装Docker和NPU驱动：

```bash
# 检查Docker版本
docker --version

# 检查NPU设备
npu-smi info
```

### 2. 准备模型

将模型文件放置在统一的基础路径下：

```bash
/path/to/models/
├── Qwen3-32B/
├── Qwen3-14B/
├── Qwen2.5-72B/
└── ...
```

### 3. 运行单模型性能测试

```bash
cd skills/scripts/vllm_benchmark_auto

bash run_benchmark_all_models.sh \
  -b /path/to/models \
  -r /path/to/results \
  -m "Qwen3-0.6B" \
  -n 1 \
  --mode "aclgraph"
```

### 4. 运行批量模型测试

```bash
cd skills/scripts/vllm_benchmark_auto

bash run_benchmark_all_models.sh \
  -b /path/to/models \
  -r /path/to/results
```

## 详细使用说明

### VLLM性能测试

#### 单模型测试

```bash
cd skills/scripts/vllm_benchmark_auto

bash run_benchmark_all_models.sh \
  -b /path/to/models \
  -r results_vllm_single \
  -m "模型名称" \
  -n "NPU数" \
  --mode "图模式" \
  -e 1
```

#### 批量模型测试

```bash
cd skills/scripts/vllm_benchmark_auto

bash run_benchmark_all_models.sh \
  -b /path/to/models \
  -r results_vllm_all
```

### MindIE性能测试

#### 单模型测试

```bash
cd skills/scripts/mindie_benchmark_auto

bash mindie_auto_test.sh \
  -b /path/to/models \
  -r results_mindie_single \
  -m "模型名称" \
  -n "NPU数"
```

#### 批量模型测试

```bash
cd skills/scripts/mindie_benchmark_auto

bash mindie_auto_test.sh \
  -b /path/to/models \
  -r results_mindie_all
```

### 模型精度测试

#### 单模型测试

```bash
cd skills/scripts/evalscope_auto

bash run_accuracy_all_models.sh \
  -b /path/to/models \
  -r results_accuracy_single \
  -m "模型名称" \
  -n "NPU数" \
  --mode "图模式" \
  --datasets "数据集"
```

#### 批量模型测试

```bash
cd skills/scripts/evalscope_auto

bash run_accuracy_all_models.sh \
  -b /path/to/models \
  -r results_accuracy_all
```

### 联合测试(性能+精度)

#### 单模型联合测试

```bash
cd skills/scripts/vllm_benchmark_auto && \
bash run_benchmark_all_models.sh -b /path/to/models -r results_vllm_single -m "模型名称" -n "NPU数" --mode "图模式" -e 1 && \
cd ../mindie_benchmark_auto && \
bash mindie_auto_test.sh -b /path/to/models -r results_mindie_single -m "模型名称" -n "NPU数" && \
cd ../evalscope_auto && \
bash run_accuracy_all_models.sh -b /path/to/models -r results_accuracy_single -m "模型名称" -n "NPU数" --mode "图模式" --datasets "数据集"
```

## 配置参数说明

### 通用参数

| 参数 | 说明 | 必需 | 示例 |
|------|------|------|------|
| `-b, --base-model-path` | 模型文件基础路径 | 是 | `/data/models` |
| `-r, --result-dir` | 结果保存目录 | 是 | `/data/results` |
| `-m, --model` | 单模型测试的模型名称 | 否 | `Qwen3-32B` |
| `-n, --npu-count` | NPU数量 | 否 | `4` |
| `--mode` | 执行模式 | 否 | `aclgraph` |
| `-t, --temperature` | 生成温度参数 | 否 | `0.65` |
| `-R, --request-rate` | 请求速率 | 否 | `0` |
| `-d, --docker-tag` | Docker镜像标签 | 否 | `v0.12.0rc1` |
| `--datasets` | 精度测试数据集 | 否 | `mmlu` |
| `-e, --executable-module` | 执行标志 | 否 | `1` |
| `--debug` | 启用调试模式 | 否 | - |

### 执行模式说明

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `eager` | 急切执行模式 | 快速原型开发和调试 |
| `aclgraph` | ACL图模式 | 生产环境，性能优化 |
| `xlite` | X-Lite模式 | 轻量级部署场景 |
| `torchair` | TorchAIR模式 | PyTorch生态集成 |
| `mindie` | MindIE模式 | 华为MindIE推理 |

## 测试类型

### 1. 单模型性能测试

测试单个模型的VLLM和MindIE推理性能，适用于：

- 模型调优验证
- 新模型性能评估
- 特定场景性能分析

### 2. 单模型VLLM性能测试

仅测试VLLM推理引擎性能，适用于：

- VLLM引擎性能对比
- VLLM特定场景优化验证

### 3. 单模型MindIE性能测试

仅测试MindIE推理引擎性能，适用于：

- MindIE引擎性能评估
- 昇腾生态优化验证

### 4. 单模型精度测试

测试单个模型的精度，适用于：

- 模型质量验证
- 量化精度损失评估

### 5. 全套模型性能测试

批量测试所有配置的模型，适用于：

- 回归测试
- 全面性能评估
- 自动化测试流水线

### 6. 全套模型VLLM性能测试

批量测试所有模型的VLLM性能

### 7. 全套模型MindIE性能测试

批量测试所有模型的MindIE性能

### 8. 全套模型精度测试

批量测试所有模型的精度

### 9. 全套模型性能和精度测试报告

完整测试所有模型的性能和精度，生成综合报告

### 10. 单模型性能和精度测试报告

完整测试单个模型的性能和精度

## 执行模式

### 混合并行模式

框架采用混合并行执行策略：

1. **推理服务顺序启动**: 确保服务稳定性
2. **VLLM性能测试并行执行**: 提高整体效率
3. **MindIE性能测试串行执行**: 确保各个模型之间不相互影响
4. **资源动态分配**: 优化NPU利用率

### 资源管理

- **NPU自动分配**: 根据模型需求自动分配NPU资源
- **端口动态管理**: 自动分配和释放端口(2800-2899)
- **容器自动清理**: 测试完成后自动清理容器

### 错误处理

- **超时等待**: NPU资源最长等待10小时
- **服务就绪检查**: 推理服务启动最大等待20分钟
- **异常恢复**: 自动清理异常状态和残留资源

## 结果分析

### 测试结果目录结构

```
# vllm性能测试结果目录
results/
├── vllm_v0.12.0rc1/
│   ├── log/                          # 测试日志
│   │   ├── x86_64_start_vllm_Qwen3-32B_*.log  #vllm服务启动日志
│   │   └── x86_64_benchmark_Qwen3-32B_*.log  #vllm性能测试日志
│   └── x86_64_vllm_results_Qwen3-8B_*.csv          # 性能结果

# mindie性能测试结果目录
results/
├── mindie_v0.12.0rc1/
│   ├── log/                          # 测试日志
│   │   ├── x86_64_start_mindie_Qwen3-32B_*.log  #mindie服务启动日志
│   │   └── x86_64_mindie_benchmark_Qwen3-32B_*.log  #mindie性能测试日志
│   └── x86_64_mindie_results_Qwen3-8B_*.csv          # 性能结果

# 精度测试结果目录
results/
├── vllm_acc_v0.12.0rc1/
│   ├── log/                          # 测试日志
│   │   ├── x86_64_start_vllm_acc_Qwen3-32B_*.log  #vllm服务启动日志
│   │   └── x86_64_accuracy_Qwen3-32B_*.log  #精度测试日志
│   └──  x86_64_results_Qwen3-8B_*.csv          # 精度结果

```

### 性能指标说明

**CSV结果文件包含以下指标**:

| 指标 | 说明 | 单位 |
|------|------|------|
| Process Num | 并发进程数 | 个 |
| Input Length | 输入token长度 | tokens |
| Output Length | 输出token长度 | tokens |
| TTFT | 首token生成时延 | ms |
| avg TPS (without prefill) | 平均吞吐量(不含预填充) | tokens/s |
| avg TPS (with prefill) | 平均吞吐量(含预填充) | tokens/s |
| Total Time | 总推理时间 | ms |
| TPS (without prefill) | 总吞吐量(不含预填充) | tokens/s |
| TPS (with prefill) | 总吞吐量(含预填充) | tokens/s |
| avg input Tokens | 平均输入token数 | tokens |
| avg output Tokens | 平均输出token数 | tokens |

### 日志文件

- **启动日志**: 记录容器启动过程
- **测试日志**: 记录测试执行过程
- **结果日志**: 记录测试结果输出

### 查看测试结果

```bash
# 查看性能结果
cat results/vllm_v0.12.0rc1/performance_results/results.csv

# 查看测试日志
cat results/vllm_v0.12.0rc1/log/benchmark_Qwen3-32B_*.log

# 查看精度结果
cat results/vllm_acc_v0.12.0rc1/accuracy_results/eval_results.json
```

## 常见问题

### 1. NPU资源不足

**问题**: 等待NPU资源超时

**解决方案**:
- 检查当前NPU占用情况: `npu-smi info`
- 减少测试并发数
- 清理未释放的NPU资源

### 2. 端口冲突

**问题**: 无法分配可用端口

**解决方案**:
- 检查端口占用: `netstat -tuln | grep 28`
- 修改端口范围(编辑脚本中的`DEFAULT_PORT_RANGE_START`和`DEFAULT_PORT_RANGE_END`)
- 清理残留容器: `docker rm -f $(docker ps -aq --filter "name=vllm_")`

### 3. 容器启动失败

**问题**: 推理服务容器启动失败

**解决方案**:
- 检查Docker是否正常运行: `docker ps`
- 检查模型路径是否正确
- 查看容器日志: `docker logs <container_name>`
- 检查NPU驱动状态: `npu-smi info`

### 4. 模型路径不存在

**问题**: 脚本跳过测试，提示模型路径不存在

**解决方案**:
- 确认模型路径拼写正确
- 检查模型文件是否完整
- 验证文件权限是否正确
- 支持软链接，可以使用软链接指向模型

### 5. 测试结果异常

**问题**: 性能指标异常或精度下降

**解决方案**:
- 查看详细测试日志
- 检查模型是否正常加载
- 验证测试参数设置是否合理
- 使用`--debug`模式获取详细调试信息

## 高级使用

### 自定义测试配置

编辑对应的脚本文件，修改`TEST_CONFIGS`数组：

```bash
declare -a TEST_CONFIGS=(
    "Qwen3-32B:4:aclgraph"
    "Qwen2.5-72B:4:eager"
    # 添加自定义配置...
)
```

### 修改测试参数

在脚本顶部修改默认参数：

```bash
DEFAULT_TEMPERATURE="0.65"
DEFAULT_REQUEST_RATE="0"
DEFAULT_DOCKER_TAG="v0.12.0rc1"
```

### 集成到CI/CD

可以将测试脚本集成到自动化流水线中：

```bash
#!/bin/bash
# CI/CD集成示例

cd /data/models_test/skills/scripts/vllm_benchmark_auto

bash run_benchmark_all_models.sh \
  -b /path/to/models \
  -r /path/to/results

# 检查测试结果
if [ $? -eq 0 ]; then
    echo "测试通过"
else
    echo "测试失败"
    exit 1
fi
```

