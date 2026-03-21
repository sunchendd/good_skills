# Good Skills

Self-developed AI agent skills with Python automation scripts.

## Skills

| Skill | Description |
|-------|-------------|
| [daily-newsletter](skills/daily-newsletter/) | 每日科技早报。27+ RSS 源聚合，智能分类，质量评分，邮件+Bark 推送 |
| [arxiv-daily](skills/arxiv-daily/) | 每日 arXiv AI 论文精选。DeepSeek 评分筛选，中文摘要 |
| [vibe-daily](skills/vibe-daily/) | 每日 AI 编程工具动态。Cursor/Claude Code/Copilot 更新和技巧 |
| [super-wardrobe](skills/super-wardrobe/) | 每日穿搭建议。实时天气 + AI 搭配方案 |
| [super-fitness](skills/super-fitness/) | 三个月科学减脂计划。每日 AI 生成运动+饮食方案 |
| [weekly-report](skills/weekly-report/) | 自动周报生成。汇总日历+GitHub+思源，AI 分析 |
| [daily-digest](skills/daily-digest/) | 每日日志聚合。汇总所有 daily skill 输出 |
| [patent-search](skills/patent-search/) | 专利搜索。多库检索、新颖性评估、侵权分析 |
| [patent-specialist](skills/patent-specialist/) | 专利撰写。技术交底书 → 权利要求书 |

## Install

```bash
git clone https://github.com/sunchendd/good-skills.git
cd good-skills
./install.sh
cp .env.example .env  # Fill in API keys
```

`install.sh` will:
1. Install self-developed skills via `npx skills add .`
2. Install [superpowers](https://github.com/obra/superpowers) workflows
3. Install curated open-source skills (Next.js, React best practices)
4. Install Python dependencies

## Usage

Skills are used by AI agents (Claude Code, etc.) automatically via SKILL.md trigger matching.

Python automation scripts can also be run directly:

```bash
python skills/daily-newsletter/run_daily_newsletter.py
python skills/arxiv-daily/run_arxiv_daily.py
python skills/super-wardrobe/run_wardrobe.py
```

## License

MIT
