# START HERE — AWMA R17 six-hour unattended continuation

Date: 2026-09-30

This handoff is designed for an unattended block. Do not stop for ordinary engineering issues or after every intermediate result. Continue through the bounded stages below until a preregistered scientific STOP condition is reached.

## Lane assignment

- **Lane F / node109 / RTX4080**: primary R17 resident graph-search Native screen and bounded diagnosis.
- **Lane G / CPU/source only**: parallel related-work / source-boundary consumer for the same R17 question plus at most one future backup problem card.
- **Lane E / 174-new**: STOP. No Accel-Sim work is authorized.

109 has one RTX4080. Only Lane F may use CUDA in this handoff, and every CUDA/NSYS/NCU/build/search job must hold:

`/data/c16/locks/c16_gpu_campaign.lock`

Lane G must stay CPU/source-only and must not acquire the GPU lock.

## Scientific parent

Literature/problem-screen authority:
`5ff0287ce45c3909d53ac44975f6fa488664b085`

Read:
- `docs/vm_tlb/literature_notes/awma/rounds/2026-09-30_ROUND_17_RETRIEVAL_PROBLEM_SCREEN.md`
- `docs/vm_tlb/literature_notes/awma/problem_cards/R17_GPU_RESIDENT_GRAPH_SEARCH_PREPARATION.md`

Round16 final closeout remains authoritative for what must not be reopened.

## External baseline authority frozen for this handoff

Runtime baseline:
- NVIDIA cuVS PyPI stable release: `cuvs-cu12==26.8.1`
- source tag `v26.08.01`, commit `25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab`

Current-main source audit reference only:
- `NVIDIA/cuvs@d3df668c77da45bce9f7ff80b6adc62f91d4ba01`
- do not silently run current main after timing begins.

Relevant stable-source facts:
- AUTO chooses MULTI_CTA at low max_queries and SINGLE_CTA only after the occupancy threshold for itopk<=512.
- MULTI_CTA derives multiple CTAs/query from the requested global itopk/search width.
- persistent search exists but is supported only with SINGLE_CTA.
- persistent mode does not expose the normal per-query executed-iteration observer.

The execution lane must rebind these identities locally before claiming them.

## Unattended behavior

Ordinary issues such as environment creation, package conflicts, wrapper files, download resume, build fixes, profiler CLI syntax, deterministic manifest reconstruction, or Git transport problems: solve and continue.

Stop without user input only when a scientific contract changes, real input/quality cannot qualify, the strong baseline closes the problem, or the bounded Goal reaches its final classification.

Do not wait for the user, poll for approval, or keep the GPU busy merely because time remains.

## General research rule

```
real input + mature baseline
-> quality/semantic qualification
-> natural timing
-> existing software/mode counterfactuals
-> bounded profiling/localization
-> sealed holdout
-> review
```

Large traffic, random-looking addresses, low occupancy, or a profiler stall percentage alone never authorizes hardware.

## Branch isolation

Lane F execution branch:
`hrl/awma-r17-graph-search-native-109-v1`

Lane G CPU branch:
`hrl/awma-r17-graph-search-related-work-cpu-v1`

Neither lane merges the other during execution.

## Closure

Each lane publishes an exact commit/tree, fetch-back verification and clean worktree, then STOP.

No lane may auto-start 174, a hardware mechanism, R102, VLA, CCE/Liger, or a second GPU workload.
