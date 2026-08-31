# EP-L2 Streaming / Temporal-Reuse Characterization Extension — Handoff

Status: **AUTHORIZED — independent extension lane**

## 1. Objective

Extend the already-reviewed Motivation characterization without changing or overwriting it.

The scientific purpose is to distinguish:

1. **spatial continuation inside one 128-B L2 line** — first accesses to different 32-B sectors of a line;
2. **true temporal sector reuse** — a previously touched 32-B sector is referenced again;
3. **far temporal reuse** — true sector reuse exists, but the intervening distinct-sector working set is large enough that ordinary retention is unlikely to capture it.

Then:

```text
new sector-aware telemetry
    -> validate timing neutrality / exactness
    -> screen existing runnable trace pool
    -> identify 2–3 additional formal streaming / far-reuse workloads
    -> rerun the original Motivation 10-workload set with the new sidecar
    -> generate Figure 1 v2
    -> publish one independently reviewable extension pack
```

This lane does **not** reopen or replace the accepted Motivation blocking/WBUF study.

---

## 2. Immutable prior evidence — MUST NOT BE OVERWRITTEN

The following are immutable provenance and must remain byte-for-byte untouched:

```text
Core frozen Motivation source:
2a6a31591bc42023e5997cca969e4b672efe0405

Framework frozen Motivation runtime:
02f36816f60afcff55e910cdef2b60937e691cdc

Existing branch:
hrl/ep-l2-motivation-v0

Existing result root:
/workspace/results/ep_l2_motivation/

Existing review pack:
docs/ep_l2/review_packs/MOTIVATION_FIGURES_r1/

Existing figures:
FIG1_L2_REUSE_DISTANCE_STACKED.*
FIG2_L2_BLOCKING_BREAKDOWN_WBUF8.*
FIG2S_WBUF_4_8_16_SENSITIVITY.*
```

Hard rules:

- do not amend/rebase/force-push the existing Motivation branch;
- do not write new files into `/workspace/results/ep_l2_motivation/`;
- do not modify, regenerate, rename, or delete anything under `MOTIVATION_FIGURES_r1/`;
- do not reuse an old output directory as a destination;
- old raw logs and old CSVs may be **read/reference-checked only**;
- if an old value is copied for comparison, record its original path and checksum rather than replacing the source artifact.

Any violation of these preservation rules is a lane FAIL.

---

## 3. New isolated source / results

Start from the frozen Motivation source pair above and create fresh isolated worktrees:

```text
Framework:
/workspace/worktrees/accel-sim-ep-l2-streaming-reuse/

Core:
/workspace/worktrees/gpgpu-sim-ep-l2-streaming-reuse/

Branch in both repositories:
hrl/ep-l2-streaming-reuse-v0

New result root:
/workspace/results/ep_l2_streaming_reuse/
```

New evidence locations:

```text
docs/ep_l2/codex_handoff/LANE_STREAMING_REUSE_LATEST.md

docs/ep_l2/review_packs/STREAMING_REUSE_CHARACTERIZATION_r1/
```

No other active EP-L2 worktree/result root may be modified.

---

## 4. New telemetry family — do not mutate EPL2MOTV1 semantics

Add a **separate default-OFF observation-only telemetry family**. Suggested option/schema:

```text
-gpgpu_ep_l2_sector_reuse_stats 0/1
EPL2SRV1
```

The exact option name may differ, but:

- default must be OFF;
- no production admission/scheduling/resource predicate may read it;
- existing `EPL2MOTV1` output semantics must remain unchanged;
- formal extension runs may enable both `EPL2MOTV1` and `EPL2SRV1` so line-level and sector-level data come from the same execution.

---

## 5. Primary reference stream

Use the same production frontend-demand stream already accepted for Motivation:

- per physical L2 slice;
- reset primary reuse state at the accepted kernel/epoch boundary;
- 128-B L2 block normalization;
- 32-B sector identity within that block;
- include demand reads and demand writes;
- exclude `L1_WRBK_ACC`, `L2_WRBK_ACC`, fills/returns and internal bookkeeping/retry duplication exactly as the reviewed Motivation stream does.

One frontend request may reference multiple sectors through its sector mask.

### 5.1 Sector-event expansion

For each set bit in the real request sector mask, create one logical **sector reference event** with identity:

```text
(slice, 128B block address, sector index 0..3)
```

A sector bit occurs at most once inside one request; do not manufacture ordering among bits.

All classification of the sector bits in one request must use the state **before that request** commits to the profiler. This prevents a multi-sector request on a new line from making later bits in the same request look like artificial spatial continuation.

---

## 6. Spatial-vs-temporal classification

For every logical sector-reference event classify exactly one of:

```text
A. NEW_SECTOR_ON_NEW_LINE
   sector has never appeared in this epoch and the 128B line was also unseen
   before this request.

B. NEW_SECTOR_ON_SEEN_LINE
   sector has never appeared in this epoch but the 128B line had already been
   referenced by an earlier request in this epoch.
   This is spatial continuation, NOT temporal reuse.

C. TEMPORAL_SECTOR_REUSE
   this exact 32B sector identity was referenced previously in this epoch.
```

