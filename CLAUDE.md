# Good Skills

Self-developed AI agent skills with Python automation. Skills are in `skills/` subdirectories.

## Setup

```bash
./install.sh          # One-time setup
cp .env.example .env  # Fill in API keys
```

## Running Skills

```bash
# Via wrapper (recommended) - auto-loads .env
scripts/run_skill.sh skills/<name>/run_<name>.py

# Via npm scripts
npm run fitness | wardrobe | newsletter | arxiv | vibe | weekly | digest

# Via npx (no install)
npx good-skills run <name>
```

**Always use `python3`, never `python`** (not available on this system).

## Project Structure

```
skills/<name>/
  run_<name>.py   # Entry point
  SKILL.md        # Skill metadata (name + description frontmatter)
  *.py            # Supporting modules
scripts/
  run_skill.sh    # Wrapper: loads .env + runs python3
  archive.sh      # Archive generated outputs to archive/YYYY-MM/
```

## Conventions

- Commits: Conventional Commits (`type(scope): subject`)
- Naming: lowercase with hyphens (e.g., `daily-newsletter`)
- Skills: SKILL.md with `name` + `description` frontmatter (skills.sh standard)

## Environment Variables

Loaded from `.env` (auto-loaded by `run_skill.sh`) and exported in `~/.zshrc`:

| Variable | Description |
|----------|-------------|
| `DEEPSEEK_API_KEY` | LLM API |
| `GITHUB_TOKEN` | GitHub API |
| `BARK_TOKEN` | iOS push notifications |
| `EMAIL_SENDER` | QQ Mail sender (`995943586@qq.com`) |
| `EMAIL_RECIPIENTS` | Recipient (`sunchend@outlook.com`) |
| `QQ_EMAIL_PASSWORD` | QQ Mail SMTP auth code |
| `SIYUAN_HOST` | SiYuan Notes API host |
| `SIYUAN_TOKEN` | SiYuan Notes API token |

## Scheduled Tasks (LaunchAgent)

Daily tasks run via macOS LaunchAgent (more reliable than cron on macOS):

| Time | Task |
|------|------|
| 06:30 | super-fitness |
| 06:35 | super-wardrobe |
| 06:40 | daily-newsletter |
| 07:00 | arxiv-daily |
| 07:30 | vibe-daily |
| 09/12/15/18/21:00 | github-watcher |
| 22:50 | archive |
| 23:00 | daily-digest |
| Sat 20:00 | weekly-report |

Manage with:
```bash
launchctl start com.goodskills.<name>   # trigger manually
launchctl list | grep goodskills        # check status
cat /tmp/good-skills-<name>.log         # view logs
```

## Output & Archive

Generated files are gitignored and archived nightly to `archive/YYYY-MM/`:
- `skills/*/newsletters/` `skills/*/outfits/` `skills/*/daily_tasks/`
- `skills/*/reports/` `skills/*/logs/`
