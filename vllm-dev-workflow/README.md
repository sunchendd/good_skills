# vLLM 开发验证工作流 Skill

这是一个符合 Claude Code Agent Skills 规范的 Skill，用于在 Ascend NPU 环境下进行 vLLM 推理服务的开发、测试和验证。

## 目录结构

```
vllm-dev-workflow/
├── SKILL.md                      # Skill 主文件（必需）
├── README.md                     # 说明文档
└── scripts/                      # 实用脚本目录
    ├── kill_vllm.sh             # 清理 vLLM 进程
    ├── start_adaptive.sh        # 启动自适应服务（实验组）
    ├── start_baseline.sh        # 启动基线服务（对照组）
    ├── run_perf_test.sh         # 性能测试脚本
    └── performance_test.py      # 性能测试核心代码
```

## 安装方式

### 1. 项目级 Skill（推荐）
将此目录放置到项目的 `.claude/skills/` 下：
```bash
cp -r vllm-dev-workflow /path/to/your/project/.claude/skills/
```

### 2. 个人 Skill
将此目录放置到个人 Skills 目录：
```bash
cp -r vllm-dev-workflow ~/.claude/skills/
```

## 使用方式

当你向 Claude 提问以下类似问题时，此 Skill 会自动激活：

- "帮我启动 vLLM 自适应投机解码服务"
- "我要对比自适应和基线的性能差异"
- "清理环境，重新部署 vLLM 服务"
- "运行性能测试"

## 脚本使用

### 清理环境
```bash
./scripts/kill_vllm.sh
```

### 启动服务
```bash
# 启动自适应服务（端口 10000，NPU 14-15）
./scripts/start_adaptive.sh

# 启动基线服务（端口 10001，NPU 12-13）
./scripts/start_baseline.sh
```

### 运行性能测试
```bash
# 测试自适应服务
./scripts/run_perf_test.sh 10000

# 测试基线服务
./scripts/run_perf_test.sh 10001
```

## 配置说明

| 配置项 | 自适应组 | 基线组 |
|--------|----------|--------|
| 端口 | 10000 | 10001 |
| NPU卡 | 14,15 | 12,13 |
| enable_adaptive | true | false |

## 版本
- v1.0.0 (2026-01-20): 初始打包发布
