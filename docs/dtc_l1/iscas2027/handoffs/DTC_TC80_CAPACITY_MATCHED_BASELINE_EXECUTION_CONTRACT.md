# DTC TC80 Capacity-Matched Baseline — Operational Execution Contract

Status on creation: `TC80_EXECUTION_CONTRACT_READY`

This file supplements, but does not replace:

`docs/dtc_l1/iscas2027/handoffs/DTC_TC80_CAPACITY_MATCHED_BASELINE_HANDOFF.md`

Codex Goal mode must read **both files completely** before doing any TC80 work. The scientific handoff is authoritative for scope and interpretation; this execution contract makes the stage gates, run matrix, evidence lifecycle, and failure behavior operationally explicit.

---

## 0. Authority and immutable ancestors

Repository: `swayhrl/accel-sim-framework`

Execution branch:

`hrl/iscas2027-dtc-tc80-baseline-v0`

Branch point / frozen paper-evidence parent:

`b201b03f8100b5df0010fb64849a3e826b5a2183`

Frozen FAST64 scientific authority:

`18a68dcccd795f1b6cda75504e9450d00c9cee02`

The following are read-only inputs for this experiment:

- frozen FAST64 Base/IO/OO results;
- frozen Lane-E final package and all Lane-E QA records;
- FAST12 workload membership and trace ordering;
- accepted Base/IO/OO mechanism semantics.

The TC80 campaign creates **new conventional-cache evidence only**. It must never rewrite or regenerate accepted Base/IO/OO results in place.

---

# 1. Exact scientific question

The campaign answers only:

> If the same 80-KiB data-array byte budget used as the DTC physical pool is instead exposed as ordinary searchable capacity in a conventional tightly-coupled L1, how does performance compare with B16, IO16/80, and OO16/80?

This is a **data-array-capacity-matched** experiment.

It is not yet:

- total-area matched;
- timing matched by synthesis;
- power matched;
- large-PIB matched;
- large-MSHR matched;
- a claim that an 80-KiB conventional cache has identical metadata cost to DTC.

Those questions require later RTL/DC and/or separate ablation handoffs.

---

# 2. Fixed architecture identities

## 2.1 `B16`

Frozen FAST64 conventional baseline:

- conventional tightly-coupled Tag/Data organization;
- searchable data capacity = 16 KiB;
- line size = 128 B;
- Base PIB = 8;
- Base MSHR = 32;
- frozen replacement/write/allocation semantics;
- frozen GPU shell and downstream memory hierarchy.

## 2.2 `TC80`

New conventional baseline:

- conventional tightly-coupled Tag/Data organization;
- searchable data capacity = exactly 80 KiB;
- exactly 640 searchable lines;
- line size = exactly 128 B;
- PIB = exactly 8;
- MSHR = exactly 32;
- no Tag/Data renaming;
- no IO/OO DTC physical-line lifetime semantics;
- same modeled L1 hit latency as B16 unless source inspection proves the capacity syntax necessarily changes a different field, in which case STOP for review rather than silently accepting it;
- same bank/request bandwidth unless a capacity-geometry field mechanically implies a source-proven derived field;
- all unrelated GPU/memory parameters equal B16.

## 2.3 `IO16/80`

Frozen accepted DTC IO evidence:

- logical searchable Tag capacity = 16 KiB equivalent;
- physical data pool = 80 KiB / 640 lines;
- IO PIB = 256;
- frozen accepted IO semantics.

## 2.4 `OO16/80`

Frozen accepted DTC OO evidence:

- logical searchable Tag capacity = 16 KiB equivalent;
- physical data pool = 80 KiB / 640 lines;
- OO PIB = 128;
- frozen accepted OO semantics, including explicit physical-line lifetime/reference tracking.

---

# 3. Stage state machine

The only normal forward path is:

`CM0 -> CM1 -> CM2 -> CM3 -> CM4 -> CM5 -> CM6`

