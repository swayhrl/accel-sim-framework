# EP-L2 Parallel Workboard

Updated: 2026-08-30

Permanent coordination branch: `hrl/ep-l2-exp-v0`

This file is intentionally shared by **Codex and ChatGPT**. It tracks parallel workstreams, execution state, evidence, review state, and decisions. It is not a source-of-truth replacement for formal stage manifests or review packs.

## Update protocol

- Codex updates: `Execution status`, `Progress / result`, `Evidence / branch`.
- ChatGPT updates: `Review status`, `Review conclusion / next action`.
- Either side may add a new row with a unique task ID.
- Before updating, fetch/pull the latest coordination branch and preserve the other side's fields.
- Do not rewrite historical PASS/FAIL conclusions; append a superseding note if a later experiment changes the interpretation.
- Formal simulator runs and calibration runs must use separate result roots and separate branches/worktrees.

Status vocabulary:

```text
Execution: TODO | PREP | RUNNING | DONE | BLOCKED | OBSOLETE
Review:   PENDING | PASS | CONDITIONAL_PASS | FAIL | NOT_APPLICABLE
```

## Current parallel plan

| ID | Lane | Task | Experimental delta / purpose | Workloads | Dependency | Execution status | Progress / result | Evidence / branch | Review status | Review conclusion / next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TB26 | Formal baseline | Finish current D256 final 26-run | Frozen C7e Target Baseline, D=256, L1 base, Legacy+Banked @850 MHz | 13 x 2 | none | RUNNING | 22/26 complete; gemm + 3mm pairs remain | `review_packs/TARGET_BASELINE_FINAL_INTERIM_22OF26_r1/` | CONDITIONAL_PASS | Do not interrupt. Finish 26/26 and final aggregate. |
| SRC-C7E | Provenance | Push exact already-running C7e source commits to stable remote branches | No source rebuild/recommit; make exact formal source auditable | n/a | none | TODO | Interim manifest names Core `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`, Framework `f08d2ce857972fad73c4e1ab7162ba94c6336507` | stable C7e Core/Framework branches | PENDING | Must be remotely fetchable before final closeout. |
| D512-AUDIT | Calibration prep | Audit descriptor=512 support and telemetry dimensions | Keep line MSHR=128 and per-address cap=32; only descriptor pool 256->512. Generalize any hard-coded 257-entry telemetry/parser state if necessary. | directed + short natural | exact C7e source available | DONE | Exact C7e anchors verified. Allocator is parameter-safe; only clipped descriptor-occupancy telemetry was generalized, with D512 boundary tests. Release build + C3-C7 regressions + D512 config-diff test pass. D256 backward-equivalence is now PASS for `vectorAdd_4M`, `spmv`, and `scan`: each has seven parsed CSV artifacts byte-identical to C7e. Natural D512 telemetry is >256: Banked vectorAdd max/p95=368/339 and Banked spmv=403/382. | D512 Framework `aae62b66`; Core `878f8086`; exact-C7e equivalence Framework `f08d2ce8`; results `docs/ep_l2/calibration_results/d512_d256_equivalence/`; interim review `review_packs/D512_CALIBRATION_INTERIM_22OF26_r1/` | PASS | Observation/parameterization-only code change has passed D256 timing/output equivalence. |
| D512-PREFLIGHT | Descriptor calibration | D512 preflight | Compare D256 vs D512 with no L1 changes; verify descriptor pool blocks fall and all telemetry/invariants remain valid | vectorAdd, scan, spmv, FWT_7_21 (+ one low-pressure control) | frozen candidate; promotion waits for D256 equivalence | RUNNING | `D256_EQ_SCAN_PASS` is PASS. Banked `vectorAdd_4M`, `spmv`, `FWT_7_21`, `sad` and Legacy `vectorAdd_4M` are `COMPLETE_VALID` with frozen provenance and clean parser/invariants. Banked `scan` remains live, so B6 is `PENDING_RUNNING_SCAN`; all completed results remain `SPECULATIVE_PENDING_GATE` until `D512_PREFLIGHT_PASS`. | `docs/ep_l2/calibration_results/d512_850/` (per-row isolated roots); Framework `aae62b66`, Core `878f8086`; interim review `review_packs/D512_CALIBRATION_INTERIM_22OF26_r1/` | PENDING | Promote only after Banked scan and the D512 telemetry/preflight checks pass. |
| D512-MIRROR | Descriptor calibration | Full speculative D512 mirror campaign | B0-Legacy + B0-Banked, descriptor pool=512, MSHR=128, cap=32; otherwise exact final baseline | 13 x 2 | frozen candidate; promotion dependencies `D256_EQ_SCAN_PASS`, `D512_PREFLIGHT_PASS` | RUNNING | All 26 unique rows launched in isolated roots; 22/26 are `COMPLETE_VALID`, 4 long rows live: Banked/Legacy `scan` and Banked/Legacy `3mm`. Every completed row is provenance-audited and `SPECULATIVE_PENDING_GATE`; old post-scan waiter was stopped after process-tree verification to prevent duplicate launches. | `docs/ep_l2/calibration_results/d512_850/`; frozen Framework `aae62b66`, Core `878f8086`; interim review `review_packs/D512_CALIBRATION_INTERIM_22OF26_r1/` | PENDING | `D512_MIRROR_COMPLETE` requires 26/26 `COMPLETE_VALID` plus successful promotion of every speculative row. |
| D-COST | Baseline justification | Descriptor metadata cost estimate | Quantify 256->512 added metadata bits/bytes per slice and chip; separate simulator host structure from proposed hardware metadata | analytical | D512-AUDIT | DONE | Lane D: transparent 64/96/128-bit descriptor range; D256->D512 adds 2--4 KiB/slice and 128--256 KiB/chip (1.39--2.78% of frozen payload budget). No area/performance claim. | `docs/ep_l2/calibration/DESCRIPTOR_METADATA_COST.md`; Lane-D source `hrl/ep-l2-cal-analysis-v0` @ `cb83606` | PASS | Cost methodology and arithmetic reviewed PASS; use only as hardware-plausibility evidence, not an area/performance claim. |
| L1-D256-META | L1 causality | L1 metadata/queue headroom at D256 | Keep 64KiB/tag geometry/latency/banks fixed; MSHR 512->1024, per-line merge 8->32, MissQ 16->64 | vectorAdd, scan, spmv, convolution, btree, sad, FWT_7_21 | current formal D256 base exists | DONE | 7/7 B0-Banked rows are `COMPLETE_VALID`, including `scan` (2,151,187 cycles); provenance/config audit and parser/invariants pass. C8 full screen finds no >5% META-HR performance response or strong downstream trigger; no C9 decomposition is required. | Framework `hrl/ep-l2-l1-causality-v0` @ `dc30e67`; Core `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`; results `/workspace/results/ep_l2_l1_causality_d256/META-HR/` | PASS | D256 cell is locally accepted; final Lane-C completion still needs promoted D512 descendants and C11 pack. |
| L1-D256-BANK | L1 causality | L1 bank-throughput headroom at D256 | Keep capacity/tag/MSHR/MissQ fixed; banks 4->8 only | same 7 | current formal D256 base exists | DONE | 7/7 B0-Banked rows are `COMPLETE_VALID`, including `scan` (2,160,489 cycles); provenance/config audit, parser and invariants pass. C8 full screen has no material META-HR trigger requiring C9 decomposition. | Framework `hrl/ep-l2-l1-causality-v0` @ `dc30e67`; Core `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`; results `/workspace/results/ep_l2_l1_causality_d256/BANK-HR/` | PASS | D256 cell is locally accepted; final Lane-C completion still needs promoted D512 descendants and C11 pack. |
| L1-D512-META | Interaction | L1 metadata headroom after descriptor relief | D512 + same L1 metadata headroom | same 7 | Promotion: `D256_EQ_SCAN_PASS` + `D512_PREFLIGHT_PASS` | RUNNING | `SPECULATIVE_PENDING_GATE`; exact Lane-B candidate Core `878f80869ce212e779df20b6421e4dc7f987825d`, Framework `aae62b66685f15437cecf0193934f628e6fac6ae`; isolated Lane-C descendant Framework `hrl/ep-l2-l1-causality-d512-v0` @ `8e9693c`; 7 B0-Banked jobs launched. | `/workspace/results/ep_l2_l1_causality_d512_speculative/D512-META-HR/`; D512 overlay SHA256 `492269014ee869f9023cc7ec4fb3ac8dd7da04bf96d34e2e55ffb74d040007b3` | PENDING | Detects whether D256 descriptor pressure masks L1 or vice versa. Do not mark DONE or use as calibration evidence until both promotion gates pass. |
| L1-D512-BANK | Interaction | L1 bank headroom after descriptor relief | D512 + banks 4->8 | same 7 | Promotion: `D256_EQ_SCAN_PASS` + `D512_PREFLIGHT_PASS` | RUNNING | `SPECULATIVE_PENDING_GATE`; same exact Lane-B candidate and isolated Lane-C descendant @ `8e9693c`; 7 B0-Banked jobs launched. | `/workspace/results/ep_l2_l1_causality_d512_speculative/D512-BANK-HR/`; D512 overlay SHA256 `492269014ee869f9023cc7ec4fb3ac8dd7da04bf96d34e2e55ffb74d040007b3` | PENDING | Detects L1 bank bottleneck after descriptor relief. Do not mark DONE or use as calibration evidence until both promotion gates pass. |
| CAL-ANALYSIS | Calibration analysis | Joint D256/D512 x L1 causality analysis | Compare cycles, L1 events, L2 descriptor/MSHR, lower traffic, scheduler/BW, and temporal windows | selected + full D512 | all required calibration runs | PREP | Lane D V3 infrastructure finalized: complete 32-channel native DRAM aggregation; runtime-config SHA256-to-contract binding plus PASS config-delta evidence; exact 64/32 time-group alignment; missing-denominator fail-closed. Existing 22/26 input reprocessed successfully; awaits promoted B/C inputs for actual calibration deltas. | `review_packs/CALIBRATION_ANALYSIS_INFRA_r1/`; source `hrl/ep-l2-cal-analysis-v0` @ `cb83606`; ChatGPT final review `chatgpt_handoff/LANE_D_CHATGPT_FINAL_REVIEW.md` | PASS | V3 analysis/provenance infrastructure PASS. Keep execution PREP until promoted calibration inputs arrive; freeze analysis semantics except bug fixes. |
| BASELINE-DECISION | Decision gate | Freeze calibrated primary baseline | Do not prefer MSHR bottleneck by construction. Choose resources based on hardware plausibility + sensitivity evidence. | all evidence | CAL-ANALYSIS | TODO | — | decision record | PENDING | If D512 is adopted and D512 mirror is valid, promote/revalidate it; otherwise keep D256. |
| OPP-PREP | Code prep | Opportunity-study scaffolding only | Prepare configurable timing-neutral shadow infrastructure/tests after calibrated baseline direction is clear; no functional RO/TVD/Unified claim yet | directed only | D512-AUDIT + baseline direction | TODO | — | isolated opportunity branch | PENDING | May proceed in parallel once parameterization is stable; full opportunity runs wait for baseline decision. |

