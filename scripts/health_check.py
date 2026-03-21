#!/usr/bin/env python3
"""Good Skills Health Check - verify all skills are properly configured."""

import os
import sys
import importlib
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "skills"

# Skills with Python scripts that need imports verified
PYTHON_SKILLS = {
    "daily-newsletter": ["run_daily_newsletter", "daily_newsletter", "bark_client", "email_sender"],
    "arxiv-daily": ["run_arxiv_daily", "arxiv_fetcher", "bark_client", "email_sender"],
    "super-wardrobe": ["run_wardrobe", "wardrobe_advisor", "bark_client"],
    "super-fitness": ["run_fitness", "fitness_plan", "bark_client"],
    "vibe-daily": ["run_vibe_daily", "bark_client"],
    "weekly-report": ["run_weekly_report", "bark_client"],
    "daily-digest": ["run_daily_digest", "bark_client"],
}

# Required env vars per skill
ENV_VARS = {
    "daily-newsletter": ["OPENAI_API_KEY", "SMTP_USER", "SMTP_PASSWORD"],
    "arxiv-daily": ["OPENAI_API_KEY", "SMTP_USER", "SMTP_PASSWORD"],
    "super-wardrobe": ["OPENAI_API_KEY", "WEATHER_API_KEY"],
    "super-fitness": ["OPENAI_API_KEY"],
    "vibe-daily": ["OPENAI_API_KEY"],
    "weekly-report": ["OPENAI_API_KEY"],
    "daily-digest": [],
    "patent-search": [],
    "patent-specialist": [],
    "siyuan-note": ["SIYUAN_API_URL", "SIYUAN_API_TOKEN"],
    "xhs-skill": [],
    "humanizer-zh": [],
    "find-skills": [],
    "skill-creator": [],
}


def check_skill_md():
    """Check all skills have valid SKILL.md with required frontmatter."""
    print("\n=== SKILL.md Check ===")
    ok = 0
    fail = 0
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name == "shared":
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            print(f"  FAIL  {skill_dir.name}: missing SKILL.md")
            fail += 1
            continue

        content = skill_md.read_text()
        has_name = "name:" in content[:500]
        has_desc = "description:" in content[:500]
        if has_name and has_desc:
            print(f"  OK    {skill_dir.name}")
            ok += 1
        else:
            missing = []
            if not has_name:
                missing.append("name")
            if not has_desc:
                missing.append("description")
            print(f"  FAIL  {skill_dir.name}: missing {', '.join(missing)}")
            fail += 1
    print(f"\n  {ok} passed, {fail} failed")
    return fail == 0


def check_python_imports():
    """Check Python modules can be imported."""
    print("\n=== Python Import Check ===")
    ok = 0
    fail = 0
    for skill_name, modules in PYTHON_SKILLS.items():
        skill_dir = SKILLS_DIR / skill_name
        if not skill_dir.exists():
            print(f"  SKIP  {skill_name}: directory not found")
            continue

        sys.path.insert(0, str(skill_dir))
        for mod_name in modules:
            try:
                importlib.import_module(mod_name)
                print(f"  OK    {skill_name}/{mod_name}")
                ok += 1
            except Exception as e:
                print(f"  FAIL  {skill_name}/{mod_name}: {e}")
                fail += 1
        sys.path.pop(0)
    print(f"\n  {ok} passed, {fail} failed")
    return fail == 0


def check_env_vars():
    """Check required environment variables are set."""
    print("\n=== Environment Variables Check ===")

    # Load .env if exists
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                if val:
                    os.environ.setdefault(key.strip(), val.strip())

    ok = 0
    fail = 0
    for skill_name, vars_needed in ENV_VARS.items():
        if not vars_needed:
            continue
        missing = [v for v in vars_needed if not os.environ.get(v)]
        if missing:
            print(f"  WARN  {skill_name}: missing {', '.join(missing)}")
            fail += 1
        else:
            print(f"  OK    {skill_name}")
            ok += 1
    print(f"\n  {ok} passed, {fail} warnings")
    return True  # Env vars are warnings, not failures


def check_shared_symlinks():
    """Check shared module symlinks are valid."""
    print("\n=== Shared Symlinks Check ===")
    ok = 0
    fail = 0
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir() or skill_dir.name == "shared":
            continue
        bark = skill_dir / "bark_client.py"
        if bark.is_symlink():
            if bark.resolve().exists():
                print(f"  OK    {skill_dir.name}/bark_client.py -> shared")
                ok += 1
            else:
                print(f"  FAIL  {skill_dir.name}/bark_client.py: broken symlink")
                fail += 1
    print(f"\n  {ok} valid, {fail} broken")
    return fail == 0


if __name__ == "__main__":
    print("Good Skills Health Check")
    print("=" * 40)

    results = [
        check_skill_md(),
        check_shared_symlinks(),
        check_env_vars(),
    ]

    # Python import check is optional (may fail on missing deps)
    if "--imports" in sys.argv:
        results.append(check_python_imports())

    print("\n" + "=" * 40)
    if all(results):
        print("All checks passed!")
        sys.exit(0)
    else:
        print("Some checks failed. See above for details.")
        sys.exit(1)
