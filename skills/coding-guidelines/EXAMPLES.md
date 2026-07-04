# Examples

具体代码示例，展示四条原则在 good_skills 项目场景中的实际应用。每条原则配 1-2 个 bad/good 对比。

---

## 1. 先想后写 / Think Before Coding

### Example 1: Hidden Assumptions about API Response

**User Request:** "从 arXiv API 获取最新论文"

**❌ Bad（默默假设）**

```python
def fetch_papers(category='cs.AI'):
    resp = requests.get(f'http://export.arxiv.org/api/query?search_query=cat:{category}&max_results=10')
    feed = xml.etree.ElementTree.fromstring(resp.text)

    papers = []
    for entry in feed.findall('{http://www.w3.org/2005/Atom}entry'):
        papers.append({
            'title': entry.find('{http://www.w3.org/2005/Atom}title').text.strip(),
            'summary': entry.find('{http://www.w3.org/2005/Atom}summary').text.strip(),
            'authors': [a.find('{http://www.w3.org/2005/Atom}name').text
                       for a in entry.findall('{http://www.w3.org/2005/Atom}author')],
        })
    return papers
```

**Problems:**
- 假设 API 总是返回有效 XML（网络错误、限流、空结果都没处理）
- 假设所有 entry 都有 title/summary（缺失时 `NoneType.strip()` crash）
- 假设 author 都有 name 子元素
- 假设默认 10 条够用，没确认用户需求

**✅ Good（先澄清）**

```
从 arXiv API 获取论文前，需要确认几个点：

1. 范围：只要 cs.AI 还是多个分类（cs.LG、cs.CL 等）？
2. 数量：每次获取多少条？10 条够吗？
3. 筛选：需要按时间排序还是相关性？需要过滤条件吗？
4. 容错：API 挂了或返回空怎么处理？

当前 arxiv-daily skill 用的是多分类 + DeepSeek 评分筛选模式，
如果你只是想快速获取几篇，我可以给一个更简单的版本。

你更偏向哪种？
```

### Example 2: Multiple Interpretations of "Send Notification"

**User Request:** "发送通知"

**❌ Bad（默默选一种）**

```python
def send_notification(title, body):
    # 假设用户要 Bark 推送
    requests.post(f'{BARK_SERVER}/push', json={
        'title': title, 'body': body, 'device_key': BARK_KEY
    })
```

**✅ Good（列出选项）**

```
"发送通知"有几种方式，你想用哪个？

1. Bark 推送 — iOS 即时通知（当前 skill 的默认方式）
2. 邮件 — QQ 邮箱 SMTP，支持 HTML 格式
3. 两个都要 — Bark + Email 双通道

参考：当前 good_skills 的自动化 skill 都是 Bark + Email 双通道。
你的场景是什么？
```

---

## 2. 极简优先 / Simplicity First

### Example 1: Over-Abstracting a Simple Config Loader

**User Request:** "写个函数从 .env 加载 API key"

**❌ Bad（过度抽象）**

```python
import os
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

class EnvSource(Enum):
    FILE = 'file'
    OS = 'os'
    BOTH = 'both'

@dataclass
class EnvConfig:
    file_path: Path = Path('.env')
    source: EnvSource = EnvSource.BOTH
    required_keys: set = field(default_factory=set)
    defaults: Dict[str, Any] = field(default_factory=dict)
    transformers: Dict[str, Callable] = field(default_factory=dict)

class EnvLoader:
    def __init__(self, config: EnvConfig = EnvConfig()):
        self.config = config
        self._cache: Dict[str, str] = {}

    def _load_file(self) -> Dict[str, str]:
        if not self.config.file_path.exists():
            return {}
        result = {}
        with open(self.config.file_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                result[k.strip()] = v.strip().strip('"').strip("'")
        return result

    def get(self, key: str) -> Optional[str]:
        if key in self._cache:
            return self._cache[key]

        value = None
        if self.config.source in (EnvSource.FILE, EnvSource.BOTH):
            value = self._load_file().get(key)
        if value is None and self.config.source in (EnvSource.OS, EnvSource.BOTH):
            value = os.environ.get(key)
        if value is None:
            value = self.config.defaults.get(key)

        if value is not None and key in self.config.transformers:
            value = self.config.transformers[key](value)

        self._cache[key] = value
        return value
```

**Problems:**
- 200 行业务逻辑，实际只需要 10 行
- Enum 枚举了三种来源，实际只用一种
- dataclass 配置 + 缓存 + transformer，全是一次性代码
- 需求只是"从 .env 取一个值"

