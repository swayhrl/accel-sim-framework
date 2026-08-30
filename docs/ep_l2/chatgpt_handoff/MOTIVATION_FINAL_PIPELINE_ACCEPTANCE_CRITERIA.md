# EP-L2 Motivation Figures — Final Pipeline Acceptance Criteria

Status: **mandatory self-gating contract**

This file is the executable gate contract for `MOTIVATION_FINAL_PIPELINE_HANDOFF.md`.

Codex must not advance to the next stage until the current stage's mandatory gates pass. If an authorized repair changes simulator source/runtime semantics or provenance, re-enter Stage 4 on the new frozen candidate.

---

# Stage 4 Acceptance — Final Preflight

## P0 — Provenance / isolation

- Motivation Core/Framework branches are `hrl/ep-l2-motivation-v0`.
- Simulation runs use only the isolated Motivation worktrees/result root.
- Every formal run manifest records exact Core SHA, Framework SHA, effective config, trace identity and raw-log SHA.
- All formal Stage-4 rows use one exact frozen candidate.

## P1 — Build / regression

Required PASS:

- Release build;
- reuse-distance threshold fixtures through 1024/1025;
- kernel/epoch reset and slice independence;
- clean/dirty post-eviction fixtures;
- packet-identity WBUF lifecycle fixtures;
- same-address sequential/concurrent WB identity fixtures;
- WBUF 4/8/16 simultaneous capacity fixtures;
- demand read/write miss classification fixtures;
- exclusive blocker priority fixtures including combined blockers;
- streaming parser regression;
- cumulative terminal snapshot selection regression;
- parser terminal-WBUF fail-close regression.

## P2 — WBUF lifecycle closure

For every formal Motivation-ON pilot:

```text
wb_packets_created == wb_packets_lower_accepted
```

and every terminal slice must have:

```text
wb_active_at_snapshot == 0
```

Any nonzero terminal active state is a FAIL.

## P3 — OFF/ON exact timing neutrality

Required pairs:

```text
vectorAdd_4M
convolutionSeparable
sad
```

Require exact equality for:

- cycles;
- instructions;
- B0 parsed outputs;
- M0a parsed outputs;
- L1 parsed outputs;
- DRAM parsed outputs;
- terminal resource invariants.

## P4 — Formal pilot Motivation validity

Required formal Motivation-ON rows:

```text
vectorAdd_4M
convolutionSeparable
spmv
sad
```

For each:

- exactly 64 selected final application slices;
- reuse histogram closes;
- blocking classification closes for WBUF4/8/16;
- provenance exact;
- terminal WBUF closure PASS;
- raw-log SHA recorded;
- terminal real-resource invariants PASS.

## P5 — OTHER diagnostic

For every final pilot and C=4/8/16, report:

```text
OTHER / projected_blocked_miss_admission_cycles
```

Do not fail the entire preflight merely because a valid `OTHER` category is nonzero, but the source/cause must be auditable. Paper-facing four-category omission of `OTHER` is governed by Stage-6 criterion F2.

## P6 — Host overhead sanity

Record OFF vs ON wall-clock/RSS for at least two pilots. If Motivation instrumentation threatens host stability or prevents the broad set from running safely, optimize before broad launch while preserving exact semantics.

## Stage-4 success token

Only after P0-P6 pass:

```text
MOTIVATION_INSTRUMENTATION_PREFLIGHT_PASS
```

---

# Stage 5 Acceptance — Broad Campaign

## B0 — Frozen provenance

All ten broad Motivation-ON rows use the exact candidate that passed Stage 4. No source/runtime semantic change is allowed after first broad formal row without invalidating the entire broad formal set.

## B1 — Required workload completeness

Exactly these required workloads must appear in the final status table:

```text
scan
vectorAdd_4M
convolutionSeparable
spmv
FWT_7_21
cfd_097k
dwt2d
sad
btree
gemm
```

No silent substitution or omission.

## B2 — Per-workload formal validity

Each required row must be `COMPLETE_VALID` and satisfy:

