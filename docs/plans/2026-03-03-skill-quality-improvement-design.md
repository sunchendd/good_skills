# Good Skills 全面质量提升 设计文档

**目标**：提升 good_skills 项目整体质量——运行时可靠性、AI 调用精准度、文档一致性，以及 superpowers 的默认安装体验。

---

## 背景

### 已知问题
1. **运行时失败**：super-wardrobe 天气 API（wttr.in）调用失败无优雅降级
2. **触发不准**：部分 SKILL.md 描述模糊，AI 未能正确识别调用时机
3. **文档不一致**：CLAUDE.md 与 `.github/copilot-instructions.md` 存在潜在差异
4. **superpowers 安装体验**：install.sh 没有引导用户安装 superpowers 插件

### 设计目标
- 所有 Python 脚本具备基本错误处理和重试能力
- 所有 SKILL.md 满足触发质量标准
- CLAUDE.md 与 copilot-instructions.md 完全一致
- install.sh 引导用户完成 superpowers 安装

---

## 四条工作流

### 流 1：Python 脚本可靠性

**范围**：含 Python 脚本的 skill：
- super-wardrobe（天气 + 穿搭）
- super-fitness（健身计划）
- vibe-daily, daily-digest, daily-newsletter
- bili-daily, arxiv-daily, weekly-report
- news-tts

**标准修复项**：
- HTTP 调用加 `try/except` + `timeout` 参数
- wttr.in 天气 API：最多 3 次重试（指数退避），失败时打印明确错误并退出
- API Key 缺失时打印友好提示（不是 KeyError 崩溃）
- DeepSeek/OpenAI 调用加错误处理，区分网络错误和认证错误

**wttr.in 修复示例**：
```python
import time, urllib.error

def fetch_weather(retries=3) -> dict:
    for attempt in range(retries):
        try:
            url = f"https://wttr.in/{CITY_EN}?format=j1"
            req = urllib.request.urlopen(url, timeout=15)
            return json.loads(req.read())
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"天气 API 连续 {retries} 次失败: {e}") from e
```

---

### 流 2：SKILL.md 触发质量

**标准格式**（每个 SKILL.md 的 description 字段需满足）：
```
<是什么>. 使用时机：<触发场景>. <关键能力>.
```

**审核清单**（~60 个 skill）：
- [ ] description 包含明确的触发动词/场景
- [ ] 有 "Use when" 或 "使用时机" 说明
- [ ] 关键词足够多，覆盖用户可能说的不同说法
- [ ] 无模糊描述（如"通用工具"、"各种场景"）

**高优先级**（已知有问题的）：
- super-wardrobe, super-fitness：需补充"每日"、"推送"、"穿搭"等触发词
- news-tts：补充"语音"、"播报"
- vibe-daily, daily-digest, weekly-report：区分使用场景避免混淆

---

### 流 3：CLAUDE.md + copilot-instructions.md 优化

**检查项**：
1. 两个文件是否对齐（技能列表、触发词、安装命令）
2. 技能触发表是否覆盖所有现有 skill（目前约 60 个，表中可能缺失）
3. 包名引用：`@good-skills/cli` → 应为 `good-skills`
4. 平台路径是否最新（新增了 Cursor、Windsurf）
5. 拼写和逻辑错误

**修复策略**：以 CLAUDE.md 为主，copilot-instructions.md 保持同步更新。

---

### 流 4：install.sh 默认安装 superpowers

**方案**：安装脚本完成后，若检测到 Claude Code 环境（`~/.claude` 存在），打印 superpowers 安装提示。

```bash
# 安装完成后提示
if [ -d "$HOME/.claude" ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  💡 推荐：在 Claude Code 中安装 Superpowers 插件"
    echo "  在 Claude Code 终端依次运行："
    echo "  /plugin marketplace add obra/superpowers-marketplace"
    echo "  /plugin install superpowers@superpowers-marketplace"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
fi
```

同时更新 README.md 安装说明，将 superpowers 作为推荐步骤。

---

## 交付物

| 交付物 | 说明 |
|--------|------|
| 修复的 Python 脚本 | 含错误处理、重试、友好提示 |
| 更新的 SKILL.md | 触发质量达标 |
| 更新的 CLAUDE.md | 覆盖全部 skill，修正错误 |
| 更新的 copilot-instructions.md | 与 CLAUDE.md 同步 |
| 更新的 install.sh | 含 superpowers 安装提示 |
| 更新的 README.md | 安装说明含 superpowers |
| git commits（按流分组） | feat/fix 提交 |

---

## 实现顺序

1. **流 3**（CLAUDE.md/copilot-instructions）：最快，先完成，建立基准
2. **流 2**（SKILL.md 触发质量）：依赖流 3 的标准
3. **流 1**（Python 脚本）：最重，逐文件修复
4. **流 4**（install.sh）：最简单，最后完成
