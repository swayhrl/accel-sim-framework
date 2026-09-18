# C16 OLMoE actual-JIT NVBit selector + formal capture — node109 V36

## Execution mode

Execute in **GOAL MODE** on node109.

This is a narrow continuation of V34/V35. Do not restart model/input/capacity/target selection. Do not return to arbitrary SM86 offline cubins.

Suggested implementation branch:

`hrl/c16-olmoe-nvbit-jit-selector-formal-109-v36`

## Accepted upstream

V34:
- branch `hrl/c16-olmoe-s2-producer-109-v34`
- HEAD `ab26365dc663268b0799818db6687ed466e8c925`
- accepted target facts:
  - native BF16 S2/D32 PASS
  - layer1 decode32 natural top-8 = `[58,59,47,51,25,15,12,48]`
  - selected rank-0 expert = 58
  - semantic target = `experts[58].down_proj`
  - input `[1,1024]`
  - weight `[2048,1024]`
  - output `[1,2048]`
  - lossless dynamic weight/input/output attribution
  - exact same-module replay bitwise equal

V35:
- branch `hrl/c16-olmoe-static-audit-formal-109-v35`
- HEAD `8a56e618b228f5111c6fd4752d0b7acbc35374a7`
- decision `C16_OLMOE_STATIC_AUDIT_FORMAL_109_V35_FAIL_CLOSED_ACTUAL_CUBLAS_SM89_STATIC_SELECTOR_UNRESOLVED`
- route A established:
  - CUDA 12.8.90 `nvdisasm`/`cuobjdump` are available
  - torch-packaged `libcublasLt.so.12` static cubins only close through SM86
  - actual RTX4080 execution is SM89 driver-JIT
- route B was NOT completed:
  - no actual loaded-CUfunction NVBit static-introspection binding yet

## Hard rule

The V36 static-selector authority must come from the **actual CUfunction encountered in the exact expert58 replay process**.

Offline SM86 cubin disassembly may be retained only as auxiliary evidence.

Forbidden:
- arbitrary SM86 kernel selection
- recompiling PTX with ptxas and calling that the actual driver-JIT code
- Q30/DeepSeek selector reuse
- changing cuBLAS algorithm/backend merely to obtain easier static code
- replacing the BF16 Linear with a synthetic microkernel

## Asset/runtime reuse

Node164 remains the sole model authority.

