# Current state

## Track A status

`M1_VM_CORE_FOUNDATION`: **PASS**.

`M2_FUNCTIONAL_TRANSLATION`: **PASS — repaired M2-RF accepted**.

`G3-0`: **PASS**.

`G3-1 — PTE backend / physical request contract`: **PASS**.

`G3-2A — address provenance`: **PASS — CASE A**.

`G3-2B — generic trace-width extension`: **PASS**.

`G3-2 — real PTE L2/DRAM integration`: **PASS**.

`G3-2C — radix-prefix PTE identity`: **PASS — independently accepted**.

`G3-3 — generic PWC`: **PASS — independently accepted**.

## Accepted current source anchors

Core/GPGPU-Sim:

`1b18b3c5da6e5ba22e4a03c20e3adce498311336`

Framework/Accel-Sim evidence:

`a3af1f34b4e6fcac4f43faf8d80d8a914eb34958`

Branches:

- Core: `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- Framework: `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

## Accepted architecture

### Address contract

- raw/coalesced trace address is simulator `SimVA`;
- translated data address is `SimPA`; preserve both;
- current generic resident mapping is identity-like: `SimPA == SimVA`;
- generic trace/backend width is configurable;
- current generic baseline uses 56 bits;
- retained 49-bit configuration is for later paper-specific use;
- generic SimVA is never silently masked, truncated or canonicalized;
- requests wider than configured width are correctness stops.

### Translation path

Current functional/timing path is:

`coalesced SimVA -> per-SM L1 TLB -> shared L2 TLB -> translation MSHR -> PWQ -> walker -> PWC/intermediate PTE -> physical PTE request -> real ICNT/L2/DRAM -> matching walker -> L2/L1 fill -> waiter wakeup/replay -> SimPA -> data-cache path`

Accepted invariants include:
- one active translation walk per key;
- registered pending waiter retries do not re-probe/reconsume TLB resources;
- new waiters perform their first lookup and may merge;
- PTE requests are physical, translation-bypassing and non-recursive;
- PTE responses preserve request/walk identity;
- no data-cache request issues before translation is READY;
- store/atomic side effects remain exact-once;
- TLB/PWC state persists across ordinary kernels in the simulated context.

### PTE hierarchy

The generic page-table hierarchy is a project `MODELING_DECISION`.

For each page-size class:

`B = VA bits - page-offset bits`, `L = levels`, `r = ceil(B/L)`, `top = B-r*(L-1)`.

Accepted 4-level examples:
- 56-bit / 64KB: `[10,10,10,10]`
- 56-bit / 2MB: `[8,9,9,9]`
- 49-bit / 64KB: `[6,9,9,9]`
- 49-bit / 2MB: `[7,7,7,7]`

PTE identity at each level uses the VPN prefix through that level. Physical PTE subranges are deterministic, non-overlapping and overflow-checked.

### PWC

Accepted generic PWC:
- caches intermediate/non-leaf PTEs only;
- key = `(ASID, page-size class, level, VPN prefix)`;
- `OFF`;
- `FINITE`: 128 entries, fully-associative LRU;
- `IDEAL`: unbounded/no eviction diagnostic;
- leaf PTE always uses the accepted real PTE L2/DRAM path;
- default lookup service is configurable one-cycle generic service with no invented PWC port bottleneck.

The 128-entry seed is `REFERENCE_OTHER_PAPER`, not a Segmentation-paper or NVIDIA fact.

## G3-2C / G3-3 acceptance evidence

Directed hierarchy tests prove intended upper-level prefix sharing, leaf separation, 49/56-bit layouts, 64KB/2MB class separation, physical-range safety, original raw SimVA preservation and non-recursive PTE behavior.

Directed PWC tests prove:
- OFF: two related cold 4-level walks issue 8 PTE memory requests;
- FINITE/IDEAL: same pair issues 5 requests, with three intermediate PWC hits;
- leaf entries never hit/insert in PWC;
- partial sharing, deterministic finite LRU and 2MB behavior pass.

Integrated revalidation:
- complete BFS PWC OFF: PTE `28/28`;
- complete BFS FINITE: PTE `19/19`, PWC accesses/hits/misses `21/9/12`, nine skipped intermediate PTE requests;
- zero PTE response misassociation;
- final MSHR/PWQ/walker state quiescent;
- LUD VM-disabled and VM-ideal remain exactly `139766` cycles.

G3-2C/G3-3 are accepted as generic simulator behavior, not target-paper exact page-table/PWC behavior.

## Remaining M3 work

The current TLB path has finite lookup ports but still needs explicit non-zero L1/L2 lookup service latency before M3 can be called timing-realistic.

The final authorized continuous target is:

`G3-4A page-size foundation -> G3-4B TLB lookup timing -> G3-5 latency decomposition/causality -> G3-CLOSEOUT -> M1_M3_VM_BASELINE_CLOSEOUT`

Specification:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M3_G3_4_G3_5_FINAL_CLOSEOUT.md`

After every internal gate PASSes, Codex may continue automatically. Stop only on a hard correctness/provenance failure or after final macro closeout.

## Parameter evidence boundary

Target Segmentation paper facts remain separate from generic M3 choices.

Known paper-facing items already recorded include 64KB paging, 32-entry fully-associative L1 TLB, 768-entry/16-way L2 TLB and 16 walkers. The target paper does not establish our generic radix split, PWC organization, MSHR/PWQ sizes, generic 56-bit trace contract, or L1/L2 TLB lookup latencies.

Generic/reference seeds for final M3 include:
- current generic VA width 56: `MODELING_DECISION`;
- balanced radix-prefix hierarchy: `MODELING_DECISION`;
- intermediate-only PWC: `MODELING_DECISION`;
- 128-entry PWC: `REFERENCE_OTHER_PAPER`;
- L1/L2 TLB lookup latency seed 10/80 cycles: `REFERENCE_OTHER_PAPER` / generic `MODELING_DECISION` until stronger evidence exists.

## Scope exclusions

M1-M3 still exclude:
- page fault/migration/UVM oversubscription;
- MCM/chiplet placement;
- Segmentation;
- target-paper L2-TLB sub-entry/coalescing;
- synthetic KV injection;
- multi-ASID physical-separation claims.

## STOP boundary

STOP immediately on:
- TLB lookup polling/repeated port consumption while service is pending;
- hierarchy/PTE/PWC collision or nondeterminism;
- application/PTE physical-range overlap or overflow;
- recursive PTE translation;
- response misassociation/request loss;
- duplicate wakeup/store/atomic side effect;
- M1/M2 regression;
- deadlock/unexplained nondeterminism;
- source/provenance ambiguity;
- a materially new architecture decision outside the authorized final-stage spec.

After `M1_M3_VM_BASELINE_CLOSEOUT` PASS, STOP before M4B/Segmentation/sub-entry/synthetic-KV/new AI-aware mechanisms.