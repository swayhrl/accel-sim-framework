# C16 OLMoE fresh static audit + formal capture — node109 V35

## Execution mode

Execute in **GOAL MODE** on node109 using the normal Linux producer workflow.

This is a continuation of accepted V34 evidence. Do not restart model-selection, input-policy, capacity-planning, or target-selection work unless an exact identity check fails.

Suggested implementation branch:

`hrl/c16-olmoe-static-audit-formal-109-v35`

## Accepted upstream

V31 authorization:
- branch: `hrl/c16-olmoe-third-moe-authorization-174new-v31`
- HEAD: `4013582e5cedef3e2ecaf7b7c74d9bb45a1af8ce`
- decision: `C16_OLMOE_THIRD_MOE_AUTHORIZATION_174NEW_V31_PASS`

V34 producer continuation:
- branch: `hrl/c16-olmoe-s2-producer-109-v34`
- HEAD: `ab26365dc663268b0799818db6687ed466e8c925`
- decision: `C16_OLMOE_S2_PRODUCER_109_V34_FAIL_CLOSED_FRESH_STATIC_PATH_AUDIT_UNAVAILABLE`

Accepted V34 facts:
- exact prospective common input source closed
- OLMoE frozen S2/T2048 IDs closed
- native BF16 full-resident execution on RTX4080 closed
- S2/D32 native execution closed
- Layer1 decode32 natural top-8:
  `[58, 59, 47, 51, 25, 15, 12, 48]`
- natural expert58 is rank-0 at that state
- target:
  `OlmoeSparseMoeBlock -> experts[58] -> OlmoeMLP.down_proj -> torch.nn.Linear`
- input shape `[1,1024]`
- weight shape `[2048,1024]`
- output shape `[1,2048]`
- BF16
- lossless dynamic weight/input/output attribution
- exact same-module replay bitwise equal
- V34 blocker is only absence of a fresh actual-kernel static instruction/path selector

Do not reuse Q30/DeepSeek static indices/selectors.

## Asset residency

Node164 remains sole authority.

Expected retained node109 active replica:

`/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

Before transfer:
1. check this replica
2. verify exact required subset against node164 receipt
3. reuse it if hash/size closed
4. refresh from node164 only if missing/incomplete/mismatched

Do not delete a valid OLMoE replica at Goal end.

## Stage 0 — frozen-input and target re-establishment

Reuse V34 frozen S2 input authority. Verify its committed hashes before use.

Re-establish the V34 runtime family:
- Python 3.12.3 or exact documented equivalent
- torch 2.7.1+cu126
- transformers 4.55.0
- modeling_olmoe SHA `413888fc3be7e037727586f25900b629cc5dbc06b227a4f0d42c67cacb597bc7`

Run the exact S2/D32 state from frozen IDs and require:
- same layer/decode target
- natural top-8 IDs exactly close or a scientifically explained deterministic identity delta
- expert58 remains naturally selected for the target state
- exact module replay remains bitwise equal

If the exact target identity no longer closes because runtime/code identity changed, repair the environment to the accepted V34 runtime before changing scientific target.

## Stage 1 — static-inspection toolchain discovery/bootstrap

The V34 blocker was:
`C16_OLMOE_V34_FRESH_STATIC_PATH_AUDIT_UNAVAILABLE`

Do not stop merely because `nvdisasm`/`cuobjdump` are absent from PATH.

### Route A — external CUDA object/SASS tools

Search boundedly for usable tools under:
- current PATH
- `/usr/local/cuda*/bin`
- `/opt/**/cuda*/bin`
- existing user-local CUDA/toolkit locations
- existing C16 toolchain/cache locations

Look for:
- `nvdisasm`
- `cuobjdump`

If found:
- record absolute path
- record version
- SHA256 the binary
- prove it executes normally
- do not change CUDA driver/runtime merely to use it

If absent, provision a **user-local** official NVIDIA CUDA static-inspection toolchain under a durable path such as:

`/data/c16/toolchains/cuda-static-audit/<toolkit-version>/`

Requirements:
- obtain only the minimum official CUDA toolkit components needed for `nvdisasm`/`cuobjdump` when feasible
- exact package/source/version must be recorded
- verify downloaded package/binary hashes where available
- do not globally replace the driver
- do not mutate the active torch CUDA runtime
- avoid a full multi-GB toolkit install when a bounded command-line-tools extraction is possible

Routine network/package-manager issues should be solved and continued.

### Route B — independent NVBit static-introspection fallback

If Route A cannot be made usable or cannot map the actual cuBLAS-backed function unambiguously, do not stop immediately.

Build a **separate static-introspection utility** from the already accepted official NVBit 1.7.7.1 scaffold/source. It must be independent of the dynamic warp trace output and must inspect the actual loaded target function's static instruction stream before formal tracing.

The utility must emit for every static instruction in the selected actual function:
- function/module identity
- static instruction index / PC offset
- opcode
- operand types
- memory-space classification where available
- address/source operand register(s)
- load/store direction
- width/vector information where available
- raw instruction/string representation exposed by NVBit

This route is acceptable only if the actual target function and module/code-object identity are tied to the replay execution and the resulting selector is deterministic.

Prefer Route A plus Route B cross-check when both are available.

Stop only if neither route can establish a defensible fresh selector for the actual target function.

## Stage 2 — actual kernel/module/function identity

Using the exact expert58 replay:
- identify the actual CUDA function launched by the `down_proj` operation
- identify the owning module/code object/library as precisely as runtime interfaces permit
- record mangled function name and demangled form if available
- record grid/block dimensions
- record function occurrence needed to isolate the target replay
- record module/library path/hash or equivalent code-object identity evidence

NSYS, CUDA callbacks, NVBit function enumeration, or other bounded runtime evidence may be used to establish function identity.

Do not equate Python module identity with CUDA function identity.

## Stage 3 — fresh static path audit

For the exact selected CUDA function, produce a fresh static map.

At minimum classify:
- direct GLOBAL load/store MREF instructions
- LDGSTS instructions whose source is GLOBAL, if any
- other address-bearing paths that the tracer must cover
- non-address-bearing instructions excluded from capture

For every selected memory instruction persist:
- static index / PC offset
- opcode
- memory space
- load/store
- address source register or exact operand selector
- access width if derivable
- source of the classification: `nvdisasm`, `cuobjdump`, NVBit static API, or cross-check

The selector must be derived from this OLMoE/cuBLAS function itself.

No Q30/DeepSeek static selector reuse.

Fresh static audit PASS requires a complete deterministic selected-set definition.

## Stage 4 — warp-regsource canary

Use the validated C16 warp-regsource lifecycle, with the fresh OLMoE selector.

For a bounded subset of selected static instructions:
- fresh process/output root
- clear inherited `C16_*` and `CUDA_INJECTION64_PATH`
- exact function selector
- exact function occurrence
- exact static instruction selector
- SASS-derived or independently static-derived source address register
- sufficient capacity
- terminal closure
- drop=0
- overflow=0

Tie dynamic addresses in the canary to same-process:
- EXPERT_DOWN_WEIGHT
- EXPERT_DOWN_INPUT
- EXPERT_DOWN_OUTPUT
- OTHER_OR_UNCLASSIFIED

Require the canary to prove that the fresh selector actually observes the intended replay path.

## Stage 5 — complete formal capture

After canary PASS, capture one formal OLMoE expert58 down-projection anchor.

Suggested run identity:

`C16R_olmoe-1b-7b-0125-instruct_s2-text_decode_nvbit-warp-mref-shard_v35-l1-d32-natural-expert58-down_<timestamp>_<suffix>`

Formal scope:
- exact natural S2/D32-derived expert58 replay
- one independently replayed shard per selected static memory instruction
- complete selected static set
- executed/zero partition proven
- drop=0
- overflow=0
- terminal closure
- same-process ADDRESS_CONTEXT
- typed membership

If initial capacity is insufficient for any shard:
- do not formalize overflowed shard
- re-capture only affected shard(s) in a fresh recovery root with larger capacity
- formal set must contain only clean zero-overflow shards

Do not invent global temporal ordering across shards.

## Stage 6 — formal analysis

Report at least:
- selected static count
- executed vs zero
- active-lane events total
- per-executed-shard event distribution
- per-shard unique 128B-line distribution
- per-shard unique 4K/64K/2M-page distributions
- typed event membership fractions:
  - EXPERT_DOWN_WEIGHT
  - EXPERT_DOWN_INPUT
  - EXPERT_DOWN_OUTPUT
  - OTHER_OR_UNCLASSIFIED
- full-scope result

Do not construct:
- cross-shard VA union
- cross-shard chronology
- reuse distance
- cache/TLB causality

## Stage 7 — serial transfer/admission/ACK

Mandatory:

`FORMAL_ADMISSION_CONCURRENCY=1`

Perform:
- source manifest
- node164 transfer
- destination verification
- catalog admission
- positive ACK

No second OLMoE operator is required after one clean rank-1 anchor.

## Stage 8 — profiler evidence

NCU/NSYS evidence is optional for this V35 closure.

Do not block formal admission merely because NCU is unavailable.

If profiler evidence is collected:
- preserve raw units
- type it explicitly
- mark cross-lineage status `NOT_COMPARABLE` unless units/configuration actually close

## Stage 9 — third-lineage handoff

Produce the exact fields needed for a later independent 174-new Q30+DeepSeek+OLMoE consumer:
- model/revision
- input authority
- scenario/layer/decode state
- natural top-8 IDs/weights
- expert58 selection
- target semantic class
- input/weight/output dimensions
- CUDA function/module/grid/block identity
- static selected set
- executed/zero partition
- events
- per-shard page/line distributions
- typed membership fractions
- manifest/verification/catalog/ACK hashes

Do not declare the three-lineage common result in V35.

## Tool/model retention at cleanup

At Goal end:
- release GPU lock
- unload model from GPU
- remove transient scratch
- verify no stale profiler/NVBit/CUDA process
- return GPU to expected baseline

Retain:
- valid OLMoE node109 active replica
- useful user-local CUDA static-audit toolchain created under `/data/c16/toolchains`, with receipt/version/hash evidence

These remain replicas/tools, not node164 authority.

## Required review pack

Create:

`docs/vm_tlb/review_packs/C16_OLMOE_STATIC_AUDIT_FORMAL_109_V35/`

Include at least:
- `UPSTREAM_V34_AUTHORITY.json`
- `ASSET_REPLICA_RECEIPT.json`
- `STATIC_TOOLCHAIN_RECEIPT.json`
- `KERNEL_IDENTITY.json`
- `STATIC_PATH_AUDIT.json`
- `STATIC_SELECTOR.tsv`
- `DYNAMIC_CANARY_AUDIT.json`
- `FORMAL_SUMMARY.json`
- `FORMAL_SHARD_SUMMARY.tsv`
- `ADDRESS_MEMBERSHIP.json`
- `ADMISSION_ACK.json`
- `NCU_TYPED_EVIDENCE.json`
- `THIRD_LINEAGE_HANDOFF.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preferred full PASS:

`C16_OLMOE_STATIC_AUDIT_FORMAL_109_V35_PASS_WITH_FORMAL_MOE_ANCHOR`

Only use full PASS after fresh static selector, clean formal capture and positive ACK all close.

## Git closure

Use node109 existing Git transport. Do not install/configure `gh`.

Complete:
`review pack -> SHA256SUMS -> commit -> push -> canonical git ls-remote verify -> clean worktree -> STOP`

Routine engineering issues, including static-tool bootstrap, must be solved and execution continued. Stop only on a genuine scientific/identity/static-selector/formal-evidence blocker.
