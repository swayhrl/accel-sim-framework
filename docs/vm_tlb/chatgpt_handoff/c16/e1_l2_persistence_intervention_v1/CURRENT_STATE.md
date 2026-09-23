# C16 E1 Targeted L2 Persistence Intervention — Current State V1

## Accepted upstream closure

Natural-reuse producer:

`hrl/c16-e1-natural-reuse-residency-109-v1@ccfdc89d517766d12588ee131818efe341c7e17c`

Independent consumer:

`hrl/c16-e1-natural-reuse-residency-consumer-174new-v1@4f9242d177220721cb9e669aad5dd9e29f04407d`

Independent classification:

`CASE_B_WITH_CASE_D_ROLE_DEPENDENCE`

## Closed observations

1. Immediate post-pressure reuse:
   - AWQ q/down/up all refill in one call.
   - K2 target DRAM falls to tens of KiB.
   - RAW down/up stay near ~135.8 MB DRAM.

2. Natural full-model reuse:
   - AWQ layer0 up_proj target DRAM is ~49 MB at natural D0/D1/D3.
   - This is outside the exact isolated layer0 WARM-to-DENSE bracket on the dense side.
   - layer0 down_proj DRAM is slightly beyond isolated DENSE while timing remains within the bracket.
   - layer14 up_proj reproduces the natural ~49 MB DRAM pattern, but has no exact isolated layer14 WARM/DENSE authority.

3. Capacity-dose:
   - q/down/up sampled first-trigger ordering is role-dependent.
   - sampled triggers occur earlier than nominal residual-L2 capacity.
   - therefore nominal capacity alone is insufficient; role/kernel/access-policy effects remain.

4. Optional RAW BF16 full-model control:
   - natural execution fits without offload/backend changes;
   - layer0 up_proj remains ~136 MB DRAM.

## Hardware capability already visible in accepted raw NCU device attributes

RTX4080 device attributes observed in accepted raw NCU evidence:

- L2 size: `67,108,864 B`
- max persisting L2 set-aside: `46,137,344 B`
- max access-policy window: `134,213,632 B`

Accepted layer0 up_proj AWQ state:

- qweight: `33,947,648 B`
- qzeros: `265,216 B`
- scales: `1,060,864 B`
- total packed module state: `35,273,728 B`

The dominant qweight tensor therefore fits inside the observed persisting-L2 limit and access-policy-window limit.

## Next question

The next stage is a direct real-hardware policy intervention:

> If the dominant compressed qweight region is explicitly given CUDA persisting-L2 treatment, can natural full-model decode retain more of that state across token reuse and reduce target DRAM/timing relative to both baseline and a matched unrelated-persistence control?

This is stronger than another pressure microbenchmark because the full 28-layer model still executes naturally between target occurrences.

This stage does **not** yet implement or simulate a new cache mechanism.

No NVBit/full address trace is required.


---

## Producer completed; independent consumer must preserve a decision-rule divergence

Producer completed at:

`hrl/c16-e1-l2-persistence-intervention-109-v1@4c0e6b998528e425578cacf5912bbcc4ff3bfaf6`

Producer-scoped final state:

`MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW`

Producer evidence is internally consistent with:
- qualified CUDA persisting-L2 API;
- exact contiguous qweight windows;
- strong isolated positive control;
- strong, target-specific natural timing benefits;
- no natural point crossing the preregistered 20% DRAM materiality gate;
- budget sweep first tested material timing point at 16 MiB;
- no automatic mechanism implementation.

Consumer prep completed at:

`hrl/c16-e1-l2-persistence-intervention-consumer-174new-v1@1fc087f09f24adfbb7a404c3c4d19861bfcdd96b`

### Critical decision-rule divergence

The producer and the pre-data consumer prep operationalized the ambiguous final-state wording differently.

Producer rule:
- `MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW` if there is material timing support and target-specific support.

Frozen consumer rule:
- ready only if at least one same primary point has:
  - MATERIAL_TIMING_BENEFIT
  - MATERIAL_DRAM_BENEFIT
  - TARGET_SPECIFIC

The producer reports no primary point with MATERIAL_DRAM_BENEFIT.

Therefore the independent consumer must **not** edit or weaken its frozen pre-data rule after seeing producer results.

It must:
1. compute its strict consumer final state exactly as frozen;
2. preserve producer final state separately;
3. emit an explicit `DECISION_RULE_DIVERGENCE` artifact;
4. state that the divergence is methodological/operationalization, not a raw-evidence mismatch;
5. defer project-level mechanism authorization to ChatGPT review.

Do not silently harmonize the two labels.

### Real-artifact policy-receipt packaging mismatch

The producer raw policy authority is split across:
- raw run / PROFILE PASS object:
  - condition
  - policy_receipt
  - qweight_regions
  - semantic/token identity
- `RAW_CUDA_CAPABILITY_AND_CENSUS.json`:
  - runtime/device capability
  - accepted/runtime capability cross-check
  - qweight census
- low-level policy receipt:
  - requested/actual set-aside
  - stream value
  - access-policy window
  - reset flags
  - operations_before/after

The original synthetic consumer validator expected one already-rich receipt object.

This is a consumer packaging issue, not a producer scientific failure.

During resume, 174-new should build a deterministic normalized receipt from these raw authorities while preserving source SHA/provenance.

Important:
- do not invent a set-aside alignment rule;
- runtime query-back `actual_setaside_bytes` is authority;
- require `requested <= actual <= runtime max` where CUDA rounds upward, or exact requested==actual when observed;
- record the observed rounding explicitly;
- BASELINE and SETASIDE_ONLY do not need an invented target qweight window;
- producer budget receipts use condition `BUDGET_L0_UP`; normalize this only as the bounded partial-budget L0_UP intervention after verifying budget/window/hitRatio identity;
- all normalization must be deterministic from raw evidence and source SHAs.

No node109 rerun is requested.
