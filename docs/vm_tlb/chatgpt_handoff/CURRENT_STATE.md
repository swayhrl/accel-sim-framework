# Current state — Track A

## Review result

`M1_M3_VM_BASELINE_CLOSEOUT`: **PASS — independently accepted by ChatGPT**.

Accepted final source anchors:

- Core/GPGPU-Sim: `5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`
- Framework/Accel-Sim evidence: `47dde5767af8d30b892c7d63d932455644b7cf3a`
- Core branch: `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- Framework branch: `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

## Accepted reusable single-GPU VM baseline

The accepted generic default is:

- raw/coalesced `SimVA` preserved; translated `SimPA` preserved separately;
- current resident mapping remains identity-like (`SimPA == SimVA`);
- configurable virtual-address width; generic M3 default = 56 bits;
- 64KB page size per run, with separately validated 2MB mode;
- 32-entry fully associative per-SM L1 TLB;
- 768-entry, 16-way shared L2 TLB;
- 32 translation MSHR/PWQ entries;
- 16 walkers;
- physical, non-recursive PTE traffic through real interconnect/L2/DRAM;
- balanced radix-prefix generic page-table identity;
- FINITE-128 fully-associative LRU intermediate-only PWC;
- leaf PTEs always use the real PTE memory path;
- explicit TLB lookup service timing: L1=10 cycles, L2=80 cycles for the generic baseline;
- zero lookup latency and fixed-latency PTW retained only as diagnostics.

The radix split, PWC organization, 128-entry PWC seed and 10/80-cycle lookup seed are generic/reference modeling choices, not exact claims about NVIDIA hardware or the Segmentation paper.

## Accepted correctness/timing invariants

- one active translation walk per translation key;
- registered pending waiter retries do not re-probe or re-consume TLB ports;
- in-flight L1/L2 lookup service does not poll/re-probe while waiting;
- new waiter UIDs perform their first normal lookup and may then merge;
- port is consumed once at lookup launch;
- data-cache access waits until translation is READY;
- PTE requests are physical, translation-bypassing and non-recursive;
- PTE request/response identity remains exact;
- store/atomic replay remains exact-once;
- ordinary kernel boundaries preserve TLB/PWC state in the simulated context;
- final MSHR/PWQ/walker/lookup state quiesces.

## Accepted validation highlights

- full M1/M2/G3 directed regression: PASS;
- one-kernel LUD disabled and ideal identity are identical: 23,977 cycles, IPC 0.8205;
- real 64KB and 2MB one-kernel LUD replays: PASS;
- complete BFS real-PTW integration: PASS;
- BFS generic baseline observes 156 L2-TLB probes (132 hits / 24 misses), 7 walks, 17 MSHR merges, and 9 PWC-skipped intermediate PTE requests;
- sensitivity matrix covers L2-TLB capacity, MSHR entries, walkers, PWC modes, fixed-vs-real PTW, 64KB-vs-2MB, and zero-vs-nonzero lookup timing;
- latency accounting separates requester intervals from unique MSHR/walk/PTE-memory work and does not multiply shared PTW work by waiter count.

## Scope boundary

M1-M3 are now frozen as reusable infrastructure. They intentionally do not include:

- M4B / LLM baseline integration;
- Segmentation;
- L2-TLB sub-entry/coalescing;
- synthetic KV pressure;
- page fault/migration/UVM;
- MCM/chiplet behavior;
- multi-ASID physical-separation claims;
- mixed-page placement/promotion policy.

The LUD/BFS sensitivity results validate infrastructure and causality only. They are not paper-facing LLM characterization; capacity/MSHR/walker sweeps on the one-kernel LUD case are intentionally flat because that trace contains only one cold translation.

## Integration dependency

Track B is currently performing `M4A_MERGE_PREP` on the accepted formal LLM traces. Do not merge A/B or start M4B until Track B has passed its merge-prep review.

After Track B PASS, ChatGPT will issue a new integration handoff for a fresh Framework integration branch. The final integrated Core must start from this accepted Track-A Core:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

## Current authorization

**STOP / HOLD.** No additional Track-A implementation is authorized now.

Do not start M4B, Segmentation, sub-entry/coalescing, synthetic KV, faults/migration/UVM/MCM, or branch integration without the next ChatGPT handoff.
