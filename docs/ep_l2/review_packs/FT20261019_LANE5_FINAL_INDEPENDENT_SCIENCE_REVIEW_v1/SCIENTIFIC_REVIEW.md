# EP-L2 Lane5 finite-service terminal: independent scientific review (2026-10-19)

**Scope:** READ-ONLY audit of immutable `swayhrl/accel-sim-framework` Lane5 HEAD `94fd48b69b37adb692e6152301b317f5f2e6a1e9`, source packet publication `063ae471c161ee5d151891565aec267f209f7c61`, current science authority generation **68** at `f7b6e324ca0c4656c6db9f8f737444ad622cdea5`, and source Core `swayhrl/gpgpu-sim` `84359d4ba492acb639a2092fa271e9169038bf7d`. No simulator, source, config, binary, paper, original Goal, current acceptance, history or raw data was modified by this note.

## Decision

**SCOPED_EVIDENCE_ACCEPTED; POSITIVE_MQ2_RG1_BENEFIT_NOT_SUPPORTED.** The bounded experiment was completed according to its original deadline and acceptance rules, not exhaustively over all planned endpoints: **17/18 accepted, 1 `FWT_7_21 Unified/RG1` = `NOT_RUN_ORIGINAL_START_DEADLINE`**. All 12 independently qualified same-binary OFF/MQ2 full-application endpoints are accepted, and 5 separately qualified RG1 endpoints are accepted. No RG1 full-FWT cross-mode or crossworkload geomean exists. Charged original starts 51/72, finite stage 18/24 incl. 1 native OFF canary; 21 nominal unspent attempts have **zero** post-cutoff start authority. R6 ended naturally with no active simulator/lease, old R19 remains 20 accepted/10 pairs and closed.

Identity of all 17 accepted rows: Core `84359d4ba492acb639a2092fa271e9169038bf7d`; Framework `197741be9be9b8e390a557d639503b416d8e95f0`; vendored pybind11 `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`; binary SHA256 `f0af8515057e315af708a0e3c2fde4a3098b0c0fb3f7014471d8d8c9426f1f30`. Trace SHA within workload and per-profile runtime-config SHA are explicitly bound to each run. Terminal checks: expected full instruction count (Conv 714,547,200; FWT 791,609,344), 64-slice drain, per-run raw/binary SHA and independent CURRENT_ACCEPTED reviews. Separate 11/11 MQ2 and RG1 production gate qualifications, including directed RG1 positive witnesses. This is **not** whole-application numeric SASS correctness, atomic qualification, hardware RTL/PPA equivalence or a combined-MQ2/RG1 test.

## Exact accepted results

| Workload | Mode | OFF cycles | MQ2 cycles | RG1 cycles | OFF/RG1 |
| --- | --- | ---: | ---: | ---: | ---: |
| Conv. | B16 | 292932 | 292932 | 292323 | 1.002083312 |
| Conv. | S64 | 293258 | 293258 | 294644 | 0.995296018 |
| Conv. | Unified | 291525 | 291525 | 293117 | 0.994568722 |
| FWT | B16 | 493189 | 493189 | 493189 | 1.000000000 |
| FWT | S64 | 494627 | 494627 | 494627 | 1.000000000 |
| FWT | Unified | 491662 | 491662 | **NOT_RUN** | **undefined** |

In Conv., Unified/B16 changes from **292932/291525 = 1.004826344** (OFF or MQ2) to **292323/293117 = 0.997291184** (RG1), interaction **0.992501032** (ratio of those two ratios). This **reverses** the slight Unified advantage in this tested workload; it is not a statistically generalized result across unseen workloads. S64/Unified under RG1 is 294644/293117 = 1.005209524, compared with 293258/291525 = 1.005944602 under OFF.

## MQ2 mechanism attribution

The six MQ2 ON points report `bypasses=0` exactly. Their `wb_bank_waits` are Conv B16/S64/U = **57139/57799/58897** and FWT B16/S64/U = **21107/21037/20914**. These counters are **failed WB lower-ready observations while MQ2 is ON**, **not unique application-stall cycles** and not measurable as an OFF->ON stall reduction because OFF zero is observer-disabled. The qualified conservative safe second-entry classifier excludes `LDG.E.SYS` encountered on these full native inputs. Thus bank waits were observed, but **no eligible bypass was exercised**, and OFF and MQ2 cycles matched exactly in every case. Neither generic miss-queue HOL irrelevance nor a speedup from adding MQ2 is established. Directed qualification proof of a working constructed mechanism does not substitute an exercised workload path.

## RG1 mechanism attribution

For all 5 accepted RG1 ON points (Conv B16/S64/U, FWT B16/S64), bank-summed `held_not_ready_cycles=0`, `another_ready_cycles=0`, `recovered_grants=0`; client-summed `cancellations=0` (verified in the exact independently reviewed per-point COMPARISON.json). Some `max_first_ready_to_consume` maxima are nonzero (3 or 4 cycles) and **do not** imply a recovered grant. In Conv. the total `physical_services` differ: B16 OFF 9217033 vs RG1 9212809; S64 9213729 vs RG1 9215977; Unified 8124070 vs RG1 8118052. FWT B16/S64 service totals and cycles are unchanged.

