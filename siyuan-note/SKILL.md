---
name: siyuan-note
description: >-
  SiYuan Note API integration for managing personal knowledge base. Use when performing operations on SiYuan Note instances:
  (1) Create, read, update, delete notes and documents, (2) Search and query content using SQL,
  (3) Manage notebooks and file structure, (4) Work with blocks, attributes, and assets,
  (5) Export documents or resources, (6) Batch operations and backups, (7) Document organization.
  Requires SIYUAN_HOST and SIYUAN_TOKEN environment variables or user-provided configuration.
---

# SiYuan Note

## Quick Start

### 本地访问（默认）

```bash
export SIYUAN_HOST="http://127.0.0.1:6806"
export SIYUAN_TOKEN="your-api-token"
```

### 公网访问（远程服务器）

```YUAN_HOST="bash
export SIhttp://www.sunchendong.com:6806"
export SIYUAN_TOKEN="your-api-token"
```

> ⚠️ **安全提示**：公网访问时 Token 会明文传输，建议配置 HTTPS（需反向代理配置 SSL 证书）。

API token is found in SiYuan Settings → About.

**Test connection:**
```bash
python3 scripts/siyuan.py test
```

## Core Operations

### Notebooks

List all notebooks:
```bash
curl -X POST ${SIYUAN_HOST}/api/notebook/lsNotebooks \
  -H "Authorization: Token ${SIYUAN_TOKEN}" \
  -H "Content-Type: application/json" -d '{}'
```

Create notebook:
```bash
curl -X POST ${SIYUAN_HOST}/api/notebook/createNotebook \
  -H "Authorization: Token ${SIYUAN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Notebook"}'
```

Delete notebook by ID:
```bash
curl -X POST ${SIYUAN_HOST}/api/notebook/removeNotebook \
  -H "Authorization: Token ${SIYUAN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"notebook": "notebook-id"}'
```

### Documents

List documents in notebook:
```bash
curl -X POST ${SIYUAN_HOST}/api/filetree/listDocsByPath \
  -H "Authorization: Token ${SIYUAN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"notebook": "notebook-id", "path": "/"}'
```

Create document with Markdown:
```bash
curl -X POST ${SIYUAN_HOST}/api/filetree/createDocWithMd \
  -H "Authorization: Token ${SIYUAN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"notebook": "notebook-id", "path": "/my-note", "markdown": "# Title\nContent"}'
```

Delete document by ID:
```bash
curl -X POST ${SIYUAN_HOST}/api/filetree/removeDocByID \
  -H "Authorization: Token ${SIYUAN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"id": "doc-id"}'
```

Export document as Markdown:
```bash
curl -X POST ${SIYUAN_HOST}/api/export/exportMdContent \
  -H "Authorization: Token ${SIYUAN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"id": "doc-id"}'
```

### Search

Search content with SQL query:
```bash
curl -X POST ${SIYUAN_HOST}/api/query/sql \
  -H "Authorization: Token ${SIYUAN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stmt": "SELECT * FROM blocks WHERE content LIKE '\''%keyword%'\'' LIMIT 10"}'
```

### Blocks

Get block content:
```bash
curl -X POST ${SIYUAN_HOST}/api/block/getBlockKramdown \
  -H "Authorization: Token ${SIYUAN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"id": "block-id"}'
```

Append block to document:
```bash
curl -X POST ${SIYUAN_HOST}/api/block/appendBlock \
  -H "Authorization: Token ${SIYUAN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"dataType": "markdown", "data": "New content", "parentID": "doc-id"}'
```

## Using the Helper Script

The bundled Python script provides common operations:

### Basic Operations

```bash
# Test connection
python3 scripts/siyuan.py test

# List notebooks
python3 scripts/siyuan.py ls-notebooks

# Create notebook
python3 scripts/siyuan.py create-notebook "My Notebook"

# Delete notebook
python3 scripts/siyuan.py delete-notebook "notebook-id"

# List documents in notebook
python3 scripts/siyuan.py ls-docs "notebook-id"

# Create document
python3 scripts/siyuan.py create-doc "notebook-id" "/my-path" "# Title\nContent"

# Delete document
python3 scripts/siyuan.py delete-doc "doc-id"

# Search
python3 scripts/siyuan.py search "keyword"

# Export markdown
python3 scripts/siyuan.py export-md "doc-id" /path/to/save.md
```

### Batch Operations

```bash
# Export all documents to directory
python3 scripts/siyuan.py export-all-notebooks "/backup/path"

# Get statistics
python3 scripts/siyuan.py stats

# Find duplicate documents
python3 scripts/siyuan.py find-duplicates

# Find documents by name pattern
python3 scripts/siyuan.py find "pattern"

# Export documents from a specific notebook
python3 scripts/siyuan.py export-notebook "notebook-id" "/output/path"
```

## Common Workflows

### Workflow 1: Create New Note

```bash
# 1. List notebooks to get ID
python3 scripts/siyuan.py ls-notebooks

# 2. Create document in notebook
python3 scripts/siyuan.py create-doc "notebook-id" "/my-new-note" "# My New Note\n\nContent here"
```

### Workflow 2: Search and Export

