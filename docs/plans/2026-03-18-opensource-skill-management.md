# Open Source Skill Management Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add an `opensource/` manifest-and-script workflow so third-party skills can be refreshed quickly via `npx skills add`, while repo-root skills remain self-developed.

**Architecture:** Keep self-developed skills in the repository root and treat `opensource/` as install metadata only. The manifest stores raw install commands and thin scripts execute them line by line on Windows and POSIX systems.

**Tech Stack:** Markdown, PowerShell, POSIX shell

---

### Task 1: Add open-source skill manifest files

**Files:**
- Create: `opensource/README.md`
- Create: `opensource/sources.txt`
- Create: `opensource/install.ps1`
- Create: `opensource/install.sh`

**Step 1: Write the files**

Add a documented manifest and two small batch-install runners.

**Step 2: Sanity-check command flow**

Confirm the scripts skip blank lines and comments and execute remaining commands in order.

**Step 3: Commit**

Use a commit describing the new open-source management workflow.

### Task 2: Update repository documentation

**Files:**
- Modify: `README.md`

**Step 1: Clarify directory ownership**

Describe that root-level skills are self-developed, while `opensource/` tracks third-party installs.

**Step 2: Document update workflow**

Show how to run `opensource/install.ps1` or `opensource/install.sh`.

**Step 3: Commit**

Use a docs-focused commit message if splitting commits.
