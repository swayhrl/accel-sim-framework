# AWMA T1 negative ideal-response attribution report

Status: `COMPLETE_PHASE1_NO_CAUSAL_CONTROL`

## Scope and authorities

This stage attributes the accepted T1 observation only:

- `C_10_80 = 665802`
- `C_0_80 = 664805`
- `C_ideal = 715636`
- `S_L1 = +0.1497%`
- `S_ALL = -7.4848%`

The source parent is frozen ideal-control V3 at
`5e59fbcf7e5217e91d40e5ff2e38dfd3f48a97f8`.  The accepted ideal semantic
contract and all translation parameters are unchanged.

## Semantic and neutrality gates

All three runs use the identical accepted payload and runner index
(`payload_sha256=e36178f9a92033cd91f3c1ff4b165321b7958157c7deed2a9aaa4696e7c73e8c`,
`runner_index_sha256=c9dd68f84606deceb8d7dcece6e35c93750b16bf507ac3666c3adb2a0e0cdc41`).

| mode | cycles | instructions | CTAs | unique UID | coverage admissions |
|---|---:|---:|---:|---:|---:|
| 10/80 | 665802 | 369131520 | 384 | 7159808 | 7160265 |
| 0/80 | 664805 | 369131520 | 384 | 7159808 | 7234397 |
| ideal | 715636 | 369131520 | 384 | 7159808 | 7605378 |

The instrumented cycles and the complete signature above exactly match the
accepted runs.  Every run has `untranslated=0`, `unobserved=0`, duplicate READY
application attempts `=0`, and terminal/quiescence `=1`.  All three mapping
digests are exactly `unique=493, fnv64=12947203714122211934`.  In ideal,
lookup requests, translation MSHR allocations/active entries, PWQ occupancy,
active walkers, PTE requests/responses, PWC hits/misses, and PTE DRAM responses
are all zero.

## Observational method

The diagnostic is enabled only by
`GPGPUSIM_T1_ATTRIBUTION_DIAGNOSTICS=1`.  It records the earliest READY result
seen at the existing V1 prelaunch/head observation points and the later actual
downstream admission.  It also records true simulator-cycle release/admission
series, fixed 32/64/128-cycle windows, accessq observations, instruction/CTA
progress quantiles, and first/last data DRAM completion.  The patch does not
touch `vm_translation.cc`, translation state, arbitration predicates, queue
capacity, or request order.

The pre-existing M4C aggregate telemetry is enabled at level 2 solely for its
kernel aggregate L1/L2/DRAM and partition-queue counters.  Its legacy
transaction-count windows are not used as simulator-cycle windows.

There is no source-supported exact whole-hierarchy outstanding-request counter,
separate ICNT-injection FIFO/backpressure counter, or accepted active/eligible-
warp timeline; those metrics are unavailable rather than inferred.  Existing
global resource-stall, L2 partition-queue, scheduler-idle, and aggregate
scoreboard counters are used only under their source-defined meanings.

## Work conservation

Work amount is exactly conserved across 10/80, 0/80, and ideal:

| metric | each run |
|---|---:|
| instructions / CTAs | 369131520 / 384 |
| memory instructions / active-lane references | 447488 / 14319616 |
| coalesced downstream data transactions | 7159808 |
| requested / transaction bytes | 229113856 / 229113856 |
| data DRAM requests / bytes | 387072 / 12386304 |

Thus the ideal slowdown is not explained by more logical work, more data
transactions, or more DRAM data traffic.  `AWMA_VM_COVERAGE admissions` is a
retry-observation count and is deliberately not treated as successful work;
successful downstream admission is exactly 7159808 in every run.

## Directional attribution

The evidence closes one directional chain from the frozen intervention to the
longer critical tail:

| observation | 10/80 | 0/80 | ideal |
|---|---:|---:|---:|
| READY releases, single-cycle peak | 69 | 69 | 1216 |
| READY-to-admission delay, mean / p95 | 3.94 / 0 | 6.48 / 36 | 25.93 / 114 |
| ready entries per accessq observation, mean | 1.56 | 2.95 | 8.72 |
| downstream admissions, 32-cycle p95 / peak | 514 / 846 | 564 / 904 | 587 / 2432 |
| L1D reservation failures | 3850 | 367023 | 1825599 |
| global-memory resource stalls | 457 | 74589 | 445570 |
| average / maximum ICNT-to-memory latency | 841 / 16429 | 1214 / 17856 | 2100 / 44872 |
| mean DRAM queue occupancy | 0.8125 | 0.7897 | 0.9105 |
| partition-level parallelism | 10.7545 | 10.7706 | 10.0048 |
| shader memory stalls | 21344892 | 18978193 | 24547188 |
| scheduler idle | 7845947 | 8892778 | 12391742 |
| instruction p90 completion cycle | 597751 | 587803 | 653515 |
| CTA p90 completion cycle | 653280 | 638362 | 702233 |
| last data DRAM completion cycle | 628461 | 613365 | 684412 |

At the unchanged legal observation points, ideal makes resident translations
READY immediately.  Its single-cycle READY peak is 17.6x 10/80.  The unchanged
downstream law cannot admit that work instantaneously: ready residency and
READY-to-admission delay grow, while the 32-cycle admission peak rises 2.87x.
The same run then shows much larger L1D reservation pressure, global resource
stalls, and a 2.50x average / 2.73x maximum ICNT-to-memory latency.  With equal
work and equal DRAM request count, instruction p90 moves 55764 cycles later,
CTA p90 moves 48953 cycles later, and the last data DRAM completion moves 55951
cycles later.  This chain localizes the extra 49834 kernel cycles to temporal
release packing and resulting downstream contention/tail extension.

No single aggregate is treated as sufficient.  For example, 0/80 has more
`gpu_stall_dramfull` than ideal while completing faster, and ideal has fewer L2
reservation failures than 0/80.  The attribution rests on the aligned
release -> admission -> pressure -> progress sequence, not on monotonicity of
every queue counter.

## Hypothesis decision

- H1, burstiness/queue pressure: **supported**.  READY release burst, short
  cycle-window admission burst, L1D/ICNT pressure, and critical-tail movement
  have the required direction with conserved work.
- H2, locality/order: **not supported**.  L1D access/miss counts and data DRAM
  requests/bytes are identical; the small total-L2 difference is the 129 PTE
  responses absent by construction in ideal, not extra data locality work.
- H3, reduced latency hiding/progress: **supported as secondary**.  Scheduler
  idle rises 57.9% and instruction/CTA progress moves later.  Aggregate
  scoreboard stalls do not rise, so the claim is limited to exposed downstream
  wait/idle, not a scoreboard-specific mechanism.
- H4, not localized: **rejected** by the closed H1 -> secondary-H3 chain.

## Phase-2 decision

`IDEAL_WITH_MATCHED_RELEASE_PACING_CONTROL` was **not run**.  Phase 1 identifies
burstiness/backpressure, but the source offers no bounded neutral pacing rule:
replaying OFF READY timestamps would use treatment-dependent, workload-specific
future information, while imposing a fixed rate/window cap would add a new
downstream admission-control law.  Either choice would violate the frozen ideal
semantic boundary instead of providing a clean one-control causal test.

Accordingly there is no `CAUSAL_CONTROL.tsv`; the stage stops after Phase 1 as
required when a source-supported bounded rule is unavailable.

## Interpretation boundary

`S_ALL` remains the causal response to the specific frozen ideal-translation
intervention.  It is not a translation runtime fraction, and
`S_ALL - S_L1` is not a PTW fraction.  A negative ideal response alone does not
establish that translation is beneficial; such a claim would require the
explicit directional causal chain closed in this report.
