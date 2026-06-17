# 通用开发验证工作流 Skill

这是一个符合 Claude Code Agent Skills 规范的 Skill，用于 AI/ML 推理服务的开发、测试和验证。

## 目录结构

```
dev-workflow/
├── SKILL.md                      # Skill 主文件（必需）
├── README.md                     # 说明文档
└── scripts/                      # 实用脚本目录
    ├── kill_server.sh            # 清理服务进程
    ├── check_npu.py              # 检查 NPU 可用性
    ├── start_vllm.sh             # 启动 vLLM 服务
    ├── wait_for_service.sh       # 等待服务就绪
    └── run_perf_test.sh          # 执行性能测试
```

## 安装方式

### 1. 项目级 Skill（推荐）

将此目录放置到项目的 `.claude/skills/` 下：
```bash
cp -r dev-workflow /path/to/your/project/.claude/skills/
```

### 2. 个人 Skill

将此目录放置到个人 Skills 目录：
```bash
cp -r dev-workflow ~/.claude/skills/
```

## 使用方式

当你向 Claude 提问以下类似问题时，此 Skill 会自动激活：

- "帮我启动 vLLM 服务并进行性能测试"
- "我要对比不同配置的推理性能"
- "清理环境，重新部署推理服务"
- "测试模型在 NPU 上的性能"
- "运行基准测试"

## 脚本使用

### 清理环境
```bash
./scripts/kill_server.sh
```

### 检查 NPU
```bash
python3 scripts/check_npu.py
```

### 启动服务
```bash
# 默认配置
./scripts/start_vllm.sh 8000 2 "/data/models/Qwen3-8B" 16

# 自定义配置
./scripts/start_vllm.sh 9000 4 "/data/models/Qwen3-32B" 32
```

### 等待服务就绪
```bash
./scripts/wait_for_service.sh 8000 300
```

### 运行性能测试
```bash
./scripts/run_perf_test.sh 8000 4 1024 1024 10
```

## 支持的硬件

- **Ascend NPU**: 使用 `ASCEND_RT_VISIBLE_DEVICES` 环境变量
- **NVIDIA GPU**: 使用 `CUDA_VISIBLE_DEVICES` 环境变量

## 版本

- v1.0.0 (2026-02-03): 初始发布，基于 vllm-dev-workflow 抽象