**✅ Good（极简）**

```python
import os

def load_env(path='.env'):
    """Load .env file into os.environ. Call once at startup."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

# Usage: load_env() then os.environ['DEEPSEEK_API_KEY']
```

### Example 2: Speculative Error Handling

**User Request:** "调用 DeepSeek API 做文本摘要"

**❌ Bad（防御过当）**

```python
from openai import OpenAI

def summarize(text: str) -> str:
    try:
        client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url='https://api.deepseek.com/v1'
        )
    except Exception as e:
        raise RuntimeError(f'Client init failed: {e}')

    try:
        response = client.chat.completions.create(
            model='deepseek-chat',
            messages=[{'role': 'user', 'content': f'Summarize: {text}'}],
            max_tokens=200,
            temperature=0.7,
        )

        if not response.choices:
            raise ValueError('API returned no choices')
        if not response.choices[0].message.content:
            raise ValueError('API returned empty content')

        return response.choices[0].message.content.strip()

    except openai.APIError as e:
        logger.error(f'API error: {e}')
        raise
    except openai.APIConnectionError as e:
        logger.error(f'Connection error: {e}')
        raise
    except openai.RateLimitError as e:
        logger.error(f'Rate limited: {e}')
        raise
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        raise RuntimeError(f'Summarize failed: {e}')
```

**Problems:**
- Client 初始化几乎不会失败，加了 try/except
- 每个异常类型单独 catch，但处理方式完全一样
- 空 choices/content 不会发生（DeepSeek 总是返回 content）
- 50 行业务逻辑，实际需要 10 行

**✅ Good（只处理必要的）**

```python
from openai import OpenAI

client = OpenAI(
    api_key=os.environ['DEEPSEEK_API_KEY'],
    base_url='https://api.deepseek.com/v1'
)

def summarize(text: str) -> str:
    response = client.chat.completions.create(
        model='deepseek-chat',
        messages=[{'role': 'user', 'content': f'Summarize: {text}'}],
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()
```

---

## 3. 外科手术式改动 / Surgical Changes

### Example 1: Drive-by Refactoring While Adding a Feature

**User Request:** "给 super-wardrobe 加上防晒建议"

**❌ Bad（顺手改了太多）**

```diff
- def generate_outfit(weather_data):
+ def generate_outfit(weather_data: dict, user_prefs: dict = None) -> str:
+     """Generate daily outfit recommendation based on weather.
+
+     Args:
+         weather_data: Weather API response dict
+         user_prefs: Optional user style preferences
+
+     Returns:
+         Markdown-formatted outfit recommendation
+     """
      temp = weather_data['main']['temp']
-     humidity = weather_data['main']['humidity']
+     humidity = weather_data.get('main', {}).get('humidity', 50)
      condition = weather_data['weather'][0]['main']

      # Top
-     if temp > 30:
-         top = '短袖T恤'
-     elif temp > 20:
-         top = '长袖衬衫'
+     if temp > 32:
+         top = '速干运动T恤（防晒）'
+     elif temp > 28:
+         top = '轻薄短袖衬衫（UPF 50+）'
+     elif temp > 22:
+         top = '长袖亚麻衬衫'
+     elif temp > 15:
+         top = '薄款卫衣'
      else:
-         top = '毛衣 + 外套'
+         top = '针织衫 + 轻薄外套'

      # Bottom
-     if temp > 30:
-         bottom = '短裤'
-     elif temp > 20:
-         bottom = '薄长裤'
+     ...
+
+     # 新增：防晒建议
+     if condition == 'Clear' and temp > 25:
+         outfit += '\n- ☀️ 建议涂抹 SPF50 防晒霜，戴太阳镜'

      return outfit
```

**Problems:**
- 加了 type hints（没人要求）
- 加了 docstring（没人要求）
- 改了 `.get()` 防御式取值（风格不统一）
- 改了温度阈值（重构了原有逻辑）
- 加了 `user_prefs` 参数（投机功能）
- 顺手改了 else 分支的描述文案

**✅ Good（只加防晒建议）**

```diff
      # Bottom
      if temp > 30:
          bottom = '短裤'
      elif temp > 20:
          bottom = '薄长裤'
+
+     # 防晒建议
+     if condition == 'Clear' and temp > 25:
+         outfit += '\n- ☀️ 紫外线较强，建议涂抹防晒霜'

      return outfit
```

### Example 2: Style Drift While Fixing a Bug

