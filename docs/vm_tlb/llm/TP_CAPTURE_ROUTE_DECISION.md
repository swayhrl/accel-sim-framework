# TP=4 capture-route decision

Status: M4A pre-capture fixup. No capture has run.

| Criterion | Route E: real TP=4, trace rank 0 | Route A: one-rank emulation | Full model on one GPU |
|---|---|---|---|
| Node | 4 same-model SM86 GPUs | 1 SM86 GPU | 1 SM86 GPU |
| Weights/operators | framework-sharded runtime model and real collectives | only rank-local QKV/MLP shapes and rank shard; row-parallel peers are explicit placeholders | all model weights/operators |
| NVBit plan | only rank0 process receives injection | one process | one process |
| Collective behavior | rank0 NCCL traffic retained and tagged; no silent filtering | not real; must be labelled placeholder | absent/incorrect for TP=4 |
| Trace relation to paper | strongest self-capture candidate | approximation requiring approval | rejected as formal workload |
| Fidelity label | `PAPER_COMPATIBLE_SELF_CAPTURE` | `DOCUMENTED_APPROX` only after approval | rejected |
| Operational risk | higher: 4-GPU availability, matching image, NCCL, rank-selective tracing, larger cost | lower rental complexity but incomplete distributed semantics | low complexity but invalid workload |
| Simulator handoff | rank0 raw trace needs an explicit NCCL compatibility/retention decision | local partition trace needs approved placeholder policy | not eligible |

## Decision

Prefer Route E for the formal candidate if a 4 x SM86 node is reasonably
available. It executes actual TP=4 and captures only the rank intended for the
single-partition simulation. The exact paper implementation is unavailable, so
the result must still be labelled self-capture rather than author-exact.

Route A is intentionally not selected automatically. It becomes viable only
after the user/ChatGPT approves a documented approximation and provides or
approves an immutable local-rank weight-shard preparation policy. Its required
local shapes are recorded in `WORKLOAD_CONTRACT.md`; full-model fallback is
forbidden. This decision creates no rental authorization.