A source-level review of pinned `src/gpgpu-sim/ep-l2-rg1.inc` and `gpu-cache.h` finds `recovered_grants` increments narrowly when a physically serviced operation overtakes a **previously older unready** pending request. RG1 ON also follows `request_rg1`'s ready-aware selection instead of OFF's retained-oldest-grant selection, so the absence of recovered events **does not prove identical scheduling implementation or identical all-ready ordering**. This is a **possible** mechanism for changed cycles, NOT an established application-level causal attribution; no per-request trace proving the residual +/- cycles was accepted. The targeted *blocked-service recovery* opportunity was not observed in these five applications. Neither an RG1 positive EP-specific benefit nor a general negative about bank-scheduling potential is supported.

Note: `RG1_wait_ready_cycles` observes per-bank/cycle only when enabled; OFF zero is not proof of no baseline waiting, and overlapping banks/slices cannot be summed as disjoint application stalled cycles. `RG1_physical_services` counts actual grants also under OFF, not a measure of saved application time.

## Scientific claim consequences

1. Freeze official H0 5-workload geometric mean **1.0016002037656606** with CFD regression, existing four-mode same-binary comparisons and all R19 positive/negative results. Do not replace H0 with new `f0af` OFF rows because some cycle numbers match; they have different binary identities and are separately accepted.
2. This final attempted common-service optimization **does not support** a claim that MQ2 or RG1 removes primary EP-L2 bottlenecks, recovers observed blocked bank service, amplifies Unified speedup under more favorable downstream conditions, or gives a performance win against strong static partition across workloads.
3. No `FWT Unified RG1` metric/ratio/mean may be invented. The lack of this condition prevents FWT fair three-mode RG1 comparison and a complete two-input RG1 geometric mean. It is not a reason to rerun the expired Goal.
4. R3 mapped-area measurements and failed timing targets predate MQ2/RG1; they cannot be presented as area/timing measurements of an RG1- or MQ2-enabled design, and raw simulator cycle ratios must not be combined with local RTL mapped cell area into hardware PPA claims.
5. Full numerical SASS end-to-end correctness and many non-atomic/sector scope extensions remain outside the experimental contract. The independent 11-gate native checks establish correctness within their qualified production paths, not universal correctness.

## Paper intake recommendation

Keep the frozen EN-v17 (or later current paper) scientific base intact until separately edited. If a brief negative-result statement materially helps explain the limited benefits of common service adjustments, put one short, carefully qualified paragraph in the existing finite-condition discussion (rather than another large chart): e.g., *“In a bounded same-executable service follow-up, MQ2 observed bank-wait events but admitted no eligible bypass under the input's conservative classifier. RG1 produced mixed Convolution outcomes, with zero measured unready-grant recovery; the FWT Unified condition was not run. These measurements do not support attributing additional EP-L2 speedup to the tested scheduling changes.”* If the four-page layout cannot afford this, retain the complete immutable results in scientific provenance and make no new optimization-performance claim. Do not imply a complete factorial design or general headroom upper bound.

No need to restart Lane5, R19, or any experiment after the immutable cutoff. Optional **read-only source/static mechanism note** could characterize why `request_rg1` alters all-ready arbitration and which counters observe it, but it would **not** turn the present RG1 cycle differences into a verified recovered-service claim. Further simulator tests require separate user authorization and a new scientific question.

## Exact source index

- `docs/ep_l2/review_packs/FT20261018_LANE5_FINAL_INTAKE_COMPLETION_AUDIT_r1/FINAL_MICROOPT_MATRIX_18.csv` and `.json` (17 current + one explicit NOT_RUN), `SIGNED_SAME_CONDITION_EFFECTS.json`, `PER_ENDPOINT_ACCEPTANCE_AUDIT.json`, `QUALIFICATION_AUDIT.json`, `ROLLING_DELIVERY_AUDIT.json`.
- `docs/ep_l2/review_packs/FT20261018_LANE5_FINAL_INTAKE_REMOTE_CLOSURE_r1/RECEIPT.json`, `DATA_PUBLICATION_REMOTE_READBACK.json` and `POST_READBACK_COMPLETION_AUDIT.json`.
- MQ2 independent 11 gates: `docs/ep_l2/review_packs/FT20261018_LANE5_MQ2_ELEVEN_GATES_r1/ELEVEN_GATE_REVIEW.json`.
- RG1 independent 11 gates: `docs/ep_l2/review_packs/FT20261018_LANE5_RG1_ELEVEN_GATES_r1/ELEVEN_GATE_REVIEW.json`.
- Core static code: `swayhrl/gpgpu-sim` at `84359d4ba492acb639a2092fa271e9169038bf7d`, `src/gpgpu-sim/ep-l2-rg1.inc`, `src/gpgpu-sim/gpu-cache.h`, `src/gpgpu-sim/gpu-cache.cc`.

**Review verification method:** Retrieved published CSV+JSON+pair comparison and scientific-reviews via GitHub, inspected all 18 identity+counter rows and each accepted RG1 client summary, checked independent gate/final readback receipts and relevant frozen core source; **did not independently replay all 17 multi-GB raw simulator logs** or launch new work. Previous Lane5 producer/consumer SHA and raw checks are reported by its existing independent receipts rather than duplicated here.