- exact Core/Framework/runtime config provenance;
- exact trace identity;
- 64/64 selected application slices;
- parser PASS;
- terminal real-resource invariants PASS;
- WBUF lifecycle closure PASS;
- reuse-bin closure PASS;
- exclusive blocker closure for WBUF 4/8/16;
- raw-log SHA present;
- no duplicate formal row.

## B3 — Runtime/resource policy

- Parallel launch should use available CPU/RSS headroom.
- `scan` may run long, but may not block launching independent workloads.
- Do not launch duplicate formal cells.
- Preserve failures/timeouts in status table and logs.
- Inherited per-run timeout: 8 hours unless a stricter reviewed policy already applies to the exact trace.

## Stage-5 success token

Only after B0-B3 and 10/10 validity pass:

```text
MOTIVATION_BROAD_10OF10_PASS
```

---

# Stage 6 Acceptance — Aggregation and Figures

## F0 — Aggregate provenance

All paper-facing rows must originate from the same frozen broad source/runtime candidate and required traces.

Aggregate integer counts before ratios. Never average percentages across slices.

## F1 — Figure 1 numerical closure

For every workload with reuse instances:

```text
sum(nine reuse-distance fractions) == 1.0
```

within numerical tolerance.

Also report:

- `reuse_instance_fraction`;
- `line_reuse_coverage`;
- `one_touch_line_fraction`.

A workload with zero reuse must remain explicit (`NA` where appropriate), not silently disappear.

## F2 — Figure 2 numerical closure and OTHER policy

For WBUF=8 and every workload:

```text
SET_ASSOC + MSHR_META + MISSQ_LOWER + WB_PATH + OTHER
== projected_blocked_miss_admission_cycles
```

If every workload has:

```text
OTHER / projected_blocked <= 0.02
```

the visual main figure may emphasize only the four primary categories while keeping exact Other values in source data/caption.

If any workload exceeds 2%, `OTHER` must appear as a fifth stacked segment.

## F3 — WBUF sensitivity validity

WBUF 4/8/16 sensitivity must:

- come from the same one-run observed stream for each workload;
- retain the `trace_projected` / `would_block` wording;
- never be described as speedup/performance under physical WBUF capacities.

## F4 — Figure files

Required:

```text
figures/FIG1_L2_REUSE_DISTANCE_STACKED.svg
figures/FIG1_L2_REUSE_DISTANCE_STACKED.png
figures/FIG2_L2_BLOCKING_BREAKDOWN_WBUF8.svg
figures/FIG2_L2_BLOCKING_BREAKDOWN_WBUF8.png
figures/FIG2S_WBUF_4_8_16_SENSITIVITY.svg
figures/FIG2S_WBUF_4_8_16_SENSITIVITY.png
```

Figures must be generated from committed machine-readable source tables, not hand-edited values.

## F5 — Interpretation discipline

`MOTIVATION_FINDINGS.md` must distinguish:

- measured reuse distribution;
- measured reuse coverage;
- measured structural blocking composition;
- trace-projected WBUF capacity pressure;
- inference about workload archetype.

It must not claim mechanism performance or speedup from Motivation-only data.

## F6 — Review pack integrity

Required final pack contents:

```text
README.md
SOURCE_MAP.md
SOURCE_ANCHORS.md
FIELD_SEMANTICS.md
VALIDATION_SUMMARY.md
MOTIVATION_FINDINGS.md
WORKLOAD_STATUS.csv
RAW_LOG_INDEX.tsv
motivation_summary.csv
reuse_distance.csv
reuse_coverage.csv
post_eviction_reuse.csv
blocking_breakdown.csv
wbuf_sensitivity.csv
wbuf_lifetime.csv
figures/
validation/
SHA256SUMS
```

Also require:

- Release build evidence;
- all directed test results;
- Stage-4 OFF/ON evidence;
- broad 10/10 validity table;
- final Core/Framework/runtime SHA contract;
- `git status --short` evidence;
- `git diff --check` PASS;
- SHA256SUMS verification PASS.

## Stage-6 success token

After F0-F6 pass:

```text
MOTIVATION_FIGURES_REVIEW_READY
```

Codex stops here for independent ChatGPT review.

`MOTIVATION_FIGURES_FINAL_PASS` is reserved for ChatGPT after review.
