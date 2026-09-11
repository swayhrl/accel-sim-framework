# FAST64.4 — Primary Base/IO/OO Matrix Handoff

Status: **PREPARED — DO NOT CLAIM FAST64_4_PRIMARY_PASS UNTIL EVERY HARD ITEM BELOW IS CHECKED**

This file is the authoritative FAST64.4 stage handoff template. Goal mode must
fill and close it rather than inventing a weaker ad-hoc matrix closeout.

Detailed execution/promotion authority:
`../FAST64_3_4_EXECUTION_CONTRACT.md`.

## 1. Stage anchors

Previous required PASS anchors:

- FAST64.1: `FAST64_1_PLATFORM_PASS`
- FAST64.2: `FAST64_2_REPAIR_PASS`
- FAST64.3: `FAST64_3_BASE_PASS`

Formal identities to record at closeout:

| item | required identity |
| --- | --- |
| mechanism behavior anchor | `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9` |
| historical telemetry Core/runtime | `bbcbb5e7565417102087bc80b14c349b4e568c05` / `6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041` (literal historical evidence only) |
| current formal repaired Core/runtime | `95ccdb7a056f2d53f740d90869785cac6d4ee0f5` / `462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9` (new acquisition) |
| A1 observer SHA-256 | `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e` |
| scientific/config Framework snapshot | `037f008b330eb230353b60edf126d6be9f45afdc` |
| payload authority | `FAST64_WORKLOAD_MANIFEST.tsv` + `generated/FAST64_PAYLOAD_MANIFEST.tsv` |

Record exact Base/IO/OO config SHA-256 values in the final handoff.
Historical bbcbb rows may enter a matrix only through the explicit
`FAST64_ZERO_ACCESS_CORE_REPAIR_IDENTITY_MAP.md` classification and retain
their literal provenance; no accepted triplet may mix Core/runtime identities.

## Repaired-Core physical precompute wave

### Core-95 NN IO/OO primary acquisition (2026-09-11)

The exact 24-cell IO/OO coverage audit excludes every `FAST64_SENS_*`
sensitivity row.  At dispatch it found 18 strict-terminal reuse candidates,
two live GESUMMV/Core-95 rows, two 2DConvolution cells blocked on the final
Core-41 triplet identity, and only NN/IO plus NN/OO genuinely missing.  A
fresh resource audit admitted the two missing rows without touching any live
simulator.  Both used Core `95ccdb7a...`, runtime `462d105c...cc4dbc9`, A1,
scientific Framework `037f008b...`, their frozen FAST64 IO/OO configs, exact
NN payload, and immutable runner `bf9a84c8...` in fresh namespaces.

| row | attempt UUID | terminal / strict result | compact evidence | closure |
| --- | --- | --- | --- | --- |
| NN / PAPER_IO | `d1c7df08-769e-4b68-ba61-359d3902f86f` | exit 0 at `2026-09-11T02:20:34Z`; strict PASS | `generated/fast64_4_primary_core95_v1/fast64_4_primary_nn_io_core95ccdb7a_a1_v1.json` | 6,095 cycles / 1,284,872 instructions; lower credit `2673/2673`, IO create/issue/response `2673/2673/2673`, dependency closed/count `5346/5346`, final lower/inflight/PIB `0/0/0`, cap-full `0` |
| NN / PAPER_OO | `f7dc6dbb-1951-49cc-a865-22f07bb7de4f` | exit 0 at `2026-09-11T02:20:34Z`; strict PASS | `generated/fast64_4_primary_core95_v1/fast64_4_primary_nn_oo_core95ccdb7a_a1_v1.json` | 6,105 cycles / 1,284,872 instructions; lower credit `2673/2673`, OO create/issue/response `2673/2673/2673`, dependency closed/count `5346/5346`, final lower/inflight/PIB/active-refs `0/0/0/0`, cap-full `0` |

