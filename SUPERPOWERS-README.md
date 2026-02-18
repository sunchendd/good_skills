# Superpowers 技能组合说明

## 什么是 Superpowers

`superpowers` 不是一个单一技能，而是一个**技能组合**（skill collection），包含 14 个规范 AI 开发流程的工作流技能。

## 组织结构

```
good_skills/
├── superpowers/              # 技能组合目录
│   ├── using-superpowers/    # 核心：技能使用总则
│   ├── brainstorming/        # 需求分析
│   ├── writing-plans/        # 编写计划
│   ├── executing-plans/      # 执行计划
│   ├── test-driven-development/  # TDD
│   ├── systematic-debugging/     # 调试
│   ├── verification-before-completion/  # 验证
│   ├── finishing-a-development-branch/ # 完成分支
│   ├── requesting-code-review/       # 请求审查
│   ├── receiving-code-review/        # 接收审查
│   ├── writing-skills/               # 编写技能
│   ├── dispatching-parallel-agents/  # 并行分发
│   ├── subagent-driven-development/  # 子代理开发
│   └── using-git-worktrees/          # Git 工作树
├── bili-fetch/
├── feishu-doc-skill/
├── news-tts/
└── ...其他独立技能
```

## 使用方式

### 1. 作为整体引用
当需要规范开发流程时，使用 `superpowers` 前缀调用：
- `superpowers:brainstorming`
- `superpowers:test-driven-development`
- `superpowers:systematic-debugging`

### 2. 核心流程
```
用户请求
  ↓
superpowers:using-superpowers (检查适用技能)
  ↓
superpowers:brainstorming (需求分析)
  ↓
superpowers:writing-plans (实现计划)
  ↓
superpowers:test-driven-development (TDD 循环)
  ↓
superpowers:verification-before-completion (验证)
  ↓
superpowers:finishing-a-development-branch (完成)
```

## 关键原则

| 原则 | 说明 |
|-----|------|
| **1% 规则** | 即使 1% 可能适用也要检查技能 |
| **流程优先** | 先流程技能，后实现技能 |
| **刚性执行** | TDD 和 debugging 严格按流程 |
| **证据优先** | 完成前必须有验证证据 |

## 与其他技能的关系

- **独立技能**（如 `bili-fetch`, `news-tts`）：特定功能，直接调用
- **Superpowers**：工作流规范，指导**如何**使用技能
