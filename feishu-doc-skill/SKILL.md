---
name: feishu-doc-skill
description: Create, update, and manage Feishu cloud documents (docx) and convert local notes into cloud docs. Use when the user asks to save content to a Feishu document, create a shared cloud doc, or export workspace notes to Feishu.
---

# Feishu Cloud Document Skill

Purpose
- Provide concise, automatable instructions so Claude can create, update, or append content to Feishu cloud documents.

When to use
- The user explicitly asks to create or update a Feishu cloud doc (for example: “把这份说明写入飞书云文档”, “在飞书新建文档并粘贴以下内容”，或“把 workspace/installed-skills-summary.md 上传为飞书文档”) .
- The user requests exporting local workspace notes or generated summaries into a Feishu doc.

Core usage patterns (short)
- Create a new doc with a title and initial markdown content.
- Append content to an existing doc by doc_token or title lookup.
- Replace/overwrite a doc section when requested.

Examples (what the user might say)
- “创建一个飞书云文档，标题为：已安装技能汇总，内容为：<粘贴内容>”
- “把 /path/to/your/workspace/.openclaw/workspace/installed-skills-summary.md 的内容写入飞书文档并共享链接”
- “在现有文档 D1urdGd8gozam4xoIi4cQgc1njh 后面追加下面内容：<内容>”

Behavior rules (brief)
- Always confirm the target doc (create new vs append) if ambiguous.
- When creating a doc, include title, short description, and the content body. Confirm visibility (share/public) if the user asks.
- Do not attempt to upload large binary attachments without explicit permission.

Minimal implementation notes
- This skill assumes environment has an authenticated Feishu client (or that the agent can call the feishu_doc tool). Use the feishu_doc tool to create/append documents when available.

Examples of internal commands (for operator/automation)
- feishu_doc.create(title="...", content="...")
- feishu_doc.append(doc_token="D...", content="...")
- feishu_doc.read(doc_token="D...")
Reference: keep this SKILL.md short; put long examples or templates in references/ when needed.