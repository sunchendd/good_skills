# Good Skills

Self-developed AI agent skills with Python automation. Skills are in `skills/` subdirectories.

## Setup

```bash
./install.sh          # One-time setup
cp .env.example .env  # Fill in API keys
```

## Conventions

- Commits: Conventional Commits (`type(scope): subject`)
- Naming: lowercase with hyphens (e.g., `daily-newsletter`)
- Skills: SKILL.md with `name` + `description` frontmatter (skills.sh standard)
- Scripts run from repo: `python skills/<name>/run_<name>.py`

## Environment

See `.env.example` for required API keys (DeepSeek, SMTP, Bark, Weather).
