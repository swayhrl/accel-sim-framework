# FAST64.3 — Base Characterization Handoff

Status: **ACTIVE — 11/12 non-2D Base registry rows pass the exact final matrix
validator; historical 2DConvolution/Base and the Core-41 formal replacement
are invalid. The immutable dc6062 transition observation is terminal and
strictly retained as NONFORMAL_DIAGNOSTIC_NOT_RESULT. Its source-backed
sector-MSHR tag-identity repair is built and unit-regressed but awaits a fresh
12th formal Base row; no FAST64.3 promotion is made.**

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
| historical telemetry Core/runtime | `bbcbb5e7565417102087bc80b14c349b4e568c05` / `6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041` (literal historical evidence only) |
| current formal repaired Core/runtime | `95ccdb7a056f2d53f740d90869785cac6d4ee0f5` / `462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9` (new acquisition) |
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
| GESUMMV | historical `generated/fast64_3_gesummv_base_alias_v3/`; fresh Core95 candidate `generated/fast64_repaired_ramp2_v1/fast64_gesummv_base_core95ccdb7a_a1_r1.json` + `FAST64_3_GESUMMV_REPAIRED_BASE_STRUCTURAL_METRICS_V1.json` | promoted; fresh repaired-Core candidate | [x] | [x] | [x] | [x] | ACCEPTED; CORE95_CANDIDATE_PENDING_FINAL_REGISTRY |
| GEMM | `generated/fast64_3_gemm_base_alias_v4/` | promoted | [x] | [x] | [x] | [x] | ACCEPTED |
| 2DConvolution | historical `fast64-runs/fast64_3_2DConvolution_base_cap8192_a1_v2` and the Core-41 replacement `/workspace/fast64-stage3-repair/fast64_3_2DConvolution_base_core41d740e8_a1_v1` are preserved invalid attempts; dc6062 terminal observation evidence is nonformal | Core `6587238c...` tag-identity repair built in isolated Release mode; common/generation/completion unit regressions pass; fresh formal Base remains pending | [ ] | [ ] | [ ] | [ ] | SOURCE_CLASSIFIED_FORMAL_REPLACEMENT_PENDING |
| Btree | `generated/fast64_repaired_ramp_v1/fast64_btree_base_core95ccdb7a_a1_r1.json` + `FAST64_3_BTREE_BASE_STRUCTURAL_METRICS_V1.json` + `FAST64_BTREE_REPAIRED_CORE_TRIPLET_V1.json` | fresh repaired-Core immutable v2 | [x] | [x] | [x] | [x] | STRICT_VALID_PENDING_STAGE_ACCEPTANCE |
| DWT2D | `generated/fast64_3_dwt2d_base_alias_v3/` | promoted | [x] | [x] | [x] | [x] | ACCEPTED |
| Gaussian | `generated/fast64_3_dynamic_base_v1/fast64_3_Gaussian_base_cap8192_a1_v2.json` + `FAST64_3_GAUSSIAN_BASE_{DYNAMIC,STRUCTURAL_METRICS}_V1` | fresh immutable v2 | [x] | [x] | [x] | [x] | STRICT_VALID_PENDING_STAGE_ACCEPTANCE |
| Hotspot1 | `generated/fast64_repaired_core_qual_v1/fast64_hotspot1_base_core95ccdb7a_a1_v1.json` + `FAST64_3_HOTSPOT1_REPAIRED_BASE_STRUCTURAL_METRICS_V1.json` + `FAST64_HOTSPOT1_REPAIRED_CORE_TRIPLET_V1.json` | fresh repaired-Core immutable v2 | [x] | [x] | [x] | [x] | STRICT_VALID_PENDING_STAGE_ACCEPTANCE |
| LUD | `generated/fast64_3_dynamic_base_v1/fast64_3_LUD_base_cap8192_a1_v2.json` + `FAST64_3_LUD_BASE_{DYNAMIC,STRUCTURAL_METRICS}_V1` | fresh immutable v2 | [x] | [x] | [x] | [x] | STRICT_VALID_PENDING_STAGE_ACCEPTANCE |
| NN | `generated/fast64_3_nn_core95_v1/fast64_3_nn_base_core95ccdb7a_a1_v1.json` + `FAST64_3_NN_BASE_STRUCTURAL_METRICS_V1.json`; literal bbcbb Base remains historical anchor only | fresh Core95 immutable v2 | [x] | [x] | [x] | [x] | STRICT_VALID_PENDING_STAGE_ACCEPTANCE |
| MRI-Q | `generated/fast64_repaired_ramp_v1/fast64_mriq_base_core95ccdb7a_a1_r1.json` + `FAST64_3_MRI_Q_REPAIRED_BASE_STRUCTURAL_METRICS_V1.json` + `FAST64_MRIQ_REPAIRED_CORE_TRIPLET_V1.json` | fresh repaired-Core immutable v2; historical bbcbb compact retained as mapped anchor | [x] | [x] | [x] | [x] | STRICT_VALID_PENDING_STAGE_ACCEPTANCE |

