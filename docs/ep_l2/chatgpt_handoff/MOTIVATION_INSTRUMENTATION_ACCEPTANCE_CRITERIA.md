# EP-L2 Motivation Instrumentation — Acceptance Criteria

Status: **mandatory self-gating contract**

The stage is complete only if every mandatory gate below passes.

## Gate A — Provenance and isolation

- Core parent is exactly `1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e`.
- Framework runtime parent is exactly `d61ffd23c926a25fa463a3e6e955c885b45f0f8a`.
- New source lives only in the isolated motivation worktrees/branch.
- Existing M0b/M3A/M0a/M1 worktrees and result roots are untouched.
- Formal manifests record final Core/Framework SHA, branch, runtime config composite hash, trace identity and motivation enable bit.

## Gate B — Default-OFF timing neutrality

For at least:

```text
vectorAdd_4M
convolutionSeparable
sad
```

compare:

```text
M0A_ON + MOTIVATION_OFF + M1_STATIC
vs
M0A_ON + MOTIVATION_ON  + M1_STATIC
```

Required exact equality:

- simulated cycles;
- simulated instructions;
- existing B0/L1/DRAM parsed outputs;
- M0a parsed outputs except the new motivation-family files;
- terminal invariants;
- no request/resource leak.

If any simulation-control difference is attributable to motivation telemetry, FAIL and repair before broad runs.

## Gate C — Reuse-stream source semantics

Produce a source-to-stream map proving:

- exact frontend demand-reference producer point;
- 128-B block normalization;
- included request classes;
- excluded internal WB/fill/retry classes;
- exact kernel/epoch reset point.

No paper-facing data are valid until this map is explicit.

## Gate D — Reuse-distance exactness

Permanent deterministic fixtures must cover at least:

1. first-touch only sequence;
2. immediate repeat, expected distance 0 / `<=8`;
3. known distances around every threshold: 8/9, 16/17, 32/33, 64/65, 128/129, 256/257, 512/513, 1024/1025;
4. repeated address after >1024 distinct addresses -> `>1024`;
5. kernel/epoch reset prevents cross-epoch reuse contamination;
6. multiple slices remain independent;
7. first touches do not enter the nine-bin reuse denominator;
8. nine-bin counts sum to `reuse_instances` exactly.

The implementation must compute exact bounded stack distance through 1024 distinct lines. Approximate hashing/sampling is not accepted for the primary figure.

## Gate E — Reuse coverage bookkeeping

On deterministic fixtures verify exactly:

```text
eligible_demand_references
reuse_instances
unique_lines
unique_lines_reused_at_least_once
one_touch_unique_lines
```

and all derived fractions.

No zero/empty workload may be silently normalized to 1.0.

## Gate F — Post-eviction supplement

Directed fixtures must prove:

- eviction event is sourced from a real resident-line eviction;
- next demand re-reference is associated with the correct 128-B block;
- eviction/re-reference state is epoch-safe;
- a second eviction updates the correct generation/event rather than double counting stale state;
- instrumentation never changes real hit/miss outcomes.

## Gate G — WBUF source lifecycle

Produce source evidence for:

```text
WB packet creation
WB lower-path acceptance
WAD allocation
WAD release / set_done
```

Directed tests must prove:

1. one dirty victim creates exactly one active WB staging lifetime;
2. active WB count increments at WB packet creation;
3. active WB count decrements exactly once at successful lower acceptance;
4. `set_done()` does **not** define WBUF release;
5. WAD can remain live after WBUF release;
6. no negative occupancy, double release or leaked active WB remains at termination.

## Gate H — WBUF 4/8/16 simultaneous capacity behavior

Using one deterministic event stream, verify:

- 4 active WBs: C4 full, C8/C16 not full;
- fifth dirty-WB opportunity: C4 would-block, C8/C16 would not;
- 8 active WBs: C4/C8 full, C16 not;
- 16 active WBs: all full;
- one real lower acceptance updates all three shadow-capacity evaluations consistently;
- no capacity model changes real WB creation/issue timing.