Reuse the retained node109 OLMoE replica if hash-closed:
`/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

Re-establish the accepted V34 runtime family:
- torch 2.7.1+cu126
- transformers 4.55.0
- modeling_olmoe SHA `413888fc3be7e037727586f25900b629cc5dbc06b227a4f0d42c67cacb597bc7`

Reuse the exact V34 frozen S2 IDs and replay contract.

## Stage 0 — build an independent NVBit actual-function census tool

Use the already accepted official NVBit 1.7.7.1 lifecycle/scaffold available on node109.

Build a **separate discovery/static-introspection tool**, not the formal tracer.

At CUDA launch callbacks, for all relevant launch API variants actually observed:
- obtain the actual launched `CUfunction`
- record launch ordinal
- record function handle for process-local correlation only
- record `nvbit_get_func_name(ctx, func)`
- record grid/block dimensions
- record stream if safely available
- query stable CUDA function attributes where available, including binary/PTX version, register count, static shared memory, max threads or equivalent
- record related function set only where needed

For each actual function encountered in the isolated replay:
- call the NVBit static instruction enumeration API on that actual loaded function
- dump a deterministic static instruction stream:
  - static instruction index
  - instruction offset/PC if available
  - opcode
  - full printable SASS/instruction string exposed by NVBit
  - operand count/types
  - register operands
  - memory-space classification where derivable
  - load/store direction
  - width/vector information where derivable
- compute a deterministic static-function fingerprint SHA256 from the normalized dump

Do not assume the on-disk library cubin is the authority for this dump.

## Stage 1 — isolated exact expert58 replay launch census

Run only the exact accepted expert58 `down_proj` module replay, with explicit synchronization before and after the call.

In the same process record current:
- input pointer/range
- weight pointer/range
- output pointer/range
- any workspace ranges that can be defensibly identified

Produce a complete launch census for the isolated call.

The goal is to identify every CUDA function that executes as part of this exact one-module replay.

If only one substantive cuBLAS/cuBLASLt kernel executes, bind it directly subject to the dynamic-address gate below.

If multiple kernels execute, do not choose by name intuition.

## Stage 2 — typed dynamic launch attribution

Extend the independent census tool, or build a bounded companion NVBit tool, to instrument candidate launch functions sufficiently to determine which actual launch(es) touch the expert58 object ranges.

For every candidate launch, record dynamic evidence keyed by:
- actual function name
- static-function fingerprint
- launch ordinal / same-name occurrence
- static instruction index
- accessed address
- load/store classification where available

Classify addresses only against same-process ranges:
- `EXPERT_DOWN_WEIGHT`
- `EXPERT_DOWN_INPUT`
- `EXPERT_DOWN_OUTPUT`
- `WORKSPACE_IF_PROVEN`
- `OTHER_OR_UNCLASSIFIED`

Prefer the function/occurrence that is the actual principal expert58 down-projection memory consumer and has defensible typed relation to the semantic module.

Do not require one kernel to touch all three objects if the real cuBLASLt implementation decomposes the operation; instead:
- document the actual decomposition
- choose the narrowest actual kernel whose semantic role is defensible
- if the formal evidence class must narrow from full `NATURAL_SELECTED_EXPERT_DOWN_PROJ` to a subkernel memory-consumer class, STOP only if that changes the scientific comparison contract materially
- otherwise preserve the rank-1 module-level target and explicitly type the captured actual kernel as the main module-backed compute/memory kernel

If no actual launch can be losslessly connected to the expert58 replay, fail closed.

## Stage 3 — cross-process selector reproducibility

Repeat the isolated replay in at least two fresh processes.

Require the selected actual function to reproduce by a stable selector tuple such as:
- exact function name
- static-function fingerprint
- grid/block
- same-name occurrence within isolated replay
- function attributes

The raw `CUfunction` handle itself is process-local and must NOT be the selector authority.

If function names differ but the actual static fingerprint + launch envelope provides an unambiguous stable selector, document and use that only if the formal tracer can deterministically select the same runtime function.

If actual JIT output or launch selection is nondeterministic across fresh processes, attempt normal warmup/replay stabilization without changing backend/algorithm policy. Fail closed only if deterministic formal selection remains impossible.

## Stage 4 — fresh static selector from actual loaded function

For the selected actual JIT function, classify the static instruction set directly from the NVBit-enumerated instruction stream.

Include:
- direct GLOBAL reads/writes
- LDGSTS with GLOBAL source, if present
- any other address-bearing global-memory path required by the tracer

For every selected static instruction persist:
- actual function name
- static-function fingerprint
- static index
- PC/offset if exposed
- opcode
- load/store
- memory-space classification
- exact source address register / operand index
- access width where available
- classification evidence

Use the official NVBit instruction/operand APIs and the same operand semantics previously validated in C16.

Do not infer source registers from an unrelated cubin.

## Stage 5 — selector/tracer integration

Make the minimum surgical change needed so the known-good warp-regsource tracer can select the actual runtime function using the reproducible selector from Stage 3.

Preferred selector:
- exact runtime function name
- same-name occurrence ordinal
- selected static instruction index

Add a static-fingerprint guard where feasible:
- before enabling formal instrumentation, independently enumerate the selected function
- hash its normalized static dump
- require equality to the V36 discovery fingerprint

If fingerprint mismatch occurs in a fresh formal process, do not trace under a stale selector.

## Stage 6 — bounded canary

For a bounded subset of selected static memory instructions:
- fresh process
- exact isolated expert58 replay
- exact function selector
- exact same-name occurrence
- exact static index
- exact source address register
- sufficient capacity
- terminal closure
- drop=0
- overflow=0

Require dynamic events to map defensibly to same-process expert58 ranges.

Canary PASS must prove:
- selector reaches the intended actual JIT function
- source-address register is correct
- events are not from an unrelated cuBLAS launch

## Stage 7 — complete formal capture

After canary PASS, capture one formal OLMoE expert58 anchor.

Suggested run ID:
`C16R_olmoe-1b-7b-0125-instruct_s2-text_decode_nvbit-warp-mref-shard_v36-l1-d32-natural-expert58-down_<timestamp>_<suffix>`

Formal policy:
- one selected static instruction per independently replayed shard
- complete selected static set
- executed/zero partition
- terminal closure
- drop=0
- overflow=0
- same-process ADDRESS_CONTEXT
- typed object attribution
- no global ordering across shards

If a shard overflows:
- exclude that attempt
- recapture only that shard in a fresh recovery root at larger capacity

## Stage 8 — formal analysis

Report:
- selected static count
- executed / zero
- active-lane event total
- per-executed-shard event distribution
- per-shard unique 128B lines
- per-shard unique 4K / 64K / 2M pages
- typed event fractions:
  - EXPERT_DOWN_WEIGHT
  - EXPERT_DOWN_INPUT
  - EXPERT_DOWN_OUTPUT
  - WORKSPACE_IF_PROVEN
  - OTHER_OR_UNCLASSIFIED

Do not compute:
- cross-shard VA union
- cross-shard chronology
- reuse distance
- cache/TLB causality

## Stage 9 — serial transfer/admission/ACK

Mandatory:
`FORMAL_ADMISSION_CONCURRENCY=1`

Complete:
- source manifest
- node164 transfer
- destination verification
- catalog admission
- positive ACK

One clean OLMoE formal anchor is enough. Do not add another OLMoE operator.

## Stage 10 — three-lineage handoff

Prepare exact handoff for later independent 174-new consumer:
- Q30 accepted natural expert21 anchor
- DeepSeek accepted natural expert4 anchor
- new OLMoE expert58 anchor

Do NOT declare the three-lineage common result in V36.

## Cleanup / retention

At end:
- release GPU lock
- unload GPU
- remove transient scratch
- no stale NVBit/profiler/CUDA process
- GPU baseline restored

Retain:
- valid node109 OLMoE active replica
- V36 NVBit actual-function census/static-introspection tool and source under a durable C16 tools path, because it may be useful for future driver-JIT/cuBLAS kernels

## Required review pack

Create:
`docs/vm_tlb/review_packs/C16_OLMOE_NVBIT_JIT_SELECTOR_FORMAL_109_V36/`

Include at least:
- `UPSTREAM_V35_AUTHORITY.json`
- `NVBIT_INTROSPECTOR_RECEIPT.json`
- `JIT_LAUNCH_CENSUS.tsv`
- `JIT_FUNCTION_FINGERPRINTS.tsv`
- `TYPED_LAUNCH_ATTRIBUTION.json`
- `CROSS_PROCESS_SELECTOR_REPRODUCIBILITY.json`
- `ACTUAL_JIT_FUNCTION_IDENTITY.json`
- `ACTUAL_JIT_STATIC_PATH_AUDIT.json`
- `STATIC_SELECTOR.tsv`
- `DYNAMIC_CANARY_AUDIT.json`
- `FORMAL_SUMMARY.json`
- `FORMAL_SHARD_SUMMARY.tsv`
- `ADDRESS_MEMBERSHIP.json`
- `ADMISSION_ACK.json`
- `THIRD_LINEAGE_HANDOFF.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preferred full PASS:
`C16_OLMOE_NVBIT_JIT_SELECTOR_FORMAL_109_V36_PASS_WITH_FORMAL_MOE_ANCHOR`

Fail closed only if:
- actual loaded JIT function cannot be enumerated/introspected by NVBit
- actual replay cannot be losslessly tied to a deterministic runtime function/occurrence
- cross-process selector cannot be made reproducible
- source address operand cannot be established
- dynamic canary/formal closure fails
- scientific target semantics would have to be changed materially

Routine NVBit build/lifecycle/API issues are engineering problems: solve and continue.

## Git closure

Use node109's existing Git transport. Do not install/configure `gh`.

Complete:
`review pack -> SHA256SUMS -> commit -> push -> canonical git ls-remote verify -> clean worktree -> STOP`