```bash
# 1. Search for content
python3 scripts/siyuan.py search "keyword"

# 2. Get document ID from results and export
python3 scripts/siyuan.py export-md "doc-id" "/output/note.md"
```

### Workflow 3: Batch Backup

```bash
# Export all notebooks to backup directory
python3 scripts/siyuan.py export-all-notebooks "~/Desktop/siyuan_backup_$(date +%Y%m%d)"
```

### Workflow 4: Organize Documents

```bash
# 1. List documents in notebook
python3 scripts/siyuan.py ls-docs "notebook-id"

# 2. Find documents by pattern
python3 scripts/siyuan.py find "test" --notebook "notebook-id"

# 3. Delete unwanted documents in batch
echo "id1\nid2\nid3" | xargs -I {} python3 scripts/siyuan.py delete-doc {}
```

### Workflow 5: Create Structured Documentation

```bash
# Create new notebook
python3 scripts/siyuan.py create-notebook "Project Docs"

# Get notebook ID (or use directly)
NOTEBOOK_ID="new-notebook-id"

# Create folder structure
python3 scripts/siyuan.py create-doc "$NOTEBOOK_ID" "/Documentation" "# Documentation"
python3 scripts/siyuan.py create-doc "$NOTEBOOK_ID" "/Documentation/Getting Started" "# Getting Started"
python3 scripts/siyuan.py create-doc "$NOTEBOOK_ID" "/Documentation/API Reference" "# API Reference"
python3 scripts/siyuan.py create-doc "$NOTEBOOK_ID" "/Documentation/Examples" "# Examples"
```

### Workflow 6: Analyze and Reorganize Notes

```bash
# Get notebook statistics
python3 scripts/siyuan.py stats

# Find potential duplicates
python3 scripts/siyuan.py find-duplicates

# Export all notes for analysis
python3 scripts/siyuan.py export-all-notebooks "backup_dir"

# Then import organized notes as needed
```

## API Response Format

All endpoints return:

```json
{
  "code": 0,
  "msg": "",
  "data": {...}
}
```

Check `code === 0` for success. `msg` contains error details on failure.

## Error Handling

Common error codes:
- `-1`: Parameter/execution error
- `401`: Unauthorized (invalid token)
- `403`: Permission denied
- `404`: Resource not found
- `503`: Service unavailable (SiYuan not running)

Check `msg` field for details.

## Advanced Features

### Working with Subfolders

```bash
# Create document in subfolder
python3 scripts/siyuan.py create-doc "notebook-id" "/category/subcategory/doc-name" "# Title"

# List documents in subfolder
python3 scripts/siyuan.py ls-docs "notebook-id" "/category"
```

### Batch Export with Structure

Export all documents preserving folder structure:
```bash
python3 scripts/siyuan.py export-all-notebooks "/backup" --hierarchy
```

### Custom SQL Queries

```bash
# Find documents by title
curl -X POST ${SIYUAN_HOST}/api/query/sql \
  -H "Authorization: Token ${SIYUAN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"stmt": "SELECT * FROM blocks WHERE type = \"d\" AND content LIKE \"My Title%\""}'

# Get document tree
curl -X POST ${SIYUAN_HOST}/api/filetree/getDocTree \
  -H "Authorization: Token ${SIYUAN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"notebook": "notebook-id"}'
```

## Reference

See [references/api_reference.md](references/api_reference.md) for complete API documentation including:
- All endpoints and parameters
- Database schema
- Common block types
- Advanced operations

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SIYUAN_HOST` | SiYuan Note server URL | `http://127.0.0.1:6806` (本地) 或 `http://www.sunchendong.com:6806` (公网) |
| `SIYUAN_TOKEN` | API authentication token | (required) |

## 公网访问配置

### 场景
如果你在外网需要访问运行在家中或服务器上的 SiYuan Note：

```bash
# 公网域名访问
export SIYUAN_HOST="http://www.sunchendong.com:6806"
export SIYUAN_TOKEN="你的Token"
```

### 安全建议

1. **使用 HTTPS**（推荐）：配置 Nginx/Caddy 反向代理，启用 SSL/TLS 加密
2. **限制 IP 访问**：在防火墙或 Nginx 中限制可访问的 IP 段
3. **定期更换 Token**：如发现异常，及时在 SiYuan 设置中重置 Token
4. **避免长期暴露**：如长期不在外网使用，建议关闭公网访问

### HTTPS 配置示例（Nginx）

```nginx
server {
    listen 443 ssl;
    server_name www.sunchendong.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;

    location / {
        proxy_pass http://127.0.0.1:6806;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

配置 HTTPS 后使用：
```bash
export SIYUAN_HOST="https://www.sunchendong.com"
```

## Troubleshooting

### Connection Issues

1. **401 Unauthorized**: Check token in SiYuan Settings → About
2. **503 Service Unavailable**: Ensure SiYuan is running
3. **Connection Refused**: Check SIYUAN_HOST URL

### File Not Found

1. Verify notebook ID is correct
2. Check document path exists
3. Use `ls-docs` to list available documents

## Tips

1. **Always backup** before batch operations
2. Use descriptive names for documents and folders
3. Organize by topic/project using subfolders
4. Regular export for backup
5. Use search to find content quickly
6. Test connection first with `test` command
7. Use batch operations for efficiency