CM5 may resolve as `NOT_TRIGGERED`, but the trigger decision must still be recorded.

At every stage, emit a machine-readable status artifact containing at least:

`stage,status,input_commit_or_hash,output_artifacts,blocking_reason`

Recommended file:

`docs/dtc_l1/iscas2027/tc80/status/CMx_STATUS.tsv`

Allowed stage states:

- `NOT_STARTED`
- `IN_PROGRESS`
- `PASS`
- `NOT_TRIGGERED` (CM5 only)
- `BLOCKED_REQUIRES_USER_REVIEW`
- `FAIL`

A later stage must not be marked PASS if any mandatory earlier stage is unresolved.

---

# 4. CM0 — source/config feasibility audit

## 4.1 No simulation in CM0

CM0 is source/config inspection only. Do not launch the scientific FAST12 campaign here.

## 4.2 Required source questions

Codex must identify the exact conventional Base path and cite repository paths plus relevant functions/classes/options for:

1. configuration parser for L1 geometry;
2. conventional Tag array construction;
3. conventional data array construction;
4. set-index extraction/hash;
5. way lookup and victim selection;
6. reserved-line allocation behavior;
7. MSHR allocation/merge behavior;
8. PIB/backpressure path;
9. L1 hit-latency source;
10. runtime/config echo used to prove effective geometry;
11. Base-vs-DTC mode selection and proof that DTC-only state is inactive in Base mode.

## 4.3 Enumerate exact 640-line geometry candidates

Do not start with one assumed geometry. Enumerate source-legal candidates whose product is exactly 640 lines, including any of the following only when source-legal:

- 32 sets x 20 ways;
- 64 sets x 10 ways;
- 128 sets x 5 ways;
- other exact factorizations supported by the actual model.

For every candidate record:

- sets;
- ways;
- line size;
- total lines;
- total bytes;
- whether set count is legal;
- whether way count is legal;
- whether indexing is correct;
- whether replacement state supports that associativity;
- whether configuration is source-only/config-only;
- whether bank mapping/bandwidth changes;
- whether L1 hit latency changes;
- whether the geometry preserves B16 set indexing;
- selection disposition.

## 4.4 Geometry selection precedence

Select the primary TC80 geometry by this order:

1. exact 640 lines / 80 KiB;
2. config-only, no Core/simulator source changes;
3. preserve B16 line size;
4. preserve B16 set mapping when practical;
5. preserve bank count/request throughput;
6. preserve replacement/write policy;
7. avoid introducing a different modeled hit latency;
8. document why the chosen geometry is preferable to every other source-legal exact geometry.

Do **not** optimize the choice for better performance.

## 4.5 CM0 mandatory outputs

- `CM0_SOURCE_AND_CONFIG_AUDIT.md`
- `CM0_GEOMETRY_CANDIDATES.tsv`
- `status/CM0_STATUS.tsv`

## 4.6 CM0 PASS

PASS requires all of:

- conventional Base code path source-proven;
- exact 80 KiB representable without scientific source changes;
- exact chosen geometry source-legal;
- indexing/replacement legality established;
- L1 latency behavior established;
- conventional/DTC mode separation established;
- no frozen artifact changed.

If exact TC80 requires source modification, emit:

`CM0_BLOCKED_EXACT_TC80_REQUIRES_SOURCE_CHANGE`

and stop for user review.

---

# 5. CM1 — immutable TC80 config lock

## 5.1 Build one canonical TC80 config

Create exactly one primary TC80 configuration/overlay from the selected CM0 geometry.

Do not create multiple primary TC80 configs and choose the best after observing performance.

## 5.2 Required B16-vs-TC80 resolved diff

Generate a machine-readable resolved diff against the frozen B16 configuration.

Every changed option must be classified as:

- `REQUIRED_TC80_CAPACITY_GEOMETRY`, or
- `DERIVED_FROM_REQUIRED_GEOMETRY`.

Any other changed option is a hard gate failure.

## 5.3 Fields that must remain equal to B16

