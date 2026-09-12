# C14 Path N instrumentation audit

Status: `OBSERVATIONAL_PROXY_READY`

Core branch: `hrl/vm-m4b-c14-criticality-v0` at `290bf7b7`.

## Definitions and intended interpretation

| Field family | Definition | Explicit limitation |
|---|---|---|
| `vm_c14_criticality_pending_requester_*` | translation controller sample of active lookups plus MSHR waiters; total/sample/high-watermark | controller occupancy, not a global GPU critical-path measure |
| `C14_TRANSLATION_EXPOSURE_V1 ... HEAD_BLOCKED_CYCLES` | one cycle in which the current LDST memory-stage head access has a functional translation that is not ready | `LOCAL_LDST_HEAD_PROXY`, not all GPU issue opportunities or a global critical path |
| `TRANSLATION_READY_EVENTS` | the same tracked head access becomes translation-ready | does not prove a later DRAM request is globally exposed |
| `READY_TO_DATA_ADMISSION_*` | cycles from that ready event to successful L1D/bypass admission of the same access | data-admission proxy; deliberately not labelled “memory issue” |

Per-kernel output is keyed by C14's existing object class
(`DATA_WEIGHT`, `DATA_KV_CACHE`, `DATA_EMBEDDING_OUTPUT`, `DATA_UNKNOWN`,
and `PTE_L3`) and is emitted at normal kernel-stat boundaries.  Operator
attribution in the C14 report is an offline join to the immutable accepted
C12 map; the Core does not claim a new semantic operator classifier.

## Non-perturbation contract

- Default is off: `-gpgpu_vm_c14_criticality_telemetry 0`.
- The translation controller only samples existing containers after service;
  no scheduling/retry/ready-cycle value is changed.
- The LDST hook reads the existing functional translation result and exact
  access identity; it adds counters and a non-semantic marker only.
- The unit test compares telemetry off/on for identical controller ready
  cycles and conventional resource outcomes, then verifies the new local
  proxy text and counters independently.
- A C14 trace-replay off/on pair will be retained as the runtime
  non-perturbation receipt before any N value is interpreted.

## Known observability boundary

`vm_translation_requester_latency_cycles_total` is request lifecycle latency,
while `vm_translation_stall_cycles` is accumulated at the LDST memory head.
Neither alone determines whether a translation delay was on the GPU's global
critical path.  C14 N's head-blocked counter intentionally narrows the claim
to a local, attributable proxy and leaves scoreboard, warp scheduler, other
memory requests, and downstream DRAM issue outside its causal scope.
