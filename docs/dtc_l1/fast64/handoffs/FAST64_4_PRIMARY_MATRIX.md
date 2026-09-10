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
| MRI-Q / PAPER_IO | `generated/fast64_repaired_ramp_v1/fast64_mriq_io_core95ccdb7a_a1_r1.json` | immutable attempt `add9ada3-c014-47a3-b664-b3b4678e2a5a`; terminal receipt `2026-09-10T10:34:27Z`, exit `0`; collector PASS | `360,536` cycles / `1,411,757,056` instructions; lower acquired/released and IO create/issue/response `15,517/15,517`; dependency closed/count `15,552/15,552`; final PIB/inflight/lower `0/0/0`; cap-full and lower-create-queue-full `0` | `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` |

The Btree Base and MRI-Q Base/OO peers remain live.  These terminal rows
are retained as repaired-Core physical precompute evidence only: they do not
populate accepted FAST64.4 matrix cells or permit mixed-identity triplets.

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
