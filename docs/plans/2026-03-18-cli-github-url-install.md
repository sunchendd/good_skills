# CLI GitHub URL Install Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `good-skills add <repo> --skill <name>` so users can install a specific skill from a GitHub repository using a `skills.sh`-style flow.

**Architecture:** Introduce one shared parser for GitHub repository inputs, then wire a new `add` command into the existing installer pipeline. Keep the current `install owner/repo@skill` syntax working so old scripts do not break.

**Tech Stack:** Node.js, commander, built-in `node:test`

---

### Task 1: Add parser tests first

**Files:**
- Create: `packages/cli/src/installer.test.js`
- Modify: `packages/cli/package.json`

**Step 1: Write the failing test**

Add parser tests that expect:
- `https://github.com/vercel-labs/skills` to resolve to `owner=vercel-labs`, `repo=skills`, `branch=main`
- `vercel-labs/skills` to resolve the same way
- invalid inputs to throw

**Step 2: Run test to verify it fails**

Run: `node --test src/installer.test.js`
Expected: FAIL because the new parser does not exist yet.

**Step 3: Make the package test command portable**

Update `packages/cli/package.json` so `npm test` runs discovered tests on Windows as well.

**Step 4: Run test to verify it still fails for the right reason**

Run: `npm test`
Expected: FAIL because the parser is still missing.

### Task 2: Implement the GitHub repo parser and add command

**Files:**
- Modify: `packages/cli/src/installer.js`
- Create: `packages/cli/src/commands/add.js`
- Modify: `packages/cli/src/commands/install.js`
- Modify: `packages/cli/src/index.js`

**Step 1: Implement the parser**

Add a helper that converts GitHub URL or `owner/repo` input into `{ owner, repo, branch, rawBase }`.

**Step 2: Add the new command**

Create `add <repo>` with required `--skill`, optional `--ref`, and existing install destination flags.

**Step 3: Reuse shared install execution**

Refactor install flow just enough so `install` and `add` share the same install loop and third-party options shape.

**Step 4: Run tests**

Run: `node --test src/installer.test.js`
Expected: PASS

### Task 3: Document and verify the new user flow

**Files:**
- Modify: `README.md`

**Step 1: Add examples**

Document:
- `npx good-skills add https://github.com/vercel-labs/skills --skill find-skills`
- `npx good-skills add vercel-labs/skills --skill find-skills`
- existing shorthand `npx good-skills install vercel-labs/skills@find-skills`

**Step 2: Run final verification**

Run:
- `npm test`
- `node src/index.js add https://github.com/vercel-labs/skills --skill find-skills --help`

Expected:
- tests pass
- help output shows the new command and options
