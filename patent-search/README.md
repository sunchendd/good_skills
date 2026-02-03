# Patent Search Specialist Skill

这是一个符合 Claude Code Agent Skills 规范的 Skill，用于专利检索、新颖性评估和侵权风险分析。

## 目录结构

```
patent-search/
├── SKILL.md                   # Skill 主文件（必需）
├── README.md                  # 说明文档
└── scripts/                   # 实用脚本目录
    └── patent_finder.py       # 专利检索辅助工具
```

## 安装方式

### 1. 项目级 Skill（推荐）

将此目录放置到项目的 `.claude/skills/` 下：
```bash
cp -r patent-search /path/to/your/project/.claude/skills/
```

### 2. 个人 Skill

将此目录放置到个人 Skills 目录：
```bash
cp -r patent-search ~/.claude/skills/
```

## 使用方式

当你向 Claude 提问以下类似问题时，此 Skill 会自动激活：

- "帮我检索一下动态批处理相关的专利"
- "这个技术方案具备新颖性吗？"
- "评估一下我们的产品是否有专利侵权风险"
- "分析一下竞争对手的专利布局"
- "检索一下 Transformer 相关的专利"
- "帮我写一个专利检索报告"

## 主要功能

### 1. 专利检索

支持多数据库检索：
- Google Patents（全球专利）
- USPTO（美国专利）
- EPO（欧洲专利）
- CNIPA（中国专利）
- Patentscope（PCT国际专利）

### 2. 专利性评估

- 新颖性评估
- 创造性评估
- 技术方案对比分析

### 3. 侵权风险分析

- 高风险专利识别
- 规避建议
- 许可谈判建议

### 4. 技术全景分析

- 技术领域专利分布
- 主要专利权人分析
- 技术发展趋势

## 脚本使用

### 专利检索辅助

```bash
# 检索动态批处理相关专利
python3 scripts/patent_finder.py --keywords "dynamic batching scheduling" --database google

# 检索特定公司的专利
python3 scripts/patent_finder.py --company "OpenAI" --keywords "LLM inference"

# 检索特定技术领域的专利
python3 scripts/patent_finder.py --ipc "G06N" --years 2020-2025
```

## 检索报告示例

```
# 专利检索报告

## 检索概要
- 检索主题：动态批处理优化技术
- 检索目的：新颖性检索
- 检索数据库：Google Patents, USPTO, CNIPA

## 检索结果
- 检索到专利：156篇
- 去重后：89篇
- 高度相关：12篇
- 中度相关：23篇

## 结论
该技术方案具备一定的新颖性，但需规避以下高风险专利...
```

## 典型用法举例

```
# 新颖性检索
"帮我检索一下自适应调度相关的专利，评估这个技术能否申请专利"

# 侵权风险评估
"我们的AI推理系统可能涉及哪些专利侵权风险？"

# 竞争对手分析
"帮我分析一下 NVIDIA 在 GPU 调度优化方面的专利布局"

# 技术全景
"检索一下大模型推理优化技术的专利分布情况"
```

## 版本

- v1.0.0 (2026-02-03): 初始发布
