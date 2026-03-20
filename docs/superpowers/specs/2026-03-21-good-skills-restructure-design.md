# Good Skills Restructure Design

## Problem Statement

The current good_skills repository is bloated and unmaintainable:

1. **47+ skills, most unused** — only 5 self-developed skills are actively used
2. **Open-source skills can't auto-update** — local copies of superpowers, best-practices guides go stale
3. **5 competing install systems** — install.sh, update.sh, npm CLI (good-skills), remote-install.sh, opensource/ scripts
4. **Oversized CLAUDE.md** — a massive trigger index table that duplicates what SKILL.md descriptions already handle
5. **No standardization** — custom formats diverge from the skills.sh ecosystem standard

## Decision

Restructure good_skills into a **lean, skills.sh-compatible repository** containing only self-developed skills. Open-source skills (superpowers, best-practices, etc.) are managed externally via `npx skills add`.

## Design

### Retained Skills (5 + shared library)

| Skill | Purpose |
|-------|---------|
| daily-newsletter | Daily tech news aggregation from 27+ RSS feeds, categorized, scored, email+Bark push |
| arxiv-daily | Daily arXiv AI paper curation with scoring and Chinese summaries |
| super-wardrobe | Daily outfit suggestions based on real-time weather |
| patent-search | Patent search across USPTO/EPO/WIPO databases |
| patent-specialist | Patent disclosure and claims writing |
| shared/ | Python utility library (bark, email, siyuan, llm, config) |

### Removed Content

| What | Why |
|------|-----|
| `packages/cli/` (good-skills npm CLI) | Replaced by skills.sh CLI (`npx skills add`) |
| `install.sh / update.sh / uninstall.sh / remote-install.sh` | Replaced by single new `install.sh` |
| `skills-registry.json` | skills.sh uses GitHub repos as sources, no custom registry needed |
| `opensource/` directory and scripts | Open-source skills installed via `npx skills add` |
| `superpowers/` directory (16 workflows) | Managed via `/plugin install superpowers@claude-plugins-official` |
| `.claude-plugin/marketplace.json` | No longer hosting plugin marketplace |
| `manifest.json` files in each skill | skills.sh uses SKILL.md frontmatter for metadata |
| 40+ unused skill directories | Not actively used; can be retrieved from git history if needed |
| Trigger index table in CLAUDE.md | Redundant — SKILL.md description fields handle trigger matching |
| `PLATFORM_SUPPORT.md`, `INSTALL.md`, `SUPERPOWERS-README.md` | Outdated docs for removed features |
| `theplasmak/`, `inference-shell/` | Third-party content, not maintained |
| `run.py`, `debug_patent_raw.json` | Leftover artifacts |

### Target Repository Structure

```
good-skills/
├── skills/
│   ├── daily-newsletter/
│   │   ├── SKILL.md            # skills.sh standard format
│   │   └── scripts/            # Python automation scripts
│   ├── arxiv-daily/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── super-wardrobe/
│   │   ├── SKILL.md
│   │   └── scripts/
│   ├── patent-search/
│   │   ├── SKILL.md
│   │   └── references/         # Deep-dive docs loaded on demand
│   ├── patent-specialist/
│   │   ├── SKILL.md
│   │   └── references/
│   └── shared/                 # Python utility library
│       ├── __init__.py
│       ├── bark.py
│       ├── email_utils.py
│       ├── siyuan.py
│       ├── llm.py
│       └── config.py
├── install.sh                  # Single install script
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview and usage
├── CLAUDE.md                   # Minimal project instructions
└── .gitignore
```

### SKILL.md Format (skills.sh Compatible)

Each SKILL.md follows the skills.sh standard:

```markdown
---
name: <skill-name>
description: <What it does>. Use when <trigger phrases>. <Key capabilities>.
---

# <Skill Title>

(Skill instructions for the agent...)
```

Required frontmatter fields: `name`, `description`.
No `manifest.json` — all metadata lives in SKILL.md frontmatter.

### CLAUDE.md (Minimal)

The new CLAUDE.md contains only:

- One-line project description
- Development conventions (commit style, naming)
- Environment variable reference
- Note that skills are in `skills/` directory

No trigger index table. Trigger matching is handled by each SKILL.md's `description` field, which is how skills.sh and Claude Code natively work.

### install.sh (Unified Installer)

A single script that installs everything needed:

```bash
#!/bin/bash
set -e

echo "=== Good Skills Installer ==="

# 1. Install self-developed skills (from this repo)
echo "Installing self-developed skills..."
npx skills add .

# 2. Install superpowers workflows
echo "Installing superpowers..."
npx skills add obra/superpowers

# 3. Install curated open-source skills
echo "Installing curated open-source skills..."
npx skills add vercel-labs/skills -s next-best-practices
npx skills add vercel-labs/skills -s react-best-practices
# Uncomment as needed:
# npx skills add vercel-labs/skills -s supabase-postgres-best-practices
# npx skills add vercel-labs/skills -s remotion-best-practices

# 4. Install Python dependencies (for self-developed skills)
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "=== Installation complete ==="
```

Users run `./install.sh` once. To update: `npx skills update`.

### Migration Strategy

1. **Create a new branch** for the restructure
2. **Move retained skills** into `skills/` directory with updated SKILL.md format
3. **Move shared/** into `skills/shared/`
4. **Update Python import paths** in skill scripts to reference new shared/ location
5. **Write new CLAUDE.md** (minimal)
6. **Write new README.md** (project overview + install instructions)
7. **Write install.sh** (unified installer)
8. **Update .env.example and requirements.txt**
9. **Delete everything else** — old skills, CLI, scripts, docs, configs
10. **Verify** all 5 retained skills' SKILL.md files are valid skills.sh format
11. **Test** `npx skills add .` works with the new structure

### Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Losing skill content permanently | All content preserved in git history; can be recovered anytime |
| skills.sh CLI breaking changes | install.sh pins to known-good behavior; fallback is manual symlink |
| shared/ import path changes break scripts | Update imports during migration; test each skill |
| Missing a skill that's actually needed | Start lean; add back from git history if needed |

## Success Criteria

- Repository contains exactly 5 skill directories + shared/ + install.sh
- All SKILL.md files pass skills.sh format validation
- `npx skills add .` successfully installs all self-developed skills
- `./install.sh` completes without errors
- CLAUDE.md is under 30 lines
- No unused files remain in the repository
