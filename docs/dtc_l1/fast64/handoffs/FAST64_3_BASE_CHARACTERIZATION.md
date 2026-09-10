# FAST64.3 — Base Characterization Handoff

Status: **ACTIVE — 5/12 Base rows promoted; 7/12 fresh immutable Base rows pending resource-safe acquisition**

This file is the authoritative FAST64.3 stage handoff and is intentionally
created before execution so Goal mode can fill it in rather than invent a new
closeout format.

Detailed execution/promotion authority:
`../FAST64_3_4_EXECUTION_CONTRACT.md`.

## 1. Stage anchors

Previous required PASS anchors:

- FAST64.1: `FAST64_1_PLATFORM_PASS`
- FAST64.2: `FAST64_2_REPAIR_PASS`

Formal identities to record at closeout:

| item | required identity |
| --- | --- |
| mechanism behavior anchor | `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9` |
| formal instrumented Core | `bbcbb5e7565417102087bc80b14c349b4e568c05` |
| runtime SHA-256 | `6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041` |
| A1 observer SHA-256 | `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e` |
| scientific/config Framework snapshot | `037f008b330eb230353b60edf126d6be9f45afdc` |
| Base config | record exact current `FAST64_BASE.config` SHA-256 |
| payload authority | `FAST64_WORKLOAD_MANIFEST.tsv` + `generated/FAST64_PAYLOAD_MANIFEST.tsv` |

Current review/controller HEAD is recorded separately and is not substituted
for the scientific execution snapshot.

## 2. Fixed FAST12 Base roster

Fill one authoritative accepted row for every member. Exact-identity valid
precomputes should be promoted instead of rerun after all entry gates pass.

| workload | accepted namespace/evidence | origin (`fresh`/`promoted`) | natural exit | strict parse | metric complete | cap-full=0 or resolution | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ATAX | `generated/fast64_3_atax_base_alias_v3/` | promoted | [x] | [x] | [x] | [x] | ACCEPTED |
| BICG | `generated/qualification_r2_full_wave_alias_v2/` + `generated/fast64_3_bicg_base_structural_v1/` | promoted | [x] | [x] | [x] | [x] | ACCEPTED |
| GESUMMV | `generated/fast64_3_gesummv_base_alias_v3/` | promoted | [x] | [x] | [x] | [x] | ACCEPTED |
| GEMM | `generated/fast64_3_gemm_base_alias_v4/` | promoted | [x] | [x] | [x] | [x] | ACCEPTED |
| 2DConvolution | TBD | TBD | [ ] | [ ] | [ ] | [ ] | PENDING |
| Btree | TBD | TBD | [ ] | [ ] | [ ] | [ ] | PENDING |
| DWT2D | `generated/fast64_3_dwt2d_base_alias_v3/` | promoted | [x] | [x] | [x] | [x] | ACCEPTED |
| Gaussian | TBD | TBD | [ ] | [ ] | [ ] | [ ] | PENDING |
| Hotspot1 | TBD | TBD | [ ] | [ ] | [ ] | [ ] | PENDING |
| LUD | TBD | TBD | [ ] | [ ] | [ ] | [ ] | PENDING |
| NN | TBD | TBD | [ ] | [ ] | [ ] | [ ] | PENDING |
| MRI-Q | TBD | TBD | [ ] | [ ] | [ ] | [ ] | PENDING |

No row may be dropped for pressure level, runtime, or later benefit.

## 3. Promotion/reuse audit

`generated/fast64_3_base_promotion_audit_v1.tsv` is the authoritative
row-level audit. It verifies all five promoted rows against the frozen payload
manifest and formal Base identity, then verifies natural immutable terminal,
strict accounting/drain, host fields, required structural companion, and
`DTC_L1_lower_cap_full_events=0`. The remaining seven rows are explicitly
listed as `MISSING`; NN is deliberately reacquired because its historical
precompute did not use the current frozen Framework execution snapshot.

Before launching a Base row, document whether exact-identity evidence already
exists. At closeout list every promoted row and prove:

- workload/payload SHA identity;
- Base config SHA identity;
- Core/runtime/A1/scientific Framework identity;
- natural exit zero;
- one accepted execution epoch;
- strict accounting/drain;
- FAST64.3 metric completeness.

Promotion candidates may include formal R2 BICG Base and already strict-valid
Base precomputes. Names alone are not sufficient evidence.

## 4. Required structural-pressure table

Create `generated/fast64_3_structural_pressure.tsv` with at least these columns
or explicit source-backed unsupported classifications:

