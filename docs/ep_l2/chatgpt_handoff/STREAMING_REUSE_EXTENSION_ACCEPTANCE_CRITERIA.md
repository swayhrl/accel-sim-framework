# EP-L2 Streaming / Temporal-Reuse Extension — Acceptance Criteria

Status: **mandatory self-gating / self-repair contract**

The extension is review-ready only when every applicable gate below passes.

---

## Gate A — Preservation and isolation

Must prove:

```text
immutable prior Core      2a6a31591bc42023e5997cca969e4b672efe0405
immutable prior Framework 02f36816f60afcff55e910cdef2b60937e691cdc
immutable prior branch    hrl/ep-l2-motivation-v0
immutable prior results   /workspace/results/ep_l2_motivation/
immutable prior pack      docs/ep_l2/review_packs/MOTIVATION_FIGURES_r1/
```

Required checks:

- no modification under `MOTIVATION_FIGURES_r1/`;
- no new output under `/workspace/results/ep_l2_motivation/`;
- no amend/rebase/force-push of `hrl/ep-l2-motivation-v0`;
- new work uses only the isolated streaming-reuse worktrees/branch/result root;
- a preservation manifest records immutable prior SHA/checksums before extension work begins and rechecks them at closeout.

Any failure is fatal until repaired without deleting prior evidence.

---

## Gate B — Source parent / provenance

New lane must be a descendant of exactly:

```text
Core parent      2a6a31591bc42023e5997cca969e4b672efe0405
Framework parent 02f36816f60afcff55e910cdef2b60937e691cdc
```

Formal manifests record:

- final extension Core SHA;
- final extension Framework SHA;
- branch names;
- effective config hash;
- trace identity/input;
- old `EPL2MOTV1` enable state;
- new sector telemetry enable state.

---

## Gate C — Separate default-OFF telemetry family

Required:

- new option default OFF;
- separate versioned schema, preferably `EPL2SRV1`;
- no existing `EPL2MOTV1` field meaning is changed;
- no production cache/controller decision reads new telemetry state;
- OFF does not allocate/update sector profiler state.

Source map must identify exact hooks.

---

## Gate D — Demand stream and sector identity correctness

Directed/source evidence must prove:

- frontend demand read/write stream matches reviewed Motivation stream;
- `L1_WRBK_ACC` and `L2_WRBK_ACC` excluded;
- fills/returns/internal WB excluded;
- frontend retry of the same request is not counted as a new logical demand reference;
- sector identity is `(slice, block_addr_128B, sector_index_0..3)`;
- request sector mask is the production mask actually used by the modeled L2 path;
- epoch reset clears all sector temporal-reuse state;
- physical slices remain independent.

---

## Gate E — Spatial-vs-temporal exact classification

Permanent fixtures must cover at least:

1. one request to one never-seen sector of a never-seen line -> `NEW_SECTOR_ON_NEW_LINE`;
2. four sequential single-sector requests to sectors 0/1/2/3 of one line -> one new-line request followed by spatial new-sector touches and **zero temporal sector reuse**;
3. immediate repeat of the exact same sector -> one temporal reuse;
4. revisit a different already-touched sector of the same line -> temporal reuse;
5. a multi-sector request on an unseen line -> every referenced sector classified against the pre-request state, with no artificial within-request spatial/temporal ordering;
6. a later multi-sector request mixing already-touched and never-touched sectors -> repeated sector bits are temporal reuse and new bits are spatial continuation;
7. cross-epoch same address -> first touch again, not reuse;
8. same address on two slices -> independent state;
9. write demand path behaves identically to read demand for classification semantics;
10. writeback traffic contributes zero demand-sector events.

Required conservation for every fixture and formal workload:

```text
new_sector_on_new_line
+ new_sector_on_seen_line
+ temporal_sector_reuse
== total_sector_reference_events
```

Also:

```text
unique_sectors_reused_at_least_once + one_touch_unique_sectors
== unique_sector_identities
```

---

## Gate F — Sector temporal reuse-distance exactness

Permanent deterministic fixtures must cover distances:

```text
0
8 / 9
16 / 17
32 / 33
64 / 65
128 / 129
256 / 257
512 / 513
1024 / 1025
2048 / 2049
4096 / 4097
```