Required conservation:

```text
A + B + C == total_sector_reference_events
```

Derived primary metrics:

```text
sector_temporal_reuse_fraction = C / total_sector_reference_events
spatial_new_sector_fraction     = B / total_sector_reference_events
cold_new_line_sector_fraction   = A / total_sector_reference_events
```

Also maintain:

```text
unique_sector_identities
unique_sectors_reused_at_least_once
one_touch_unique_sectors
one_touch_sector_fraction
```

This is the primary correction for the old line-level metric. A stream that touches four different 32-B sectors of each 128-B line exactly once must report **zero temporal sector reuse**, even though the old line-level reuse metric can be 75%.

---

## 7. Exact bounded temporal-sector reuse distance

For class-C events only, compute exact bounded reuse/stack distance over **distinct 32-B sector identities in the same slice and epoch**.

Keep enough MRU state to be exact through 4096 distinct sectors.

Required bins:

```text
<=8
9-16
17-32
33-64
65-128
129-256
257-512
513-1024
1025-2048
2049-4096
>4096
```

Semantics:

```text
reuse distance = number of more-recent distinct sector identities between
consecutive references to this same sector identity
```

First sector touches are not reuse instances and never enter this histogram denominator.

Rationale for 4096: the calibrated slice has 1024 resident 128-B lines x 4 sectors. `>4096` is therefore a deliberately conservative indicator of temporal reuse beyond the full sector-count payload footprint; it is not a direct cache-hit prediction because tags/replacement/sector validity still operate at the modeled architecture's own semantics.

Do not call `distance <= C` an exact C-entry LRU capture condition; exact fully-associative LRU capture uses `distance < C`.

Choose an exact implementation with acceptable host overhead. If a bounded list scan is too expensive, optimize the data structure while preserving exact results.

---

## 8. Existing line-level and post-eviction evidence

Do not discard the old line-level result. The extension must make the distinction explicit:

```text
EPL2MOTV1 line reuse
    = line-level locality, may include first touches to other sectors

EPL2SRV1 temporal sector reuse
    = true repeated reference to the same 32-B sector
```

Formal extension runs should enable reviewed `EPL2MOTV1` concurrently so that selected new workloads also obtain:

```text
line reuse distance / coverage
post-eviction rereference evidence
blocking/WBUF data (supplemental only for this lane)
```

For the original 10 workloads, compare the newly emitted `EPL2MOTV1` scientific fields against the immutable `MOTIVATION_FIGURES_r1` tables. They must remain exact if trace/config identity is unchanged.

---

## 9. Stage A — source audit and preflight

Before broad screening:

1. source-map the exact sector-mask producer and frontend request classes;
2. implement `EPL2SRV1` default OFF;
3. add deterministic directed fixtures;
4. Release build;
5. parser/aggregation regressions;
6. timing-neutrality controls.

Controls:

```text
EPL2MOTV1 ON + EPL2SRV1 OFF
vs
EPL2MOTV1 ON + EPL2SRV1 ON
```

Run at least:

```text
vectorAdd_4M
convolutionSeparable
sad
```

Exact equality required for simulation cycles/instructions and every pre-existing production/telemetry output except the new `EPL2SRV1` files.

Host overhead must be measured. If new telemetry increases wall time by roughly >50% on a meaningful pilot or creates dangerous RSS growth, optimize before screening.

Stage-A terminal state:

```text
STREAMING_REUSE_PREFLIGHT_PASS
```

---

## 10. Stage B — screening the existing trace pool

Do not generate new hardware traces in this lane unless separately authorized.

Inventory the currently available runnable trace pool and build a screening shortlist of preferably **12–16 workloads** (minimum 10 if the pool materially limits runnable candidates), spanning at least four semantic/suite families where available.

`vectorAdd_4M` must be included as the known spatial-streaming control but does **not** count as one of the required 2–3 additional formal workloads.

Candidate selection should be source/trace-informed rather than benchmark-name-only. Reasonable priors such as bandwidth kernels, BFS/graph traversal, nearest-neighbor, sorting, option-pricing or other sweep-like kernels may be considered only if they actually exist in the local runnable trace inventory.

Every screening run must use the same frozen extension source pair and the full selected trace represented by its manifest; no hidden shortened-prefix result may be promoted as a formal workload.

Produce:

```text
SCREENING_CANDIDATES.csv
SCREENING_RANKING.csv
SCREENING_NOTES.md
```

At minimum rank by:

```text
sector_temporal_reuse_fraction        ascending
one_touch_sector_fraction             descending
spatial_new_sector_fraction           descending
far_sector_reuse_share_gt1024         descending
far_sector_reuse_share_gt4096         descending
post_eviction_referenced_fraction     ascending for streaming candidates
```

Selection heuristics, not claims:

