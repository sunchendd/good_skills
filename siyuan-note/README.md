# SiYuan Note Skill - Enhanced Version

Enhanced integration for SiYuan Note with batch operations, organization tools, and backup features.

## Setup

1. Configure environment variables:
```bash
export SIYUAN_HOST="http://127.0.0.1:6806"
export SIYUAN_TOKEN="your-api-token"
```

2. Test connection:
```bash
python3 scripts/siyuan.py test
```

## Features

### 1. Basic Operations

```bash
# List notebooks
python3 scripts/siyuan.py ls-notebooks

# Create notebook
python3 scripts/siyuan.py create-notebook "My Notebook"

# List documents
python3 scripts/siyuan.py ls-docs "notebook-id"

# Create document
python3 scripts/siyuan.py create-doc "nb-id" "/path" "# Title\nContent"
```

### 2. Search & Find

```bash
# Search content
python3 scripts/siyuan.py search "keyword"

# Find documents by pattern
python3 scripts/siyuan.py find "test"

# Find duplicates
python3 scripts/siyuan.py find-duplicates
```

### 3. Export & Backup

```bash
# Export single document
python3 scripts/siyuan.py export-md "doc-id" output.md

# Export entire notebook
python3 scripts/siyuan.py export-notebook "nb-id" ./backup

# Export all notebooks
python3 scripts/siyuan.py export-all-notebooks ~/backup

# Quick backup script
./scripts/backup_all.sh ~/my_backup
```

### 4. Statistics & Organization

```bash
# Get statistics
python3 scripts/siyuan.py stats

# Run organization helper
./scripts/organize.sh
```

## Helper Scripts

### backup_all.sh
Quick backup of all notebooks to a timestamped directory.

```bash
./scripts/backup_all.sh
./scripts/backup_all.sh ~/custom_backup_path
```

### organize.sh
Analyze your SiYuan setup and find areas for improvement.

```bash
./scripts/organize.sh
```

## Common Workflows

### Workflow 1: Regular Backup

```bash
# Set up cron job for daily backups
0 2 * * * /path/to/backup_all.sh ~/backups/siyuan_$(date +\%Y\%m\%d)
```

### Workflow 2: Content Migration

```bash
# 1. Export all from old instance
python3 scripts/siyuan.py export-all-notebooks ./export

# 2. Review and organize exported files
# 3. Import organized content to new instance
```

### Workflow 3: Content Cleanup

```bash
# 1. Analyze
./scripts/organize.sh

# 2. Find test documents
python3 scripts/siyuan.py find "test"

# 3. Delete unwanted documents
# (manually review before deletion)
```

## API Coverage

- ✅ Notebook management (list, create, delete)
- ✅ Document operations (list, create, delete, export)
- ✅ Content search and query
- ✅ Batch operations
- ✅ Statistics and analysis
- ✅ Duplicate detection

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SIYUAN_HOST` | No | `http://127.0.0.1:6806` | SiYuan server URL |
| `SIYUAN_TOKEN` | Yes | - | API authentication token |

## Troubleshooting

**Connection failed (401)**
- Verify SIYUAN_TOKEN is correct
- Get token from SiYuan → Settings → About

**Connection failed (503)**
- Ensure SiYuan is running
- Check SIYUAN_HOST URL

**Export failed**
- Check write permissions for output directory
- Ensure document ID is valid

## Tips

1. Always test connection first: `python3 scripts/siyuan.py test`
2. Use `stats` to understand your note structure
3. Regular backups prevent data loss
4. Use `find-duplicates` to identify redundant content
5. Organize with subfolders for better navigation

## License

MIT License - Free to use and modify.

## Support

For SiYuan Note API documentation: https://github.com/siyuan-note/siyuan
