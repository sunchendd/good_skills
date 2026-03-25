---
name: github-watcher
description: GitHub 仓库监控。监控 vllm-ascend 新版本发布、DeepSeek 新仓库创建、以及 vLLM 相关有价值的新 PR，发现更新立即 Bark 推送通知。
---

# GitHub 监控

实时监控关注的 GitHub 仓库动态，发现更新立即 Bark 推送。

## 监控目标

| 目标 | 类型 | 说明 |
|------|------|------|
| vllm-project/vllm-ascend | Release | 新版本发布 |
| deepseek-ai | New Repo | 新仓库创建 |
| vllm-project/vllm | PR | 有价值的新 PR |
| vllm-project/vllm-ascend | PR | 有价值的新 PR |

## PR 价值判断标准

满足以下任一条件：
- 标题含关键词：speculative、eagle、mtp、kv_cache、kv cache、attention、prefix caching
- 变更行数 > 200
- 带有标签：feature、enhancement、new feature

## 工作原理

```
GitHub API → 比对本地 state.json → 发现变更 → Bark 推送
```

有状态记忆（state.json），避免重复通知。首次运行初始化状态，不发通知。

## 环境变量

| 变量 | 必需 | 说明 |
|------|------|------|
| `GITHUB_TOKEN` | ✅ | GitHub Personal Access Token |
| `BARK_TOKEN` | 可选 | Bark 推送 |

## 用法

```bash
python3 run_github_watcher.py    # 建议每2小时运行
```