**User Request:** "修复 bark_client 中 timeout 没生效的 bug"

**❌ Bad（格式不一致）**

```diff
- def bark_notify(title, body, sound='default'):
-     url = f'{BARK_SERVER}/push'
-     resp = requests.post(url, json={
-         'title': title,
-         'body': body,
-         'device_key': BARK_KEY,
-         'sound': sound,
-     })
+ def bark_notify(title: str, body: str, sound: str = "default") -> bool:
+     """Send Bark push notification.
+     
+     Args:
+         title: Notification title
+         body: Notification content
+         sound: Sound name (default: "default")
+     
+     Returns:
+         True if notification sent successfully
+     """
+     response = requests.post(
+         f"{BARK_SERVER}/push",
+         json={
+             "title": title,
+             "body": body,
+             "device_key": BARK_KEY,
+             "sound": sound,
+         },
+         timeout=10
+     )
+     return response.status_code == 200
```

**Problems:**
- 加了 type hints（没人要求）
- 加了 docstring（没人要求）
- 改了引号风格 `'` → `"`
- 改了变量名 `resp` → `response`
- 改了返回值类型 `None` → `bool`
- 实际修复只需要加 `timeout=10`

**✅ Good（只修 bug）**

```diff
-     resp = requests.post(url, json={
+     resp = requests.post(url, json={
          'title': title,
          'body': body,
          'device_key': BARK_KEY,
          'sound': sound,
-     })
+     }, timeout=10)
```

---

## 4. 目标驱动执行 / Goal-Driven Execution

### Example 1: Vague vs. Verifiable Fix

**User Request:** "daily-newsletter 有时候发不出邮件"

**❌ Bad（模糊目标，直接改）**

```
我来优化邮件发送逻辑。
[改了 80 行：加重试、加超时、改端口、换连接方式...]
应该好了。
```

**Problems:**
- 没搞清楚"有时候"是哪种错误
- 没复现就动手改
- 改完不知道是否真的修好了
- 可能改了无关代码

**✅ Good（先定义成功标准）**

```
"有时候发不出"需要先定位。我先看一下日志：

1. 查日志定位根因
   → 验证：找到 3 次发送失败的具体错误信息（超时？认证？限流？）

2. 复现问题
   → 验证：用同样的条件手动调用，确认能复现

3. 针对性修复
   → 验证：连续发送 10 封邮件，9/10 以上成功

4. 回归检查
   → 验证：常规内容的邮件格式正确，Bark 通知不受影响

先做第 1 步，看看日志里的错误是什么？
```

### Example 2: Test-First Bug Fix

**User Request:** "archive.sh 不能正确处理带下划线格式的日期（fitness_20260323.md）"

**❌ Bad（直接改，没验证）**

```bash
# 直接改了正则，没测边界情况
sed -i 's/_[0-9]\{8\}/_[0-9]\{8\}/g' archive.sh
```

**✅ Good（先写测试）**

```bash
# 1. 先创建一个最小复现
mkdir -p /tmp/test-archive
touch /tmp/test-archive/fitness_20260323.md
touch /tmp/test-archive/outfit_2026-03-23.md

# 2. 跑当前的 archive.sh → 验证它挂了
bash scripts/archive.sh /tmp/test-archive
# 期望：fitness_20260323.md 没被正确归档
# 实际：确实没被归档 → bug 已复现 ✓

# 3. 修 date extraction 正则
# 4. 再跑 → 两个文件都被正确归档 ✓
# 5. 清理测试数据
```

---

## Anti-Patterns Summary

| 原则 | 反模式 | 正确做法 |
|------|--------|---------|
| 先想后写 | 默默假设 API 返回格式/字段 | 列出假设，不确定就澄清 |
| 极简优先 | 50 行需求写 200 行抽象 | 一个函数搞定，需要时再加 |
| 外科手术式改动 | 修 timeout 顺手改引号/type hints/docstring | 只改 timeout，风格保持一致 |
| 目标驱动 | "我来优化一下" | "第1步：查日志定位 → 第2步：复现 → 第3步：修复 → 第4步：回归" |

## 关键认知

"过度复杂"的例子不是明显错的——它们遵循设计模式和最佳实践。问题是 **时机**：在需要之前就加了复杂度，导致：

- 代码更难理解
- 引入更多 bug
- 实现时间更长
- 测试更难写

"简单"的版本：
- 更容易理解
- 实现更快
- 更容易测试
- 等真正需要复杂时再重构

**好代码解决今天的问题，而不是提前解决明天的问题。**
