---
name: scientific-evidence-review
description: Read-only scientific audit of AWMA, AI-ARCH or historical C16 experiment reports, Codex review packs, frozen Git commits, numerical results and claims. Use for independent evidence/claim qualification; not for routine code styling or to launch experiments.
---

# Scientific evidence review

## Entry and hard boundaries

1. Read the user's concrete question, exact branch/commit, named report and scientific contract. If no exact authority is given, discover candidate sources but **do not conflate** latest navigation with accepted result. Preserve fixed commit/tree/SHA, source version and review state.
2. **Read-only by default**: inspect docs, manifests, code, log excerpts and existing consumer reports. No resetting branches, modifying simulation parameters, rerunning GPU/CPU campaigns, regenerating data, changing holdouts or installing tools unless separately authorized. A new scientific task needs a separate Goal.
3. Identify whether information is direct raw evidence, derived/independently recomputed evidence, simulator/model result, native GPU measurement, source inspection, or literature. Mark unavailable data as unverified; never invent source lines, hash matches, numerical closure or time measurements.

## Review procedure

1. **Question and scope**: define workload, input identity, phase/operator, backend/precision, device/model, sampling unit, intervention and reported metric/unit. Separate discovery from formal holdout; note if the sample was already used for tuning.
2. **Evidence chain**: verify the exact commit, runner/tool/config/build, manifest, checksums/receipt where actually accessible, raw-to-derived relationships, independent consumer status and any STOP condition. Do not equate a path existing with matching SHA, nor a manifest PASS with independent scientific review.
3. **Completeness**: inspect negative/zero/failed cases, canaries, actual sample counts and denominators, missing telemetry, address-path coverage and inferred kernel semantics. Do not reinterpret `ZERO_EXECUTION` as dropped capture without proof.
4. **Numerical and causal logic**: check units and comparator. For kernel latency, `speedup = baseline_time / candidate_time`, while `reduction = (baseline_time - candidate_time)/baseline_time`; they are not interchangeable. Translation service reduction, bytes reduced, occupancy, footprint or duplicate accesses are **not** speedup. Distinguish kernel-family response, workload-weighted estimate and measured end-to-end. Do not label cold replay as real application warm-state evidence.
5. **Claims and alternatives**: name supporting and contradicting evidence; distinguish scientific correctness, observational fidelity, mechanism activation, relevant cost, strong software baseline, headroom and generalization. A scoped benefit stays scoped; a STOP can mean numerical identity or observability failure rather than a hypothesis's scientific falsification.
6. **Decision**: `ACCEPT_SCOPED`, `REJECT`, `PARTIAL`, `STOP`, or `UNVERIFIED`, with exact claim text, gaps and a minimal discriminating check if authorized. Never promote a mechanism, schedule GPU work, or merge branches on the strength of this skill alone.

## Project-specific traps

- AWMA simulated 10/80 is a research-model setting, not verified RTX4080 silicon TLB timing. Pre-L1 translation service savings do not imply a uniform speedup. Do not merge separate AWMA execution branches into AI-ARCH coordination.
- Latest 2026-10-13 AWMA R27R3 independent review accepted **B0 reference repeatability STOP**: 25 / 262,668,288 BF16 gradient elements exceeded its original elementwise threshold between two independent B0 processes; source of discrepancy unresolved; C1/S2 component attribution and capacity not run. Do not call that an S2 failure or a capacity result. Revalidate against fixed authority before repeating these facts in newer tasks.
- Historical C16 Stage A four DQs incomplete; two compiled Mode A/B correctness results do not authorize Observer V3, Tier1, renewed GPU tasks or mechanisms.
- AI-ARCH Discovery P01/P13 is a research direction, not an active native campaign; paper evidence does not automatically authorize execution.

## Response contract

Use the report structure in [references/REVIEW_OUTPUT_TEMPLATE.md](references/REVIEW_OUTPUT_TEMPLATE.md). Write the human summary in concise Chinese: what was observed; what it supports; what it cannot show; whether to proceed. Internal PASS/STOP labels may remain in tables and audit files. Cite exact immutable commit paths and lines wherever possible. If a raw artifact is unavailable from GitHub, say `GITHUB_ONLY_NOT_RAW_REVALIDATED` rather than claiming independent recomputation.