The coverage state is now 21 strict-terminal candidates, one live Core-95
GESUMMV/IO row, and two cells blocked on the final 2DConvolution Core-41
identity.  These rows are
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`; they neither form an accepted
triplet nor advance FAST64.4, and no GM or primary-stage claim is made.

### Future-only 36-cell collector-registry preparation

`prepare_fast64_4_primary_registry_v1.py` is a future-only, fail-closed bridge
from the final Core-41 FAST64.3 Base registry plus the 24-cell IO/OO coverage
table to the existing 36-cell primary collector.  It has no simulator or
controller authority, refuses a live/blocked/nonterminal coverage cell,
requires every compact JSON to be present and schema-valid, and refuses any
nonzero `DTC_L1_lower_cap_full_events` until an explicit source resolution
exists.  It writes one new immutable registry only after all 36 inputs are
strict-terminal; it neither rewrites source registries nor publishes a PASS
marker.  The synthetic 36-cell positive regression and a nonzero-cap negative
regression both pass.  Its current production dry run correctly fails at the
absent final Core-41 Base registry, so it cannot prematurely compose a
primary-matrix candidate.

### Core-41 2DConvolution IO/OO future path (prepared, not dispatched)

The historical bbcbb 2DConvolution IO/OO rows remain literal precompute only
and may not be paired with the live Core-41 Base replacement.  Future-only
`dispatch_fast64_4_2d_core41_v1.sh` binds both successor modes to Core
`41d740e8...`, runtime `6e72d366...`, A1, the frozen 2D payload and exact
FAST64 IO/OO configs.  Before even a dry run can pass, it requires both the
strict Core-41 Base compact JSON and its structural companion, verifies that
the companion binds that exact Base summary and terminal lower/PIB drain, and
refuses any pre-existing namespace.  Its current pre-Base check fails closed;
no 2DConvolution IO/OO simulator has been launched by this path.

### 2026-09-11 primary-acquisition coverage and capacity audit

The current exact 24-cell IO/OO audit is: 21
`STRICT_TERMINAL_REUSE_CANDIDATE`, one Core-95 GESUMMV/IO cell
`LIVE_NONTERMINAL`, and two 2DConvolution cells
`BLOCKED_ON_FINAL_CORE_IDENTITY`.  There is no
`MISSING_READY_TO_DISPATCH` non-2DConvolution cell, so no duplicate primary
row was launched merely to consume available capacity.  Every
`FAST64_SENS_*` sensitivity row remains excluded from this audit.

Two fresh, read-only three-window admission observations used the FAST64-only
RSS distribution, cgroup limits, memory PSI/OOM, CFS throttling, cgroup I/O,
swap-out, and output capacity.  At 13 live FAST64 leaves, both the total-16
(three additional workers) and total-20 (seven additional workers) scenarios
passed: p95 RSS was 3,443,523,584 B, `MemAvailable` was respectively
91,457,060,864 B and 92,874,694,656 B, cgroup headroom exceeded 214 GB,
projected post-admission `MemAvailable` remained 80,881,209,344 B and
68,747,837,440 B, memory PSI/OOM/CFS throttling were zero, and the total-20
window had zero swap-out.  Output free space was about 89.7 GiB.  The first
total-16 window saw a one-sample, 105-page swap-out transient but no major
fault, PSI, OOM, or sustained swap activity; it is recorded as an observation,
not used to launch a duplicate.  The exact temporary audit records are
`/tmp/fast64-r4-admission-16-20260911T024945Z.tsv` and
`/tmp/fast64-r4-admission-20-20260911T025043Z.tsv` on the execution host.

Thus capacity is ready for the already-authorized priority order—first the
strict-gated Core-41 2DConvolution IO/OO successors, then any genuinely
missing primary row—but it does not override the no-duplicate and
common-triplet-identity rules.

To avoid an unattended gap at that precise transition, the future-only
`auto_dispatch_fast64_4_2d_core41_v1.sh` controller is prepared and statically
regressed.  It pins the SHA-256 of the Core-41 dispatcher, generic strict
collector, and resource-audit helper; requires the exact strict Base JSON plus
structural companion; takes a new two-worker admission audit; and only then
dispatches fresh IO/OO namespaces on distinct eligible CPUs and starts their
strict terminal monitors.  A helper-byte mismatch, missing Base artifact,
unsafe audit, pre-existing namespace, or collector output causes no launch.
The current `--once` regression reached only
`FAST64_4_2D_CORE41_WAIT_BASE_STRICT_GATE` and proved that it cannot
prematurely dispatch either successor while Base remains live.

The first post-transition wave is active under
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`: Btree Base/IO/OO, MRI-Q
Base/IO/OO, ATAX/OO and GESUMMV/OO.  Each has a fresh immutable-v2 START
receipt in `/workspace/fast64-repaired-ramp/`, Core `95ccdb7a...`, runtime
`462d105c...cc4dbc9`, A1 observer, frozen Framework snapshot/payload identity,
and a distinct physical CPU.  These rows are not formal FAST64.4 results until
their natural terminal, strict collector, stage-3 and triplet gates pass.