Requirements:

- exact bounded stack distance through 4096 distinct sector identities;
- a previously seen sector outside the retained exact window maps to `>4096`;
- first touches do not enter reuse-distance denominator;
- all distance-bin counts sum exactly to `sector_temporal_reuse_instances`;
- kernel/epoch reset prevents cross-epoch contamination;
- slices independent.

---

## Gate G — Coverage bookkeeping

Directed fixtures verify exactly:

```text
total_sector_reference_events
unique_sector_identities
sector_temporal_reuse_instances
unique_sectors_reused_at_least_once
one_touch_unique_sectors
new_sector_on_new_line_events
new_sector_on_seen_line_events
```

Derived fractions must be calculated from aggregated counts.

No zero denominator may silently become 0% or 100%; use `NA` where mathematically undefined.

---

## Gate H — Old line-level telemetry compatibility

With `EPL2MOTV1 ON`, adding `EPL2SRV1 ON` must not alter old Motivation measurements.

At minimum, the preflight controls must compare old Motivation scientific fields exactly for:

```text
vectorAdd_4M
convolutionSeparable
sad
```

Before final Figure-1-v2 promotion, every rerun original-10 workload must compare the new-run `EPL2MOTV1` key scientific fields against immutable `MOTIVATION_FIGURES_r1` values when trace/config identity matches.

Required exact fields include at least:

```text
eligible_demand_references
reuse_instances
all line-level reuse bins
unique_lines / unique_lines_reused / one-touch
post-eviction counters
blocking_breakdown counters
WBUF lifecycle counts
```

Any mismatch attributable to new sector telemetry is a FAIL.

---

## Gate I — Timing neutrality

Controls:

```text
EPL2MOTV1 ON + sector telemetry OFF
vs
EPL2MOTV1 ON + sector telemetry ON
```

For:

```text
vectorAdd_4M
convolutionSeparable
sad
```

Required exact equality:

- simulated cycles;
- simulated instructions;
- existing B0 output;
- M0a output;
- L1 output;
- DRAM output;
- old `EPL2MOTV1` output;
- terminal resource invariants.

New sector telemetry may affect only host execution overhead and new schema output.

---

## Gate J — Host overhead / memory safety

Measure OFF vs ON wall time and peak RSS on at least two meaningful pilots, including one large/reuse-heavy case.

If ON overhead is roughly >50% or RSS growth threatens parallel screening stability:

- optimize exact profiler implementation;
- rerun directed tests and neutrality;
- do not launch full screening until stable.

No publication claim about profiler overhead is required.

---

## Gate K — Parser / aggregation fail-close

Unit/regression tests must prove:

- streaming raw-log parsing; no whole-file loading for multi-GB logs;
- exactly expected application-slice terminal records;
- cumulative terminal record selection is explicit and auditable;
- duplicate/conflicting records fail or are handled by documented final-record policy;
- source/config/trace mismatches fail closed;
- classification conservation is checked;
- reuse-distance bins close exactly;
- slice aggregation is by counts, not mean percentages;
- `NA` distinct from zero;
- old/new schema rows cannot be cross-mixed.

---

## Gate L — Preflight state

All Gates A–K must pass before screening expansion.

Required state:

```text
STREAMING_REUSE_PREFLIGHT_PASS
```

Do not launch candidate-screening fanout before this state.

---

## Gate M — Screening inventory quality

Produce a local trace-pool inventory and screening shortlist.

Target:

```text
12–16 candidate workloads
minimum 10 if actual runnable inventory materially limits selection
at least four semantic/suite families where available
```

Must include:

```text
vectorAdd_4M as control
```

but vectorAdd does not count toward the required 2–3 new formal workloads.

Each candidate record must state:

- suite/benchmark/input;
- trace path/identity;
- why it was screened;
- final source/config provenance;
- completion status.

Do not claim coverage of the entire trace pool unless it was actually exhaustive.

---

## Gate N — Screening result validity

Every screening row used for selection must pass:

- complete run / terminal invariants;
- parser success;
- sector classification conservation;
- sector distance closure;
- provenance match;
- no telemetry leak.

Ranking table must expose raw metrics, not only a synthetic score.

