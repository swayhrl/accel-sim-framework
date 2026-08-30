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
5. `WORKLOAD_ARCHETYPES_PRELIMINARY.md` — current evidence-backed preliminary workload map; final Lane-D convergence may revise it.
6. `MECHANISM_IMPLEMENTATION_PLAN.md` — staged M0-M7 build plan from opportunity telemetry through integrated EP-L2.
7. `EXPERIMENT_MODE_SWITCH_CONTRACT.md` — mandatory baseline/mechanism switching, ablation, config, and provenance interface for all functional stages.
8. `EXPERIMENT_ROADMAP.md` — baseline calibration -> causal probes -> performance headroom -> opportunity mechanisms.
9. `PERFORMANCE_HEADROOM_PLAN.md` — how to separate L2-local improvement from downstream masking.
10. `WORKFLOW_GOVERNANCE.md` — ChatGPT/Codex/GitHub ownership and update discipline.
11. `decisions/` — architecture/research ADRs for major decisions.

## One-sentence research objective

> Under comparable L2 storage budget and basic L2 timing, increase the L2's ability to sustain concurrent misses, pending transactions, and payload state while reducing structural blocking caused by static resource/lifetime coupling; end-to-end application speedup is a stronger outcome, but is not the only valid evidence of a better L2 when another subsystem becomes the new bottleneck.

## Near-term engineering path

```text
Final calibration convergence
        -> BASELINE-DECISION
        -> M0 mechanism-readiness / shadow opportunity
        -> M1 behavior-preserving elastic substrate
        -> first functional resource-decoupling mechanism
        -> remaining mechanism families
        -> integrated EP-L2
        -> performance-headroom / robustness / full-suite evaluation
```

A separate Lane-F source-audit/preparation stage may run in parallel with final calibration convergence because it does not modify functional simulator behavior or choose the primary baseline.

Every functional stage must preserve an explicit baseline/OFF path and use the experiment-mode contract so the same source/binary family can run baseline, single-mechanism, ablation, and integrated configurations without branch/source switching.

## What this directory is not

It is not a replacement for per-stage manifests or review packs. Exact runtime source/config/trace provenance always comes from the corresponding reviewed experiment pack.

It is also not permission for Codex to continue into a later mechanism. Current execution authorization still comes from `chatgpt_handoff/*TARGET_GOAL.md` / stage handoffs and explicit STOP boundaries.
