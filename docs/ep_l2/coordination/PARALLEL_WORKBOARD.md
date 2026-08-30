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
| D512-AUDIT | Calibration prep | Audit descriptor=512 support and telemetry dimensions | Keep line MSHR=128 and per-address cap=32; only descriptor pool 256->512. Generalize any hard-coded 257-entry telemetry/parser state if necessary. | directed + short natural | exact C7e source available | RUNNING | Exact C7e anchors verified. Allocator is parameter-safe; only clipped descriptor-occupancy telemetry was generalized, with D512 boundary tests. Release build + C3-C7 regressions + D512 config-diff test pass. `vectorAdd_4M` and `spmv` D256 backward-equivalence are COMPLETE_VALID with all parsed CSVs byte-identical to C7e; long `scan` D256 equivalence is actively running. | Framework `/workspace/worktrees/accel-sim-ep-l2-d512` @ `aae62b6`; Core `/workspace/worktrees/gpgpu-sim-ep-l2-d512` @ `878f8086`; exact-C7e equivalence Framework `/workspace/worktrees/accel-sim-ep-l2-d512-eq` @ `f08d2ce8`; results `docs/ep_l2/calibration_results/d512_d256_equivalence/` | PENDING | Any code change must be observation/parameterization-only; prove D256 timing equivalence if code changes. |
| D512-PREFLIGHT | Descriptor calibration | D512 preflight | Compare D256 vs D512 with no L1 changes; verify descriptor pool blocks fall and all telemetry/invariants remain valid | vectorAdd, scan, spmv, FWT_7_21 (+ one low-pressure control) | D512-AUDIT | TODO | Awaiting D256 backward-equivalence gate; frozen D512 overlays and runner are prepared. | `tests/ep_l2/b0_{legacy,banked}_d512_850.config`; separate root `docs/ep_l2/calibration_results/d512_preflight/` | PENDING | If valid, launch speculative full D512 mirror campaign in parallel. |
| D512-MIRROR | Descriptor calibration | Full speculative D512 mirror campaign | B0-Legacy + B0-Banked, descriptor pool=512, MSHR=128, cap=32; otherwise exact final baseline | 13 x 2 | D512-PREFLIGHT PASS | TODO | Blocked only by the mandatory preflight gate; no mirror simulator job launched. | planned root `docs/ep_l2/calibration_results/d512_850/` | PENDING | Label `SPECULATIVE_CALIBRATION`, not primary formal baseline until reviewed. |
| D-COST | Baseline justification | Descriptor metadata cost estimate | Quantify 256->512 added metadata bits/bytes per slice and chip; separate simulator host structure from proposed hardware metadata | analytical | D512-AUDIT | DONE | Lane D: transparent 64/96/128-bit descriptor range; D256->D512 adds 2--4 KiB/slice and 128--256 KiB/chip (1.39--2.78% of frozen payload budget). No area/performance claim. | `docs/ep_l2/calibration/DESCRIPTOR_METADATA_COST.md`; Lane-D source `hrl/ep-l2-cal-analysis-v0` @ `1b1f5f3` | PENDING | Needed to justify 512 as a reasonable baseline rather than tuning for performance. |
| L1-D256-META | L1 causality | L1 metadata/queue headroom at D256 | Keep 64KiB/tag geometry/latency/banks fixed; example headroom: MSHR 512->1024, per-line merge 8->32, MissQ 16->64 | vectorAdd, scan, spmv, convolution, btree, sad, FWT_7_21 | current formal D256 base exists | RUNNING | Isolated C7e-derived runner/config audit PASS; seven-workload B0-Banked cell launched. | Framework `hrl/ep-l2-l1-causality-v0` @ `2bcfed2`; Core `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`; results `/workspace/results/ep_l2_l1_causality_d256/META-HR/` | PENDING | Tests whether L1 metadata/queue resources causally limit performance under current D256 baseline. |
| L1-D256-BANK | L1 causality | L1 bank-throughput headroom at D256 | Keep capacity/tag/MSHR/MissQ fixed; banks 4->8 only | same 7 | current formal D256 base exists | RUNNING | Isolated C7e-derived runner/config audit PASS; seven-workload B0-Banked cell launched. | Framework `hrl/ep-l2-l1-causality-v0` @ `2bcfed2`; Core `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`; results `/workspace/results/ep_l2_l1_causality_d256/BANK-HR/` | PENDING | Separates L1 bank/latency-pipeline pressure from metadata pressure. |
| L1-D512-META | Interaction | L1 metadata headroom after descriptor relief | D512 + same L1 metadata headroom | same 7 | D512 preflight/pass | TODO | — | isolated factorial result root | PENDING | Detects whether D256 descriptor pressure masks L1 or vice versa. |
| L1-D512-BANK | Interaction | L1 bank headroom after descriptor relief | D512 + banks 4->8 | same 7 | D512 preflight/pass | TODO | — | isolated factorial result root | PENDING | Detects L1 bank bottleneck after descriptor relief. |
| CAL-ANALYSIS | Calibration analysis | Joint D256/D512 x L1 causality analysis | Compare cycles, L1 events, L2 descriptor/MSHR, lower traffic, scheduler/BW, and temporal windows | selected + full D512 | all required calibration runs | PREP | Lane D analyzer/fixtures ready; ingested the 22/26 D256 interim scope (11 pairs), including repaired raw-stream cardinality, temporal distributions, burst and channel-imbalance metrics. Awaiting DONE D512/L1 evidence before deltas/causality conclusion. | `review_packs/CALIBRATION_ANALYSIS_INFRA_r1/`; source `hrl/ep-l2-cal-analysis-v0` @ `1b1f5f3` | PENDING | Classify L1-local vs downstream backpressure vs L1-throttling-L2; decide D256 vs D512 primary baseline. |
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
  => D256 was throttling, but the true limit is downstream; MSHR-bypass motivation remains weak.

Descriptor blocks collapse + little other change
  => 256 produced retry pressure but not meaningful performance loss.

Descriptor blocks remain material at 512
  => consider whether pool needs further calibration, but require hardware-cost justification before increasing again.
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
