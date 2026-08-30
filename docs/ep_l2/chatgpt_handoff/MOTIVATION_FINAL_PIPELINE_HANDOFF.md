# EP-L2 Motivation Figures — Final End-to-End Pipeline Handoff

Status: **AUTHORIZED — one continuous target-mode execution**

This handoff supersedes the previous step-by-step continuation requests for the Motivation Figures lane. The lane should now proceed continuously through:

```text
Stage 4  FINAL PREFLIGHT PILOTS
   ->
Stage 5  BROAD MOTIVATION CAMPAIGN
   ->
Stage 6  AGGREGATION + FIGURES + FINAL REVIEW PACK
   ->
MOTIVATION_FIGURES_REVIEW_READY
```

The lane does **not** wait for ChatGPT between stages when the immediately preceding mandatory gate passes.

---

## 1. Scientific objective

Produce two paper-facing motivation figures from one reviewed, timing-neutral instrumentation family:

1. **L2 reuse-distance distribution across workloads**;
2. **L2 frontend demand-miss structural blocking breakdown**, with one primary blocker per eligible blocked attempt/cycle and simultaneous shadow WBUF capacities 4/8/16.

The figures must remain motivation/characterization evidence. Shadow WBUF 4/8/16 is not a counterfactual performance simulation.

---

## 2. Current frozen candidate

Current candidate entering Stage 4:

```text
Core
2a6a31591bc42023e5997cca969e4b672efe0405

Framework
02f36816f60afcff55e910cdef2b60937e691cdc

Branch in both repositories
hrl/ep-l2-motivation-v0
```

The source family is derived from the promoted M0a+M1 integrated parent and contains only observation-side Motivation instrumentation changes.

Do not silently change these SHAs during normal execution.

If a mandatory correctness gate fails and the failure is in instrumentation/parser/runner/plotting logic, Codex is authorized to repair it inside this lane. Any source/runtime change creates a **new frozen candidate** and must follow the provenance invalidation rules in Section 8.

---

## 3. Worktrees and result root

Continue using only the existing isolated Motivation lane:

```text
Framework worktree
/workspace/worktrees/accel-sim-ep-l2-motivation/

Core worktree
/workspace/worktrees/gpgpu-sim-ep-l2-motivation/

Result root
/workspace/results/ep_l2_motivation/
```

The permanent coordination worktree remains read/write only for documentation/handoff mirroring:

```text
/workspace/worktrees/accel-sim-ep-l2/
branch hrl/ep-l2-exp-v0
```

Do not use M0b, M3A, M0a, M1, calibration, or coordination worktrees as Motivation simulator source.

---

# Stage 4 — Final Preflight Pilots

## 4.1 Required formal preflight set

On one exact frozen provenance pair, close:

```text
vectorAdd_4M          OFF + ON
convolutionSeparable  OFF + ON
sad                   OFF + ON
spmv                  ON
```

The corrected vectorAdd ON evidence already demonstrates packet-identity WBUF lifecycle closure, but every formal row used for Stage-4 promotion must bind the same final frozen source/config provenance.

Old rows from earlier Core/Framework candidates remain diagnostic only.

## 4.2 Mandatory preflight properties

For OFF/ON pairs:

```text
M0A_ON + MOTIVATION_OFF + M1_STATIC
vs
M0A_ON + MOTIVATION_ON  + M1_STATIC
```

Require exact equality of:

- simulated cycles;
- simulated instructions;
- existing B0 parsed outputs;
- existing M0a parsed outputs;
- L1 parsed outputs;
- DRAM parsed outputs;
- terminal real-resource invariants;
- request/resource leak state.

For Motivation-ON rows require:

- exactly 64 terminal application slice records after cumulative-terminal selection;
- nine reuse bins sum exactly to `reuse_instances`;
- exclusive primary blocking accounting closes for WBUF 4/8/16;
- WBUF packet lifecycle closes:
  `wb_packets_created == wb_packets_lower_accepted`;
- every terminal slice has `wb_active_at_snapshot == 0`;
- parser fail-closes malformed/duplicate/provenance-invalid inputs;
- `OTHER` is explicitly emitted;
- Release build and permanent directed tests remain PASS.