At minimum verify equality for:

- mode selector = conventional/Base;
- line size = 128 B;
- Base PIB = 8;
- Base MSHR = 32;
- L1 hit latency;
- write policy;
- replacement policy;
- allocation policy apart from geometry-only representation;
- Tag/data request bandwidth;
- cluster/core counts;
- scheduler settings;
- L2 geometry and latency;
- DRAM geometry/timing;
- memory partitions/subpartitions;
- trace payload identity.

## 5.4 Hash lock

Freeze:

- TC80 config SHA-256;
- resolved effective config SHA-256;
- B16 source config identity;
- tool/controller script identities used to launch the campaign.

## 5.5 CM1 outputs

- canonical TC80 config/overlay;
- `CM1_TC80_CONFIG_LOCK.md`;
- `CM1_B16_VS_TC80_RESOLVED_CONFIG_DIFF.tsv`;
- `CM1_CONFIG_SHA256.tsv`;
- `status/CM1_STATUS.tsv`.

## 5.6 CM1 PASS

PASS requires exact effective 80-KiB conventional searchable capacity, 640 lines, Base PIB/MSHR 8/32, no DTC semantics, and zero unrelated configuration differences.

---

# 6. CM2 — smoke/identity qualification

## 6.1 Required smoke workloads

Run these three canonical workloads unless a frozen execution-path constraint makes one impossible and is documented:

1. `NN`
2. `Btree`
3. `BICG`

They are qualification rows, not the final scientific aggregate.

## 6.2 Immutable attempt rule

Every execution attempt gets a unique namespace/attempt ID.

Never overwrite a failed attempt with a rerun.

For a retry:

- preserve failed raw output;
- record the failure class;
- create a new attempt ID/directory;
- link the accepted attempt to all prior attempts in the manifest.

## 6.3 Per-row identity fields

Record at least:

- workload;
- attempt ID;
- trace/payload member identity;
- trace hash/manifest lineage;
- TC80 config SHA;
- runtime/binary identity;
- selected TC80 sets/ways/line bytes;
- runtime-proven total lines/bytes;
- PIB value;
- MSHR value;
- start/end/natural-exit state;
- instructions;
- cycles;
- parser status;
- fatal/assert/deadlock/error scan status;
- terminal accounting status;
- disposition.

## 6.4 Scientific qualification

Do not use speedup as a smoke PASS condition.

A slower TC80 row is scientifically valid if identity and execution are correct.

## 6.5 CM2 outputs

- `CM2_SMOKE_RUN_MANIFEST.tsv`;
- `CM2_SMOKE_VALIDATION.tsv`;
- `CM2_RAW_PROVENANCE.tsv`;
- `status/CM2_STATUS.tsv`.

## 6.6 CM2 PASS

All three workloads must have at least one naturally terminating, strict-accepted attempt under the exact frozen TC80 config, with no identity ambiguity and no mixed execution epoch.

---

# 7. CM3 — exact FAST12 TC80 primary campaign

## 7.1 Primary workload order is fixed

Use exactly this ordered membership from the frozen FAST12 authority:

1. `ATAX`
2. `BICG`
3. `GESUMMV`
4. `GEMM`
5. `2DConvolution`
6. `Btree`
7. `DWT2D`
8. `Gaussian`
9. `Hotspot1`
10. `LUD`
11. `MRI-Q`
12. `NN`

No workload may be omitted because TC80 is slower, neutral, or inconvenient.

No extra workload may enter the FAST12 GM.

## 7.2 New simulation scope

New scientific runs in CM3 are TC80 only.

B16/IO/OO values must be imported from the frozen accepted FAST64/Lane-E package using exact commit/hash lineage.

Do not rerun B16/IO/OO simply for convenience.

## 7.3 Safe execution policy

Codex may parallelize independent TC80 rows when system resources permit, but must:

- avoid oversubscription that creates OOM/host instability;
- record the launch/controller identity;
- never reuse one output directory for multiple attempts;
- never classify timeout termination as scientific completion;
- preserve every raw attempt;
- accept only natural terminal rows.

If a controller or environment failure occurs, retry in a new immutable namespace after fixing the non-scientific root cause.

## 7.4 Per-row mandatory acceptance

Every accepted row requires:

- exact workload membership;
- exact trace/payload identity;
- exact TC80 config SHA;
- exact conventional mode;
- exact effective 80 KiB / 640 lines;
- PIB=8 and MSHR=32;
- natural exit code 0;
- strict parser PASS;
- instruction count equal to frozen workload identity;
- no assertion/fatal/deadlock/trace/output error;
- terminal queue/request/dependency accounting closed;
- unique accepted execution epoch;
- raw output and compact result hash-bound.

## 7.5 Required frozen-source binding

For every workload, the summary must carry or be traceable to:

- B16 frozen cycles source;
- IO frozen cycles source;
- OO frozen cycles source;
- TC80 new run source.

Never copy cycle numbers manually without lineage.

## 7.6 CM3 primary summary schema

At minimum:

`workload,instructions,b16_cycles,tc80_cycles,io_cycles,oo_cycles,speedup_tc80_over_b16,speedup_io_over_b16,speedup_oo_over_b16,speedup_io_over_tc80,speedup_oo_over_tc80,b16_source,tc80_source,io_source,oo_source`

Definitions are fixed:

- `speedup_tc80_over_b16 = b16_cycles / tc80_cycles`
- `speedup_io_over_b16 = b16_cycles / io_cycles`
- `speedup_oo_over_b16 = b16_cycles / oo_cycles`
- `speedup_io_over_tc80 = tc80_cycles / io_cycles`
- `speedup_oo_over_tc80 = tc80_cycles / oo_cycles`

## 7.7 CM3 outputs

- `CM3_TC80_FAST12_RUN_MANIFEST.tsv`;
- `CM3_TC80_FAST12_SUMMARY.tsv`;
- `CM3_TC80_INPUT_AND_OUTPUT_MANIFEST.tsv`;
- `CM3_FAILED_AND_SUPERSEDED_ATTEMPTS.tsv` if any;
- `status/CM3_STATUS.tsv`.

## 7.8 CM3 PASS

Exactly 12 ordered accepted TC80 rows, with no missing/duplicate workload, exact frozen B16/IO/OO bindings, and no diagnostic/observer rows in the primary aggregate.

---

# 8. CM4 — paper-facing fairness analysis

## 8.1 Geometric means

All GMs must use unrounded per-workload integer cycle ratios over the exact 12 members.

Compute:

- `GM_TC80_OVER_B16 = GM(b16_cycles / tc80_cycles)`;
- `GM_IO_OVER_B16 = GM(b16_cycles / io_cycles)`;
- `GM_OO_OVER_B16 = GM(b16_cycles / oo_cycles)`;
- `GM_IO_OVER_TC80 = GM(tc80_cycles / io_cycles)`;
- `GM_OO_OVER_TC80 = GM(tc80_cycles / oo_cycles)`.

Cross-check frozen IO/B16 and OO/B16 GMs against the accepted values; mismatch is a hard lineage/arithmetic failure, not something to round away.

## 8.2 Per-workload comparison

Retain numeric ratios for all workloads.

For descriptive classification only, use a symmetric 1% near-tie window unless a different tolerance is explicitly approved:

- ratio > 1.01: numerator-named design is faster according to the declared ratio;
- 0.99 <= ratio <= 1.01: `NEAR_TIE`;
- ratio < 0.99: denominator-named design is faster.

Classification never replaces the numeric ratio and is not an acceptance gate.

## 8.3 Paper claim boundary

The primary paper statement may say:

- TC80 is an exact 80-KiB conventional searchable-capacity baseline;
- DTC uses 16-KiB logical searchable Tag capacity and an 80-KiB physical data pool;
- therefore the comparison asks whether the same data-array bytes are better used as ordinary locality capacity or as decoupled physical state.

