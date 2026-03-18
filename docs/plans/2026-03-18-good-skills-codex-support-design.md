# Good Skills Codex Support Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:writing-plans to create the implementation plan.

**Goal:** Add Codex as a first-class installation target in `good-skills` so both the npm CLI and shell installers can install skills into Codex skill directories.

**Architecture:** Treat Codex like the existing platform entries by adding it to the shared platform mapping and then propagating the new platform name through CLI help text, shell installers, uninstall/update scripts, and installation docs. Use the Codex desktop convention of `~/.codex/skills` for global installs and `.codex/skills` for project installs.

**Key Decisions:**
- Keep `codex` as a standalone platform name rather than reusing `antigravity`.
- Update both JavaScript and shell entrypoints so CLI installs and script installs stay consistent.
- Add a targeted platform-resolution unit test first to prevent the new platform from being only partially wired in.

**Testing:**
- Add a Node test covering `resolvePaths('codex')` and project path mapping.
- Run the CLI package tests.
- Verify shell scripts and docs mention `--codex`.
