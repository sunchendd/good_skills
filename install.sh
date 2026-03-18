#!/bin/bash
# Good Skills Installation Script
# Installs skills to multiple AI agent platforms using symbolic links

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

# Function to display help
show_help() {
    cat << EOF
Good Skills Installation Script

Usage: $0 [OPTIONS]

 Options:
     --all               Install to all supported platforms
     --github-copilot    Install to GitHub Copilot (~/.copilot/skills/)
     --claude            Install to Claude Code (~/.claude/skills/)
     --opencode          Install to OpenCode (~/.config/opencode/skill/)
     --openclaw          Install to OpenClaw (~/.openclaw/skills/)
     --antigravity       Install to Antigravity (~/.agent/skills/) - used as default base
     --codex             Install to Codex (~/.codex/skills/)
     --cursor            Install to Cursor (~/.cursor/skills/)
     --windsurf          Install to Windsurf (~/.codeium/windsurf/skills/)
     --global            Install globally (default)
     --project           Install to current project directory
     --default-dir <path> Base directory for skills (default: ~/.agent/skills)
     --force             Auto-replace existing links/dirs without prompting
     --skip              Skip existing links/dirs without prompting
     --dry-run           Show what would be done without making changes
     -h, --help          Show this help message

Examples:
    $0 --all                    # Install to all platforms
    $0 --github-copilot         # Install to GitHub Copilot only
    $0 --claude --opencode      # Install to Claude and OpenCode
    $0 --all --project          # Install to all platforms in project directory

Note: Trae requires manual configuration via Settings > Rules and Skills.
      You can manually copy or symlink skills to .trae/skills/ in your project.

EOF
}

# Function to get global path for a platform
get_global_path() {
    case "$1" in
        github-copilot)
            echo "$HOME/.copilot/skills"
            ;;
        claude)
            echo "$HOME/.claude/skills"
            ;;
        opencode)
            echo "$HOME/.config/opencode/skill"
            ;;
        openclaw)
            echo "$HOME/.openclaw/skills"
            ;;
        antigravity)
            echo "$HOME/.agent/skills"
            ;;
        codex)
            echo "$HOME/.codex/skills"
            ;;
        cursor)
            echo "$HOME/.cursor/skills"
            ;;
        windsurf)
            echo "$HOME/.codeium/windsurf/skills"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Function to get project path for a platform
get_project_path() {
    case "$1" in
        github-copilot)
            echo ".github/skills"
            ;;
        claude)
            echo ".claude/skills"
            ;;
        opencode)
            echo ".opencode/skill"
            ;;
        openclaw)
            echo ".openclaw/skills"
            ;;
        antigravity)
            echo ".agent/skills"
            ;;
        codex)
            echo ".codex/skills"
            ;;
        cursor)
            echo ".cursor/skills"
            ;;
        windsurf)
            echo ".windsurf/skills"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Parse command line arguments
INSTALL_ALL=false
INSTALL_GLOBAL=true
PLATFORMS=""
FORCE_REPLACE=false
SKIP_existing=false
DRY_RUN=false
DEFAULT_DIR="$HOME/.agent/skills"

if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            INSTALL_ALL=true
            shift
            ;;
        --github-copilot)
            PLATFORMS="$PLATFORMS github-copilot"
            shift
            ;;
        --claude)
            PLATFORMS="$PLATFORMS claude"
            shift
            ;;
        --opencode)
            PLATFORMS="$PLATFORMS opencode"
            shift
            ;;
        --openclaw)
            PLATFORMS="$PLATFORMS openclaw"
            shift
            ;;
        --antigravity)
            PLATFORMS="$PLATFORMS antigravity"
            shift
            ;;
        --codex)
            PLATFORMS="$PLATFORMS codex"
            shift
            ;;
        --cursor)
            PLATFORMS="$PLATFORMS cursor"
            shift
            ;;
        --windsurf)
            PLATFORMS="$PLATFORMS windsurf"
            shift
            ;;
        --default-dir)
            DEFAULT_DIR="$2"
            shift 2
            ;;
        --force)
            FORCE_REPLACE=true
            shift
            ;;
        --skip)
            SKIP_existing=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --global)
            INSTALL_GLOBAL=true
            shift
            ;;
        --project)
            INSTALL_GLOBAL=false
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# If --all is specified, add all platforms
if [ "$INSTALL_ALL" = true ]; then
    PLATFORMS="github-copilot claude opencode openclaw antigravity codex cursor windsurf"
