# Resume plan after Window A terminal

**Evidence label: `SPECULATIVE_DIAGNOSTIC`**

This is a decision-gated recovery plan, not execution authorization. Window A must be terminal first; its worktree, processes, binary, scratch, logs, configs, and manifests remain out of scope.

## Entry gates

Before any recovery job, the B owner records the following without inspecting or altering Window A/C private state.

1. Window A terminal status is externally confirmed.
2. `MemAvailable`, its short-term trend, swap-in/out, and iowait show no persistent pressure.
3. Initially admit no more than one actual B high-load worker; never restore historical farm concurrency automatically.
4. Each job class has measured peak RSS (E07/E08 if absent) and a reserve based on that peak and current memory trend.
5. Record exact B branch/config/object-map/trace identity; validate realization and counter conservation before a continuous ROI.
6. Keep every stateful ROI continuous in one simulator process per arm; never split it into a process per kernel.

If a gate fails, do not start another B high-load job. Preserve artifacts and classify the gap until conditions recover.

## First recovery batch: E01--E10

1. E01--E06 are six Decode1 diagnostic smoke controls that test whether PWC, page size, or translation controls have a sampled signature worth carrying into a continuous ROI.
2. E07/E08 are one streaming representative decoder/prefill mining memory calibration each; they are resource measurements, not a trace fan-out.
3. E09/E10 are a matched, signature-stratified 16-kernel static budget per phase, with object-map, boundary, provenance, and UNKNOWN audit.

This replaces B7's 1321-item resume list with a minimal sequence that can reject a conventional-first explanation, unsafe mining assumption, phase premise, or Weight-attribution premise before a high-cost continuous ROI.

## Decision gates after the first batch

| Condition | Required action |
|---|---|
| Config unrealized, telemetry conservation fails, or control semantics ambiguous | Repair/validate first; do not interpret a delta or launch Tier 1. |
| Persistent swap, falling available memory, or materially worse iowait | Do not start another B high-load worker; safely stop/checkpoint only current B work if protocol permits. |
| E07/E08 lacks reserve | Defer that job class; do not assume a smaller sample is safe without calibration. |
| E09/E10 has high or unstable UNKNOWN | Do not make a Weight-specific B claim; retain `NEEDS_RUNTIME_EVIDENCE`. |
| E01--E06 has no stable translation signature | De-prioritize Tier 1 translation sweeps and report the bounded null. |
| A stable conventional signature appears and all gates are clean | Admit only its matching Tier 1 bundle, one at a time. |

## Tier 1 B continuous-ROI sequence

Tier 1 is conditional, not a five-job commitment: E11 PWC ladder, E12 page/translation controls, E13 L2-TLB bracket, E14 walker bracket, then E15 prefill-versus-decode contrast. Required observables and all three outcome branches are predeclared in the experiment table. End a branch after its falsifier or bounded null; do not expand a sweep for confirmation.

B3 runtime cache, B4 non-LLM comparison, and B5 TLBxL2 grid are outside the first batch because current evidence gives them less information gain than the translation and attribution gates. They remain `PLANNED_ONLY` unless a later result supplies a specific falsifier requiring them.

## Tier 2 candidate experiments are Window C-owned

E16--E18 require C-owner authorization and C's own terminal/resource/correctness gates. B must not start, supervise, modify, or read C private work to execute them. C outputs retain their own executable context and are never numerically pooled with B.

## Stop and reporting rules

- Stop a branch at its predeclared falsifier or bounded null.
- Report workload, ROI continuity, kernel coverage, realized geometry, provenance, counter conservation, and all outcome branches for every arm.
- Keep all recovered output `SPECULATIVE_DIAGNOSTIC` pending independent policy.
- Preserve B7 partial evidence and retries; do not overwrite successes or restart the historical breadth-first farm.