## 4.3 Stage-4 promotion

Only when all mandatory Stage-4 gates pass may Codex record:

```text
MOTIVATION_INSTRUMENTATION_PREFLIGHT_PASS
```

and immediately continue into Stage 5 without waiting for ChatGPT.

Publish/update an intermediate checkpoint under:

```text
docs/ep_l2/review_packs/MOTIVATION_FIGURES_PREFLIGHT_r1/
```

but do not stop merely because this checkpoint is complete.

---

# Stage 5 — Broad Motivation Campaign

## 5.1 Formal broad workload set

Launch the following Motivation-ON workloads on the exact Stage-4 promoted frozen candidate:

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

Each workload is one formal Motivation-ON replay. OFF controls are not repeated in broad mode because timing neutrality was already proved in Stage 4.

## 5.2 Parallel execution policy

- Launch independent workloads in parallel where host CPU/RSS/disk permit.
- Do **not** serially wait for `scan` before launching other workloads.
- Avoid duplicate simulator jobs for the same formal cell.
- Retain per-run isolated result directories and manifests.
- Continue completing/packing short rows while long rows run.
- Use the inherited 8-hour per-run timeout unless an existing reviewed runtime policy for this exact trace is stricter.
- A timeout/failure must remain visible in `WORKLOAD_STATUS.csv`; never silently drop or replace a workload.

## 5.3 Formal validity for every broad row

Every row entering the paper-facing aggregate must satisfy:

- `COMPLETE_VALID`;
- exact final Core/Framework provenance;
- exact Motivation-ON effective config;
- expected trace identity;
- 64/64 terminal slice records;
- Motivation parser PASS;
- real terminal invariants PASS;
- WBUF lifecycle closure PASS;
- reuse histogram closure PASS;
- exclusive blocker accounting PASS for C=4,8,16;
- no malformed/duplicate final record ambiguity;
- raw-log SHA recorded.

## 5.4 Stage-5 promotion

Only when all ten required workload rows are valid may Codex record:

```text
MOTIVATION_BROAD_10OF10_PASS
```

and immediately continue into Stage 6.

---

# Stage 6 — Aggregation, Figures, and Final Evidence

## 6.1 Required machine-readable aggregate tables

Generate one provenance-bound aggregate set containing at least:

```text
motivation_summary.csv
reuse_distance.csv
reuse_coverage.csv
post_eviction_reuse.csv
blocking_breakdown.csv
wbuf_sensitivity.csv
wbuf_lifetime.csv
WORKLOAD_STATUS.csv
RAW_LOG_INDEX.tsv
```

Aggregation rules:

- aggregate integer event counts across 64 slices before forming ratios;
- never average per-slice percentages;
- keep `NA` distinct from measured zero;
- no workload may appear more than once in a paper-facing aggregate;
- all rows must share the final frozen Core/Framework/runtime contract.

## 6.2 Primary Figure 1 — L2 Reuse Distance Distribution

Generate publication-ready first-version SVG and PNG:

```text
FIG1_L2_REUSE_DISTANCE_STACKED.svg
FIG1_L2_REUSE_DISTANCE_STACKED.png
```

For each workload, one stacked bar over reuse instances:

```text
<=8
9-16
17-32
33-64
65-128
129-256
257-512
513-1024
>1024
```

Mandatory properties:

- when `reuse_instances > 0`, the nine fractions sum to 1.0 within numerical tolerance;
- first touches are excluded from the nine-bin denominator;
- the source table reports alongside each workload:
  `reuse_instance_fraction`, `line_reuse_coverage`, and `one_touch_line_fraction`;
- do not call a `<=C` bin a C-entry victim-cache capture rate: exact fully-associative LRU capture is `distance < C`;
- post-eviction re-reference is supplemental, not substituted for stack-distance reuse.

## 6.3 Primary Figure 2 — Structural Blocking Breakdown

Generate publication-ready first-version SVG and PNG using **WBUF=8** as the reference shadow capacity:

```text
FIG2_L2_BLOCKING_BREAKDOWN_WBUF8.svg
FIG2_L2_BLOCKING_BREAKDOWN_WBUF8.png
```

For each workload, normalize by projected blocked frontend demand-miss admission cycles.

Primary categories:

```text
SET_ASSOC
MSHR_META
MISSQ_LOWER
WB_PATH
```

`OTHER` handling:

- compute and retain `OTHER` for every workload;
- if `OTHER / projected_blocked <= 0.02` for every plotted workload, the main figure may present the four primary categories while the exact Other values remain in the table/caption;
- if any workload exceeds 2%, include `OTHER` as an explicit fifth segment; never renormalize it away.

`WB_PATH` means WAD/order restrictions plus the timing-neutral shadow dirty-WB packet staging pressure. It must not be labeled as an existing physical baseline WBUF.

## 6.4 WBUF 4/8/16 sensitivity

Generate:

```text
FIG2S_WBUF_4_8_16_SENSITIVITY.svg
FIG2S_WBUF_4_8_16_SENSITIVITY.png
```

This figure/table must clearly state that all three capacities were evaluated on the same observed event stream and represent `trace_projected` / `would_block` pressure, not three performance simulations.

## 6.5 Interpretation summary

Create:

```text
MOTIVATION_FINDINGS.md
```

For every workload, summarize only evidence-supported observations about:

- short vs long reuse tendency;
- reuse coverage / one-touch behavior;
- dominant structural blocking category;
- whether WB-path pressure is sensitive to WBUF 4/8/16;
- whether the workload is better described as reuse-oriented, concurrency/admission-oriented, downstream-oriented, or low-pressure/control.

Do not infer a mechanism speedup from these motivation figures.

---

# 7. Final review pack

Create/finalize:

```text
docs/ep_l2/review_packs/MOTIVATION_FIGURES_r1/
```

Required contents:

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

Also publish:

```text
docs/ep_l2/codex_handoff/LANE_MOTIVATION_LATEST.md
```

Record final:

- Core/Framework SHAs;
- runtime config composite hash;
- Release build command/result;
- directed/unit regression results;
- preflight OFF/ON evidence;
- broad 10/10 status;
- `git status --short`;
- `git diff --check`;
- review-pack SHA256 verification.

---

# 8. Self-repair and provenance invalidation rules

Codex should continue autonomously through recoverable failures inside the authorized Motivation scope.

## 8.1 Source/producer correctness failure

Examples:

- lifecycle mismatch;
- wrong producer point;
- non-neutral instrumentation;
- classifier accounting bug;
- reuse-distance semantic bug.

Action:

1. preserve failing evidence as diagnostic;
2. repair the source;
3. create/push a new candidate SHA;
4. invalidate all formal Stage-4/5 rows generated under the superseded source;
5. rerun the complete mandatory Stage-4 preflight on the new candidate;
6. broad rows may start only after the new preflight passes.

## 8.2 Parser/runner/plotting-only failure

If raw simulator output is semantically sufficient and simulator source/config does not change:

- repair parser/runner/plotting;
- reprocess existing raw logs;
- no simulator rerun is required unless provenance/output completeness cannot be proved.

## 8.3 Workload-specific simulator failure

- preserve logs/status;
- determine whether the cause is Motivation instrumentation, runner/environment, or intrinsic workload/runtime;
- repair/retry when inside authorized scope;
- never silently omit the workload.

If an intrinsic workload cannot complete within the inherited policy after justified retry, stop at a clearly labeled incomplete state and request review rather than fabricating 10/10.

---

# 9. End state

Codex may stop only after one of the following:

### Success

```text
MOTIVATION_FIGURES_REVIEW_READY
```

with all Stage-4/5/6 mandatory gates satisfied and final pack pushed.

### Unrecoverable / out-of-scope blocker

A clearly documented blocker requiring research-policy or architecture semantics outside this handoff.

Codex must not self-declare `MOTIVATION_FIGURES_FINAL_PASS`; that state is reserved for the independent ChatGPT review after `MOTIVATION_FIGURES_REVIEW_READY` is published.