### Terminal precompute observations (not matrix acceptance)

| row | compact evidence | natural/strict evidence | terminal accounting | status |
| --- | --- | --- | --- | --- |
| Btree / PAPER_IO | `generated/fast64_repaired_ramp_v1/fast64_btree_io_core95ccdb7a_a1_r1.json` | immutable attempt `002abb01-33c5-469a-b593-1cebc125d4aa`; terminal receipt `2026-09-10T10:36:28Z`, exit `0`; collector PASS | `244,231` cycles / `444,467,849` instructions; lower acquired/released and IO create/issue/response `507,779/507,779`; dependency closed/count `2,388,513/2,388,513`; final PIB/inflight/lower `0/0/0`; cap-full and lower-create-queue-full `0` | `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` |
| Btree / PAPER_OO | `generated/fast64_repaired_ramp_v1/fast64_btree_oo_core95ccdb7a_a1_r1.json` | immutable attempt `49062c94-3354-4b33-b8b8-03e885335095`; terminal receipt `2026-09-10T10:30:28Z`, exit `0`; collector PASS | `172,795` cycles / `444,467,849` instructions; lower acquired/released and OO create/issue/response `502,450/502,450`; dependency closed/count `2,388,513/2,388,513`; final PIB/inflight/lower `0/0/0`; cap-full and lower-create-queue-full `0` | `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` |
| GESUMMV / PAPER_OO | `generated/fast64_repaired_ramp_v1/fast64_gesummv_oo_core95ccdb7a_a1_r1.json` | immutable attempt `023b0b17-4d77-490a-ae14-fb42daddc17e`; terminal receipt `2026-09-11T03:50:40Z`, exit `0`; collector PASS | `143,059,605` cycles / `190,918,656` instructions; lower acquired/released and OO create/issue/response `34,598,098/34,598,098`; dependency closed/count `35,651,712/35,651,712`; final PIB/inflight/lower/active-refs `0/0/0/0`; cap-full `0` | `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` |
| MRI-Q / PAPER_BASE | `generated/fast64_repaired_ramp_v1/fast64_mriq_base_core95ccdb7a_a1_r1.json` | immutable attempt `53d3653f-1b85-4bd1-9d41-1c8fd0783812`; terminal receipt `2026-09-10T10:37:58Z`, exit `0`; collector PASS | `366,667` cycles / `1,411,757,056` instructions; PIB admit/retire `21,792/21,792`; lower acquired/released `62,208/62,208`; final PIB/lower `0/0`; cap-full `0` | `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` |
| MRI-Q / PAPER_IO | `generated/fast64_repaired_ramp_v1/fast64_mriq_io_core95ccdb7a_a1_r1.json` | immutable attempt `add9ada3-c014-47a3-b664-b3b4678e2a5a`; terminal receipt `2026-09-10T10:34:27Z`, exit `0`; collector PASS | `360,536` cycles / `1,411,757,056` instructions; lower acquired/released and IO create/issue/response `15,517/15,517`; dependency closed/count `15,552/15,552`; final PIB/inflight/lower `0/0/0`; cap-full and lower-create-queue-full `0` | `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` |
| MRI-Q / PAPER_OO | `generated/fast64_repaired_ramp_v1/fast64_mriq_oo_core95ccdb7a_a1_r1.json` | immutable attempt `e32fff64-f847-4c79-9c3d-94c41622dd54`; terminal receipt `2026-09-10T10:37:45Z`, exit `0`; collector PASS | `361,415` cycles / `1,411,757,056` instructions; lower acquired/released and OO create/issue/response `15,516/15,516`; dependency closed/count `15,552/15,552`; final PIB/inflight/lower `0/0/0`; cap-full and lower-create-queue-full `0` | `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` |

The Btree Base peer has now naturally exited `0`, strict-collected, and joins
the Btree IO/OO rows in the common repaired-Core triplet
`generated/fast64_repaired_ramp_v1/FAST64_BTREE_REPAIRED_CORE_TRIPLET_V1.json`.
The companion `FAST64_3_BTREE_BASE_STRUCTURAL_METRICS_V1.json` records Base
lower acquire/release `1,458,407/1,458,407`, cacheline-reservation events
`590`, Tag-bank conflicts `1,751,328`, MSHR-entry-full `1,622,927`, and zero
MSHR-merge/downstream-full.  These terminal rows remain repaired-Core physical
precompute evidence only: they do not populate accepted FAST64.4 matrix cells
before FAST64.3 PASS.

