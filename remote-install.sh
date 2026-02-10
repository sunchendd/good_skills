#!/bin/bash
# Good Skills Remote Installation Script
# Usage: curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash
# Or with options: curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash -s -- --all

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Default values
REPO_URL="https://github.com/sunchendd/good_skills.git"
INSTALL_DIR="$HOME/.good_skills"
INSTALL_ARGS="--all"
BRANCH="main"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --github-copilot|--claude|--opencode|--antigravity|--cursor|--windsurf)
            INSTALL_ARGS="$1"
            shift
            ;;
        --all)
            INSTALL_ARGS="--all"
            shift
            ;;
        --project)
            INSTALL_ARGS="$INSTALL_ARGS --project"
            shift
            ;;
        --global)
            INSTALL_ARGS="$INSTALL_ARGS --global"
            shift
            ;;
        --dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        -h|--help)
            cat << EOF
Good Skills Remote Installation Script

Usage: 
  curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash
  curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash -s -- [OPTIONS]

Options:
    --all               Install to all supported platforms (default)
    --github-copilot    Install to GitHub Copilot only
    --claude            Install to Claude Code only
    --opencode          Install to OpenCode only
    --antigravity       Install to Antigravity only
    --cursor            Install to Cursor only
    --windsurf          Install to Windsurf only
    --global            Install globally (default)
    --project           Install to current project directory
    --dir <path>        Install repository to custom directory (default: ~/.good_skills)
    --branch <name>     Clone specific branch (default: main)
    -h, --help          Show this help message

Examples:
    # Install to all platforms
    curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash

    # Install to specific platforms
    curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash -s -- --github-copilot --claude

    # Install to current project
    curl -fsSL https://raw.githubusercontent.com/sunchendd/good_skills/main/remote-install.sh | bash -s -- --all --project

EOF
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo ""
print_info "========================================="
print_info "  Good Skills Remote Installation"
print_info "========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi

# Clone or update repository
if [ -d "$INSTALL_DIR" ]; then
    print_info "Repository already exists at $INSTALL_DIR"
    print_info "Updating repository..."
    cd "$INSTALL_DIR"
    git fetch origin
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
    print_success "Repository updated"
else
    print_info "Cloning repository to $INSTALL_DIR..."
    git clone --branch "$BRANCH" "$REPO_URL" "$INSTALL_DIR"
    print_success "Repository cloned"
fi

echo ""
print_info "Running installation script..."
echo ""

# Run the installation script
cd "$INSTALL_DIR"
chmod +x install.sh
./install.sh $INSTALL_ARGS

echo ""
print_success "========================================="
print_success "  Installation Complete!"
print_success "========================================="
echo ""
print_info "Repository location: $INSTALL_DIR"
print_info "To update skills in the future:"
print_info "  cd $INSTALL_DIR && git pull"
echo ""
print_info "To uninstall:"
print_info "  cd $INSTALL_DIR && ./uninstall.sh --all"
echo ""
