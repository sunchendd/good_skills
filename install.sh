#!/bin/bash
set -e

echo "=== Good Skills Installer ==="

# Set GOOD_SKILLS_HOME to repo root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Add GOOD_SKILLS_HOME to shell profile if not already set
if ! grep -q "GOOD_SKILLS_HOME" ~/.zshrc 2>/dev/null; then
  echo "export GOOD_SKILLS_HOME=$SCRIPT_DIR" >> ~/.zshrc
  echo "Added GOOD_SKILLS_HOME to ~/.zshrc"
fi
export GOOD_SKILLS_HOME="$SCRIPT_DIR"

# 1. Install self-developed skills (SKILL.md -> ~/.claude/skills/)
echo ""
echo "[1/4] Installing self-developed skills..."
npx skills add .

# 2. Install superpowers workflows
echo ""
echo "[2/4] Installing superpowers..."
npx skills add obra/superpowers

# 3. Install curated open-source skills
echo ""
echo "[3/4] Installing curated open-source skills..."
npx skills add vercel-labs/skills -s next-best-practices
npx skills add vercel-labs/skills -s react-best-practices
# Uncomment as needed:
# npx skills add vercel-labs/skills -s supabase-postgres-best-practices
# npx skills add vercel-labs/skills -s remotion-best-practices

# 4. Install Python dependencies
echo ""
echo "[4/4] Installing Python dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt"

# Remind about .env
echo ""
if [ ! -f "$SCRIPT_DIR/.env" ]; then
  echo "WARNING: Copy .env.example to .env and fill in your API keys:"
  echo "  cp .env.example .env"
  echo ""
fi

echo "=== Installation complete ==="
