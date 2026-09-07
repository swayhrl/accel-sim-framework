# Window A checkpoint: motivation only

## Provenance boundary

`EXISTING_MODEL_FACT`: this section was read only from git object
`73d25ebbdd96833ee1ddb8ea42b9017cefbceb75`, specifically the isolated M4C C3 progress checkpoint
documents. C9 did not access Window A's worktree, supervisor, binary, scratch, logs, configs, traces
or objects. No Window A value appears in a C9 accounting formula, latency parameter, capacity choice
or future success target.

## Design implications, not calibration inputs

The checkpoint provides only these qualitative motivations:

1. `EXISTING_MODEL_FACT`: terminal decode controls show a material translation-related headroom between
   generic/paper paging profiles and ideal/disabled controls. This motivates keeping translation
   latency and stall observability in future C reporting.
2. `EXISTING_MODEL_FACT`: at that checkpoint, the paper profile showed lower aggregate TLB-miss counts
   than generic but did not show a corresponding cycle improvement. This demonstrates that miss rate
   is insufficient to judge an optimization.
3. `EXISTING_MODEL_FACT`: paper prefill was nonterminal at the checkpoint. C9 therefore makes **no**
   paper-vs-generic prefill conclusion.

`C9_MODEL_DECISION`: the v1 `HIT_FIRST / MISS_JOIN` policy and local one-accept-per-cycle table are
chosen for semantic correctness and to avoid an unjustified L1-hit serialization. They were not tuned
to reproduce any Window A IPC, cycle, miss-rate, walker or stall number. The N=8 capacity is based on
the paper's small multi-model context plus explicit C9 admission/fallback design, not an A result.

## Mandatory observables implied by the checkpoint

`USER_APPROVED_DIRECTION`: C10/C5 evidence must retain queue/backpressure/latency/stall observables,
not only TLB hit/miss rates. At minimum, future C results must keep the following separable:

| Category | Required observation |
| --- | --- |
| Segment front end | accept rate, port denials, queue depth/wait, admission backpressure and `Lseg` point. |
| completion ordering | L1-first versus Segment-first owner, miss-join duration, late result discard and consistency faults. |
| conventional translation | L1/L2 service and queue intervals, MSHR/PWQ allocation/merge/full waits, walker waits, PWC and PTE timing. |
| architectural outcome | requester critical-path latency/stall plus frontend data/store/atomic exact-once conservation. |
| fair context | arm bit budget, descriptor replication, group/exact/PWC capacity and page-policy class. |

No C9 document combines any Window A count with C4/C7 telemetry, treats the A checkpoint as terminal
paper evidence, or uses it to claim a future C speedup. The checkpoint only prevents the methodological
error “fewer misses implies fewer cycles.”
