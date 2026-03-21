---
name: xhs-skill
description: 小红书检索与发布 Skill（基于本地 MCP Server 或 xhs-mcp CLI）。
---

# xhs-skill

提供：search / view / publish 三个命令，封装本地 xhs-mcp 或 mcporter MCP 接口。

用法示例：

```
python run_xhs.py search "产品评测"
python run_xhs.py view 1234567890
python run_xhs.py publish --title "自动化发布测试" --content file:post.md --images img1.jpg img2.jpg --tags 测评 自动化
```
