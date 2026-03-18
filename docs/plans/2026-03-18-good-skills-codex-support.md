# Good Skills Codex Support Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add full Codex platform support to `good-skills`.

**Architecture:** Extend the shared platform map first, then wire the platform name into the CLI and shell scripts, and finally update the installation documentation so all entrypoints agree on the same Codex paths.

**Tech Stack:** Node.js, shell scripts, built-in `node:test`

---

### Task 1: Add a failing Codex platform test

**Files:**
- Create: `packages/cli/src/platforms.test.js`

**Step 1: Write the failing test**

Cover:
- `resolvePaths("codex")` global path is `~/.codex/skills`
- `resolvePaths("codex", true)` project path is `.codex/skills`

**Step 2: Run test to verify it fails**

Run: `node --test src/platforms.test.js`
Expected: FAIL because Codex is not in the platform map yet.

### Task 2: Implement Codex in platform mappings

**Files:**
- Modify: `packages/cli/src/platforms.js`
- Modify: `packages/cli/src/index.js`

**Step 1: Add Codex path mapping**

Add a `codex` entry to the CLI platform map with global and project paths.

**Step 2: Update CLI help text**

Include `codex` in platform help descriptions for install/add/status flows.

**Step 3: Run tests**

Run: `npm test`
Expected: PASS

### Task 3: Update shell installers and docs

**Files:**
- Modify: `install.sh`
- Modify: `remote-install.sh`
- Modify: `update.sh`
- Modify: `uninstall.sh`
- Modify: `INSTALL.md`
- Modify: `PLATFORM_SUPPORT.md`

**Step 1: Add `--codex` support to shell scripts**

Update option parsing, help text, all-platform expansion, and install paths.

**Step 2: Update docs**

Document Codex global and project paths wherever supported platforms are listed.

**Step 3: Final verification**

Run:
- `npm test`
- `node src/index.js install --help`
- `Select-String` checks for `codex`, `.codex/skills`, and `--codex`

Expected:
- tests pass
- CLI help shows Codex
- shell/docs references are consistent
