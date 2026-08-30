# EP-L2 Project Specification

Status: **canonical long-lived research/design specification**.

Ownership: ChatGPT/user research decisions. Codex may read these files but must not silently redefine them during execution.

This directory is deliberately separate from transient execution state:

```text
docs/ep_l2/project_spec/        long-lived goals, architecture, claim model, roadmap
docs/ep_l2/chatgpt_handoff/     current ChatGPT -> Codex executable instructions
docs/ep_l2/codex_handoff/       current Codex -> ChatGPT execution reports
docs/ep_l2/review_packs/        independently reviewable evidence
docs/ep_l2/coordination/        shared multi-lane execution/status board
```

## Canonical reading order

1. `RESEARCH_CHARTER.md` — what EP-L2 is trying to improve and what counts as success.
2. `ARCHITECTURE_BLUEPRINT.md` — frozen/current architecture, calibration resources, and future mechanism boundaries.
3. `EVIDENCE_AND_CLAIM_MODEL.md` — three evidence levels and what each can legitimately support.
4. `WORKLOAD_CHARACTERIZATION_SCHEMA.md` — common 13-workload classification/evidence contract.
5. `WORKLOAD_ARCHETYPES_PRELIMINARY.md` — historical/pre-convergence workload map; final Lane-D review pack is the current evidence source.
6. `MECHANISM_IMPLEMENTATION_PLAN.md` — full M0-M7 design space and mechanism-family detail.
7. `MECHANISM_SEQUENCE_CURRENT.md` — **authoritative near-term sequence after Lane-D/F review; overrides older assumptions about M2 being first.**
8. `EXPERIMENT_MODE_SWITCH_CONTRACT.md` — mandatory baseline/mechanism switching, ablation, config, and provenance interface for all functional stages.
9. `EXPERIMENT_ROADMAP.md` — baseline calibration -> causal probes -> performance headroom -> opportunity mechanisms.
10. `PERFORMANCE_HEADROOM_PLAN.md` — how to separate L2-local improvement from downstream masking.
11. `MOTIVATION_FIGURES_PLAN.md` — canonical definitions for the reuse-distance and structural-blocking motivation figures, including the WBUF 4/8/16 shadow model.
12. `WORKFLOW_GOVERNANCE.md` — ChatGPT/Codex/GitHub ownership and update discipline.
13. `decisions/` — architecture/research ADRs, including the accepted calibrated baseline, Unified-payload precondition, and motivation-WBUF shadow definition.

## One-sentence research objective

> Under comparable L2 storage budget and basic L2 timing, increase the L2's ability to sustain concurrent misses, pending transactions, and payload state while reducing structural blocking caused by static resource/lifetime coupling; end-to-end application speedup is a stronger outcome, but is not the only valid evidence of a better L2 when another subsystem becomes the new bottleneck.

## Accepted calibrated research baseline

See `decisions/ADR-005-calibrated-research-baseline.md`.

Primary mechanism-development baseline:

```text
Descriptor pool        512
Line MSHR              128
per-address cap         32
L1                     BASE
WAD                     128
payload storage        1152 x 128 B / slice
payload banks          4 x 288
L2->DRAM               128
FR-FCFS scheduler      128/channel
ReturnQ                192/channel
DRAM                    850 MHz primary
```

D512 is selected to remove a bounded-cost descriptor metadata throttle from the research baseline, not because it is faster or because it exposes an MSHR bottleneck.

## Near-term engineering path

```text
M0a generic observation  ||  M1 behavior-preserving elastic substrate
                 \              /
                  \            /
                   -> M0b mechanism-specific opportunity shadows
                          |
                          -> choose first functional mechanism from evidence
                          |
                          -> compose validated mechanisms
                          |
                          -> performance-headroom / robustness / full-suite evaluation
```

`ADR-006-unified-payload-opportunity-precondition.md` records the Lane-F finding that the current 128 bypass slots have no production consumer and that fixed 1024 resident tags mean M2 alone cannot create extra resident-line capacity. Do not fabricate bypass traffic to justify Unified Payload.

Every functional stage must preserve an explicit baseline/OFF path and use the experiment-mode contract so the same source/binary family can run baseline, single-mechanism, ablation, and integrated configurations without branch/source switching.

## Motivation-figure contract

`MOTIVATION_FIGURES_PLAN.md` freezes two paper-facing motivation measurements:

```text
Figure 1: L2 reuse-distance distribution
Figure 2: L2 miss-admission structural blocking composition
```

The WB-path study uses a timing-neutral finite dirty-writeback-data WBUF shadow at capacities 4/8/16 in one workload replay. `decisions/ADR-009-motivation-wbuf-shadow-definition.md` freezes WBUF lifetime as WB-packet creation -> successful lower-path acceptance; WAD remains a separate longer-lived ordering resource.

## What this directory is not

It is not a replacement for per-stage manifests or review packs. Exact runtime source/config/trace provenance always comes from the corresponding reviewed experiment pack.

It is also not permission for Codex to continue into a later mechanism. Current execution authorization still comes from `chatgpt_handoff/*TARGET_GOAL.md` / stage handoffs and explicit STOP boundaries.
