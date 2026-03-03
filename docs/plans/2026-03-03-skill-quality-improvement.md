# Good Skills 全面质量提升 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 全面提升 good_skills 项目质量——修复运行时失败、提高 AI 触发精准度、统一文档、引导安装 superpowers。

**Architecture:** 四条并行工作流：(1) CLAUDE.md/copilot-instructions.md 同步修复，(2) 缺失 skill 的 SKILL.md 触发质量补全，(3) Python 脚本错误处理加固，(4) install.sh 添加 superpowers 安装引导。

**Tech Stack:** Python 3, urllib, bash, Markdown

---

## Task 1：修复 CLAUDE.md + copilot-instructions.md

**Files:**
- Modify: `CLAUDE.md`
- Modify: `.github/copilot-instructions.md`

### Step 1：审查 CLAUDE.md 中缺失的 skill

目前 CLAUDE.md 技能触发表**缺少**以下 skill（目录中存在但未在触发表中）：
- `arxiv-daily`、`bili-daily`、`chess-advisor`
- `daily-digest`、`daily-newsletter`
- `github-watcher`
- `super-fitness`、`super-wardrobe`
- `tts-skill`
- `vibe-daily`、`weekly-report`
- `wuyu-xiaohongshu`、`xhs-skill`

在 CLAUDE.md 触发表末尾（"Platform-Specific" 章节之后）新增 "Daily & Personal" 章节：

```markdown
### Daily & Personal

| Skill | Invoke when user says | Do NOT use when |
|-------|----------------------|-----------------|
| `super-wardrobe` | "今天穿什么", "穿搭建议", "wardrobe", "衣橱" | 查询天气但不需要穿搭 |
| `super-fitness` | "健身计划", "今天运动", "减脂", "fitness plan" | 泛泛健康咨询 |
| `vibe-daily` | "AI 编程工具动态", "Claude Code 更新", "vibe coding 资讯" | 非 AI 编程类新闻 |
| `daily-digest` | "每日日志", "今日汇总", "daily digest" | 单个 skill 输出 |
| `daily-newsletter` | "科技早报", "每日新闻", "RSS 聚合", "daily newsletter" | 单主题搜索 |
| `bili-daily` | "B站 AI 视频", "今日 B 站", "bili daily" | 搜索特定 B 站视频（用 bili-fetch）|
| `arxiv-daily` | "今日 arXiv", "AI 论文精选", "每日论文" | 搜索特定论文 |
| `weekly-report` | "周报", "本周总结", "weekly report" | 每日汇报 |
| `github-watcher` | "GitHub 仓库监控", "版本更新通知" | 手动查看 PR/commits |
| `chess-advisor` | "象棋", "棋盘分析", "chess", "走法建议" | 国际象棋（非中国象棋）|
| `tts-skill` | "文字转语音", "TTS", "朗读", "语音合成" | 已有 news-tts 时 |
| `wuyu-xiaohongshu` | "无语哥", "小红书文案", "奇葩新闻文案" | 普通小红书内容 |
| `xhs-skill` | "小红书检索", "发布小红书", "xhs MCP" | 生成文案（用 wuyu-xiaohongshu）|
```

### Step 2：更新 copilot-instructions.md 与 CLAUDE.md 同步

`.github/copilot-instructions.md` 目前只有 56 行，是 CLAUDE.md（236 行）的简化版。
将其**完整替换**为 CLAUDE.md 的全部内容（去掉 Claude Code 专属的第一行说明）：

在 `.github/copilot-instructions.md` 文件开头保留：
```
Good Skills 项目是 AI 助手技能的集合，支持多种 AI 编程平台（Claude Code、GitHub Copilot、OpenCode 等）。
```
然后将 CLAUDE.md 中的全部技能触发表、架构说明、安装命令全部复制过来（包括 Task 1 Step 1 新增的章节）。

### Step 3：提交

```bash
git add CLAUDE.md .github/copilot-instructions.md
git commit -m "docs(claude): add missing skills to trigger table and sync copilot-instructions

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 2：修复 super-wardrobe 天气 API 可靠性（最高优先级）

**Files:**
- Modify: `super-wardrobe/wardrobe_advisor.py:44-65`（`fetch_weather` 函数）

### Step 1：找到 `fetch_weather` 函数

当前代码（`wardrobe_advisor.py` 约第 47-65 行）：
```python
def fetch_weather() -> dict:
    """获取杭州今日天气"""
    url = f"https://wttr.in/{CITY_EN}?format=j1"
    req = urllib.request.urlopen(url, timeout=15)
    data = json.loads(req.read())
    ...
