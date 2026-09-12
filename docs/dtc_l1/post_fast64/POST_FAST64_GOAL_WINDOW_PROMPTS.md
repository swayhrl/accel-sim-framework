# POST-FAST64 Goal Window Prompts

Status: **READY FOR MULTI-WINDOW GOAL MODE**

Read first in every window:

- `docs/dtc_l1/post_fast64/POST_FAST64_MULTI_GOAL_CONTRACT.md`
- `docs/dtc_l1/post_fast64/POST_FAST64_LANE_HANDOFFS.md`

Frozen accepted authority:

`hrl/decoupled-l1-fast64-v0@18a68dcccd795f1b6cda75504e9450d00c9cee02`

Do not modify the completed FAST64 branch.

The current already-started Codex window may remain the coordinator/orchestrator. Before it pushes, it must `git fetch` and integrate these remote planning documents rather than overwrite them.

---

# Window A — Paper results lane

Recommended branch:

`hrl/post-fast64-paper-v0`

Paste-ready Goal:

```text
START GOAL MODE NOW.

You own POST-FAST64 Lane A only.

Read and obey:
  docs/dtc_l1/post_fast64/POST_FAST64_MULTI_GOAL_CONTRACT.md
  docs/dtc_l1/post_fast64/POST_FAST64_LANE_HANDOFFS.md

Frozen FAST64 authority:
  18a68dcccd795f1b6cda75504e9450d00c9cee02

Create/use a separate worktree and branch:
  hrl/post-fast64-paper-v0

Execute A0 -> A1 -> A2 -> A3 -> A4 -> A5 to:
  A_PAPER_RESULTS_READY

Do not launch simulator work unless a source/derivation validation absolutely requires it; this lane should primarily consume accepted evidence.

Produce reproducible plot-ready tables/scripts and the paper-facing analysis, preserving exact provenance and negative results.

Ordinary parser/path/table/plot problems must be solved, not used to stop Goal mode.

Use:
  OBSERVE -> CLASSIFY -> INSPECT SOURCE/EVIDENCE -> FIX -> REGRESS -> RESUME

Pause only at the researcher boundaries in the Multi-Goal Contract.

Commit/push meaningful lane checkpoints only. Never git add . or -A.

Terminal state:
  A_PAPER_RESULTS_READY
```

---

# Window B — Physical pool causal lane

Recommended branch:

`hrl/post-fast64-physical-causal-v0`

Paste-ready Goal:

```text
START GOAL MODE NOW.

You own POST-FAST64 Lane B only.

Read and obey:
  docs/dtc_l1/post_fast64/POST_FAST64_MULTI_GOAL_CONTRACT.md
  docs/dtc_l1/post_fast64/POST_FAST64_LANE_HANDOFFS.md

Frozen FAST64 authority:
  18a68dcccd795f1b6cda75504e9450d00c9cee02

Create/use:
  hrl/post-fast64-physical-causal-v0

Execute B0 -> B1 -> B2 -> B3 immediately from source + accepted Stage6 evidence.

Do NOT start new runs until B0-B3 identify the exact unresolved telemetry gaps.

If B4 proves new telemetry is required, coordinate through Lane D artifacts or, if no separate D window exists, implement only the minimum observer path allowed by the contract and run B5.

Classify every hypothesis only as:
  SOURCE_PROVEN
  MEASURED_CORRELATION
  DATA_DOES_NOT_SUPPORT
  INSUFFICIENT_NEEDS_TELEMETRY

Do not force a causal story from correlation.

Ordinary build/parser/row/resource problems are work to solve. Do not stop Goal mode after a failed hypothesis or row.

Terminal state:
  B_PHYSICAL_CAUSAL_READY
```

---

# Window C — Duplicate miss / thesis 4.2.2 lane

Recommended branch:

`hrl/post-fast64-duplicate-miss-v0`

Paste-ready Goal:

```text
START GOAL MODE NOW.

You own POST-FAST64 Lane C only.

Read and obey:
  docs/dtc_l1/post_fast64/POST_FAST64_MULTI_GOAL_CONTRACT.md
  docs/dtc_l1/post_fast64/POST_FAST64_LANE_HANDOFFS.md

Frozen FAST64 authority:
  18a68dcccd795f1b6cda75504e9450d00c9cee02

Create/use:
  hrl/post-fast64-duplicate-miss-v0

Execute C0 -> C1 -> C2 -> C3 first using accepted FAST64 evidence only.

The central question is the dissertation 4.2.2 claim that, without conventional MSHR merge, duplicate lower requests are rare because locality normally lets the cache Tag identify an in-flight same-line request.

Prove source semantics of DTC_L1_io_duplicate_after_eviction before using it.
Quantify all FAST12 IO rows without rerunning them.
Retain exceptions and distribution; do not hide them behind an average.

If OO comparison is scientifically needed and accepted evidence lacks an exact counter, write the precise C4 telemetry requirement and consume Lane D observer evidence when available. Do not invent an OO proxy.

Ordinary evidence/parser/source issues must be solved rather than stopping.

Terminal state:
  C_DUPLICATE_MISS_READY
```

---

# Window D — Observer telemetry lane

Recommended Framework branch:

`hrl/post-fast64-observer-v0`

Core branches, only when required:

- `hrl/dtc-l1-post-fast64-observer95-v0` rooted at accepted Core95
- `hrl/dtc-l1-post-fast64-observer658-v0` rooted at accepted Core658 for 2D

Paste-ready Goal:

```text
START GOAL MODE NOW.

You own POST-FAST64 Lane D only.

Read and obey:
  docs/dtc_l1/post_fast64/POST_FAST64_MULTI_GOAL_CONTRACT.md
  docs/dtc_l1/post_fast64/POST_FAST64_LANE_HANDOFFS.md

Frozen FAST64 authority remains immutable.

Do not instrument speculative metrics just because CPU is available.
First read B4/C4 handoffs if they exist and instrument only counters that close a named unresolved scientific question.

Execute D0 -> D1 -> D2 -> D3.
Do not launch the expensive diagnostic wave before D3 exact observer-equivalence PASS.

Then execute D4/D5 dynamically with no duplicate runs and with the researcher disk floor >=10 GiB after projected launch.

Every new row is:
  POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT

Observer state must never affect Tag/victim/allocation/free/retire/reclaim/lower/completion behavior.

If any pre-existing scientific output changes in observer equivalence, treat that as an observer bug, investigate, repair, and rerun only affected qualification. Do not use the data.

Ordinary build/test/path/resource/row-local problems must be solved, not used to stop Goal mode.

Terminal state:
  D_OBSERVER_EVIDENCE_READY_IF_NEEDED
```

---

# Coordinator / integration window

Recommended branch:

`hrl/decoupled-l1-fast64-post-analysis-v0`

The already-running Codex window can serve this role.

Paste-ready continuation after fetching this planning commit:

```text
CONTINUE GOAL MODE AS POST-FAST64 COORDINATOR.

First:
  git fetch origin
and integrate the remote planning authority under:
  docs/dtc_l1/post_fast64/

Do not overwrite it with stale local copies.

Read:
  POST_FAST64_MULTI_GOAL_CONTRACT.md
  POST_FAST64_LANE_HANDOFFS.md
  POST_FAST64_GOAL_WINDOW_PROMPTS.md

Your role is:
- continue any lane work you already started without duplication;
- monitor/consume compact commits from separate lane branches;
- do not have multiple windows write this coordinator branch concurrently;
- keep accepted FAST64 immutable;
- prepare E0/E1/E2 integration only after required lane PASS artifacts exist.

If another lane encounters an ordinary problem, it should solve it locally. Do not convert a lane-local build/parser/resource/negative-result issue into a researcher stop.

When lane commits are ready, inspect/cherry-pick only compact scientific artifacts and validators; preserve branch provenance in an integration manifest.

Terminal state:
  POST_FAST64_PAPER_ANALYSIS_AND_MECHANISM_EXPLORATION_READY_FOR_REVIEW
```

## Suggested concurrency

If opening multiple windows, preferred split is:

1. Existing/current window: coordinator + whatever work it already owns.
2. Window A: paper results, no simulator burden.
3. Window B: physical-pool source/existing-data analysis.
4. Window C: duplicate-request source/existing-data analysis.
5. Window D: open only when B4/C4 have concrete telemetry requirements, unless the current window has already begun D work.

This prevents three windows from independently inventing overlapping instrumentation.