```text
STRONG_STREAMING prior:
  sector_temporal_reuse_fraction <= 0.10
  AND one_touch_sector_fraction >= 0.80

VERY_STRONG_STREAMING prior:
  sector_temporal_reuse_fraction <= 0.05
  AND one_touch_sector_fraction >= 0.90

FAR_REUSE prior:
  enough true reuse to be statistically meaningful
  AND a material fraction of temporal-sector reuse lies >1024 sectors;
  >4096 is the strongest conservative evidence.
```

Do not fabricate a far-reuse archetype if the screened pool does not contain one.

---

## 11. Stage C — choose 2–3 additional formal workloads

Select **2–3 additional workloads beyond the existing Motivation 10**.

Preferred outcome:

```text
at least 1–2 strong streaming / low-temporal-reuse workloads
+
1 far-reuse workload if one is genuinely supported
```

If no strong far-reuse workload exists in the screened pool:

- select 2–3 strongest streaming/low-temporal-reuse workloads;
- report `NO_STRONG_FAR_REUSE_FOUND_IN_SCREENED_POOL` explicitly;
- do not relabel the least-bad candidate as far reuse.

Selection must consider both metric strength and usefulness as a paper-facing archetype. Avoid choosing three nearly identical kernels unless the trace pool leaves no better semantic diversity.

Record selection rationale in:

```text
FORMAL_WORKLOAD_SELECTION.md
```

A screening row may be promoted without rerun only if it already used the final frozen extension source/config/trace and passed every formal terminal/parser gate.

---

## 12. Stage D — formal Figure-1-v2 dataset

The Figure-1-v2 formal dataset is:

```text
original Motivation 10 workloads
+
selected 2–3 additional workloads
```

Run every original Motivation workload once with the new sector telemetry on the final frozen extension source. Reuse a screening run for a selected new workload only under the promotion rule above.

Original 10:

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

All formal rows must be `COMPLETE_VALID` under one source/config family.

---

## 13. Figure 1 v2

Do not overwrite Figure 1 r1. Generate new distinct filenames.

Required main figure:

```text
FIG1V2_L2_SECTOR_TEMPORAL_REUSE.png
FIG1V2_L2_SECTOR_TEMPORAL_REUSE.svg
```

It should make **reuse amount** and **reuse distance conditional on reuse** visible together. Preferred two-panel design:

### Panel A — temporal-reuse availability

For each workload in one fixed order show enough information to see whether it is actually reusable:

```text
sector_temporal_reuse_fraction
one_touch_sector_fraction
spatial_new_sector_fraction
```

The plot must make a streaming workload visibly different from a reuse-rich workload even if both would have short conditional reuse distance.

### Panel B — temporal-sector reuse distance

Stacked distribution over class-C events only:

```text
<=8 ... >4096
```

Every nonempty stacked bar sums to 1.0. Annotate each workload with its temporal-reuse fraction so a low-reuse workload cannot be misread from the conditional stack alone.

Required supplemental figure:

```text
FIG1S_LINE_VS_SECTOR_REUSE.png
FIG1S_LINE_VS_SECTOR_REUSE.svg
```

Compare old/new locality views, e.g. line-level reuse-instance fraction vs true temporal-sector reuse fraction. The intended diagnostic is to expose spatial-only streams such as vectorAdd if the data support that interpretation.

Do not alter any Figure-2 artifact from Motivation r1.

---

## 14. Required machine-readable outputs

At minimum:

```text
sector_reuse_summary.csv
sector_reuse_distance.csv
sector_reuse_coverage.csv
line_vs_sector_reuse.csv
screening_candidates.csv
screening_ranking.csv
formal_workload_selection.csv
formal_workload_status.csv
raw_log_index.tsv
aggregation_manifest.json
```

All ratios must be derived from aggregated counts, not averaged per-slice percentages.

`NA` must remain distinct from measured zero.

---

## 15. Autonomous repair / provenance policy

Codex may autonomously repair bugs limited to:

```text
observation-only sector-reuse producer
parser / aggregator
runner / manifest handling
plotting / packaging
directed tests
```

If simulator source or telemetry semantics change after formal runs start:

1. preserve all failing/old output under its existing directory;
2. create a new commit/SHA;
3. freeze the new pair;
4. invalidate only formal extension results that depended on the old pair;
5. rerun required preflight/formal rows.

Never delete old results to make the tree look clean.

---

## 16. Stop condition

Continue autonomously through implementation, preflight, screening, formal workload selection, original-10+new formal runs, aggregation and Figure 1 v2.

Publish:

```text
docs/ep_l2/codex_handoff/LANE_STREAMING_REUSE_LATEST.md

docs/ep_l2/review_packs/STREAMING_REUSE_CHARACTERIZATION_r1/
```

Terminal status:

```text
STREAMING_REUSE_FIG1V2_REVIEW_READY
```

Then push exact Core/Framework branches and STOP for independent ChatGPT review.

Do not self-declare final scientific PASS.