fi

# Check if any platforms are selected
if [ -z "$PLATFORMS" ]; then
    print_error "No platforms specified. Use --all or specify individual platforms."
    show_help
    exit 1
fi

# Get list of skills (directories with SKILL.md)
get_skills() {
    local skills=""
    for dir in "$SCRIPT_DIR"/*/; do
        if [ -f "$dir/SKILL.md" ]; then
            local skill_name=$(basename "$dir")
            if [ -z "$skills" ]; then
                skills="$skill_name"
            else
                skills="$skills $skill_name"
            fi
        fi
    done
    echo "$skills"
}

# Function to create symbolic link
create_symlink() {
    local source="$1"
    local target="$2"
    local skill_name="$3"

    if [ "$DRY_RUN" = true ]; then
        echo "[DRY RUN] Would link '$skill_name': $source -> $target"
        return 0
    fi

    # Check if target already exists
    if [ -e "$target" ] || [ -L "$target" ]; then
        if [ -L "$target" ]; then
            local existing_target=$(readlink "$target")
            if [ "$existing_target" = "$source" ]; then
                print_info "Skill '$skill_name' already linked correctly"
                return 0
            else
                print_warning "Existing symlink for '$skill_name' points to different location"
                print_info "  Current: $existing_target"
                print_info "  New: $source"
                if [ "$FORCE_REPLACE" = true ]; then
                    print_info "Auto-replacing (--force)"
                    rm "$target"
                elif [ "$SKIP_existing" = true ]; then
                    print_info "Skipping (--skip)"
                    return 0
                else
                    read -p "Replace existing link? (y/n) " -n 1 -r
                    echo
                    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                        print_info "Skipping '$skill_name'"
                        return 0
                    fi
                    rm "$target"
                fi
            fi
        elif [ -d "$target" ]; then
            print_warning "Directory '$skill_name' already exists (not a symlink)"
            print_info "  Location: $target"
            if [ "$FORCE_REPLACE" = true ]; then
                print_info "Auto-replacing (--force)"
                rm -rf "$target"
            elif [ "$SKIP_existing" = true ]; then
                print_info "Skipping (--skip)"
                return 0
            else
                read -p "Replace with symlink? (y/n) " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    print_info "Skipping '$skill_name'"
                    return 0
                fi
                rm -rf "$target"
            fi
        else
            print_warning "File/directory exists at target location"
            if [ "$FORCE_REPLACE" = true ]; then
                print_info "Auto-replacing (--force)"
                rm -f "$target"
            elif [ "$SKIP_existing" = true ]; then
                print_info "Skipping (--skip)"
                return 0
            else
                rm -f "$target"
            fi
        fi
    fi

    # Create symbolic link
    if [ "$DRY_RUN" = false ]; then
        ln -s "$source" "$target"
        print_success "Installed '$skill_name'"
    fi
}

# Function to install skills to default directory
install_to_default_dir() {
    print_info "Installing skills to default directory: $DEFAULT_DIR"

    # Create default directory if it doesn't exist
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "$DEFAULT_DIR"
    fi

    # Get list of skills
    local skills=$(get_skills)

    # Count skills
    local skill_count=0
    for skill in $skills; do
        ((skill_count++)) || true
    done

    if [ $skill_count -eq 0 ]; then
        print_warning "No skills found in $SCRIPT_DIR"
        return
    fi

    print_info "Found $skill_count skills"

    # Install each skill to default directory
    local installed=0
    for skill in $skills; do
        local source_path="$SCRIPT_DIR/$skill"
        local target_path="$DEFAULT_DIR/$skill"

        if create_symlink "$source_path" "$target_path" "$skill"; then
            ((installed++)) || true
        fi
    done

    echo ""
    print_success "Installed $installed skills to default directory"
    echo ""
}

# Function to install skills to a platform
install_to_platform() {
    local platform="$1"
    local is_global="$2"

    local base_path
    if [ "$is_global" = true ]; then
        base_path=$(get_global_path "$platform")
    else
        base_path="$(pwd)/$(get_project_path "$platform")"
    fi

    print_info "Installing to $platform ($([ "$is_global" = true ] && echo "global" || echo "project"))..."
    print_info "Target: $base_path"

    # Skip if this is the default directory platform
    if [ "$is_global" = true ] && [ "$base_path" = "$DEFAULT_DIR" ]; then
        # Already installed via install_to_default_dir
        echo ""
        return
    fi

    # Create base directory if it doesn't exist
    if [ "$DRY_RUN" = false ]; then
        mkdir -p "$base_path"
    fi

    # Get list of skills
    local skills=$(get_skills)

    # Count skills
    local skill_count=0
    for skill in $skills; do
        ((skill_count++)) || true
    done

    if [ $skill_count -eq 0 ]; then
        print_warning "No skills found in $SCRIPT_DIR"
        return
    fi

    print_info "Found $skill_count skills"
    print_info "Linking from default directory: $DEFAULT_DIR"

    # Install each skill from default directory to platform
    local installed=0
    for skill in $skills; do
        local source_path="$DEFAULT_DIR/$skill"
        local target_path="$base_path/$skill"

        if create_symlink "$source_path" "$target_path" "$skill"; then
            ((installed++)) || true
        fi
    done

    echo ""
    print_success "Installed $installed skills to $platform"
    echo ""
}

# Main installation
echo ""
print_info "========================================="
print_info "  Good Skills Installation Script"
print_info "========================================="
echo ""
print_info "Source directory: $SCRIPT_DIR"
print_info "Default directory: $DEFAULT_DIR"
print_info "Installation mode: $([ "$INSTALL_GLOBAL" = true ] && echo "global" || echo "project")"
print_info "Platforms: $PLATFORMS"
echo ""

# First install to default directory
if [ "$INSTALL_GLOBAL" = true ]; then
    install_to_default_dir
fi

# Then install to each selected platform
for platform in $PLATFORMS; do
    install_to_platform "$platform" "$INSTALL_GLOBAL"
done

echo ""
print_success "========================================="
print_success "  Installation Complete!"
print_success "========================================="
echo ""
print_info "All skills have been installed using symbolic links."
print_info "Skills are in default directory: $DEFAULT_DIR"
print_info "Updates to skills in this repository will"
print_info "automatically be reflected in your AI agents."
echo ""
print_info "To update, run: ./update.sh"
print_info "To uninstall, run: ./uninstall.sh"
echo ""

# Superpowers plugin prompt for Claude Code users
if [ -d "$HOME/.claude" ] || [ -d "$HOME/Library/Application Support/Claude" ]; then
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}  💡 推荐：安装 Superpowers 工作流插件（Claude Code）${NC}"
    echo -e "${YELLOW}  在 Claude Code 终端中依次运行以下两条命令：${NC}"
    echo ""
    echo -e "${BLUE}  /plugin marketplace add obra/superpowers-marketplace${NC}"
    echo -e "${BLUE}  /plugin install superpowers@superpowers-marketplace${NC}"
    echo ""
    echo -e "${YELLOW}  安装后重启 Claude Code 即可获得完整工作流技能。${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
fi
