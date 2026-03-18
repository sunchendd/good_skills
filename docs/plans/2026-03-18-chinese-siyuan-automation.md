# Chinese SiYuan Automation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Unify Good Skills SiYuan output into a Chinese directory structure, remove embedded secrets and personal data, and leave the npm CLI publish path in a sanitized, releasable state.

**Architecture:** Centralize SiYuan path generation and notebook selection in `shared/`, migrate direct API callers onto the shared layer, then remove hardcoded secrets and generated artifacts. Keep npm publishing scoped to `packages/cli/`.

**Tech Stack:** Python scripts, shell installer/docs, npm CLI metadata

---

### Task 1: Add shared SiYuan path model

**Files:**
- Modify: `shared/config.py`
- Modify: `shared/siyuan.py`
- Test: `shared/` smoke checks by static inspection

**Step 1: Write the failing test**

Define the expected interface on paper first:

- shared config exposes safe defaults only
- shared SiYuan helper can build `AI自动化/<功能中文名>/<日报中文名>/<日期>`
- shared helper can create the configured notebook path without per-skill custom URL logic

**Step 2: Run test to verify it fails**

Run environment verification for Python if available.
Expected: if runtime is unavailable, document that execution is blocked and proceed with code-first static refactor plus later verification notes.

**Step 3: Write minimal implementation**

- add Chinese notebook and path helpers
- normalize host/token handling
- add a single save function for automated reports

**Step 4: Run test to verify it passes**

If Python runtime is available, run a small import/smoke check.
Otherwise, verify call sites can import the new API by static inspection.

**Step 5: Commit**

Commit after the shared SiYuan layer is stable.

### Task 2: Migrate SiYuan-writing skills to shared API

**Files:**
- Modify: `wuyu-xiaohongshu/run_wuyu.py`
- Modify: `weekly-report/run_weekly_report.py`
- Modify: `daily-digest/run_daily_digest.py`
- Modify: `siyuan-daily/run_siyuan_daily.py`
- Modify: `arxiv-daily/run_arxiv_daily.py`
- Modify: `daily-newsletter/run_daily_newsletter.py`
- Modify: `vibe-daily/run_vibe_daily.py`
- Modify: `super-fitness/run_fitness.py`
- Modify: `super-wardrobe/run_wardrobe.py`

**Step 1: Write the failing test**

List the per-skill target mapping:

- `论文追踪/arXiv日报`
- `科技资讯/每日早报`
- `开发动态/Vibe日报`
- `健身助手/健身日报`
- `穿搭助手/穿搭日报`
- `内容创作/无语哥选题`
- `效率复盘/每日汇总`
- `效率复盘/周报`
- `效率复盘/思源日报`

**Step 2: Run test to verify it fails**

Search for remaining direct `createDocWithMd` and notebook lookup logic.
Expected: current repository still contains direct call sites.

**Step 3: Write minimal implementation**

- replace direct SiYuan API calls with shared helper usage
- pass Chinese feature/report names explicitly
- keep content generation unchanged

**Step 4: Run test to verify it passes**

Search again for direct path-building code.
Expected: targeted scripts now rely on shared helper instead of custom notebook/path logic.

**Step 5: Commit**

Commit once the targeted scripts consistently use the shared path scheme.

### Task 3: Remove hardcoded secrets and personal defaults

**Files:**
- Modify: `.env.example`
- Modify: `README.md`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `shared/config.py`
- Modify: `shared/email_utils.py`
- Modify: skill scripts that hardcode sender or recipients

**Step 1: Write the failing test**

Define forbidden patterns:

- real sender email
- hardcoded recipient list
- personal public host
- non-empty default Bark token

**Step 2: Run test to verify it fails**

Search repository for those patterns.
Expected: matches still exist before cleanup.

**Step 3: Write minimal implementation**

- replace with env-based config
- update docs to placeholder values
- keep examples obviously fake and safe

**Step 4: Run test to verify it passes**

Search again for the forbidden patterns.
Expected: no real values remain in tracked source files.

**Step 5: Commit**

Commit after sensitive defaults are fully removed.

### Task 4: Remove generated artifacts and add ignore rules

**Files:**
- Modify: `.gitignore`
- Delete: tracked `__pycache__` files
- Delete: generated report/test output files containing personal paths or data
- Optionally add: `.npmignore`

**Step 1: Write the failing test**

Define artifact classes that must not ship:

- `__pycache__/`
- generated newsletters / logs / test output
- downloaded thumbnails / result snapshots

**Step 2: Run test to verify it fails**

Search git-tracked files for those artifacts.
Expected: repository currently contains them.

**Step 3: Write minimal implementation**

- remove tracked artifacts
- extend ignore rules to prevent reintroduction

**Step 4: Run test to verify it passes**

Check git status and repeat artifact search.
Expected: artifacts are gone from tracked content.

**Step 5: Commit**

Commit after repository contents are publish-safe.

### Task 5: Prepare npm publish metadata and release notes

**Files:**
- Modify: `packages/cli/package.json`
- Modify: `README.md`
- Modify: `INSTALL.md`
- Modify: any CLI docs that mention install/publish flow

**Step 1: Write the failing test**

Define publish-ready expectations:

- npm package location is explicit
- release notes mention sanitized env setup
- install docs do not depend on personal infrastructure

**Step 2: Run test to verify it fails**

Inspect current docs and metadata.
Expected: documentation is incomplete or still tied to personal defaults.

**Step 3: Write minimal implementation**

- refresh package metadata only where needed
- document `npx good-skills ...`
- document required env vars as placeholders

**Step 4: Run test to verify it passes**

Review package and docs for consistency.
Expected: docs point to `packages/cli` as the publish target and no longer expose personal data.

**Step 5: Commit**

Commit once publish documentation is coherent.

### Task 6: Final verification and publish-readiness summary

**Files:**
- Modify: `docs/plans/2026-03-18-chinese-siyuan-automation-design.md`
- Modify: `docs/plans/2026-03-18-chinese-siyuan-automation.md`

**Step 1: Write the failing test**

Create a final checklist:

- targeted skills migrated
- sensitive defaults removed
- artifacts deleted
- npm path documented

**Step 2: Run test to verify it fails**

Run final searches and status review before completion.

**Step 3: Write minimal implementation**

Record actual verification results and remaining blockers such as missing Node/npm or npm login.

**Step 4: Run test to verify it passes**

Review the repository diff and note what is ready versus what still needs environment credentials.

**Step 5: Commit**

Create a final commit for the implementation batch if the user wants commits during this session.
