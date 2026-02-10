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
    --antigravity       Install to Antigravity (~/.gemini/antigravity/skills/)
    --cursor            Install to Cursor (~/.cursor/skills/)
    --windsurf          Install to Windsurf (~/.codeium/windsurf/skills/)
    --global            Install globally (default)
    --project           Install to current project directory
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

# Platform installation paths
declare -A GLOBAL_PATHS=(
    ["github-copilot"]="$HOME/.copilot/skills"
    ["claude"]="$HOME/.claude/skills"
    ["opencode"]="$HOME/.config/opencode/skill"
    ["antigravity"]="$HOME/.gemini/antigravity/skills"
    ["cursor"]="$HOME/.cursor/skills"
    ["windsurf"]="$HOME/.codeium/windsurf/skills"
)

declare -A PROJECT_PATHS=(
    ["github-copilot"]=".github/skills"
    ["claude"]=".claude/skills"
    ["opencode"]=".opencode/skill"
    ["antigravity"]=".agent/skills"
    ["cursor"]=".cursor/skills"
    ["windsurf"]=".windsurf/skills"
)

# Parse command line arguments
INSTALL_ALL=false
INSTALL_GLOBAL=true
PLATFORMS=()

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
            PLATFORMS+=("github-copilot")
            shift
            ;;
        --claude)
            PLATFORMS+=("claude")
            shift
            ;;
        --opencode)
            PLATFORMS+=("opencode")
            shift
            ;;
        --antigravity)
            PLATFORMS+=("antigravity")
            shift
            ;;
        --cursor)
            PLATFORMS+=("cursor")
            shift
            ;;
        --windsurf)
            PLATFORMS+=("windsurf")
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
    PLATFORMS=("github-copilot" "claude" "opencode" "antigravity" "cursor" "windsurf")
fi

# Check if any platforms are selected
if [ ${#PLATFORMS[@]} -eq 0 ]; then
    print_error "No platforms specified. Use --all or specify individual platforms."
    show_help
    exit 1
fi

# Get list of skills (directories with SKILL.md)
get_skills() {
    local skills=()
    for dir in "$SCRIPT_DIR"/*/; do
        if [ -f "$dir/SKILL.md" ]; then
            local skill_name=$(basename "$dir")
            skills+=("$skill_name")
        fi
    done
    echo "${skills[@]}"
}

# Function to create symbolic link
create_symlink() {
    local source="$1"
    local target="$2"
    local skill_name="$3"
    
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
                read -p "Replace existing link? (y/n) " -n 1 -r
                echo
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    print_info "Skipping '$skill_name'"
                    return 0
                fi
                rm "$target"
            fi
        elif [ -d "$target" ]; then
            print_warning "Directory '$skill_name' already exists (not a symlink)"
            print_info "  Location: $target"
            read -p "Replace with symlink? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_info "Skipping '$skill_name'"
                return 0
            fi
            rm -rf "$target"
        else
            print_warning "File/directory exists at target location"
            rm -f "$target"
        fi
    fi
    
    # Create symbolic link
    ln -s "$source" "$target"
    print_success "Installed '$skill_name'"
}

# Function to install skills to a platform
install_to_platform() {
    local platform="$1"
    local is_global="$2"
    
    local base_path
    if [ "$is_global" = true ]; then
        base_path="${GLOBAL_PATHS[$platform]}"
    else
        base_path="$(pwd)/${PROJECT_PATHS[$platform]}"
    fi
    
    print_info "Installing to $platform ($([ "$is_global" = true ] && echo "global" || echo "project"))..."
    print_info "Target: $base_path"
    
    # Create base directory if it doesn't exist
    mkdir -p "$base_path"
    
    # Get list of skills
    local skills=($(get_skills))
    
    if [ ${#skills[@]} -eq 0 ]; then
        print_warning "No skills found in $SCRIPT_DIR"
        return
    fi
    
    print_info "Found ${#skills[@]} skills"
    
    # Install each skill
    local installed=0
    for skill in "${skills[@]}"; do
        local source_path="$SCRIPT_DIR/$skill"
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
print_info "Installation mode: $([ "$INSTALL_GLOBAL" = true ] && echo "global" || echo "project")"
print_info "Platforms: ${PLATFORMS[*]}"
echo ""

# Install to each selected platform
for platform in "${PLATFORMS[@]}"; do
    install_to_platform "$platform" "$INSTALL_GLOBAL"
done

echo ""
print_success "========================================="
print_success "  Installation Complete!"
print_success "========================================="
echo ""
print_info "All skills have been installed using symbolic links."
print_info "This means updates to skills in this repository will"
print_info "automatically be reflected in your AI agents."
echo ""
print_info "To uninstall, run: ./uninstall.sh"
echo ""