No row may be dropped for pressure level, runtime, or later benefit.

## 3. Promotion/reuse audit

`generated/fast64_3_base_promotion_audit_v1.tsv` is the authoritative
row-level audit. It verifies all five promoted rows against the frozen payload
manifest and formal Base identity, then verifies natural immutable terminal,
strict accounting/drain, host fields, required structural companion, and
`DTC_L1_lower_cap_full_events=0`. The earlier NN dynamic Base compact result
is an immutable literal bbcbb row (not a Core95 row as a stale handoff sentence
previously implied). Its source-inert Base evidence is preserved, but it cannot
form a common-identity triplet with the strict Core95 NN IO/OO rows. Fresh
Core95 `fast64_3_nn_base_core95ccdb7a_a1_v1` naturally exited `0`, strict
validated, and records `6,985` cycles / `1,284,872` instructions, lower
`10,691/10,691`, PIB `4,011/4,011`, final lower/PIB `0/0`, cap-full `0`, and
the required structural companion. It is now the NN candidate; the literal
bbcbb Base remains historical-only. The remaining rows retain their existing
active/queued/reuse classification as listed above.

The fresh Core95 GESUMMV/Base candidate naturally exited `0` at
`2026-09-11T08:11:22Z` and strict-collected as immutable attempt
`574a2455-f21a-4024-8299-85417c9e5e9b`.  It binds the exact frozen GESUMMV
payload, Base config SHA `1a016e3c...`, Core `95ccdb7a...`, runtime
`462d105c...`, A1 observer and Framework `037f008b...`; it records
194,986,098 cycles / 190,918,656 instructions, lower acquire/release
34,394,773/34,394,773, final lower/PIB zero and cap-full zero.  Its new
source-defined structural companion independently reconciles Base cacheline,
MSHR and miss-queue families against the terminal perf stream.  This is a
strict, nonpromoting Core95 candidate for the eventual common GESUMMV
Base/IO/OO triplet; the active V2 registry is deliberately not modified while
its inherited closeout supervisor remains live.

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

