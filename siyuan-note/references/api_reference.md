# SiYuan Note API Reference

Complete API reference for SiYuan Note API (v1.3.5+).

## Configuration

- **Default Endpoint**: `http://127.0.0.1:6806`
- **Authentication**: Header `Authorization: Token <token>`
- **Method**: All endpoints use POST
- **Content-Type**: `application/json`

## Response Format

All responses use this format:

```json
{
  "code": 0,
  "msg": "",
  "data": {}
}
```

- `code`: 0 for success, non-zero for error
- `msg`: Empty on success, error message on failure
- `data`: Varies by endpoint (`{}`, `[]`, or `null`)

## Notebooks

### List Notebooks
- **Endpoint**: `/api/notebook/lsNotebooks`
- **Params**: `{}`
- **Returns**: Array of notebook objects with `id`, `name`, `icon`, `sort`, `closed`

### Create Notebook
- **Endpoint**: `/api/notebook/createNotebook`
- **Params**: `{"name": "Notebook name"}`
- **Returns**: Created notebook object

### Delete Notebook
- **Endpoint**: `/api/notebook/removeNotebook`
- **Params**: `{"notebook": "<notebook-id>"}`
- **Returns**: `null`

### Rename Notebook
- **Endpoint**: `/api/notebook/renameNotebook`
- **Params**: `{"notebook": "<notebook-id>", "name": "New name"}`
- **Returns**: `null`

### Open/Close Notebook
- **Endpoints**: `/api/notebook/openNotebook`, `/api/notebook/closeNotebook`
- **Params**: `{"notebook": "<notebook-id>"}`
- **Returns**: `null`

### Get/Set Notebook Config
- **Endpoints**: `/api/notebook/getNotebookConf`, `/api/notebook/setNotebookConf`
- **Params**: `{"notebook": "<id>", "conf": {...}}` (set only)
- **Returns**: Config object

## Documents

### Create Document with Markdown
- **Endpoint**: `/api/filetree/createDocWithMd`
- **Params**:
```json
{"notebook": "<notebook-id>", "path": "/foo/bar", "markdown": "# Title\nContent"}
```
- **Returns**: Created document ID
- **Note**: Same path will create new doc, not overwrite

### Rename Document
- **Endpoints**: `/api/filetree/renameDoc`, `/api/filetree/renameDocByID`
- **Params**:
  - By path: `{"notebook": "<id>", "path": "/doc.sy", "title": "New title"}`
  - By ID: `{"id": "<doc-id>", "title": "New title"}`
- **Returns**: `null`

### Delete Document
- **Endpoints**: `/api/filetree/removeDoc`, `/api/filetree/removeDocByID`
- **Params**:
  - By path: `{"notebook": "<id>", "path": "/doc.sy"}`
  - By ID: `{"id": "<doc-id>"}`
- **Returns**: `null`

### Move Documents
- **Endpoints**: `/api/filetree/moveDocs`, `/api/filetree/moveDocsByID`
- **Params**:
  - By path: `{"fromPaths": ["/doc.sy"], "toNotebook": "<id>", "toPath": "/"}`
  - By ID: `{"fromIDs": ["<doc-id>"], "toID": "<target-id>"}`
- **Returns**: `null`

### Resolve Paths
- **Endpoints**:
  - `/api/filetree/getHPathByPath` - Get human-readable path from path
  - `/api/filetree/getHPathByID` - Get human-readable path from ID
  - `/api/filetree/getIDByHPath` - Get ID from human-readable path
- **Params**: Varies by endpoint
- **Returns**: Path or ID

## Blocks

### Insert/Prepend/Append Blocks
- **Endpoints**: `/api/block/insertBlock`, `/api/block/prependBlock`, `/api/block/appendBlock`
- **Params**:
```json
{
  "dataType": "markdown",
  "data": "Content",
  "parentID": "<parent-block-id>",
  "previousID": "<previous-block-id>"  // optional, for insert
}
```
- **Returns**: Array of operation results

### Update Block
- **Endpoint**: `/api/block/updateBlock`
- **Params**:
```json
{
  "id": "<block-id>",
  "data": "<div>Updated HTML</div>",
  "dataType": "dom"
}
```
- **Returns**: Array of operation results

### Delete Block
- **Endpoint**: `/api/block/deleteBlock`
- **Params**: `{"id": "<block-id>"}`
- **Returns**: Array of operation results

### Move Block
- **Endpoint**: `/api/block/moveBlock`
- **Params**:
```json
{
  "id": "<block-id>",
  "previousID": "<prev-block-id>",
  "parentID": "<parent-block-id>"
}
```
- **Returns**: Array of operation results

