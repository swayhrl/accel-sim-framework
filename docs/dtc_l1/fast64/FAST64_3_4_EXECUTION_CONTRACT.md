# DTC FAST64.3/4 Execution and Acceptance Contract

Status: **MANDATORY OPERATING CONTRACT FOR FAST64.3 AND FAST64.4**

This document refines execution, reuse, promotion, and closeout behavior for
FAST64.3 and FAST64.4. It does not weaken `FAST64_ACCEPTANCE_CONTRACT.md`; if a
conflict is discovered, the stricter existing scientific requirement wins and
the conflict must be resolved explicitly rather than silently reinterpreted.

Authoritative default identity for new formal acquisition is:

- mechanism behavior anchor: `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`;
- formal repaired Core: `95ccdb7a056f2d53f740d90869785cac6d4ee0f5`;
- formal runtime SHA-256: `462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9`;
- A1 observer SHA-256: `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`;
- frozen scientific/config Framework snapshot: `037f008b330eb230353b60edf126d6be9f45afdc`;
- FAST12 membership and payload identities: `FAST64_WORKLOAD_MANIFEST.tsv` and
  `generated/FAST64_PAYLOAD_MANIFEST.tsv`.

The narrow 2DConvolution exception is Core
`6587238c60214d99491f4048e28ce8a3458c1509` with runtime SHA-256
`29a3dd9f57a5accb89822ca3fcf06b11c437bfe864ee43d2ff5f26c8c056f3c1`.
It applies only to the repaired common 2DConvolution Base/IO/OO triplet and
its cap-resolution controls or required reacquisition.  The source-backed
scope, anti-mixing rule, and non-supersession status are mandatory in
`handoffs/FAST64_2D_TAG_IDENTITY_CORE_AUTHORITY_MAP.md`.

No current controller/review HEAD may replace the frozen scientific execution
snapshot in a result identity.

Historical bbcbb/runtime rows retain their literal identity and require the
explicit map in `handoffs/FAST64_ZERO_ACCESS_CORE_REPAIR_IDENTITY_MAP.md`; they
must never be rewritten as repaired-Core rows.  No new long formal row may use
the former bbcbb runtime after this authority transition.

## 1. Stage-order and physical-acquisition rule

Logical promotion remains strictly:

`FAST64.1 -> FAST64.2 -> FAST64.3 -> FAST64.4`.

Physical acquisition may overlap only under the already-authorized pending
classes. A physically completed row is not promoted merely because it exists.

- Base rows acquired before FAST64.1/2 close remain
  `PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE` until their owning gates pass.
- Main-matrix IO/OO acquisition begins only after `FAST64_2_REPAIR_PASS`; rows
  acquired before FAST64.3 logical PASS remain
  `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`.
- No IO/OO observation may alter FAST12 membership, input, or Base
  characterization decisions.

## 2. FAST64.3 — Base characterization

### 2.1 Fixed roster

FAST64.3 contains exactly one accepted Base row for each frozen member:

1. ATAX
2. BICG
3. GESUMMV
4. GEMM
5. 2DConvolution
6. Btree
7. DWT2D
8. Gaussian
9. Hotspot1
10. LUD
11. NN
12. MRI-Q

No member may be removed because it is low-pressure, slow, inconvenient, or
later shows weak/negative DTC benefit.

### 2.2 Reuse before rerun

Before launching a Base row, search current compact evidence for an exact-
identity completed Base attempt. Reuse is preferred over rerun when all of the
following match and validate:

- workload and frozen payload identity;
- `FAST64_BASE` config SHA and lower-cap setting;
- formal Core/runtime/A1 observer/scientific Framework identities;
- immutable attempt/receipt chain where required by the active execution path;
- natural exit zero and strict parser/accounting acceptance;
- required FAST64.3 metric completeness or a source-backed explicit
  unsupported-field classification.

A precomputed row is promoted only after FAST64.1 and FAST64.2 are formally
closed. Promotion changes classification, not simulator output.

Known candidate reuse sources include exact-identity BICG Base from the formal
R2 wave and already strict-valid Base precomputes; Codex must verify identities
rather than rerun them by name alone.

