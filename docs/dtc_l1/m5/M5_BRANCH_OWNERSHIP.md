# M5 Multi-Window Branch and Ownership Contract

Status: **ACTIVE — REQUIRED FOR PARALLEL CODEX WINDOWS**

Purpose: prevent compute, Extended-20, and graphics work from editing the same worktree/branch or mutable handoff files concurrently.

## 1. Active Paper/Extended compute window

### Core

`hrl/decoupled-l1-m5-v0`

### Framework

`hrl/decoupled-l1-exp-m5-v0`

Owner: **Compute Codex window**.

Scope:

- current R5DV/M5.0B recovery;
- Paper-10 through M5.6;
- M5.E1-E3 Extended-20 formal track after its dependencies;
- compute review packs;
- active `codex_handoff/LATEST_REPORT.md`;
- `M5.COMPUTE_FREEZE` join handoff.

No other Codex window writes these branches/worktrees.

## 2. Extended-20 selection branch

Framework:

`hrl/decoupled-l1-exp-m5-extended20-select-v0`

Reviewed selection commit:

`d43b6eec93f68efa94057f34ffa699463b53e6a6`

Status: **reviewed/frozen selection evidence**.

Do not run formal simulations or modify Core from this branch. Keep it as provenance for why the 20 workloads were chosen.

## 3. Graphics research window — available before compute freeze

Framework-only branch:

`hrl/decoupled-l1-exp-m5-graphics-research-v0`

Owner: **Graphics Research Codex window**.

Scope only:

- M5.7 provenance;
- M5.8 path recovery;
- source/artifact search;
- non-Core helper/research scripts where appropriate;
- `LATEST_GRAPHICS_RESEARCH_REPORT.md`;
- implementation/test plans for later M5.9.

Forbidden before compute freeze:

- modifying GPGPU-Sim Core;
- writing active compute Framework branch;
- running Paper/Extended formal waves;
- editing active compute `LATEST_REPORT.md`;
- starting M5.9 integration.

## 4. Graphics integration branches — created only after compute freeze

After `M5.COMPUTE_FREEZE`, create from exact freeze SHAs:

Core:

`hrl/decoupled-l1-m5-graphics-v0`

Framework:

`hrl/decoupled-l1-exp-m5-graphics-v0`

Owner: graphics integration window.

The branch bases must be exactly:

- `COMPUTE_FREEZE_CORE_SHA`;
- `COMPUTE_FREEZE_FRAMEWORK_SHA`.

Do not base graphics integration on the earlier graphics-research branch's stale compute tree. Transfer only reviewed research documents/scripts/patches intentionally.

## 5. Shared-file ownership

### Compute-owned mutable files

Only the compute window updates on active compute branches:

- `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
- active compute issue log entries
- Paper/Extended current-state handoffs
- formal result registries

### Graphics-research-owned mutable files

Only graphics research updates on its branch:

- `docs/dtc_l1/codex_handoff/LATEST_GRAPHICS_RESEARCH_REPORT.md`
- M5.7/M5.8 graphics handoffs/evidence

### ChatGPT/researcher authority files

Roadmap/approval documents written by ChatGPT/researcher are not silently rewritten by either window. Codex may propose corrections in its own report/handoff; semantic changes that alter approved experiment meaning require the normal decision process.

## 6. Worktree isolation

Use a distinct git worktree per branch/window. Never point two Codex windows at the same working directory.

Before fetch/merge/rebase:

1. `git status --short`;
2. identify local uncommitted files/process-owned outputs;
3. preserve them;
4. do not `reset --hard`, `clean`, or blind-pull over another window's work;
5. fast-forward or reconcile deliberately.

Never use `git add .` or `git add -A`; stage explicit paths only.

## 7. Process/output isolation

Each simulation job uses a unique output directory keyed by experiment identity. Research windows must not reuse `/tmp` directories owned by live compute jobs.

Do not kill another window's processes unless the owning window has explicitly classified them obsolete/unsafe.

## 8. Merge/cherry-pick discipline

- Selection evidence is referenced by immutable commit; it need not be merged wholesale into compute history.
- Graphics research evidence may later be cherry-picked/copied onto graphics integration branches, but avoid merges that reintroduce stale pre-freeze compute state.
- Any Core patch needed by graphics after freeze is implemented/reviewed on the graphics Core branch, never back-written into frozen compute branches.