### Fold/Unfold Block
- **Endpoints**: `/api/block/foldBlock`, `/api/block/unfoldBlock`
- **Params**: `{"id": "<block-id>"}`
- **Returns**: `null`

### Get Block Kramdown
- **Endpoint**: `/api/block/getBlockKramdown`
- **Params**: `{"id": "<block-id>"}`
- **Returns**: `{"id": "...", "kramdown": "..."}`

### Get Child Blocks
- **Endpoint**: `/api/block/getChildBlocks`
- **Params**: `{"id": "<parent-id>"}`
- **Returns**: Array of block objects with `id`, `type`, `subType`

### Transfer Block Ref
- **Endpoint**: `/api/block/transferBlockRef`
- **Params**:
```json
{
  "fromID": "<def-block-id>",
  "toID": "<target-block-id>",
  "refIDs": ["<ref-block-id>"]  // optional
}
```
- **Returns**: `null`

## Attributes

### Set Block Attributes
- **Endpoint**: `/api/attr/setBlockAttrs`
- **Params**:
```json
{
  "id": "<block-id>",
  "attrs": {"custom-attr1": "value"}
}
```
- **Note**: Custom attributes must be prefixed with `custom-`
- **Returns**: `null`

### Get Block Attributes
- **Endpoint**: `/api/attr/getBlockAttrs`
- **Params**: `{"id": "<block-id>"}`
- **Returns**: Attribute object

## Search (SQL)

### Execute SQL Query
- **Endpoint**: `/api/query/sql`
- **Params**: `{"stmt": "SELECT * FROM blocks WHERE content LIKE '%keyword%' LIMIT 10"}`
- **Returns**: Array of result objects

Common query examples:
- Search content: `SELECT * FROM blocks WHERE content LIKE '%keyword%'`
- Get docs in notebook: `SELECT * FROM blocks WHERE box='<notebook-id>' AND type='d'`
- Get block by ID: `SELECT * FROM blocks WHERE id='<block-id>'`

### Flush Transaction
- **Endpoint**: `/api/sqlite/flushTransaction`
- **Params**: None
- **Returns**: `null`

## Export

### Export Markdown
- **Endpoint**: `/api/export/exportMdContent`
- **Params**: `{"id": "<doc-id>"}`
- **Returns**: `{"hPath": "...", "content": "..."}`

### Export Resources
- **Endpoint**: `/api/export/exportResources`
- **Params**:
```json
{
  "paths": ["/path1", "/path2"],
  "name": "export-name"  // optional
}
```
- **Returns**: `{"path": "temp/export/xxx.zip"}`

## Assets

### Upload Asset
- **Endpoint**: `/api/asset/upload`
- **Params**: Multipart form with `file`
- **Returns**: Updated block with asset URL

## Templates

### Render Template
- **Endpoint**: `/api/template/render`
- **Params**: `{"id": "<doc-id>", "path": "/path/to/template.md"}`
- **Returns**: Rendered content

## File Operations

### Get File
- **Endpoint**: `/api/file/getFile`
- **Params**: `{"path": "/data/<notebook-id>/file.sy"}`
- **Returns**: File content (status 200) or JSON error (status 202)

### Put File
- **Endpoint**: `/api/file/putFile`
- **Params**: Multipart form with `path`, `file`, optional `isDir`, `modTime`
- **Returns**: `null`

### Remove/Rename File
- **Endpoints**: `/api/file/removeFile`, `/api/file/renameFile`
- **Params**: `{"path": "/data/...", "newPath": "/data/..."}` (rename only)
- **Returns**: `null`

### List Files
- **Endpoint**: `/api/file/readDir`
- **Params**: `{"path": "/data/<notebook-id>/folder"}`
- **Returns**: Array of file objects

## System

### Get Version
- **Endpoint**: `/api/system/version`
- **Params**: None
- **Returns**: Version string

### Get Current Time
- **Endpoint**: `/api/system/currentTime`
- **Params**: None
- **Returns`: Unix timestamp (ms)

## Notification

### Push Message
- **Endpoint**: `/api/notification/pushMsg`
- **Params**: `{"msg": "message", "timeout": 7000}`
- **Returns**: `{"id": "message-id"}`

## Common Block Types

- `d`: Document
- `h`: Heading (subType: h1, h2, h3, h4, h5, h6)
- `p`: Paragraph
- `l`: List (subType: u = unordered, o = ordered, t = task)
- `b`: Blockquote
- `c`: Code block
- `s`: Super block
- `i`: Inline math
- `m`: Math block

## Database Schema

### Blocks Table

Common fields:
- `id`: Block ID
- `box`: Notebook ID
- `type`: Block type
- `content`: Block content
- `created`: Creation timestamp
- `updated`: Update timestamp
- `hpath`: Human-readable path