Required columns include:

```text
sector_temporal_reuse_fraction
one_touch_sector_fraction
spatial_new_sector_fraction
cold_new_line_sector_fraction
far_sector_reuse_share_gt1024
far_sector_reuse_share_gt4096
sector_temporal_reuse_instances
post_eviction_referenced_fraction (when available)
```

---

## Gate O — Formal new-workload selection

Select 2–3 **additional** workloads beyond the original Motivation 10.

Required scientific behavior:

- prioritize at least 1–2 genuinely low-temporal-reuse/streaming workloads if present;
- select a far-reuse workload only if raw metrics genuinely support it;
- do not promote a candidate purely because its benchmark name sounds streaming;
- do not force a far-reuse label if none exists.

If no strong far-reuse candidate exists:

```text
NO_STRONG_FAR_REUSE_FOUND_IN_SCREENED_POOL
```

must be stated in selection notes.

Formal selection document must explain why each chosen workload adds a distinct archetype relative to the original 10.

---

## Gate P — Formal Figure-1-v2 dataset

Formal set:

```text
original Motivation 10
+
2–3 selected new workloads
```

Every row must use one final frozen extension source/config family and be `COMPLETE_VALID`.

Original 10 are rerun with sector telemetry; their old `EPL2MOTV1` key fields must pass Gate H compatibility.

A screening row for a selected new workload may be promoted without rerun only if it already used the final frozen source/config/trace and passed every formal gate.

No missing/timeout row may be silently omitted from Figure 1 v2.

---

## Gate Q — Figure 1 v2 semantics

Required files:

```text
FIG1V2_L2_SECTOR_TEMPORAL_REUSE.png
FIG1V2_L2_SECTOR_TEMPORAL_REUSE.svg
```

Main figure must expose both:

1. **amount of true temporal reuse**, and
2. **distance distribution conditional on true reuse**.

A workload with almost no true reuse must not visually look highly reusable merely because its few reuse events are short-distance.

Required annotations/data availability:

```text
sector_temporal_reuse_fraction
one_touch_sector_fraction
spatial_new_sector_fraction
```

The conditional distance bar sums to 1.0 only when reuse count >0; zero-reuse cases must be shown explicitly rather than normalized.

Required supplemental files:

```text
FIG1S_LINE_VS_SECTOR_REUSE.png
FIG1S_LINE_VS_SECTOR_REUSE.svg
```

These compare line-level locality with true sector temporal reuse and must preserve the distinction between spatial continuation and temporal reuse.

Do not modify Figure-1-r1 or any Figure-2-r1 artifact.

---

## Gate R — Review-pack completeness

Required pack:

```text
docs/ep_l2/review_packs/STREAMING_REUSE_CHARACTERIZATION_r1/
```

Must include at minimum:

```text
README.md
SOURCE_MAP.md
FIELD_SEMANTICS.md
VALIDATION_SUMMARY.md
PRESERVATION_MANIFEST.md
SCREENING_CANDIDATES.csv
SCREENING_RANKING.csv
SCREENING_NOTES.md
FORMAL_WORKLOAD_SELECTION.md
formal_workload_status.csv
raw_log_index.tsv
sector_reuse_summary.csv
sector_reuse_distance.csv
sector_reuse_coverage.csv
line_vs_sector_reuse.csv
aggregation_manifest.json
figures/
validation/
SHA256SUMS
```

`validation/` includes actual commands/results for:

- Release build;
- directed tests;
- parser/aggregator tests;
- OFF/ON neutrality;
- host wall/RSS;
- old-Motivation compatibility checks;
- `git status --short`;
- `git diff --check`;
- pack checksum verification.

---

## Gate S — Preservation closeout

Recheck immutable prior evidence at final pack creation.

The closeout must explicitly prove that:

```text
MOTIVATION_FIGURES_r1
/workspace/results/ep_l2_motivation/
hrl/ep-l2-motivation-v0
```

were not overwritten or rewritten by this extension lane.

---

## Final review-ready state

Only after every applicable gate passes may Codex report:

```text
STREAMING_REUSE_FIG1V2_REVIEW_READY
```

This state authorizes independent ChatGPT review only. Codex must not self-declare the scientific extension final PASS.
