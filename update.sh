#!/bin/bash
# Good Skills Update Script
# Updates existing installations by adding new skills and fixing broken links

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
        openclaw-workspace)
            echo "$HOME/clawd/skills"
            ;;
        antigravity)
            echo "$HOME/.gemini/antigravity/skills"
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

# Function to display help
show_help() {
    cat << EOF
Good Skills Update Script

Usage: $0 [OPTIONS]

Options:
    --all               Update all supported platforms
    --github-copilot    Update GitHub Copilot
    --claude            Update Claude Code
    --opencode          Update OpenCode
    --openclaw          Update OpenClaw (both ~/.openclaw/skills and ~/clawd/skills)
    --antigravity       Update Antigravity
    --cursor            Update Cursor
    --windsurf          Update Windsurf
    --global            Update in global locations (default)
    --project           Update in current project directory
    --default-dir <path> Base directory for skills (default: ~/.agent/skills)
    --add-missing       Only add missing skills (don't touch existing)
    --dry-run           Show what would be done without making changes
    -h, --help          Show this help message

Examples:
    $0 --all                    # Update all platforms
    $0 --github-copilot         # Update GitHub Copilot only
    $0 --all --add-missing      # Only add new skills to all platforms

EOF
}

# Parse command line arguments
UPDATE_ALL=false
UPDATE_GLOBAL=true
PLATFORMS=""
ADD_MISSING_ONLY=false
DRY_RUN=false
DEFAULT_DIR="$HOME/.agent/skills"

if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            UPDATE_ALL=true
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
        --add-missing)
            ADD_MISSING_ONLY=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --global)
            UPDATE_GLOBAL=true
            shift
            ;;
        --project)
            UPDATE_GLOBAL=false
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
if [ "$UPDATE_ALL" = true ]; then
    PLATFORMS="github-copilot claude opencode openclaw antigravity cursor windsurf"
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

    # Create symbolic link
    ln -s "$source" "$target"
    print_success "Added '$skill_name'"
}

# Function to update default directory
update_default_dir() {
    local added=0
    local fixed=0
    local kept=0
    local skipped=0

    print_info "Updating default directory: $DEFAULT_DIR"

    # Check if default directory exists
    if [ ! -d "$DEFAULT_DIR" ]; then
        print_warning "Default directory does not exist, creating: $DEFAULT_DIR"
        if [ "$DRY_RUN" = false ]; then
            mkdir -p "$DEFAULT_DIR"
        fi
    fi

    # Get list of skills
    local skills=$(get_skills)

    local skill_count=0
    for skill in $skills; do
        ((skill_count++)) || true
    done

    if [ $skill_count -eq 0 ]; then
        print_warning "No skills found in $SCRIPT_DIR"
        return
    fi

    print_info "Found $skill_count skills"

    # Process each skill
    for skill in $skills; do
        local source_path="$SCRIPT_DIR/$skill"
        local target_path="$DEFAULT_DIR/$skill"

        if [ ! -e "$target_path" ] && [ ! -L "$target_path" ]; then
            # Skill doesn't exist, add it
            create_symlink "$source_path" "$target_path" "$skill"
            ((added++)) || true
        elif [ -L "$target_path" ]; then
            local existing_target=$(readlink "$target_path")
            if echo "$existing_target" | grep -q "good_skills"; then
                # Existing good_skills link
                if [ "$existing_target" = "$source_path" ]; then
                    # Correct link, check if still valid
                    if [ -e "$existing_target" ]; then
                        print_info "OK: '$skill' (correct link)"
                        ((kept++)) || true
                    else
                        print_warning "Broken link: '$skill' (target not accessible)"
                        if [ "$ADD_MISSING_ONLY" = false ]; then
                            rm "$target_path"
                            create_symlink "$source_path" "$target_path" "$skill"
                            ((fixed++)) || true
                        else
                            ((skipped++)) || true
                        fi
                    fi
                else
                    # Different good_skills path, update it
                    if [ "$ADD_MISSING_ONLY" = false ]; then
                        print_info "Updating '$skill' (different good_skills location)"
                        rm "$target_path"
                        create_symlink "$source_path" "$target_path" "$skill"
                        ((fixed++)) || true
                    else
                        print_info "Keeping: '$skill' (different good_skills location)"
                        ((kept++)) || true
                    fi
                fi
            else
                # Non-good_skills link
                print_info "Keeping: '$skill' (external source)"
                ((kept++)) || true
            fi
        elif [ -d "$target_path" ]; then
            # Actual directory (not a symlink)
            print_info "Keeping: '$skill' (real directory)"
            ((kept++)) || true
        fi
    done

    echo ""
    print_success "Summary for default directory:"
    print_info "  Added: $added"
    if [ "$ADD_MISSING_ONLY" = false ]; then
        print_info "  Fixed: $fixed"
    fi
    print_info "  Kept: $kept"
    print_info "  Skipped (broken/external): $skipped"
    echo ""
}