It may **not** say, without future RTL/DC evidence:

- equal total area;
- equal timing;
- equal power;
- equal metadata cost;
- DTC's performance difference is caused only by Tag/Data decoupling;
- TC80 represents an optimized large-PIB/MSHR conventional design.

## 8.4 Optional explanatory counters

Only add counters whose definitions and denominators are source-proven and comparable across all required modes.

Do not synthesize an average MLP metric from cumulative events.

## 8.5 CM4 outputs

- `CM4_CAPACITY_MATCHED_COMPARISON.tsv`;
- `CM4_CAPACITY_MATCHED_ANALYSIS.md`;
- `CM4_PAPER_PLOT_READY.tsv`;
- `status/CM4_STATUS.tsv`.

---

# 9. CM5 — geometry robustness decision and bounded experiment

## 9.1 Trigger decision is mandatory

Always emit:

`CM5_TRIGGER_DECISION.tsv`

The decision must explicitly evaluate every trigger from the scientific handoff.

## 9.2 Expected likely trigger

If the primary geometry preserves 32 B16 sets by using 20 ways, CM5 is automatically triggered because associativity is substantially larger than B16 and >8 ways.

## 9.3 Preferred alternate exact-80-KiB geometry

If source-legal, prefer another exact factorization such as:

- 64 sets x 10 ways, or
- 128 sets x 5 ways,

rather than a different capacity, because this holds total data bytes exactly at 80 KiB while changing set/way geometry.

Do not assume either is legal before CM0 source proof.

## 9.4 Minimal CM5 workload set

Default representative set:

- `BICG`;
- `Btree`;
- `2DConvolution`.

These rows are robustness diagnostics and never enter FAST12 primary GM.

## 9.5 If no second exact geometry exists

Use source-legal bracketing capacities only if necessary, e.g. 64/96 KiB, while retaining all unrelated Base parameters.

Label them as bracketing diagnostics, not capacity-matched primary baselines.

## 9.6 CM5 interpretation

CM5 PASS means the chosen primary TC80 result is not obviously an invalid artifact of an unsupported/peculiar geometry.

It does not require all geometries to have equal performance.

## 9.7 CM5 outputs

- `CM5_TRIGGER_DECISION.tsv`;
- `CM5_GEOMETRY_ROBUSTNESS_RUNS.tsv` if triggered;
- `CM5_GEOMETRY_ROBUSTNESS_ANALYSIS.md` if triggered;
- `status/CM5_STATUS.tsv`.

---

# 10. CM6 — final evidence package and freeze

## 10.1 Review-pack location

`docs/dtc_l1/iscas2027/tc80/review_pack/`

## 10.2 Mandatory contents

At minimum include compact, reviewable copies/references for:

- CM0 source/config audit;
- geometry candidate table;
- canonical TC80 config and hashes;
- B16-vs-TC80 resolved diff;
- smoke manifest/validation;
- FAST12 run manifest;
- FAST12 TC80 summary;
- frozen B16/IO/OO bindings;
- capacity-matched comparison;
- CM5 trigger decision and robustness evidence if triggered;
- claim/evidence boundaries;
- limitations;
- reproducibility instructions;
- input/output SHA-256 manifest;
- stage status table.

## 10.3 Final independent validation

Before READY status, verify machine-readable facts:

- exact FAST12 ordered membership;
- exactly 12 accepted TC80 primary rows;
- exact 640-line 80-KiB conventional geometry;
- Base PIB/MSHR = 8/32;
- zero unrelated config differences;
- five GMs regenerated from integer cycles;
- IO/B16 and OO/B16 reproduce frozen accepted GMs within exact/declared numeric formatting policy;
- no CM5 diagnostic row enters primary GM;
- frozen Lane-E and FAST64 accepted trees remain unchanged;
- git diff is confined to the TC80 branch experiment scope.

## 10.4 Final status