The `FAST64_FUTURE_PRECOMPUTE_RESOURCE_AUDIT_V1` at
`/tmp/fast64-stage3-base-oneworker-audit-20260910T0729Z.tsv` passed one worker
with zero sampled swap-out, OOM, and memory PSI. It admitted the first missing
Base row only: 2DConvolution/Base namespace
`fast64_3_2DConvolution_base_cap8192_a1_v2`, immutable attempt
`844f1ba7-58a9-4208-98e5-71e01b1a6885`, CPU `0`, and classification
`PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`. The detached dynamic pool has a
single worker. Its initial controller exited immediately after launch because
it incorrectly read the headered `supervisor_pid` record as TSV column one;
the live immutable 2DConvolution runner was not touched. Future-only
`util/dtc_l1/continue_fast64_dynamic_pool_v3.sh` (SHA-256
`9fe78b45e048e97534cd4179b71d12b789a86d3c52cdabc91c6cdc678c6418c1`) adopts
that runner read-only, parses the receipt header correctly, and strictly
alias-v3 validates its natural terminal before it refills the next frozen
workload. Future-only `util/dtc_l1/monitor_fast64_3_dynamic_base_evidence_v1.py`
(SHA-256 `3d437ff5b8470ab0eee0ec1de576b6a7e6b601320e986d59c64df32a52ef7dd5`)
then waits for the pool's strict summary before materializing compact JSON/TSV
evidence and the separate source-defined Base structural companion. It never
writes a live run directory. No raw log is committed and no accepted result is
claimed until that validation completes.

The later four-worker audit at
`/tmp/fast64-future-wave4-audit-20260910T0807Z.tsv` passed with zero sampled
swap-out/OOM/memory-PSI/CFS-throttling, 208,555,491,328 bytes cgroup headroom,
125,939,712,000 bytes output free space, and four distinct CPU slots. It
admitted fresh immutable Base rows Gaussian (CPU 5, attempt
`3ec79940-ae70-444a-8991-816d6f570223`), Hotspot1 (CPU 6,
`409dbf6b-9a36-41c8-8c34-4aad51e6154a`), LUD (CPU 7,
`3a5f2814-bfb6-4f77-84c0-8c860d93b6e4`), and NN (CPU 8,
`7500b5ff-1b6e-4ead-882f-5a1f2aa24f29`). All use the same frozen Base
identity and `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` classification.

NN naturally exited `0` and was strict-collected into
`generated/fast64_3_dynamic_base_v1/`: cycles/instructions `6,985/1,284,872`,
lower acquired/released `10,691/10,691`, PIB admits/retires `4,011/4,011`,
final lower/PIB `0/0`, and lower-cap-full `0`. The generic v1 closeout monitor
was retained for its live users but cannot execute the non-executable Python
validator directly. Future-only `monitor_fast64_precomputed_row_v2.sh` invokes
the identical frozen validator via `python3`; it strictly collected NN and is
watching the three remaining parallel rows. This is a host-controller repair
only and changes no simulator/config/payload/result semantics.

LUD/IO and LUD/OO were physically acquired only after FAST64.2 PASS and have
now both naturally exited `0` and strict-collected through that future-only v2
path. Their compact records are
`generated/fast64_4_precomputed_rows_v1/fast64_4_lud_io_cap8192_a1_v3.json`
and `generated/fast64_4_precomputed_rows_v1/fast64_4_lud_oo_cap8192_a1_v3.json`.
The IO attempt `ad50c217-c4cc-4cf4-a514-91a368509f03` records
`1,089,813` cycles / `184,963,840` instructions; the OO attempt
`ce6a4a2b-8986-4d3d-b8e0-c40f8141f76e` records `1,086,338` cycles at the
same instructions. Each has balanced lower create/issue/response and
dependencies, zero final PIB/inflight/lower state, and OO active refs zero.
They remain `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE`, not accepted FAST64.4
evidence, until the FAST64.3 Base gate and later triplet audit pass.

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

For all future FAST64.3/4 launch decisions, use the future-only
`util/dtc_l1/audit_fast64_future_precompute_resources_v2.sh`, not the v1
single-window any-swap rejection. V2 captures repeated short windows and
classifies one positive `pswpout` observation as transient activity while
rejecting only sustained swap activity or independent OOM/PSI/memory/output/
CPU safety failures. The initial v2 two-window calibration reports zero
swap-out, major faults, PSI, OOM, and throttling; formal FAST64 p95/max RSS is
`4.79 GiB`, with roughly `209 GiB` cgroup memory headroom. This supports a
measured total-worker target of up to 20, verified incrementally after each
material refill. It changes scheduling only, never scientific row identity.

