# SiYuan Note Batch Backup Example

#!/bin/bash

# Configuration
SIYUAN_HOST="${SIYUAN_HOST:-http://127.0.0.1:6806}"
SIYUAN_TOKEN="${SIYUAN_TOKEN:-}"
BACKUP_DIR="${1:-$HOME/Desktop/siyuan_backup_$(date +%Y%m%d_%H%M%S)}"

# Check token
if [ -z "$SIYUAN_TOKEN" ]; then
    echo "Error: SIYUAN_TOKEN not set"
    echo "Usage: export SIYUAN_TOKEN='your-token'"
    echo "       ./backup_all.sh [backup_directory]"
    exit 1
fi

# Export function
export_all() {
    python3 "$(dirname "$0")/scripts/siyuan.py" export-all-notebooks "$BACKUP_DIR"
}

# Run backup
echo "📦 SiYuan Note Backup"
echo "===================="
echo "Host: $SIYUAN_HOST"
echo "Backup to: $BACKUP_DIR"
echo ""

export_all

echo ""
echo "✅ Backup completed!"
echo "📂 $BACKUP_DIR"