| workload | PIB pressure | cacheline allocation fail | Tag-bank conflict | MSHR entry full | MSHR merge full | miss/lower/downstream full |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TBD | | | | | | |

Tag-bank arbitration must remain separate from true Tag/cacheline allocation
failure and lower/miss-queue pressure.

## 5. Required live-miss/lower table

Create `generated/fast64_3_live_misses.tsv` with the common supported lifecycle
fields:

| workload | lower/live-miss create/acquire | complete/release | avg | peak | final outstanding | cap-full events |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TBD | | | | | | |

Every row requires balanced terminal lifecycle/accounting. A nonzero
`DTC_L1_lower_cap_full_events` must be explicitly resolved before performance
interpretation; it cannot be ignored.

## 6. Required Base performance and host-planning table

Create `generated/fast64_3_base_rows.tsv` and
`generated/fast64_3_host_runtime.tsv` including:

- cycles and dynamic instructions;
- source-domain operations when available;
- parser-supported cache/traffic fields;
- wall/user/sys time;
- simulated cycles/s and instructions/s when available;
- peak RSS;
- raw-log external reference.

## 7. Identity/evidence manifest

Create `generated/fast64_3_identity_manifest.tsv` containing at minimum:

`workload, accepted_row, classification, compact_evidence_path, evidence_sha256, config_sha256, payload_sha256, core_sha, runtime_sha256, observer_sha256, scientific_framework_sha, raw_run_ref`.

Do not commit raw multi-GB outputs.

## 8. Issues and retry/obsolete map

Record every issue that affected scientific validity or execution and its
resolution. Row-local problems must be repaired/rerun without restarting valid
independent rows.

| issue/resolution ID | affected row(s) | classification | action | authoritative replacement |
| --- | --- | --- | --- | --- |
| TBD | | | | |

## 9. Resource calibration

Record the worker-pool calibration actually used:

- cgroup CPU quota/cpuset;
- physical-core placement policy;
- N_safe and adjustment history;
- p95/max RSS;
- MemAvailable and cgroup memory headroom;
- swap/OOM/PSI/iowait observations;
- output-space headroom;
- aggregate useful simulator throughput when available.

Efficiency decisions are not scientific result identities.

## 10. FAST64.3 HARD acceptance checklist

Do not change `Status` to PASS until every applicable item is checked.

- [ ] FAST64.1 PASS anchor verified.
- [ ] FAST64.2 PASS anchor verified.
- [ ] Exactly 12 frozen FAST12 Base members accepted.
- [ ] Every row naturally exited zero.
- [ ] Every row strict-parsed under the recorded versioned parser/validator contract.
- [ ] Every row consumed its exact frozen payload identity/order.
- [ ] Every row has complete terminal lower/PIB/accounting drain.
- [ ] No assertion/fatal/actual deadlock/output mismatch/unresolved controller anomaly remains.
- [ ] Required performance fields complete for all 12.
- [ ] PIB pressure complete for all 12.
- [ ] true Tag/cacheline allocation pressure complete for all 12.
- [ ] Tag-bank arbitration kept separate for all 12.
- [ ] MSHR entry/merge pressure complete or explicitly unsupported with source proof.
- [ ] lower/miss-queue/downstream pressure complete for all 12.
- [ ] live-miss/lower lifecycle complete for all 12.
- [ ] supported cache/traffic fields recorded.
- [ ] host runtime/RSS planning fields recorded.
- [ ] all cap-full observations reviewed; no unresolved binding-cap condition remains.
- [ ] no workload removed or retuned based on pressure/performance.
- [ ] required compact tables/manifests/raw-log index exist and reconcile.
- [ ] retry/obsolete map is complete.
- [ ] `git diff --check` passes and only intended compact files are staged.

PASS state, only after all checks:

`FAST64_3_BASE_PASS`

## 11. Mechanism/scientific finding

At closeout summarize only what Base characterization directly supports:
which conventional structures experience pressure, which workloads are
low-pressure, and what runtime/metric completeness means for FAST64.4/5.
Do not infer IO/OO benefit from Base-only evidence.

## 12. Exact next executable action

After `FAST64_3_BASE_PASS`:

- promote already-acquired exact-identity IO/OO rows if allowed;
- launch all remaining FAST64.4 IO/OO rows through a measured dynamic worker
  pool;
- continue automatically without researcher approval for the normal stage
  transition.

## 13. Do-not-redo list

At closeout list accepted/promoted rows that must not be rerun without a
specific invalidation reason.
