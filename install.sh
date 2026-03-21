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
npx skills add . -y -g

# 2. Install superpowers workflows
echo ""
echo "[2/4] Installing superpowers..."
npx skills add obra/superpowers -y -g

# 3. Install curated open-source skills
echo ""
echo "[3/4] Installing curated open-source skills..."
# Add more as needed:
# npx skills add <owner>/<repo> -y -g
echo "No additional open-source skills configured. Edit install.sh to add."

# 4. Install Python dependencies
echo ""
echo "[4/4] Installing Python dependencies..."
if command -v uv &>/dev/null; then
  uv pip install -r "$SCRIPT_DIR/requirements.txt"
else
  pip3 install --user -r "$SCRIPT_DIR/requirements.txt"
fi

# Remind about .env
echo ""
if [ ! -f "$SCRIPT_DIR/.env" ]; then
  echo "WARNING: Copy .env.example to .env and fill in your API keys:"
  echo "  cp .env.example .env"
  echo ""
fi

echo "=== Installation complete ==="
