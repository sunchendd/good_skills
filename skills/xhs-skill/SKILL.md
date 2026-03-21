---
name: xhs-skill
description: >-
  小红书检索与发布工具。Use when "小红书检索", "发布小红书", "xhs MCP", "搜索小红书内容".
  基于本地 MCP Server 或 xhs-mcp CLI，支持搜索、查看、发布三种操作。
---

# 小红书检索与发布

封装本地 xhs-mcp 或 mcporter MCP 接口，提供 search / view / publish 三个命令。

## 前提条件

- 本地运行 xhs-mcp 服务或 mcporter MCP 服务器
- Python 3.8+

## 使用方式

### 搜索笔记

```bash
python skills/xhs-skill/run_xhs.py search "产品评测"
```

### 查看笔记详情

```bash
python skills/xhs-skill/run_xhs.py view <note_id>
```

### 发布笔记

```bash
python skills/xhs-skill/run_xhs.py publish \
  --title "自动化发布测试" \
  --content file:post.md \
  --images img1.jpg img2.jpg \
  --tags 测评 自动化
```

## 重要规则

- **ALWAYS** 发布前预览内容，确认后再发布
- **NEVER** 未经用户确认直接发布内容
- 搜索结果默认返回前 10 条，可通过 `--limit` 参数调整