Only after all mandatory checks pass:

`ISCAS2027_TC80_CAPACITY_MATCHED_BASELINE_READY_FOR_PAPER`

Then mark the TC80 package read-only.

Future conventional large-PIB/MSHR, area-matched, power, RTL/DC, or L2 experiments must start from a new handoff and must not rewrite this package.

---

# 11. Failure taxonomy and Goal-mode recovery

Classify failures before acting:

## `ENVIRONMENT_FAILURE`

Examples: host transient, missing mount, scheduler/controller failure.

Action: preserve evidence, fix environment, rerun in a new immutable attempt namespace.

## `CONFIGURATION_FAILURE`

Example: wrong option/hash or TC80 not actually effective.

Action: do not accept the run; repair config only within CM0/CM1 contract; create new config hash/version if necessary and invalidate prior TC80 attempts.

## `CONTROLLER_OR_PARSER_FAILURE`

Action: preserve raw run; repair tooling without altering simulator semantics; revalidate from immutable raw evidence when possible, otherwise rerun in a new namespace.

## `EXPECTED_SCIENTIFIC_REGRESSION`

Example: TC80 is slower than B16/DTC.

Action: accept if all execution/identity checks pass. Never rerun to seek a favorable value.

## `MODEL_OR_SOURCE_BLOCKER`

Examples: exact 80 KiB cannot be represented without source changes; source indexing is invalid for every exact geometry.

Action: stop for user review. Do not patch scientific source under this handoff.

## `IDENTITY_CONTAMINATION`

Examples: mixed epochs, wrong trace, wrong config, overwritten raw result.

Action: row is invalid. Preserve it, dispatch a new clean attempt. Never repair the accepted number by hand.

---

# 12. Acceptance checklist

CM6 must materialize an equivalent checklist with actual evidence paths.

| Gate | Required state |
|---|---|
| CM0 conventional Base path source-proven | PASS |
| CM0 exact 80-KiB config-only geometry legal | PASS |
| CM0 indexing/replacement/latency semantics audited | PASS |
| CM1 canonical TC80 config hash frozen | PASS |
| CM1 only sanctioned B16->TC80 differences | PASS |
| CM2 NN smoke | PASS |
| CM2 Btree smoke | PASS |
| CM2 BICG smoke | PASS |
| CM3 exact ordered FAST12 membership | PASS |
| CM3 12/12 TC80 rows naturally terminate | PASS |
| CM3 all TC80 rows strict identity/terminal validation | PASS |
| CM3 B16/IO/OO values hash-bound to frozen evidence | PASS |
| CM4 five GMs regenerated from integer cycles | PASS |
| CM4 paper claim boundary explicit | PASS |
| CM5 trigger decision | PASS or NOT_TRIGGERED |
| CM5 required robustness experiment | PASS or NOT_TRIGGERED |
| Frozen Lane-E tree unchanged | PASS |
| Frozen FAST64 accepted evidence unchanged | PASS |
| No simulator/Core scientific source change | PASS |
| Final review-pack SHA manifest | PASS |
| Reproduction instructions | PASS |

---

# 13. Final Codex report format

The final Goal-mode report must include, in this order:

1. start branch/commit and final commit/remote HEAD;
2. selected TC80 geometry;
3. source proof that the geometry is legal;
4. exact total lines/bytes and runtime proof;
5. exact B16-vs-TC80 resolved config differences;
6. smoke matrix and dispositions;
7. TC80 FAST12 12/12 matrix;
8. the five geometric means;
9. per-workload IO-vs-TC80 and OO-vs-TC80 ratios/classification;
10. CM5 trigger decision and robustness results if required;
11. raw run and compact provenance locations;
12. exact files changed/added;
13. confirmation that frozen Lane-E/FAST64 accepted artifacts are unchanged;
14. confirmation that simulator/Core scientific source was not modified;
15. final status token.

Do not provide only a prose summary; include the actual numeric result table or exact artifact path containing it.