### 2.3 Per-row correctness HARD gate

Every accepted Base row must have:

- natural simulator exit `0`;
- exactly one accepted execution epoch;
- exact frozen payload order/identity;
- exact Base config and common formal identities;
- no assertion, fatal, actual deadlock, trace/output mismatch, or unexplained
  execution-controller anomaly;
- lower accounting balanced and final lower outstanding `0`;
- PIB accounting balanced and final PIB state `0`;
- any parser-required Base lifecycle/accounting fields balanced;
- positive cycle/instruction progress.

`DTC_L1_lower_cap_full_events` must be collected for every row. A nonzero value
is not silently accepted: it reopens the upstream non-binding-cap assumption
for source-correct resolution before primary performance interpretation.

### 2.4 Required metric completeness

Each accepted row must provide parser-valid values, or an explicit source-
backed unsupported-field classification, for these groups:

- performance: cycles, dynamic instructions;
- source-domain operations when available: Load/Store/Atomic/FENCE_OP;
- PIB: admits/retires, current/final, peak, full/backpressure where modeled;
- true Tag/cacheline allocation pressure;
- Tag-bank arbitration/conflicts kept separate from allocation pressure;
- MSHR entry-full and merge-full pressure kept distinct;
- lower/miss-queue/downstream capacity pressure;
- lower/live-miss lifecycle: create/complete or acquire/release, average/peak
  when supported;
- L1/L2 accesses/hits/misses and supported traffic/NoC/DRAM fields;
- host planning fields: wall/user/sys time, host throughput, peak RSS;
- terminal drain/accounting status and result identity/provenance.

Do not map an internal `BK_CONF` retry to Tag-bank conflict unless the source
semantics actually identify a Tag-bank arbitration event.

### 2.5 Required compact FAST64.3 outputs

Before FAST64.3 PASS, generate compact, reviewable outputs at minimum:

- `generated/fast64_3_base_rows.tsv` — one accepted row per FAST12 member;
- `generated/fast64_3_structural_pressure.tsv` — separated pressure categories;
- `generated/fast64_3_live_misses.tsv` — common lower/live-miss lifecycle fields;
- `generated/fast64_3_host_runtime.tsv` — host planning/resource fields;
- `generated/fast64_3_identity_manifest.tsv` — row evidence path + SHA-256;
- a raw-log index referencing external run directories without committing raw
  multi-GB output.

### 2.6 FAST64.3 PASS

FAST64.3 may become `FAST64_3_BASE_PASS` only when:

- FAST64.1 and FAST64.2 are PASS;
- all 12 frozen Base rows satisfy per-row HARD correctness/fidelity;
- metric completeness is closed for all 12;
- no unresolved implementation/modeling issue is hidden as a workload result;
- the required compact outputs exist and agree with row evidence;
- `handoffs/FAST64_3_BASE_CHARACTERIZATION.md` contains the full stage handoff
  and explicitly checked HARD acceptance list.

## 3. FAST64.4 — Primary Base/IO/OO matrix

### 3.1 Fixed matrix

The primary matrix is exactly `12 workloads x 3 modes = 36 rows`.

Reuse the 12 accepted FAST64.3 Base rows. Acquire exactly the 24 missing IO/OO
rows unless an exact-identity valid precomputed row already exists and passes
promotion checks.

No workload or mode may be removed because of performance outcome.

### 3.2 Triplet identity HARD gate

For each workload, Base/IO/OO must share:

- identical frozen payload identity and processed trace order;
- common formal Core/runtime/A1 observer/scientific Framework identity;
- identical unrelated platform settings;
- the same workload-independent observer policy;
- only the documented Base/IO/OO mechanism-required configuration differences.

Dynamic instructions and source-domain operation identity must match where the
model contract requires equality. Any unexpected difference is a correctness
investigation, not a performance result.

### 3.3 Per-row correctness HARD gate

Every primary row must:

- naturally terminate with exit `0`;
- strict-parse under the active versioned validator/parser contract;
- have one accepted execution epoch and valid identity/receipt provenance;
- have no assertion, fatal, actual deadlock, trace/output mismatch, or
  unresolved controller anomaly;
