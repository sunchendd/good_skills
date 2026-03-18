# Open Source Skill Management Design

**Date:** 2026-03-18

## Goal

Make open-source skills easy to refresh without vendoring their source into this repository, while keeping self-developed skills and shared infrastructure in the repo root.

## Decision

Use an `opensource/` directory as a lightweight source-of-truth for third-party skill installs instead of storing their code in this repo.

The directory will contain:

- `sources.txt`: one install command per line using `npx skills add ...`
- `install.ps1`: executes each non-comment line in order
- `install.sh`: POSIX equivalent for macOS/Linux
- `README.md`: explains the workflow and the separation from local self-developed skills

## Why This Approach

- Fast updates: refreshing open-source skills becomes “edit manifest, rerun script”
- Lower repo noise: avoids copying third-party code, caches, and generated files into version control
- Clear ownership: root-level skills remain self-developed and can evolve independently
- Compatible with skills.sh: the install commands match the documented `npx skills add` workflow

## Scope

In scope:

- Add the `opensource/` management directory
- Document the new workflow in the repo README
- Seed the manifest with a small verified set of open-source skills

Out of scope for this pass:

- Reorganizing every existing directory into a new physical tree
- Auto-detecting all third-party skills already present on a machine
- Implementing version pinning or lockfile behavior for skills.sh installs
