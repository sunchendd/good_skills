# good_skills

这个仓库现在按两类内容维护：

- 根目录：自研 skill、共享代码、发布脚本、文档
- [opensource](./opensource/)：第三方开源 skill 的安装来源和批量安装脚本

## 当前策略

### 自研 skill

保留在仓库根目录，例如：

- [daily-newsletter](./daily-newsletter/)
- [arxiv-daily](./arxiv-daily/)
- [vibe-daily](./vibe-daily/)
- [bili-daily](./bili-daily/)
- [wuyu-xiaohongshu](./wuyu-xiaohongshu/)
- [daily-digest](./daily-digest/)
- [weekly-report](./weekly-report/)
- [siyuan-daily](./siyuan-daily/)
- [super-fitness](./super-fitness/)
- [super-wardrobe](./super-wardrobe/)

### 开源 skill

不再把第三方 skill 源码长期 vendoring 到仓库里，而是通过 `skills.sh` 推荐方式统一安装。

安装清单在：

- [opensource/sources.txt](./opensource/sources.txt)

批量安装脚本：

- Windows: [opensource/install.ps1](./opensource/install.ps1)
- macOS / Linux: [opensource/install.sh](./opensource/install.sh)

批量更新脚本：

- Windows: [opensource/update.ps1](./opensource/update.ps1)
- macOS / Linux: [opensource/update.sh](./opensource/update.sh)

## 使用方式

Windows:

```powershell
pwsh .\opensource\install.ps1
```

macOS / Linux:

```bash
bash ./opensource/install.sh
```

更新已安装的开源 skill：

Windows:

```powershell
pwsh .\opensource\update.ps1
```

macOS / Linux:

```bash
bash ./opensource/update.sh
```

## CLI 安装示例

```bash
npx good-skills add https://github.com/vercel-labs/skills --skill find-skills
npx good-skills add vercel-labs/skills --skill find-skills
npx good-skills install vercel-labs/skills@find-skills
npx good-skills install git-commit --platform codex
```

## 思源目录结构

自动写入思源时，为了避开中文路径乱码，统一使用下面这四条英文目录：

```text
AI Automation/Content Creation/Wuyu Daily Report/...
AI Automation/Efficiency Review/Daily Summary/...
AI Automation/Efficiency Review/Weekly Report/...
AI Automation/Knowledge Base Maintenance/Knowledge Daily Report/...
```

## 常用环境变量

```bash
export DEEPSEEK_API_KEY="your-deepseek-api-key"
export QQ_EMAIL_PASSWORD="your-qq-smtp-code"
export GITHUB_TOKEN="your-github-token"
export SIYUAN_HOST="http://127.0.0.1:6806"
export SIYUAN_TOKEN="your-siyuan-token"
export SIYUAN_AUTOMATION_NOTEBOOK="AI Automation"
export EMAIL_SENDER="your-email@example.com"
export EMAIL_RECIPIENTS="first@example.com,second@example.com"
export BARK_TOKEN="your-bark-token"
```

## 说明

- `shared/` 中维护自研 skill 复用的公共逻辑
- `packages/cli/` 中维护 `good-skills` 的 npm CLI 包
- `docs/plans/` 中保留设计与实施记录
