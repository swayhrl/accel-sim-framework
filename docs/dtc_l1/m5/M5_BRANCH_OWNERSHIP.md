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

- current M5.0B workload recovery (R5DV/M5-T005 already closed);
- Paper-10 through M5.6;
- M5.E1-E3 Extended-20 formal track after its dependencies;
- compute review packs;
- active `codex_handoff/LATEST_REPORT.md`;
- `M5.COMPUTE_FREEZE` join handoff;
- final M5.12 negative-evidence synthesis after compute freeze.

No other Codex window writes these branches/worktrees.

## 2. Extended-20 selection branch

Framework:

`hrl/decoupled-l1-exp-m5-extended20-select-v0`

Reviewed selection commit:

`d43b6eec93f68efa94057f34ffa699463b53e6a6`

Status: **reviewed/frozen selection evidence**.

Do not run formal simulations or modify Core from this branch. Keep it as provenance for why the 20 workloads were chosen.

The active compute branch contains the researcher/ChatGPT review-refined approved portfolio. Do not change membership on the selection branch based on later DTC results.

## 3. Graphics research branch — completed/frozen

Framework-only branch:

`hrl/decoupled-l1-exp-m5-graphics-research-v0`

Reviewed closeout commit:

`ed36abb8f98372dbd1fef11d5b0e8780fb8bf17d`

Status:

`GRAPHICS_SOURCE_BACKED_UNAVAILABLE`

Owner: **no active writer under current evidence**. Treat this branch as frozen research evidence.

Completed scope:

- M5.7 provenance;
- M5.8 path recovery;
- source/artifact/history audit;
- `LATEST_GRAPHICS_RESEARCH_REPORT.md`;
- accepted negative-evidence handoffs.

Do not continue editing this branch merely to search the same already-audited routes again. Reopen only if genuinely new original/source-backed evidence appears.

## 4. No graphics integration branches under current closeout

The earlier plan to create:

- Core `hrl/decoupled-l1-m5-graphics-v0`;
- Framework `hrl/decoupled-l1-exp-m5-graphics-v0`;

after compute freeze is **inactive** because M5.8 closed `GRAPHICS_SOURCE_BACKED_UNAVAILABLE` and that result was accepted in `M5_GRAPHICS_RESEARCH_CLOSEOUT_APPROVAL.md`.

Do not create those branches merely to restate unavailability or to build a proxy.

If a genuinely new artifact later reopens M5.8 and establishes `GRAPHICS_PATH_SOURCE_BACKED`, then create fresh graphics integration branches from the exact `COMPUTE_FREEZE_CORE_SHA` / `COMPUTE_FREEZE_FRAMEWORK_SHA`. Never base integration on the stale pre-freeze graphics-research tree.

## 5. Shared-file ownership

### Compute-owned mutable files

Only the compute window updates on active compute branches:

- `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
- active compute issue log entries
- Paper/Extended current-state handoffs
- formal result registries
- `M5_COMPUTE_FREEZE.md`
- final M5.12 synthesis/review pack

### Frozen graphics-research files

The accepted graphics branch contains:

- `docs/dtc_l1/codex_handoff/LATEST_GRAPHICS_RESEARCH_REPORT.md`
- M5.7/M5.8 graphics handoffs/evidence

These are evidence inputs, not active mutable coordination files after closeout.

### ChatGPT/researcher authority files

Roadmap/approval documents written by ChatGPT/researcher are not silently rewritten by Codex. Codex may propose corrections in its own report/handoff; semantic changes that alter approved experiment meaning require the normal decision process.

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

Each simulation job uses a unique output directory keyed by experiment identity.

Do not kill another window's processes unless the owning window has explicitly classified them obsolete/unsafe.

Under the current graphics-unavailable closeout there should be no graphics simulation jobs competing with active compute waves.

## 8. Merge/cherry-pick discipline

- Selection evidence is referenced by immutable commit; it need not be merged wholesale into compute history.
- Graphics research evidence is referenced by immutable closeout commit and consumed by final M5.12; no merge of stale pre-freeze compute state is needed.
- If graphics is ever reopened by new source-backed artifacts, transfer only reviewed evidence/patches intentionally onto integration branches created from compute-freeze SHAs.
