#!/bin/bash
set -e

INSTALL_DIR="${1:-$HOME/good_skills}"
REPO_URL="https://github.com/sunchendd/good_skills.git"

if [ -d "$INSTALL_DIR" ]; then
  echo "=> Updating existing install at $INSTALL_DIR"
  cd "$INSTALL_DIR"
  git pull --rebase origin main
else
  echo "=> Cloning to $INSTALL_DIR"
  git clone "$REPO_URL" "$INSTALL_DIR"
  cd "$INSTALL_DIR"
fi

bash install.sh --update
echo ""
echo "=> Done. Run 'cd $INSTALL_DIR && npm run fitness' to try it out."