All three capacities must be emitted from one simulator run.

## Gate I — Exclusive primary-block classifier

First freeze the actual production admission order in `SOURCE_MAP.md`.

Permanent fixtures must individually create:

```text
SET_ASSOC only
MSHR_META only
MISSQ_LOWER only
WB_PATH/WAD only
WB_PATH/WBUF-shadow only
```

and at least two combined-blocker cases that verify priority/order.

For each C in `{4,8,16}`:

```text
SET_ASSOC_C
+ MSHR_META_C
+ MISSQ_LOWER_C
+ WB_PATH_C
+ OTHER_C
== projected_blocked_miss_admission_cycles_C
```

Every eligible cycle/attempt receives at most one primary blocker.

The classifier must be non-mutating.

## Gate J — Diagnostic `OTHER`

For each broad workload and C in `{4,8,16}`, report `OTHER` explicitly.

The four-category paper-facing Figure 2 is accepted only if:

```text
OTHER / projected_blocked <= 0.02
```

for every plotted workload.

If not, retain an `Other` segment and request review; do not renormalize it away.

## Gate K — Parser / aggregation

Unit tests must verify:

- per-slice counters merge without averaging percentages;
- per-kernel/epoch reuse histograms aggregate by counts;
- every Figure-1 workload bar sums to 1.0 within numerical tolerance;
- every Figure-2 workload/capacity bar, including diagnostic `Other`, sums to 1.0;
- `NA` is distinct from measured zero;
- WBUF4/8/16 are not cross-mixed;
- duplicate run/workload records fail closed;
- source/config/trace mismatches fail closed.

## Gate L — Host-overhead sanity

Measure motivation OFF vs ON host wall time and peak RSS on at least two pilot workloads, including one reuse-heavy/longer case if practical.

No strict publication claim is required, but if ON overhead exceeds roughly 50% or memory growth threatens broad-run stability, optimize the profiler before launching all long workloads.

Simulation cycles/instructions must remain exact regardless of host overhead.

## Gate M — Pilot production runs

Before broad launch, all four pilots must be `COMPLETE_VALID`:

```text
vectorAdd_4M
convolutionSeparable
spmv
sad
```

Required evidence:

- reuse histogram nonempty where reuse exists;
- coverage metrics sane;
- WBUF metrics present;
- primary-block accounting closes;
- terminal invariants pass;
- source/config provenance exact.

## Gate N — Broad motivation set

After pilot gates pass, run in parallel where safe:

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

No failure/timeout may be silently dropped from the main table.

## Gate O — Figure 1 readiness

For every plotted workload:

- nine reuse-distance fractions sum to 1.0 when reuse_instances >0;
- `reuse_instance_fraction` and `line_reuse_coverage` are reported alongside the stacked-bar source table;
- one-touch/never-reuse interpretation is not inferred from the stacked bar alone;
- post-eviction data are clearly supplemental.

## Gate P — Figure 2 readiness

Primary figure uses WBUF=8 unless a later research decision explicitly changes the reference capacity.

For every plotted workload:

- denominator is projected blocked frontend demand-miss admission cycles;
- categories are exclusive;
- category names map to documented resource semantics;
- WB-path is explicitly a WAD + shadow-WBUF path category;
- shadow WBUF is not called an existing baseline physical buffer;
- WBUF4/16 remain available as sensitivity.

## Gate Q — Review pack integrity

Review pack must include:

```text
README.md
SOURCE_MAP.md
SOURCE_ANCHORS.md
FIELD_SEMANTICS.md
VALIDATION_SUMMARY.md
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

Also record:

```text
git status --short
git diff --check
Release build command/result
all directed/unit tests
all OFF/ON controls
```

## Final accepted state

Only after all mandatory gates pass may Codex report:

```text
MOTIVATION_FIGURES_REVIEW_READY
```

This state still does not authorize performance claims for shadow WBUF capacities.