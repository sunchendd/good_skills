# Skill 优化设计文档

**日期**: 2026-03-03  
**范围**: 3 个优化方向

---

## 方向一：内容抓取 Skills 时间过滤优化

### 问题

- `bili-daily`: `search_bili()` 抓取后没有时间过滤，B站 API 默认按综合排序，可能返回数年前内容
- `bili-daily` 小红书部分：通过 Google 搜索无日期限制，关键词含 "2026" 但不可靠
- `vibe-daily` B站部分：同样无时间过滤

### 设计方案

**两层过滤策略（推荐）**：

1. **API 层**：B站搜索加 `order=pubdate`（按最新发布时间排序），确保优先返回新内容
2. **后处理层**：过滤 `pubdate >= today - 7天`，硬性丢弃过时内容
3. **小红书/Google 搜索**：在关键词后附加 `after:YYYY-MM-DD`（Google 支持），或用 Brave Search 的 `freshness` 参数

**时间窗口**: 默认 7 天，可通过常量 `MAX_AGE_DAYS = 7` 配置

**关键改动**（`bili-daily/run_bili_daily.py`）:
```python
CUTOFF = datetime.datetime.now() - datetime.timedelta(days=7)

# 1. API 排序
url += "&order=pubdate"

# 2. 后处理
videos = [v for v in all_videos if v['pubdate'] >= CUTOFF.strftime('%Y-%m-%d')]
```

**小红书搜索改动**：关键词改为动态生成含年月的查询：
```python
this_month = datetime.datetime.now().strftime("%Y年%m月")
keywords = [f"小红书 AI工具 {this_month}", ...]
# 附加 Google after: 参数
url = f"https://www.google.com/search?q={kw_enc}&tbs=qdr:w"  # qdr:w = past week
```

---

## 方向二：vibe-daily 新增 X/Twitter + 小红书数据源

### 设计方案

**X/Twitter**：因无官方 API 且有封锁，采用 **Nitter 公共镜像 + Brave 搜索** 双路径：
1. 主路径：通过 Brave Search API 搜索 `from:@AnthropicAI OR from:@opencode_ai site:twitter.com/x.com`
2. 备用路径：通过 SerpAPI/Google 搜索近 7 天推文快照
3. 关注账号列表：
   - `@AnthropicAI`（Claude 官方）
   - `@dario_amodei`（Anthropic CEO）
   - `@OpenCodeAI`（OpenCode）
   - `@github`（Copilot 更新）
   - `@cursor_ai`（Cursor）

**小红书**：与 bili-daily 同方案，通过 Google/Brave `site:xiaohongshu.com` 搜索 + `tbs=qdr:w`（一周内）

**新增函数**（`vibe-daily/run_vibe_daily.py`）：
```python
CREATOR_ACCOUNTS = [
    {"handle": "AnthropicAI",  "label": "Anthropic"},
    {"handle": "dario_amodei", "label": "Dario Amodei"},
    {"handle": "opencode_ai",  "label": "OpenCode"},
    {"handle": "cursor_ai",    "label": "Cursor"},
]

def fetch_creator_updates() -> list[dict]:
    """通过 Brave Search 搜索创始人/官方账号近期推文"""
    ...

def fetch_xiaohongshu_vibe() -> list[dict]:
    """搜索小红书 Vibe Coding 相关内容"""
    ...
```

---

## 方向三：npx good-skills 易用性优化

### 发现的问题

1. **安装不完整**：`installSkill()` 只下载 `SKILL.md`，遗漏 `references/`、`scripts/`、`assets/` 目录
2. **无重试机制**：网络失败直接报错，不重试
3. **Symlink bug**：`fs.lstatSync(dest).isSymbolicLink().catch(...)` - `lstatSync` 是同步函数，不返回 Promise
4. **版本号硬编码**：`index.js` 写死 `'0.1.0'`，与 `package.json` 的 `0.1.1` 不同步
5. **find 不能直接安装**：`find` 搜索结果没有 install 提示
6. **无进度反馈**：安装时只有 `...` 没有文件级进度

### 设计方案

**优先级排序（P0 必做，P1 重要）**：

**P0 - 修复功能性 bug**：
- `installer.js`: 修复 symlink bug
- `index.js`: 从 `package.json` 动态读取版本号

**P0 - 完整安装 SKILL.md + manifest.json + references/**：
- `installer.js`: 扩展 `getSkillFilesRemote()` 以下载 `references/` 目录
- 策略：用 GitHub Contents API 列出目录文件，再批量下载

**P1 - 重试机制**：
```javascript
async function fetchWithRetry(url, retries = 3, delay = 1000) {
  for (let i = 0; i < retries; i++) {
    try { return await fetchText(url); }
    catch (e) {
      if (i === retries - 1) throw e;
      await sleep(delay * (i + 1)); // exponential backoff
    }
  }
}
```

**P1 - find 命令改进**：
- 搜索结果显示技能描述
- 末尾提示：`Run: npx good-skills install <name>`

**P1 - 进度显示**：
- 安装时显示 `[1/3] Downloading SKILL.md...`
- 完成后汇总：`✅ Installed git-commit (3 files)`

### 测试计划

```bash
# 测试基础安装
npx good-skills install git-commit --platform claude

# 测试有 references/ 的 skill
npx good-skills install github-pr-review --platform github-copilot

# 测试错误处理（不存在的 skill）
npx good-skills install nonexistent-skill

# 测试查找
npx good-skills find "pr review"
```

---

## 实施顺序

1. **bili-daily 时间过滤** (30 分钟)
2. **vibe-daily 时间过滤 + B站过滤** (20 分钟)  
3. **vibe-daily X/Twitter + 小红书数据源** (45 分钟)
4. **npx CLI P0 bugfix** (30 分钟)
5. **npx CLI P1 重试 + 进度 + find** (45 分钟)
6. **测试验证** (30 分钟)
