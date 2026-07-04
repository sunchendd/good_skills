# Good Skills

自研 AI Agent 技能集合，含 Python 自动化与定时推送（邮件 + Bark）。

## 安装

```bash
/plugin marketplace add sunchendd/good-skills
/plugin install good-skills@good-skills
```

## 技能列表

### 每日推送

| 技能 | 说明 |
|------|------|
| [daily-newsletter](skills/daily-newsletter/) | 每日科技早报，27+ RSS 源并发抓取，智能分类 + 质量评分，邮件+Bark 推送 |
| [arxiv-daily](skills/arxiv-daily/) | 每日 arXiv AI 论文精选，DeepSeek 评分筛选，中文摘要，邮件+Bark 推送 |
| [vibe-daily](skills/vibe-daily/) | 每日 AI 编程工具动态，Cursor/Claude Code/Copilot 更新和技巧 |
| [super-wardrobe](skills/super-wardrobe/) | 每日穿搭建议，自动获取杭州天气，AI 搭配上衣/裤子/鞋/帽子/配色 |
| [super-fitness](skills/super-fitness/) | 科学减脂计划，每日 AI 生成个性化运动+饮食方案 |
| [github-watcher](skills/github-watcher/) | GitHub 仓库监控，vllm-ascend 新版本、DeepSeek 新仓库、vLLM 有价值 PR |

### 总结与报告

| 技能 | 说明 |
|------|------|
| [daily-digest](skills/daily-digest/) | 每日日志聚合，汇总 GitHub 动态 + 当日所有 skill 输出 |
| [weekly-report](skills/weekly-report/) | 周报生成，汇总日历+GitHub+笔记，AI 分析工作总结+时间统计 |

### 开发工具

| 技能 | 说明 |
|------|------|
| [vllm-dev](skills/vllm-dev/) | vLLM 推理引擎开发，推测解码(Eagle3/MTP)、KV Cache 优化、Attention Backend |
| [vllm-test](skills/vllm-test/) | vLLM 性能测试，基准测试、吞吐/延迟对比 |
| [dev-workflow](skills/dev-workflow/) | 通用开发验证工作流，支持 Ascend NPU/GPU，vLLM/MindIE 引擎 |

### 知识管理

| 技能 | 说明 |
|------|------|
| [patent-search](skills/patent-search/) | 专利搜索，多库检索、新颖性评估、侵权分析 |
| [patent-specialist](skills/patent-specialist/) | 专利撰写，技术交底书 -> 权利要求书 |
| [xhs-skill](skills/xhs-skill/) | 小红书检索与发布，基于 MCP Server |
| [humanizer-zh](skills/humanizer-zh/) | 中文去 AI 痕迹，24 种模式检测与修复 |

### 编码规范

| 技能 | 说明 |
|------|------|
| [coding-guidelines](skills/coding-guidelines/) | 减少 LLM 编码失误的行为准则，源自 Andrej Karpathy 的观察 |

### 技能管理

| 技能 | 说明 |
|------|------|
| [find-skills](skills/find-skills/) | 技能发现与安装指南 |
| [skill-creator](skills/skill-creator/) | 技能创建指南 |
| [skill-cleanup](skills/skill-cleanup/) | 清理失效 skill 符号链接 |

## 环境变量

| 变量 | 说明 |
|------|------|
| `DEEPSEEK_API_KEY` | LLM API |
| `GITHUB_TOKEN` | GitHub API |
| `BARK_TOKEN` | iOS 推送通知 |
| `EMAIL_SENDER` | QQ 邮箱发件人 |
| `EMAIL_RECIPIENTS` | 收件人 |
| `QQ_EMAIL_PASSWORD` | QQ 邮箱 SMTP 授权码 |

## License

MIT
