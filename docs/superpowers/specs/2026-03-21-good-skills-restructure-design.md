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

### Retained Skills (5 self-contained skills)

Each skill is **self-contained** — has its own bark_client.py, email_sender.py etc. No shared library needed.

| Skill | Purpose |
|-------|---------|
| daily-newsletter | Daily tech news aggregation from 27+ RSS feeds, categorized, scored, email+Bark push |
| arxiv-daily | Daily arXiv AI paper curation with scoring and Chinese summaries |
| super-wardrobe | Daily outfit suggestions based on real-time weather |
| patent-search | Patent search across USPTO/EPO/WIPO databases |
| patent-specialist | Patent disclosure and claims writing |

### Runtime Model

Skills have two layers:

1. **SKILL.md** (agent instructions) — installed by `npx skills add .` into `~/.claude/skills/`. Tells the agent what to do.
2. **Python scripts** (automation) — run directly from the git-cloned repo. SKILL.md references scripts via absolute path or `$GOOD_SKILLS_HOME`.

`npx skills add .` only installs SKILL.md files. Python scripts are NOT copied — they are executed from the repo checkout. This is by design: scripts need `.env`, dependencies, and local state.

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
| `shared/` directory | Not used by retained skills — each skill is self-contained |
| 40+ unused skill directories | Not actively used; can be retrieved from git history if needed |
| Trigger index table in CLAUDE.md | Redundant — SKILL.md description fields handle trigger matching |
| `PLATFORM_SUPPORT.md`, `INSTALL.md`, `SUPERPOWERS-README.md` | Outdated docs for removed features |
| `theplasmak/`, `inference-shell/` | Third-party content, not maintained |
| `run.py`, `debug_patent_raw.json` | Leftover artifacts |
| Test/debug artifacts in patent-search/ | `test_*.py`, `debug_*.py`, `*_results.json`, `*_report.md` |

### Target Repository Structure

```
good-skills/
├── skills/
│   ├── daily-newsletter/
│   │   ├── SKILL.md            # skills.sh standard format
│   │   ├── run_daily_newsletter.py
│   │   ├── bark_client.py      # self-contained utilities
│   │   ├── email_sender.py
│   │   └── newsletters/        # generated output (gitignored)
│   ├── arxiv-daily/
│   │   ├── SKILL.md
│   │   ├── run_arxiv_daily.py
│   │   ├── arxiv_fetcher.py
│   │   ├── bark_client.py
│   │   └── email_sender.py
│   ├── super-wardrobe/
│   │   ├── SKILL.md
│   │   ├── run_wardrobe.py
│   │   ├── wardrobe_advisor.py
│   │   ├── bark_client.py
│   │   └── outfits/            # generated output (gitignored)
│   ├── patent-search/
│   │   ├── SKILL.md
│   │   └── references/         # deep-dive docs loaded on demand
│   └── patent-specialist/
│       ├── SKILL.md
│       └── references/
├── install.sh                  # Single install script
├── .env.example                # Environment variable template
├── .env                        # Actual env (gitignored)
├── requirements.txt            # Consolidated Python dependencies
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

## Setup
Scripts are located at `$GOOD_SKILLS_HOME/skills/<skill-name>/`.
Run with: `python $GOOD_SKILLS_HOME/skills/<skill-name>/run_<name>.py`

(Agent instructions...)
```

Required frontmatter fields: `name`, `description`.
No `manifest.json` — all metadata lives in SKILL.md frontmatter.

### CLAUDE.md (Minimal)

The new CLAUDE.md contains only:

- One-line project description
- `$GOOD_SKILLS_HOME` path convention
- Development conventions (commit style, naming)
- Note that skills are in `skills/` directory

No trigger index table. Trigger matching is handled by each SKILL.md's `description` field.

### Environment Variables

Required by self-developed skills (documented in `.env.example`):

```bash
# Good Skills
GOOD_SKILLS_HOME=/path/to/good-skills   # Repo root path

# LLM API
OPENAI_API_KEY=                          # DeepSeek API key (OpenAI-compatible)
OPENAI_BASE_URL=                         # DeepSeek endpoint

# Email (SMTP)
SMTP_SERVER=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=
EMAIL_TO=

# Bark Push Notifications
BARK_KEY=
BARK_SERVER=                             # Optional, defaults to api.day.app

# Weather (super-wardrobe)
WEATHER_API_KEY=                         # OpenWeatherMap or similar

# SiYuan Notes (optional, for saving outputs)
SIYUAN_API_URL=                          # e.g. http://127.0.0.1:6806
SIYUAN_API_TOKEN=
```

### install.sh (Unified Installer)

A single script that installs everything needed:

```bash
#!/bin/bash
set -e

echo "=== Good Skills Installer ==="

# Set GOOD_SKILLS_HOME to repo root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "export GOOD_SKILLS_HOME=$SCRIPT_DIR" >> ~/.zshrc
export GOOD_SKILLS_HOME="$SCRIPT_DIR"

# 1. Install self-developed skills (SKILL.md → ~/.claude/skills/)
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

# 5. Remind about .env
if [ ! -f "$SCRIPT_DIR/.env" ]; then
  echo ""
  echo "⚠ Copy .env.example to .env and fill in your API keys:"
  echo "  cp .env.example .env"
fi

echo "=== Installation complete ==="
```

Users run `./install.sh` once. To update self-developed skills: re-run `npx skills add .`. To update open-source skills: `npx skills update`.

### Migration Strategy

1. **Create a new branch** `restructure` for the work
2. **Move retained skills** into `skills/` directory, preserving existing scripts
3. **Clean artifacts** from retained skills (remove test_*.py, debug_*.py, *_results.json, etc. from patent-search/)
4. **Update SKILL.md format** — ensure valid skills.sh frontmatter (name + description), add `$GOOD_SKILLS_HOME` script paths
5. **Write new CLAUDE.md** (minimal, under 50 lines)
6. **Write new README.md** (project overview + install instructions)
7. **Write install.sh** (unified installer)
8. **Create .env.example** with all required environment variables
9. **Consolidate requirements.txt** — merge dependencies from daily-newsletter, arxiv-daily, super-wardrobe
10. **Create .gitignore** — `__pycache__/`, `*.pyc`, `.env`, `venv/`, `newsletters/`, `outfits/`, `*.json` output files
11. **Verify** — all 5 SKILL.md files have valid frontmatter, scripts are runnable
12. **Test** — `npx skills add .` works with the new structure
13. **Delete everything else** — old skills, CLI, scripts, docs, configs (separate commit for easy revert)

### Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Losing skill content permanently | All content preserved in git history; can be recovered anytime |
| skills.sh CLI breaking changes | install.sh pins to known-good behavior; fallback is manual symlink |
| `npx skills add .` doesn't discover skills/ subdir | Verify during migration; fallback is placing SKILL.md at skill root dirs |
| Missing a skill that's actually needed | Start lean; add back from git history if needed |
| Python scripts reference wrong paths after move | Use `$GOOD_SKILLS_HOME` env var; test each script |

## Success Criteria

- Repository contains exactly 5 skill directories + install.sh
- Each skill is self-contained (no shared/ dependency)
- All SKILL.md files have valid skills.sh frontmatter (name + description)
- `npx skills add .` successfully installs all SKILL.md files
- `./install.sh` completes without errors
- `.env.example` documents all required environment variables
- `requirements.txt` includes all Python dependencies
- CLAUDE.md is under 50 lines
- No unused files remain in the repository
- Deletion is a separate commit from restructure (safe rollback)
