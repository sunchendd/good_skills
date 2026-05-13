#!/usr/bin/env python3
"""Clean up broken skill symlinks across all AI agent config directories."""

import os
import shutil
import sys
from pathlib import Path

HOME = Path.home()

AGENT_SKILL_DIRS = [
    HOME / ".agent" / "skills",
    HOME / ".agents" / "skills",
    HOME / ".claude" / "skills",
    HOME / ".config" / "opencode" / "skill",
    HOME / ".config" / "opencode" / "skills",
    HOME / ".opencode" / "skills",
    HOME / ".copilot" / "skills",
    HOME / ".codex" / "skills",
    HOME / ".codex" / "tmp",
    HOME / ".cursor" / "skills",
    HOME / ".iflow" / "skills",
    HOME / ".openclaw" / "skills",
    HOME / ".openclaw" / "workspace" / "skills",
    HOME / ".windsurf" / "skills",
    HOME / ".gemini-cli" / "skills",
    HOME / ".antigravity" / "skills",
]


def find_broken_symlinks(base_dir: Path) -> list[Path]:
    """Find all broken symlinks under a directory."""
    if not base_dir.exists():
        return []
    broken = []
    for item in base_dir.rglob("*"):
        if item.is_symlink() and not item.exists():
            broken.append(item)
    return broken


def cleanup_skills(dry_run: bool = False) -> dict:
    """Clean up broken symlinks across all agent skill directories.

    Returns dict with summary stats.
    """
    total_removed = 0
    per_dir: dict[str, int] = {}

    for skill_dir in AGENT_SKILL_DIRS:
        broken = find_broken_symlinks(skill_dir)
        if not broken:
            continue

        dir_name = str(skill_dir).replace(str(HOME), "~")
        per_dir[dir_name] = len(broken)

        for link in broken:
            target = os.readlink(link)
            if dry_run:
                print(f"  [DRY-RUN] {link} -> {target}")
            else:
                try:
                    link.unlink()
                    total_removed += 1
                except OSError as e:
                    print(f"  FAIL  {link}: {e}", file=sys.stderr)

    # Clean up empty directories
    for skill_dir in AGENT_SKILL_DIRS:
        if not skill_dir.exists():
            continue
        for root, dirs, files in list(os.walk(str(skill_dir), topdown=False)):
            if root == str(skill_dir):
                continue
            if not os.listdir(root):
                try:
                    os.rmdir(root)
                except OSError:
                    pass

    return {"per_dir": per_dir, "total": total_removed}


def main():
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    print("Skill Symlink Cleanup")
    print("=" * 50)

    result = cleanup_skills(dry_run=dry_run)

    if not result["per_dir"]:
        print("\nNo broken symlinks found.")
        return

    print(f"\nBroken symlinks found:")
    for dir_name, count in sorted(result["per_dir"].items()):
        print(f"  {dir_name:60s} {count:>4}")

    print(f"\n{'=' * 50}")
    if dry_run:
        print(f"Total: {result['total']} broken symlinks (dry-run, not removed)")
    else:
        print(f"Removed {result['total']} broken symlinks")


if __name__ == "__main__":
    main()
