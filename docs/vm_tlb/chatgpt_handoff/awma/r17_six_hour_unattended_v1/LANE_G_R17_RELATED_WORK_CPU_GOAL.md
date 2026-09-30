# Codex Goal — Lane G / CPU-only
## AWMA R17 graph-search related-work and next-problem consumer V1

Date: 2026-09-30

This is a CPU/source/web/repository-only task. It may run in parallel with Lane F. It must not use CUDA, the GPU lock, node174 simulation, or modify Lane F's worktree.

Execution branch:
`hrl/awma-r17-graph-search-related-work-cpu-v1`

Starting authority:
`5ff0287ce45c3909d53ac44975f6fa488664b085`

## Purpose

Do two bounded rounds without user review between them:

1. Deepen the novelty/nearest-neighbor boundary for R17 resident GPU graph search.
2. If and only if that review makes R17 obviously crowded or likely software-complete, identify at most **one** materially different next problem candidate with a real public input path and a falsifiable first experiment.

Do not create a second candidate merely to fill time.

## Round A — graph-search nearest-neighbor map

Read full text or key primary-source sections where available for:
- CAGRA
- GPU-Accelerated Algorithms for Graph Vector Search (2026)
- Jasper
- BOA
- GrAND
- earlier relevant GPU graph ANN systems / GPU beam-search work found through citations.

Also inspect:
- NVIDIA cuVS stable v26.08.01 source
- current main only for capability deltas
- current Jasper source at a pinned commit.

Produce a matrix separating:
- single-query latency
- low-batch throughput
- multi-CTA / multi-trajectory execution
- persistent kernel / launch suppression
- visited-set/hash organization
- distance-computation tiling/vectorization
- graph compression/layout
- prefetch/cache/locality
- adaptive beam/search-width algorithms
- dynamic update support.

For every proposed “remaining problem,” identify the closest existing capability first.

Do not reproduce performance rankings across incomparable datasets/GPUs.

## Round B — mechanism boundary, no mechanism claim

From source and papers, answer:

- Does any existing work already directly attack the sequential discovery of the next useful node/edge on GPU without merely increasing search work?
- Which techniques alter the ANN algorithm/recall versus preserve the same graph/search semantics?
- Is low-query parallelism already intentionally addressed by CAGRA/Jasper strongly enough that the remaining likely residual is only necessary distance math?
- What observables can Lane F use to distinguish these cases without invasive tracing?

Prepare:
- `R17_RELATED_WORK_MATRIX.tsv`
- `R17_NOVELTY_BOUNDARY.md`
- `R17_NATIVE_INTERPRETATION_GUIDE.md`

This is advisory; do not change Lane F's preregistered experiment.

## Round C — at most one backup candidate

Only after Round A/B.

Search 2026 primary sources for a materially different GPU/AI workload issue that:
- is not one of the closed Round16 mechanisms;
- has a real public workload/input path;
- is not already directly covered by a strong software/compiler system;
- admits a cheap Native falsification on RTX4080 or CPU/source authority gate;
- has a clear nearest-neighbor comparison.

Candidates must not be selected merely because a model/data asset already exists.

If none meets the bar, explicitly conclude:
`NO_SECOND_CANDIDATE_QUALIFIED`.

If one qualifies, write one problem card only:
`R18_<NAME>_PREPARATION.md`

Do not write or authorize an execution Goal for it.

## Scope rules

No CUDA.
No model/data download larger than small metadata/source files.
No new trace.
No credentials.
No node164 bulk scan.
No 174.
No hardware design.
No changes to accepted experiment packs.

## Deliverables

Under:
`docs/vm_tlb/literature_notes/awma/rounds/`
and
`docs/vm_tlb/literature_notes/awma/problem_cards/`

Add a compact Round18-preparation note if appropriate and update the literature README with current status.

Push/fetch-back verify branch and STOP.
