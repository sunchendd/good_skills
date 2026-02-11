---
name: siyuan-note
description: >-
  SiYuan Note API integration for managing personal knowledge base. Use when performing operations on SiYuan Note instances:
  (1) Create, read, update, delete notes and documents, (2) Search and query content using SQL,
  (3) Manage notebooks and file structure, (4) Work with blocks, attributes, and assets,
  (5) Export documents or resources. Requires SIYUAN_HOST and SIYUAN_TOKEN environment variables or user-provided configuration.
---

# SiYuan Note

## Quick Start

Configure SiYuan Note connection:

```bash
export SIYUAN_HOST="http://127.0.0.1:6806"
export SIYUAN_TOKEN="your-api-token"
```

API token is found in SiYuan Settings → About.

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

```bash
# List notebooks
python3 scripts/siyuan.py ls-notebooks

# Create notebook
python3 scripts/siyuan.py create-notebook "My Notebook"

# Create document
python3 scripts/siyuan.py create-doc "notebook-id" "/my-path" "# Title\nContent"

# Delete document
python3 scripts/siyuan.py delete-doc "doc-id"

# Search
python3 scripts/siyuan.py search "keyword"

# Export markdown
python3 scripts/siyuan.py export-md "doc-id"
```

## Common Workflows

### Create New Note

1. Get notebook ID: `ls-notebooks`
2. Create document: `create-doc <notebook-id> /path/note-name "# Title\nContent"`

### Search and Retrieve

1. Search: `sql` endpoint with WHERE clause
2. Get block content: `getBlockKramdown` for full content
3. Export: `exportMdContent` for entire doc

### Bulk Operations

Use SQL queries to identify IDs, then batch process with individual API calls.

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

## Reference

See [references/api_reference.md](references/api_reference.md) for complete API documentation including:
- All endpoints and parameters
- Database schema
- Common block types
- Advanced operations

## Error Handling

Common error codes:
- `-1`: Parameter/execution error
- `404`: Resource not found
- `403`: Permission denied

Check `msg` field for details.