```

### Step 2：替换为带重试的实现

在文件顶部 `import` 区域确认已有 `import time`（若没有则添加），然后将 `fetch_weather` 替换为：

```python
def fetch_weather(retries: int = 3) -> dict:
    """获取杭州今日天气，失败自动重试"""
    import urllib.error
    url = f"https://wttr.in/{CITY_EN}?format=j1"
    last_error = None
    for attempt in range(retries):
        try:
            req = urllib.request.urlopen(url, timeout=15)
            data = json.loads(req.read())
            cur = data['current_condition'][0]
            today = data['weather'][0]
            tomorrow = data['weather'][1] if len(data['weather']) > 1 else today

            hourly = today.get('hourly', [])
            max_rain_chance = max(int(h.get('chanceofrain', 0)) for h in hourly) if hourly else 0
            max_snow_chance = max(int(h.get('chanceofsnow', 0)) for h in hourly) if hourly else 0

            weather_code = cur.get('weatherCode', '116')
            weather_desc = WEATHER_CODE_MAP.get(weather_code, cur['weatherDesc'][0]['value'])

            return {
                'temp_now': int(cur['temp_C']),
                'feels_like': int(cur['FeelsLikeC']),
                'temp_max': int(today['maxtempC']),
                'temp_min': int(today['mintempC']),
                'humidity': int(cur['humidity']),
                'wind_kmph': int(cur['windspeedKmph']),
                'weather_desc': weather_desc,
                'rain_chance': max_rain_chance,
                'snow_chance': max_snow_chance,
                'uv_index': int(cur.get('uvIndex', 0)),
                'date': today['date'],
                'sunrise': today['astronomy'][0]['sunrise'],
                'sunset': today['astronomy'][0]['sunset'],
            }
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
            last_error = e
            if attempt < retries - 1:
                wait = 2 ** attempt
                logger.warning(f"天气 API 第 {attempt + 1} 次失败，{wait}s 后重试: {e}")
                time.sleep(wait)
    raise RuntimeError(f"天气 API 连续 {retries} 次请求失败: {last_error}")
```

### Step 3：在 `run_wardrobe.py` 的主流程捕获天气失败

找到 `run_wardrobe.py` 中调用 `fetch_weather()` 的地方，确保外层有 `try/except RuntimeError`，失败时打印清晰消息并退出（`sys.exit(1)`）。若已有 `try/except Exception`，则已覆盖，无需修改。

### Step 4：验证修改

```bash
cd super-wardrobe
python -c "from wardrobe_advisor import fetch_weather; print(fetch_weather())"
```

Expected：输出天气字典，或打印重试日志后 RuntimeError。

### Step 5：提交

```bash
git add super-wardrobe/wardrobe_advisor.py
git commit -m "fix(super-wardrobe): add retry logic to weather API fetch

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 3：加固其他 Python 脚本的 HTTP 错误处理

**范围**：vibe-daily、daily-digest、bili-daily、arxiv-daily、weekly-report

**Files:**
- Modify: `vibe-daily/run_vibe_daily.py`
- Modify: `daily-digest/run_daily_digest.py`
- Modify: `bili-daily/run_bili_daily.py`
- Modify: `arxiv-daily/arxiv_fetcher.py`
- Modify: `weekly-report/run_weekly_report.py`

### Step 1：统一检查每个文件的 `urlopen` 调用

对每个文件，找到所有 `urllib.request.urlopen(...)` 调用，检查是否有 `try/except`。

运行：
```bash
grep -n "urlopen\|requests.get" vibe-daily/run_vibe_daily.py daily-digest/run_daily_digest.py bili-daily/run_bili_daily.py arxiv-daily/arxiv_fetcher.py weekly-report/run_weekly_report.py
```

### Step 2：对每个**裸调用**（无 try/except）包裹错误处理

标准模式：
```python
import urllib.error

try:
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())
except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
    logger.warning(f"请求失败，跳过: {e}")
    return []  # 或 return None，按函数返回类型决定
```

逐文件执行：
1. `vibe-daily/run_vibe_daily.py` — 检查第 43 行附近
2. `daily-digest/run_daily_digest.py` — 检查第 26、71 行附近
3. `bili-daily/run_bili_daily.py` — 检查第 22、27 行附近
4. `arxiv-daily/arxiv_fetcher.py` — 检查 `fetch_arxiv_papers` 函数
5. `weekly-report/run_weekly_report.py` — 检查第 89、94 行附近

### Step 3：检查 API Key 缺失时的提示

对所有脚本，在文件入口处（`main()` 函数或顶层）确保：
```python
if not os.environ.get("DEEPSEEK_API_KEY"):
    print("❌ 错误：缺少环境变量 DEEPSEEK_API_KEY")
    sys.exit(1)
```

若已有检查则跳过。

### Step 4：提交