- satisfy mode-specific lower create/issue/response conservation;
- satisfy dependency create/complete conservation where applicable;
- finish with PIB/inflight/lower state `0`;
- finish OO active refs/reclaim state `0` where applicable.

Collect `DTC_L1_lower_cap_full_events` for every primary row. A nonzero value
must be source-classified and resolved before accepting the row as evidence for
a non-binding-cap performance comparison.

### 3.4 Primary performance calculation

Per workload:

- `speedup_IO = cycles_BASE / cycles_IO`;
- `speedup_OO = cycles_BASE / cycles_OO`.

Aggregate:

- `GM-FAST12_IO` is the geometric mean of all 12 `speedup_IO` values;
- `GM-FAST12_OO` is the geometric mean of all 12 `speedup_OO` values.

Membership is exactly FAST12. No exclusion is permitted for weak, zero, or
negative speedup.

### 3.5 Required compact FAST64.4 outputs

Before FAST64.4 PASS, generate at minimum:

- `generated/fast64_4_primary_matrix.tsv` — all 36 row identities/statuses;
- `generated/fast64_4_triplets.tsv` — Base/IO/OO cycles/instructions and exact
  identity checks by workload;
- `generated/fast64_4_speedup.tsv` — per-workload IO/OO speedup + GM-FAST12;
- `generated/fast64_4_accounting.tsv` — mode-specific conservation/drain;
- `generated/fast64_4_identity_manifest.tsv` — evidence path + SHA-256;
- `generated/fast64_4_retry_obsolete_map.tsv` — every replaced/failed attempt
  and why it is non-authoritative;
- raw-log index referencing external raw run directories.

FAST64.4 may also retain parser-supported structural/live-miss/traffic fields
needed by FAST64.5, but FAST64.4 PASS must not wait for paper-facing causal
interpretation beyond correctness and primary-matrix completeness.

### 3.6 Retry and invalidation discipline

When one row fails:

`OBSERVE -> REPRODUCE -> CLASSIFY -> INVESTIGATE -> SOURCE-CORRECT REPAIR ->
REGRESS -> INVALIDATE ONLY AFFECTED IDENTITY -> RERUN ONLY AFFECTED ROW -> RESUME`.

Do not restart the full matrix for a row-local failure. Preserve failed attempts
as explicit non-authoritative evidence with a reason.

Negative performance is not a failure and must never trigger retuning.

### 3.7 FAST64.4 PASS

FAST64.4 may become `FAST64_4_PRIMARY_PASS` only when:

- FAST64.3 is PASS;
- all 36 rows are accepted or exact-identity promoted evidence;
- every triplet passes identity/instruction/correctness/drain checks;
- all 12 IO and 12 OO speedups are computed from accepted rows;
- GM-FAST12 uses exactly 12 members for each mode;
- retry/obsolete history is explicit and no unresolved correctness issue remains;
- all required compact outputs exist and reconcile;
- `handoffs/FAST64_4_PRIMARY_MATRIX.md` contains the full stage handoff and
  explicitly checked HARD acceptance list.

## 4. Scheduling and Goal behavior

Logical stage order does not require physical serialization. After FAST64.2
PASS, missing Base/IO/OO acquisition may use a measured dynamic worker pool,
subject to the pending classifications above.

Use current cgroup/topology/memory/I/O measurements to choose `N_safe`. Prefer
aggregate useful simulated throughput, not maximal process count.

A HARD gate blocks stage/result promotion, not the persistent Goal. Ordinary
build/config/parser/controller/storage/scheduling/workload-local failures are
problems to solve. Codex must investigate and repair them using a source-correct
path rather than stop at the first failure.

Pause only at the true researcher-decision boundaries in
`FAST64_EXECUTION_RUNBOOK.md`.

## 5. Git and evidence discipline

- never use `git add .` or `git add -A`;
- never commit raw multi-GB simulator output;
- preserve unique scientific evidence and untracked user artifacts;
- commit compact manifests, hashes, summaries, handoffs, and raw-log indices;
- do not overwrite an accepted attempt; use a fresh namespace for reruns;
- do not modify a live long-running controller/runner in place; create a
  versioned future-only path when behavior must change.
