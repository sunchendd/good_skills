#!/bin/bash
set -e

echo "=== Good Skills Installer ==="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Parse flags
UPDATE_MODE=false
for arg in "$@"; do
  case $arg in
    --update) UPDATE_MODE=true ;;
  esac
done

# Set GOOD_SKILLS_HOME
if ! grep -q "GOOD_SKILLS_HOME" ~/.zshrc 2>/dev/null; then
  echo "export GOOD_SKILLS_HOME=$SCRIPT_DIR" >> ~/.zshrc
  echo "Added GOOD_SKILLS_HOME to ~/.zshrc"
fi
export GOOD_SKILLS_HOME="$SCRIPT_DIR"

# 1. Install self-developed skills
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

# Anthropic official skills: brainstorming, frontend-design, mcp-builder, tdd, agent-browser, etc.
npx skills add anthropics/skills -y -g || echo "  (anthropics/skills skipped)"

# Lark/飞书 full suite: 25+ skills (calendar, doc, im, base, approval, etc.)
npx skills add larksuite/cli -y -g || echo "  (larksuite/cli skipped)"

# Superpowers dev workflows: tdd, brainstorming, executing-plans, writing-plans, etc.
npx skills add obra/superpowers -y -g || echo "  (obra/superpowers skipped)"

# Gemini CLI
npx skills add google-gemini/gemini-cli -y -g || echo "  (gemini-cli skipped)"

npx skills add ascend/agent-skills -y -g || echo "  (ascend/agent-skills skipped)"
# ByteDance Volcano Engine: image & video generation
#npx skills add volcengine/ai-arena-tools -y -g || echo "  (volcengine skipped)"

# 4. Install Python dependencies
echo ""
echo "[4/4] Installing Python dependencies..."
if command -v uv &>/dev/null; then
  uv pip install --system -r "$SCRIPT_DIR/requirements.txt"
else
  pip3 install --user -r "$SCRIPT_DIR/requirements.txt"
fi

# 5. Validate .env
echo ""
if [ ! -f "$SCRIPT_DIR/.env" ]; then
  echo "WARNING: .env not found. Copy and configure:"
  echo "  cp .env.example .env"
else
  echo "[Env Check]"
  MISSING=0
  for VAR in DEEPSEEK_API_KEY GITHUB_TOKEN BARK_TOKEN EMAIL_SENDER EMAIL_RECIPIENTS QQ_EMAIL_PASSWORD; do
    if ! grep -q "^${VAR}=.\+" "$SCRIPT_DIR/.env" 2>/dev/null; then
      echo "  MISSING: $VAR"
      MISSING=$((MISSING + 1))
    fi
  done
  if [ $MISSING -eq 0 ]; then
    echo "  All required env vars configured."
  else
    echo "  $MISSING required env var(s) not set in .env"
  fi
fi

# 6. Run health check
echo ""
echo "[Health Check]"
python3 "$SCRIPT_DIR/scripts/health_check.py" 2>/dev/null || echo "Health check skipped (run manually: python3 scripts/health_check.py)"

echo ""
echo "=== Installation complete ==="
echo ""
echo "Next steps:"
echo "  - Configure .env with your API keys"
echo "  - Run a skill: npm run fitness"
echo "  - Run health check: python3 scripts/health_check.py"