```bash
git add vibe-daily/ daily-digest/ bili-daily/ arxiv-daily/ weekly-report/
git commit -m "fix(scripts): add HTTP error handling to daily scripts

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 4：SKILL.md 触发质量审核与修复

**Files:**
- Modify: `super-fitness/SKILL.md`
- Modify: `super-wardrobe/SKILL.md`
- Modify: `news-tts/SKILL.md`
- Modify: `tts-skill/SKILL.md`
- Modify: `vibe-daily/SKILL.md`
- Modify: `daily-digest/SKILL.md`
- Modify: `chess-advisor/SKILL.md`
- 以及其他 description 模糊的 skill

### Step 1：逐一检查各 SKILL.md 的 `description` 字段

标准格式：
```
<是什么>. 使用时机：当用户说 "<触发词1>"、"<触发词2>"。<关键能力>.
```

审查重点：
- description 是否包含用户可能说的自然语言触发词
- 是否能和同类 skill 区分（如 news-tts vs tts-skill）

### Step 2：修复 description 模糊的 skill

**super-wardrobe/SKILL.md**（补充触发词）：
```yaml
description: 每日穿搭建议推送。使用时机：当用户说"今天穿什么"、"穿搭建议"、"帮我搭配衣服"。自动获取杭州实时天气，AI 生成上衣/裤子/鞋/帽/手表/配色/是否带伞，邮件+Bark 推送。
```

**super-fitness/SKILL.md**（补充触发词）：
```yaml
description: 三个月科学减脂计划推送。使用时机：当用户说"今天健身"、"运动计划"、"减脂建议"、"每日健身打卡"。AI 生成个性化运动+饮食方案，邮件+Bark 推送。
```

**tts-skill/SKILL.md**（与 news-tts 区分）：
```yaml
description: 通用文字转语音工具（离线 edge-tts）。使用时机：当用户说"把这段文字转成语音"、"TTS"、"生成语音文件"。支持 14 个中文音色、情感风格、语速调节，输出 MP3。区别于 news-tts（news-tts 是新闻播报+Telegram 推送）。
```

**chess-advisor/SKILL.md**（明确触发条件）：
```yaml
description: 中国象棋顾问。使用时机：当用户说"分析这个棋局"、"象棋走法"、"下一步怎么走"、上传棋盘图片时。分析棋盘截图识别局面，给出最佳走法和战术分析。
```

**vibe-daily/SKILL.md**（明确与 daily-newsletter 区别）：
```yaml
description: 每日 AI 编程工具动态推送。使用时机：当用户说"今日 vibe coding 资讯"、"Claude Code 有什么更新"、"AI 编程工具动态"。专注 Cursor/Claude Code/Copilot 更新和 vibe coding 技巧，区别于 daily-newsletter（泛科技新闻）。
```

### Step 3：验证每个 SKILL.md 格式合法（YAML frontmatter 无语法错误）

```bash
for d in super-wardrobe super-fitness tts-skill chess-advisor vibe-daily; do
  python3 -c "
import sys
with open('$d/SKILL.md') as f: content = f.read()
assert content.startswith('---'), 'Missing frontmatter in $d'
print('OK: $d')
"
done
```

### Step 4：提交

```bash
git add super-wardrobe/SKILL.md super-fitness/SKILL.md tts-skill/SKILL.md chess-advisor/SKILL.md vibe-daily/SKILL.md daily-digest/SKILL.md
git commit -m "docs(skills): improve trigger descriptions for better AI invocation

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## Task 5：install.sh 添加 superpowers 安装引导

**Files:**
- Modify: `install.sh`（末尾 `echo ""` 之前插入）
- Modify: `README.md`（安装说明章节）

### Step 1：在 install.sh 末尾添加 superpowers 提示

找到 install.sh 最后的 `print_info "To uninstall, run: ./uninstall.sh"` 行之后插入：

```bash
# Superpowers plugin prompt for Claude Code users
if [ -d "$HOME/.claude" ] || [ -d "$HOME/Library/Application Support/Claude" ]; then
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  💡 推荐：安装 Superpowers 工作流插件（Claude Code）${NC}"
    echo -e "${YELLOW}  在 Claude Code 终端中依次运行以下两条命令：${NC}"
    echo ""
    echo -e "${BLUE}  /plugin marketplace add obra/superpowers-marketplace${NC}"
    echo -e "${BLUE}  /plugin install superpowers@superpowers-marketplace${NC}"
    echo ""
    echo -e "${YELLOW}  安装后重启 Claude Code 即可获得完整工作流技能。${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
fi
echo ""
```

### Step 2：在 README.md 安装说明中补充 superpowers 步骤

在 README.md 的安装章节（找到 `./install.sh --all` 代码块之后）添加：

```markdown
### 推荐：安装 Superpowers 工作流插件

安装 good_skills 后，建议在 **Claude Code** 中安装 Superpowers 插件，获得完整的从需求到实现的 AI 工作流：

```bash
# 在 Claude Code 终端中运行：
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

安装完成后重启 Claude Code，输入 `/brainstorming 描述你的需求` 即可启动完整工作流。
```

### Step 3：验证 install.sh 语法

```bash
bash -n install.sh && echo "Syntax OK"
```

Expected: `Syntax OK`

### Step 4：提交

```bash
git add install.sh README.md
git commit -m "feat(install): add superpowers plugin install prompt after setup

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

---

## 执行顺序

| 顺序 | Task | 理由 |
|------|------|------|
| 1 | Task 1：CLAUDE.md/copilot-instructions | 最快，无代码风险 |
| 2 | Task 5：install.sh superpowers | 简单，独立 |
| 3 | Task 2：super-wardrobe 天气修复 | 最高影响的 bug |
| 4 | Task 4：SKILL.md 触发质量 | 依赖对 skill 内容的理解 |
| 5 | Task 3：其他 Python 脚本 | 最重，放最后 |
