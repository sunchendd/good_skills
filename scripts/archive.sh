#!/bin/bash
# 归档各 skill 生成的 md/txt 文件到 archive/YYYY-MM/
# 每天自动运行（daily-digest 之前），保持工作目录整洁

REPO="$(cd "$(dirname "$0")/.." && pwd)"
ARCHIVE_ROOT="$REPO/archive"

move_files() {
  local src_dir="$1"
  local pattern="$2"   # glob pattern, e.g. "*.md"
  local skill="$3"     # label for logging

  [ -d "$src_dir" ] || return

  while IFS= read -r -d '' file; do
    # 从文件名或修改时间提取 YYYY-MM
    filename=$(basename "$file")
    # 尝试从文件名提取日期 (格式: *_20260323* 或 *_2026-03-23*)
    if [[ "$filename" =~ ([0-9]{4})[-_]?([0-9]{2})[-_]?([0-9]{2}) ]]; then
      month="${BASH_REMATCH[1]}-${BASH_REMATCH[2]}"
    else
      month=$(date -r "$file" "+%Y-%m")
    fi

    dest_dir="$ARCHIVE_ROOT/$month/$skill"
    mkdir -p "$dest_dir"
    mv "$file" "$dest_dir/"
    echo "[archive] $skill/$filename → archive/$month/$skill/"
  done < <(find "$src_dir" -maxdepth 1 -name "$pattern" -print0)
}

echo "=== Good Skills Archive $(date '+%Y-%m-%d %H:%M') ==="

move_files "$REPO/skills/super-fitness/daily_tasks"      "fitness_*.md"         "super-fitness"
move_files "$REPO/skills/super-wardrobe/outfits"         "outfit_*.md"          "super-wardrobe"
move_files "$REPO/skills/daily-newsletter/newsletters"   "daily_newsletter_*"   "daily-newsletter"
move_files "$REPO/skills/arxiv-daily/newsletters"        "arxiv_*.md"           "arxiv-daily"
move_files "$REPO/skills/vibe-daily/newsletters"         "vibe_*.md"            "vibe-daily"
move_files "$REPO/skills/weekly-report/reports"          "weekly_*.md"          "weekly-report"
move_files "$REPO/skills/daily-digest/logs"              "daily_*.md"           "daily-digest"

echo "=== 归档完成 ==="
