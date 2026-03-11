#!/bin/bash

# SiYuan Note Organization Helper
# Helps you find duplicates, test documents, and organize your notes

SIYUAN_SCRIPT="$(dirname "$0")/siyuan.py"

echo "🧹 SiYuan Note Organization Helper"
echo "=================================="
echo ""

# Check connection
echo "1️⃣ Testing connection..."
python3 "$SIYUAN_SCRIPT" test || exit 1
echo ""

# Get statistics
echo "2️⃣ Notebook Statistics"
echo "----------------------"
python3 "$SIYUAN_SCRIPT" stats
echo ""

# Find duplicates
echo "3️⃣ Finding Duplicate Documents"
echo "------------------------------"
python3 "$SIYUAN_SCRIPT" find-duplicates
echo ""

# Find test documents
echo "4️⃣ Finding Test Documents"
echo "------------------------"
python3 "$SIYUAN_SCRIPT" find "test"
python3 "$SIYUAN_SCRIPT" find "api"
echo ""

echo "📋 Summary:"
echo "- Review the duplicates list above"
echo "- Consider merging or removing duplicate content"
echo "- Remove test documents if they're no longer needed"
echo "- Use 'ls-docs <notebook-id>' to explore each notebook in detail"