# Function to update skills in a platform
update_platform() {
    local platform="$1"
    local is_global="$2"
    local base_path
    local added=0
    local fixed=0
    local kept=0
    local skipped=0

    if [ "$is_global" = true ]; then
        base_path=$(get_global_path "$platform")
    else
        base_path="$(pwd)/$(get_project_path "$platform")"
    fi

    print_info "Updating $platform ($([ "$is_global" = true ] && echo "global" || echo "project"))..."
    print_info "Target: $base_path"

    # Skip if this is the default directory
    if [ "$is_global" = true ] && [ "$base_path" = "$DEFAULT_DIR" ]; then
        print_info "Skipping (will be updated via default directory)"
        echo ""
        return
    fi

    # Handle OpenClaw special case (two locations)
    if [ "$platform" = "openclaw" ] && [ "$is_global" = true ]; then
        update_openclaw "$ADD_MISSING_ONLY"
        return
    fi

    # Check if base directory exists
    if [ ! -d "$base_path" ]; then
        print_warning "Installation directory does not exist: $base_path"
        print_info "Creating directory..."
        if [ "$DRY_RUN" = false ]; then
            mkdir -p "$base_path"
        fi
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

    # Process each skill from default directory
    for skill in $skills; do
        local source_path="$DEFAULT_DIR/$skill"
        local target_path="$base_path/$skill"

        if [ ! -e "$target_path" ] && [ ! -L "$target_path" ]; then
            # Skill doesn't exist, add it from default directory
            if [ -e "$source_path" ]; then
                create_symlink "$source_path" "$target_path" "$skill"
                ((added++)) || true
            else
                print_warning "Skill '$skill' not found in default directory, skipping"
                ((skipped++)) || true
            fi
        elif [ -L "$target_path" ]; then
            local existing_target=$(readlink "$target_path")
            if [ "$existing_target" = "$source_path" ]; then
                # Correct link to default directory
                if [ -e "$existing_target" ]; then
                    print_info "OK: '$skill' (correct link)"
                    ((kept++)) || true
                else
                    print_warning "Broken link: '$skill' (target not accessible)"
                    if [ "$ADD_MISSING_ONLY" = false ]; then
                        rm "$target_path"
                        if [ -e "$source_path" ]; then
                            create_symlink "$source_path" "$target_path" "$skill"
                            ((fixed++)) || true
                        else
                            ((skipped++)) || true
                        fi
                    else
                        ((skipped++)) || true
                    fi
                fi
            else
                # Links to different location, keep it
                print_info "Keeping: '$skill' (external link)"
                ((kept++)) || true
            fi
        elif [ -d "$target_path" ]; then
            # Real directory, keep it
            print_info "Keeping: '$skill' (real directory)"
            ((kept++)) || true
        fi
    done

    echo ""
    print_success "Summary for $platform:"
    print_info "  Added: $added"
    if [ "$ADD_MISSING_ONLY" = false ]; then
        print_info "  Fixed: $fixed"
    fi
    print_info "  Kept: $kept"
    print_info "  Skipped: $skipped"
    echo ""
}

# Special handling for OpenClaw (two locations)
update_openclaw() {
    local add_missing_only="$1"

    print_info "Updating ~/.openclaw/skills..."
    update_openclaw_location "$HOME/.openclaw/skills" "$add_missing_only"

    print_info "Updating ~/clawd/skills..."
    update_openclaw_location "$HOME/clawd/skills" "$add_missing_only"
}

update_openclaw_location() {
    local location="$1"
    local add_missing_only="$2"

    if [ ! -d "$location" ]; then
        print_warning "Directory does not exist, creating: $location"
        if [ "$DRY_RUN" = false ]; then
            mkdir -p "$location"
        fi
    fi

    local skills=$(get_skills)
    local added=0
    local fixed=0
    local kept=0
    local skipped=0

    print_info "Linking from default directory: $DEFAULT_DIR"

    for skill in $skills; do
        local source_path="$DEFAULT_DIR/$skill"
        local target_path="$location/$skill"

        if [ ! -e "$target_path" ] && [ ! -L "$target_path" ]; then
            if [ -e "$source_path" ]; then
                create_symlink "$source_path" "$target_path" "$skill"
                ((added++)) || true
            else
                print_warning "Skill '$skill' not found in default directory, skipping"
                ((skipped++)) || true
            fi
        elif [ -L "$target_path" ]; then
            local existing_target=$(readlink "$target_path")
            if [ "$existing_target" = "$source_path" ]; then
                if [ -e "$existing_target" ]; then
                    print_info "OK: '$skill'"
                    ((kept++)) || true
                else
                    if [ "$add_missing_only" = false ]; then
                        rm "$target_path"
                        if [ -e "$source_path" ]; then
                            create_symlink "$source_path" "$target_path" "$skill"
                            ((fixed++)) || true
                        else
                            ((skipped++)) || true
                        fi
                    else
                        ((skipped++)) || true
                    fi
                fi
            else
                print_info "Keeping: '$skill' (external link)"
                ((kept++)) || true
            fi
        elif [ -d "$target_path" ]; then
            print_info "Keeping: '$skill' (real directory)"
            ((kept++)) || true
        fi
    done

    echo ""
    print_success "Summary for $location:"
    print_info "  Added: $added"
    if [ "$add_missing_only" = false ]; then
        print_info "  Fixed: $fixed"
    fi
    print_info "  Kept: $kept"
    print_info "  Skipped: $skipped"
    echo ""
}

# Main update
echo ""
print_info "========================================="
print_info "  Good Skills Update Script"
print_info "========================================="
echo ""
print_info "Source directory: $SCRIPT_DIR"
print_info "Default directory: $DEFAULT_DIR"
print_info "Update mode: $([ "$UPDATE_GLOBAL" = true ] && echo "global" || echo "project")"
print_info "Platforms: $PLATFORMS"
print_info "Add missing only: $ADD_MISSING_ONLY"
print_info "Dry run: $DRY_RUN"
echo ""

# First update default directory
if [ "$UPDATE_GLOBAL" = true ]; then
    update_default_dir
fi

# Then update each selected platform
for platform in $PLATFORMS; do
    update_platform "$platform" "$UPDATE_GLOBAL"
done

echo ""
print_success "========================================="
print_success "  Update Complete!"
print_success "========================================="
echo ""
print_info "Skills have been updated. External skills and real directories"
print_info "have been preserved. Use --add-missing to only add new skills,"
print_info "or run without it to also fix broken links."
echo ""
