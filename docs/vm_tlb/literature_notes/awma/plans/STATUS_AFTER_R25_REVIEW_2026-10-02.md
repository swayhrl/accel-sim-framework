# Status after R25 review

Date: 2026-10-02.

This supersedes `STATUS_AFTER_R25_BROADER_VALIDATION_AUTHORIZATION_2026-10-02.md` for current execution state.
Historical experiment packs and labels are not rewritten.

## R25

Execution:
`2581b6592e79691c4c3e57fe31a339eba9f6b7dd`

Accepted decision:
`R25_TILED_CAPACITY_TIME_TRADEOFF`

Accepted empirical interpretation:
- stronger C1 one-full-buffer software comparator is valid and beneficial on both D0/H0;
- S2 removes the remaining full tied-weight gradient and gives additional causal target-peak reductions of 535.777 MiB on D0 and 1350.030 MiB on H0;
- capacity response therefore crosses Qwen discovery and independent Llama holdout lineages;
- S2 vs C1 timing is D0 BENEFIT and H0 REGRESSION under the frozen group classifier;
- H0 absolute regression is only ~0.050 ms / 0.130%, so do not describe it as a large slowdown;
- timing benefit does not generalize across models;
- no profiler/simulator/hardware work was required.

Detailed review:
`docs/vm_tlb/literature_notes/awma/empirical/R25_TIED_WEIGHT_BROADER_VALIDATION_REVIEW_2026-10-02.md`

## Current execution state

- Lane G / node109: R25 COMPLETE / STOP.
- R24 remains COMPLETE / STOP.
- R23G remains COMPLETE / STOP.
- Lane F / R22F1 remains STOP.
- Lane E / R22E remains STOP.
- R20 remains CLOSED.
- No AWMA GPU task is currently authorized.
- No node174/Accel-Sim task is currently authorized.
- No hardware/PPA task is authorized.

All CUDA/JIT/profile work still uses:
`/data/c16/locks/c16_gpu_campaign.lock`.

Node164 remains durable large-data authority.

## Next research boundary

Do not reopen R25 with tile tuning, extra microbenchmark inputs, or H0 performance tuning.

The next justified question, if authorized, is production-integration value:

> Does the capacity-oriented S2-like path change a real training memory-feasibility boundary or useful batch/context headroom relative to the strong C1 one-full-buffer software path, while preserving acceptable multi-step numerical/training behavior?

A future integration-oriented experiment should:
- keep C1 as the speed-oriented comparator;
- keep S2 as a capacity-oriented opt-in policy, not an unconditional default;
- use a realistic training configuration where saved capacity can be converted into a concrete capability;
- measure actual feasible batch/context/model-state headroom, not only allocator deltas;
- include limited multi-step/training-quality evidence before any training claim;
- not introduce hardware unless a later software-integrated residual remains.

No such execution is launched by this status file.
