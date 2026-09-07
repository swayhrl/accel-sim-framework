# FAST64.1 Second Lower-Cap Qualification Workload Selection

Status: **FROZEN_PRE_TERMINAL_SELECTION**

The second workload for the FAST64.1 lower-cap non-binding qualification is
**GESUMMV in PAPER_IO mode**.  This selection is frozen before any BICG or
GESUMMV cap-comparison row has a terminal result, and must not be revisited
using IO/OO speedup or any other observed performance outcome.

## Source-only selection basis

The approved candidate set in `FAST64_EXPERIMENT_MATRIX.md` is `{btree,
gesummv}`.  The decision uses only the already-frozen payload manifest and
Base/trace characteristics:

| candidate | frozen trace members | frozen trace bytes | source-only disposition |
| --- | ---: | ---: | --- |
| `gesummv` | 1 | 316,381,690 | selected: independent PolyBench vector/matrix payload, nontrivial but cheaper single-kernel qualification case |
| `btree` | 2 | 809,709,439 | retained in FAST12 and later sensitivity roster; not needed to duplicate BICG's multi-kernel qualification shape at this gate |

The source of these counts and hashes is
`generated/FAST64_PAYLOAD_MANIFEST.tsv`, generated before FAST64 IO/OO formal
performance results.  This document makes no claim about the relative DTC
benefit of either candidate.

## Executed comparison identity

The required pair is therefore:

- `GESUMMV / PAPER_IO / FAST64_IO.config / cap 8192 / A1`;
- `GESUMMV / PAPER_IO / FAST64_IO_CAP1048576.config / A1`.

The two configs differ only in the terminal lower-outstanding cap overlay.
Their result comparison must accept no scientific metric difference; the cap
identity field itself is the sole expected difference.