The current three-window V2 observation
`/tmp/fast64-review-parallelism-20260910T094045Z.tsv` strengthens that
calibration without changing an existing run: requested-new-workers `8`,
swap-out/major-fault/OOM/PSI/throttling deltas all `0`, cgroup CPU use
11.47--11.71 core-equivalents of the 384-core quota, cgroup headroom
230,305,792,000 bytes, `MemAvailable` 75,037,433,856 bytes and output free
124,287,619,072 bytes.  Its admission is `PASS_FUTURE_PRECOMPUTE_ADMISSION_V2`
for eight further workers.  The operational order remains: complete the
common repaired-Core Hotspot1 triplet, finish remaining Base acquisition, then
fill new FAST64.4 work under the settled identity; this does not authorize
altering the existing bbcbb controllers or relabelling their rows.

The later three-window V2 admission at
`/tmp/fast64-repaired-ramp3-admission-20260910T102552Z.tsv` also passes two
additional workers: sampled swap-out and major faults are `0` in all windows,
memory PSI/OOM/CFS throttling are `0`, cgroup CPU use is `20.376--20.979`
core-equivalents of the `384`-core quota, p95 RSS is `5,142,216,704` bytes,
`MemAvailable` is `28,210,438,144` bytes, cgroup headroom is
`207,717,339,136` bytes, and output free space is `120,583,127,040` bytes.
The observed `2 GiB` aggregate swap allocation is therefore not classified as
active pressure: the sampled `pswpout` rate is zero.  At that observation the
machine had eighteen live FAST64 leaf simulators.  After Btree/OO naturally
terminated, the two safe slots remain reserved for a genuinely missing,
non-duplicate repaired-Core row; no redundant row is dispatched merely to
fill a target.  Future-only
`util/dtc_l1/dispatch_fast64_repaired_core_row_v3.sh` is now the
exactly-once, SHA-pinned path for that refill and cannot alter a live
bbcbb/controller namespace.

## 9.1 Gaussian IO/OO precompute collector reconciliation

Gaussian IO and OO immutable attempts `5251ab7f-13b1-43dc-9b7d-0434ef498817`
and `40293c57-f695-42d0-8b70-9bbe6c0842b3` naturally exited `0` and their v2
validator invocations wrote compact canonical JSON evidence.  IO records
3,815,204 cycles and OO 3,818,467, each at 283,685,120 instructions.  Required
simulator stdout/stderr scans have no assertion/fatal/deadlock/mismatch
signature.  V2 then lacked its final PASS marker solely because
`simulator.launcher.log` is optional for this runner but was passed as a
required `rg` path.  Do not treat this post-validator marker defect as a
simulation failure or rewrite the live v2 GEMM monitor.  Future-only v3 fixes
only that optional-file scan and passes a deterministic Gaussian/IO replay;
the replay JSON SHA-256 exactly equals the canonical output SHA.  Gaussian
IO/OO remain `PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE` and must still satisfy
their owning stage/triplet acceptance before any promotion.

## 10. FAST64.3 HARD acceptance checklist

### Pre-closeout registry audit (2026-09-11)

The final matrix collector's own `validate()` implementation was applied
read-only to every currently promotable non-2D registry row. Eleven passed exact summary
and structural availability, frozen Framework/A1/Base-config identity, payload
identity, lower and PIB conservation/drain, non-binding-cap check, and
structural lifecycle reconciliation.  This is not a partial stage PASS: the
collector deliberately still rejects the registry while its 2DConvolution row
is `INVALID_HISTORICAL_BASE_PENDING_REPAIR`. The only remaining FAST64.3
Base-input closure is the dc6062 diagnostic's source-backed classification,
followed by a fresh source-correct formal replacement; Core-41 is preserved
invalid evidence, not a live replacement candidate.

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