## Factorial interpretation for L1 / descriptor interaction

For selected workloads, use the already-existing D256/L1-base result plus the new cells:

```text
                         L1 BASE        L1 META-HR      L1 BANK-HR
Descriptor 256          existing        run             run
Descriptor 512          mirror          run             run
```

Primary interpretation uses both performance and downstream-pressure movement:

| Observation after L1 headroom | Interpretation |
| --- | --- |
| Little speedup; L2/lower pressure nearly unchanged | L1 blocker events are mostly symptoms/backpressure, not a primary causal limit. |
| Clear speedup; L2/lower pressure changes little | L1-local independent bottleneck. Current baseline may still be valid if L1 resources are hardware-grounded. |
| Clear speedup and L2 descriptor/lower demand rises materially | L1 was throttling demand and masking L2 opportunity; primary baseline calibration must be revisited. |
| L1 events fall but speedup is small while scheduler/BW pressure rises | Headroom only moves the bottleneck downstream. |

## Descriptor 512 decision logic

Do **not** tune resources with the goal of forcing Line MSHR to become the bottleneck. The calibration question is whether 256 descriptors are an unnecessarily tight/cheap metadata cap.

Interpret D256 -> D512 as follows:

```text
Descriptor blocks collapse + meaningful speedup + Line-MSHR pressure emerges
  => D512 is a strong calibrated-baseline candidate; strengthens MSHR-related motivation.

Descriptor blocks collapse + little speedup + lower-path pressure rises
  => D256 throttled, but true limit is downstream; MSHR-bypass motivation remains weak.

Descriptor blocks collapse + little other change
  => D256 caused retry pressure with low performance sensitivity.

Descriptor blocks remain material at D512
  => further calibration requires explicit hardware-cost justification.
```

