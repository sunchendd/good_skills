#!/bin/bash
# Good Skills Uninstallation Script
# Removes symbolic links created by install.sh

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
Good Skills Uninstallation Script

Usage: $0 [OPTIONS]

Options:
    --all               Uninstall from all supported platforms
    --github-copilot    Uninstall from GitHub Copilot
    --claude            Uninstall from Claude Code
    --opencode          Uninstall from OpenCode
    --antigravity       Uninstall from Antigravity
    --cursor            Uninstall from Cursor
    --windsurf          Uninstall from Windsurf
    --global            Uninstall from global locations (default)
    --project           Uninstall from current project directory
    -h, --help          Show this help message

Examples:
    $0 --all                    # Uninstall from all platforms
    $0 --github-copilot         # Uninstall from GitHub Copilot only
    $0 --claude --opencode      # Uninstall from Claude and OpenCode

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
UNINSTALL_ALL=false
UNINSTALL_GLOBAL=true
PLATFORMS=()

if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            UNINSTALL_ALL=true
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
            UNINSTALL_GLOBAL=true
            shift
            ;;
        --project)
            UNINSTALL_GLOBAL=false
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
if [ "$UNINSTALL_ALL" = true ]; then
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

# Function to remove symbolic link
remove_symlink() {
    local target="$1"
    local skill_name="$2"
    local source="$3"
    
    # Check if target exists
    if [ ! -e "$target" ] && [ ! -L "$target" ]; then
        return 0
    fi
    
    # Check if it's a symlink
    if [ -L "$target" ]; then
        local existing_target=$(readlink "$target")
        # Only remove if it points to our source
        if [[ "$existing_target" == "$source" ]] || [[ "$existing_target" == /* && "$existing_target" == "$source" ]]; then
            rm "$target"
            print_success "Removed '$skill_name'"
            return 0
        else
            print_warning "Symlink for '$skill_name' points to different location, skipping"
            print_info "  Target: $existing_target"
            return 0
        fi
    else
        print_warning "'$skill_name' exists but is not a symlink, skipping"
        return 0
    fi
}

# Function to uninstall skills from a platform
uninstall_from_platform() {
    local platform="$1"
    local is_global="$2"
    
    local base_path
    if [ "$is_global" = true ]; then
        base_path="${GLOBAL_PATHS[$platform]}"
    else
        base_path="$(pwd)/${PROJECT_PATHS[$platform]}"
    fi
    
    print_info "Uninstalling from $platform ($([ "$is_global" = true ] && echo "global" || echo "project"))..."
    print_info "Target: $base_path"
    
    # Check if base directory exists
    if [ ! -d "$base_path" ]; then
        print_info "No installation found at $base_path"
        echo ""
        return
    fi
    
    # Get list of skills
    local skills=($(get_skills))
    
    if [ ${#skills[@]} -eq 0 ]; then
        print_warning "No skills found in $SCRIPT_DIR"
        return
    fi
    
    # Uninstall each skill
    local removed=0
    for skill in "${skills[@]}"; do
        local source_path="$SCRIPT_DIR/$skill"
        local target_path="$base_path/$skill"
        
        if remove_symlink "$target_path" "$skill" "$source_path"; then
            ((removed++)) || true
        fi
    done
    
    # Remove base directory if empty
    if [ -d "$base_path" ] && [ -z "$(ls -A "$base_path")" ]; then
        rmdir "$base_path"
        print_info "Removed empty directory: $base_path"
    fi
    
    echo ""
    print_success "Removed $removed skills from $platform"
    echo ""
}

# Main uninstallation
echo ""
print_info "========================================="
print_info "  Good Skills Uninstallation Script"
print_info "========================================="
echo ""
print_info "Source directory: $SCRIPT_DIR"
print_info "Uninstallation mode: $([ "$UNINSTALL_GLOBAL" = true ] && echo "global" || echo "project")"
print_info "Platforms: ${PLATFORMS[*]}"
echo ""

# Uninstall from each selected platform
for platform in "${PLATFORMS[@]}"; do
    uninstall_from_platform "$platform" "$UNINSTALL_GLOBAL"
done

echo ""
print_success "========================================="
print_success "  Uninstallation Complete!"
print_success "========================================="
echo ""
print_info "All Good Skills symbolic links have been removed."
print_info "The original skill files remain in $SCRIPT_DIR"
echo ""
