# CLI GitHub URL Install Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:writing-plans to create the implementation plan.

**Goal:** Let `good-skills` install a specific third-party skill using a GitHub repository argument and a `--skill` flag, similar to `npx skills add <repo> --skill <name>`.

**Architecture:** Keep the existing third-party download path in the CLI, but add a thin parsing layer for GitHub repository inputs. Expose the new behavior through an `add` command and reuse the same installer so both `owner/repo@skill-name` and `add <repo> --skill <name>` stay consistent.

**Key Decisions:**
- Add a dedicated `add <repo>` command instead of replacing the existing `install [skill]` flow.
- Reuse `installSkill()` and third-party raw GitHub download logic.
- Add a small parser helper that accepts `https://github.com/owner/repo`, `owner/repo`, and an optional branch override via `--ref`.
- Cover the parser with focused unit tests instead of end-to-end network tests.

**Error Handling:**
- Reject unsupported repo strings with a clear message that mentions the expected GitHub URL or `owner/repo` format.
- Require `--skill` for the new `add` command.
- Keep existing install behavior untouched for local registry skills and `owner/repo@skill-name`.

**Testing:**
- Add parser unit tests for GitHub URL input, shorthand repo input, and invalid input.
- Run the targeted Node test file and the CLI package test command.