## Initial L1 headroom configs

Keep these as **sensitivity configurations**, not proposed hardware baselines until reviewed.

```text
L1 BASE:
  capacity = 64 KiB
  sets/ways/line = 4 x 128 x 128B
  MSHR = 512
  merge cap = 8
  MissQ = 16
  banks = 4
  latency = 20

L1 META-HR:
  same capacity/tag geometry/latency/banks
  MSHR = 1024
  merge cap = 32
  MissQ = 64

L1 BANK-HR:
  same capacity/tag geometry/MSHR/merge/MissQ/latency
  banks = 8
```

If either headroom class gives a material performance response, decompose it further with one-at-a-time sweeps only for the sensitive workloads.

## Decision thresholds (screening heuristics, not physical laws)

```text
< 2% cycle improvement: weak sensitivity
2-5%: moderate; retain as control/calibration evidence
> 5%: strong enough to decompose and reconsider bottleneck attribution
> 5% plus material increase in L2 demand/descriptor/lower pressure:
    strong evidence that L1 was masking L2
```

All final decisions must use actual traffic/pressure movement, not speedup alone.

## Hard boundaries

- Never modify/rebuild the currently running formal TB26 worktrees/binaries.
- Every calibration lane gets a separate worktree, branch, config overlay, result root, and manifest.
- D512 changes descriptor capacity only; line MSHR remains 128 and per-address cap remains 32.
- L1 headroom tests keep L1 capacity/tag geometry fixed; first round changes flow-control or bank throughput only.
- No functional RO no-MSHR, TVD, or Unified mechanism should be treated as evidence before `BASELINE-DECISION` is reviewed.
- Calibration data is never silently promoted to formal data; promotion requires an explicit review decision.

## Current working hypothesis to test, not assume

The 22/26 data suggest strong global descriptor pressure while Line MSHR-full is usually zero, plus substantial L1 pressure in several workloads. The immediate calibration must determine whether:

```text
(1) descriptor=256 is an artificial metadata bottleneck,
(2) L1 is an independent bottleneck or merely downstream backpressure,
(3) relieving descriptors and/or L1 reveals genuine Line-MSHR pressure,
(4) or the dominant limit simply moves to L2->DRAM / scheduler / DRAM bandwidth.
```

The answer, rather than a preference for an MSHR-centric story, determines the final EP-L2 mechanism motivation.