### Recovered old-Core terminal evidence

The original terminal receipts for 2DConvolution/IO+OO, DWT2D/IO+OO,
Gaussian/IO+OO, and LUD/IO+OO have now been strict-collected into distinct
recovery evidence files. The original monitor bytes, raw output, and locks
remain preserved. The 2DConvolution/OO terminal used the future-only v3
observer because its immutable runner lacks an optional launcher-log path;
this is a host-closeout repair only. This is a
host-closeout recovery only: every record retains literal bbcbb/runtime/A1/
frozen-Framework provenance and
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`.  Refer to
`FAST64_PRECOMPUTED_CLOSEOUT_RECOVERY_V2.md`; no row is promoted into this
matrix before FAST64.3 PASS and the common-identity triplet audit.

After the fresh V2 post-MRI-Q admission passed two additional workers at
`2026-09-10T10:42:54Z` (zero sampled swap-out/major-fault/PSI/OOM/throttling,
`42,749,964,288` bytes MemAvailable and `217,963,790,336` bytes cgroup memory
headroom), the following independent repaired-Core rows were dispatched in new
immutable namespaces.  They are physical precompute only and each has a
separate read-only v2 terminal collector:

| row | CPU | immutable attempt | status |
| --- | ---: | --- | --- |
| GESUMMV / PAPER_IO | 16 | `10440267-d296-4a36-82df-38e6cf8f5ec5` | `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` (active) |
| ATAX / PAPER_BASE | 23 | `13e5b9ee-80ba-4f23-b9be-d927766c2bd8` | `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` (active) |

Their manifests bind repaired Core `95ccdb7a...`, runtime
`462d105c...cc4dbc9`, A1 observer, Framework scientific snapshot
`037f008b...`, frozen config/payload hashes, and immutable runner
`bf9a84c8...`.  Neither replaces, relabels, or interrupts its literal bbcbb
predecessor.

### Old-Core continuation deauthorization guard (2026-09-10)

The already-live historical `continue_fast64_4_precompute_v1.sh` controller is
preserved unchanged while it waits for its old-Core ATAX/IO predecessor.  Its
hard-coded bbcbb/runtime tuple is superseded for *new* long acquisition by the
repaired-Core authority above.  To prevent it from dispatching its first
old-Core successor without signalling, editing, or otherwise perturbing that
controller or any simulator, the otherwise-unused first legacy namespace
`/workspace/fast64-runs/fast64_4_atax_oo_cap8192_a1_v3` was atomically reserved
as an empty directory before the controller's prerequisite exists.  On a later
attempt the controller's own pre-existing namespace-absence check will emit
`REFUSE_NAMESPACE` and exit before a new simulator is launched.

This guard contains no receipt, configuration, payload, log, or result and is
not a failed experiment or a matrix row.  It preserves the live old ATAX/IO
process and its read-only closeout path as literal historical evidence.  Any
subsequent replacement must use a fresh repaired-Core immutable namespace and
may not reuse this legacy name.

### Current future-wave capacity calibration (2026-09-10)

The future-only V3 admission auditor is independent of all live execution and
closeout bytes.  It treats a single positive swap-out sample followed by clean
samples as `TRANSIENT_SWAP_ACTIVITY`, but rejects repeated swap-out, any memory
PSI/OOM/major-fault growth, CFS throttling, insufficient output space, or a
projected `MemAvailable` value below a declared 16-GiB reserve.

At `2026-09-10T12:18:47Z`, 13 FAST64 executable leaves used 31.1 GiB total
RSS (p50/p95/max 2.31/4.80/4.80 GiB).  The paired three-window audits retained
at `/tmp/fast64-resource-audit-v3-20260910T121815Z-target{16,20}.tsv` saw
one 65-page swap-out sample and then two zero samples, no PSI/OOM/major faults
or CFS throttling, about 39.2 GiB `MemAvailable`, 208 GiB cgroup headroom, and
111 GiB output free.  The 16-worker target (three additions) passes with a
projected 25.7 GiB `MemAvailable`; the 20-worker target fails the reserve with
only 6.5 GiB projected.  Thus the current `N_safe` is 16, with a maximum of
three new workers before fresh admission evidence is required.

No duplicate row was dispatched simply to consume this capacity.  The final
FAST64.3 Base acquisition (2DConvolution) is already live, Btree/MRI-Q have
repaired-Core terminal candidates awaiting the stage-3 reconciliation, and
the remaining physical FAST64.4 rows either have live immutable attempts or
strict terminal candidates.  The next repaired-Core dispatch must remain a
new, missing, identity-compatible row after another fresh audit; it must not
reuse a live/old namespace or defeat the old-Core guard above.

## 2. Fixed 36-row matrix

Fill exactly one accepted Base/IO/OO row per workload. Base rows must be reused
from accepted FAST64.3 unless a documented later invalidation requires a fresh
replacement.

| workload | Base accepted row | IO accepted row | OO accepted row | triplet identity PASS | instruction identity PASS | drain PASS | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ATAX | TBD | TBD | TBD | [ ] | [ ] | [ ] | PENDING |
| BICG | TBD | TBD | TBD | [ ] | [ ] | [ ] | PENDING |
| GESUMMV | TBD | TBD | TBD | [ ] | [ ] | [ ] | PENDING |
| GEMM | TBD | TBD | TBD | [ ] | [ ] | [ ] | PENDING |
| 2DConvolution | TBD | TBD | TBD | [ ] | [ ] | [ ] | PENDING |
| Btree | TBD | TBD | TBD | [ ] | [ ] | [ ] | PENDING |
| DWT2D | TBD | TBD | TBD | [ ] | [ ] | [ ] | PENDING |
| Gaussian | TBD | TBD | TBD | [ ] | [ ] | [ ] | PENDING |
| Hotspot1 | TBD | TBD | TBD | [ ] | [ ] | [ ] | PENDING |
| LUD | TBD | TBD | TBD | [ ] | [ ] | [ ] | PENDING |
| NN | TBD | TBD | TBD | [ ] | [ ] | [ ] | PENDING |
| MRI-Q | TBD | TBD | TBD | [ ] | [ ] | [ ] | PENDING |

No workload or mode may be dropped for negative/zero speedup or execution cost.

## 3. Triplet identity audit

Create `generated/fast64_4_triplets.tsv` and prove per workload:

- exact common payload SHA/order across Base/IO/OO;
- common Core/runtime/A1/scientific Framework identity;
- same unrelated platform settings;
- only documented Base/IO/OO mechanism-required config differences;
- dynamic instructions and source-domain operation identity equal where the
  model contract requires equality;
- observer identity common across the triplet.

Any unexplained instruction/source-operation difference is a correctness issue,
not a performance result.

## 4. Mode-specific correctness and drain

Create `generated/fast64_4_accounting.tsv` with at least:

| workload | mode | lower created/acquired | issued | response/released | dependency create | dependency complete | final PIB | final inflight | final lower | final OO active refs | accepted |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| TBD | | | | | | | | | | | |

Every accepted row must naturally exit zero, strict-parse, have one accepted
execution epoch, preserve required conservation, and drain all mode-specific
terminal state.

Collect `DTC_L1_lower_cap_full_events` for every primary row. Any nonzero value
must be source-classified and resolved before accepting non-binding-cap
performance interpretation.

## 5. Primary performance table

Create `generated/fast64_4_speedup.tsv`:

| workload | Base cycles | IO cycles | OO cycles | speedup_IO | speedup_OO |
| --- | ---: | ---: | ---: | ---: | ---: |
| ATAX | | | | | |
| BICG | | | | | |
| GESUMMV | | | | | |
| GEMM | | | | | |
| 2DConvolution | | | | | |
| Btree | | | | | |
| DWT2D | | | | | |
| Gaussian | | | | | |
| Hotspot1 | | | | | |
| LUD | | | | | |
| NN | | | | | |
| MRI-Q | | | | | |
| `GM-FAST12` | n/a | n/a | n/a | TBD | TBD |

Definitions:

- `speedup_IO = cycles_BASE / cycles_IO`
- `speedup_OO = cycles_BASE / cycles_OO`
- each GM is the geometric mean over exactly the 12 frozen FAST12 members.

No workload may be excluded from the GM because it is weak, zero, or negative.

## 6. Primary matrix registry

Create `generated/fast64_4_primary_matrix.tsv` with all 36 authoritative rows
and at least:

`workload, mode, accepted_namespace, origin, status, cycles, instructions, config_sha256, payload_sha256, core_sha, runtime_sha256, observer_sha256, scientific_framework_sha, evidence_path, evidence_sha256, raw_run_ref`.

`origin` should distinguish accepted FAST64.3 Base reuse, promoted precompute,
and fresh FAST64.4 acquisition.

## 7. Retry/obsolete map

Create `generated/fast64_4_retry_obsolete_map.tsv` for every non-authoritative
attempt.

| workload | mode | obsolete/failed row | reason | resolution ID | authoritative replacement |
| --- | --- | --- | --- | --- | --- |
| ATAX | IO | `fast64_4_atax_io_cap8192_a1_v2` | Relative FAST64_IO config path was resolved after immutable runner changed to run directory; simulator exited `1` before an execution epoch. | F64-IO-001 | `fast64_4_atax_io_cap8192_a1_v3` active, using identical frozen config bytes by absolute path. |

`F64-IO-001` is an execution-path-only repair. The v2 receipt, stdout,
stderr, and resource record remain externally preserved; it is not a result
and must never enter a speedup, accounting, or matrix aggregate.

Do not overwrite or silently discard failed attempts. Do not restart the full
matrix for a row-local issue.

## 8. Identity manifest and raw-log index

Create `generated/fast64_4_identity_manifest.tsv` containing compact evidence
paths + SHA-256 for all 36 rows and all aggregate/registry outputs.

Raw run outputs remain external and are referenced by a compact raw-log index;
do not commit raw multi-GB files.

## 9. Scheduling/resource calibration

Record the actual worker-pool policy and all material changes:

- cgroup CPU quota/cpuset;
- topology-aware placement;
- N_safe/ramp/refill history;
- p95/max RSS and memory headroom;
- swap/OOM/PSI/iowait;
- output-space headroom;
- aggregate useful simulated throughput;
- any reason for reducing/increasing concurrency.

Scheduling differences are not scientific identity differences.

## 10. FAST64.4 HARD acceptance checklist

Do not change `Status` to PASS until every applicable item is checked.

- [ ] FAST64.1 PASS verified.
- [ ] FAST64.2 PASS verified.
- [ ] FAST64.3 PASS verified.
- [ ] Exactly 36 primary rows accepted: 12 Base + 12 IO + 12 OO.
- [ ] All 12 Base rows are exact accepted FAST64.3 rows unless explicitly invalidated/replaced.
- [ ] Every row naturally exited zero.
- [ ] Every row strict-parsed under its recorded versioned validation contract.
- [ ] Every row consumed exact frozen payload identity/order.
- [ ] Every triplet has common Core/runtime/A1/scientific Framework identity.
- [ ] Every triplet differs only in documented mechanism-required mode parameters.
- [ ] Every triplet passes dynamic-instruction/source-operation identity where required.
- [ ] Every row has no assertion/fatal/actual deadlock/output mismatch/unresolved controller anomaly.
- [ ] IO/OO lower create/issue/response accounting conserved.
- [ ] dependency create/complete accounting conserved where applicable.
- [ ] final PIB/inflight/lower states drain to zero.
- [ ] final OO active-ref/reclaim state drains to zero where applicable.
- [ ] all cap-full observations reviewed; no unresolved binding-cap condition remains.
- [ ] per-workload IO/OO speedups computed from accepted rows.
- [ ] `GM-FAST12_IO` contains exactly 12 frozen members.
- [ ] `GM-FAST12_OO` contains exactly 12 frozen members.
- [ ] negative/zero results retained; no per-workload resource tuning performed.
- [ ] primary matrix/triplet/speedup/accounting/identity outputs reconcile.
- [ ] retry/obsolete map complete.
- [ ] raw-log index complete.
- [ ] no unresolved implementation/model correctness issue remains.
- [ ] `git diff --check` passes and only intended compact evidence is staged.

PASS state, only after all checks:

`FAST64_4_PRIMARY_PASS`

## 11. Primary findings permitted at this stage

FAST64.4 may report only primary performance facts directly supported by the
accepted matrix:

- per-workload Base/IO/OO cycles;
- IO/OO speedups;
- GM-FAST12;
- correctness/drain and primary row validity;
- descriptive outliers.

Full causal explanations belong to FAST64.5 and must not be asserted before
its cross-metric analysis is complete.

## 12. Exact next executable action

After `FAST64_4_PRIMARY_PASS`:

- immediately enter FAST64.5 causal analysis;
- reuse already-collected parser-supported structural/live-miss/traffic fields;
- generate required FAST64.5 compact datasets/plots;
- do not request researcher approval for the normal transition.

## 13. Do-not-redo list

At closeout list every accepted Base/IO/OO row that is frozen against rerun
unless a specific later correctness invalidation is documented.
