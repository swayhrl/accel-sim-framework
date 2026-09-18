# C16 OLMoE representative variant-A formal anchor — node109 V38

## Execution mode

Execute in **GOAL MODE** on node109.

This Goal closes one representative, explicitly variant-typed OLMoE formal anchor. It supersedes the V37 requirement that historical variant B must also be naturally reacquired/formalized before OLMoE can contribute a third independent lineage.

Suggested implementation branch:

`hrl/c16-olmoe-variant-a-formal-109-v38`

## Accepted upstream

V34:
- `hrl/c16-olmoe-s2-producer-109-v34@ab26365dc663268b0799818db6687ed466e8c925`
- exact prospective-common S2/T2048 frozen input
- native BF16 S2/D32
- Layer1 decode32 natural top-8:
  `[58,59,47,51,25,15,12,48]`
- natural rank-0 expert58
- semantic target:
  `OlmoeSparseMoeBlock -> experts[58] -> OlmoeMLP.down_proj -> torch.nn.Linear`
- input `[1,1024]`
- weight `[2048,1024]`
- output `[1,2048]`
- lossless dynamic attribution
- same-module replay bitwise equal

V36:
- `hrl/c16-olmoe-nvbit-jit-selector-formal-109-v36@17d8c9bcf3e48828c7eecd2289b4a4c6db7274e4`
- actual loaded SM89 JIT introspection operational
- BF16 cuBLAS `internal::gemvx::kernel`
- variant A static function has 1096 instructions
- variant A same-process typed dynamic evidence PASS
- historical variant B was observed in a different V36 instrumentation run

V37:
- `hrl/c16-olmoe-variant-aware-formal-109-v37@cd41ce1ec8c00942be824988dff5c4c564a4f131`
- 16 fresh processes under one bounded natural census protocol
- A = 16/16
- B = 0/16
- unknown = 0
- no cuBLAS algorithm/backend/workspace/determinism/stream controls were set

## Scientific policy

The formal target is now explicitly:

`OLMoE natural expert58 down_proj / accepted V34 runtime / actual cuBLAS JIT variant A / fixed V38 formal-capture protocol`

This is a **representative deployment-variant anchor**, not an estimator of all OLMoE/cuBLAS implementations.

Variant B remains valid historical evidence that another actual JIT implementation can occur under a different instrumentation context. V38 must not:
- claim B does not exist
- claim A exhausts all OLMoE implementations
- force runtime settings to suppress B
- generalize A-specific static indices to B

But B is **not required** to be reacquired or formalized for the current C16 third-lineage objective.

Later three-lineage synthesis may compare:
- Q30 accepted deployment anchor
- DeepSeek accepted deployment anchor
- OLMoE variant-A accepted deployment anchor

Any broad common claim must remain a descriptive common pattern across those three accepted deployment anchors. It must not claim OLMoE implementation-variant invariance.

## Asset/runtime

Node164 remains sole model authority.

Reuse retained node109 OLMoE replica after hash closure:
`/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`

Re-establish accepted runtime:
- torch 2.7.1+cu126
- transformers 4.55.0
- modeling_olmoe SHA `413888fc3be7e037727586f25900b629cc5dbc06b227a4f0d42c67cacb597bc7`

Reuse exact frozen V34 S2 IDs.

Reuse retained V36 NVBit actual-JIT census/static-introspection tool.

## Stage 0 — formal-protocol identity gate

Before building the formal selector, run at least 4 fresh-process probes using the **same NVBit injection/lifecycle that will be used by the formal tracer**, not a different census-only environment.

For each process:
- exact expert58 replay
- actual loaded function name
- normalized static fingerprint
- static instruction count
- grid/block
- nregs/shmem
- output hash

Classify:
- A -> `FORMAL_PROTOCOL_VARIANT_A`
- known historical B -> `FORMAL_PROTOCOL_KNOWN_VARIANT_B`
- other -> `FORMAL_PROTOCOL_UNKNOWN_VARIANT`

If at least one A is naturally obtainable and its fingerprint/static map is stable when A occurs, continue.

If B or unknown also occurs, preserve counts/evidence but do not make that a blocker by itself.

If A cannot be obtained under the actual formal protocol within a bounded set of 16 fresh probes, fail closed.

Do not alter cuBLAS settings to obtain A.

## Stage 1 — COMPLETE variant-A static path audit

Important: V36/V37 committed static selector rows 101/103 are examples only. They are **not** authorization to treat the selected static set as two instructions.

For the actual loaded variant-A function:
- enumerate all 1096 static instructions using NVBit
- classify every address-bearing memory instruction
- build the complete formal selected set

At minimum identify:
- every direct GLOBAL load
- every direct GLOBAL store
- every LDGSTS whose source is GLOBAL, if any
- any other global-memory/address-bearing instruction required by the known-good tracer

For each selected instruction persist:
- variant A fingerprint
- static index
- PC/offset
- opcode
- load/store
- memory-space classification
- exact address operand/source register
- access width/vector info where available
- classification method

Use the exact operand semantics already validated in C16.

No selector row may be included merely by opcode-name regex if its address semantics are unresolved.

Output:
`COMPLETE_VARIANT_A_STATIC_SELECTED_SET`

with exact selected count and SHA256 of the normalized selector.

## Stage 2 — typed dynamic audit of complete selected set

Using the exact expert58 isolated replay and same-process ADDRESS_CONTEXT:
- input range
- weight range
- output range
- workspace only if proven
- other/unclassified

Run a bounded dynamic audit sufficient to determine:
- which selected static instructions execute
- which typed ranges they access
- whether any selected source-register mapping is wrong

Require:
- no selected executed instruction produces invalid/unparseable address records
- typed evidence confirms this is the expert58 module-backed kernel

Do not require every instruction to touch all objects.

## Stage 3 — variant-A fingerprint-guarded tracer

Surgically extend the known-good warp-regsource tracer so a fresh process:

1. observes the actual runtime function
2. computes/verifies variant-A static fingerprint
3. instruments only if the function matches the exact A fingerprint
4. applies the complete variant-A static selector
5. uses variant-A-specific source-address registers

If process selects historical B:
- classify `NATURAL_VARIANT_MISMATCH_B`
- do not instrument using A indices
- retry naturally

If unknown:
- classify `UNKNOWN_RUNTIME_VARIANT`
- preserve evidence
- do not instrument
- retry naturally

These retries are selection for an explicitly variant-conditioned representative capture. Do not interpret retry frequency as runtime population probability.

## Stage 4 — canary

Run bounded canaries on a representative subset that covers:
- at least one input-reading instruction
- at least one weight-reading instruction
- at least one output-writing instruction
- any special path such as LDGSTS if selected

Each canary:
- fresh process
- A fingerprint guard
- exact function occurrence
- exact static instruction
- exact source register
- terminal closure
- drop=0
- overflow=0
- same-process membership

If a fresh process is B/unknown, retry naturally within a bounded policy.

Canary PASS must prove the complete selector/tracer plumbing is valid for A.

## Stage 5 — complete formal variant-A capture

Capture one formal run:

`C16R_olmoe-1b-7b-0125-instruct_s2-text_decode_nvbit-warp-mref-shard_v38-l1-d32-natural-expert58-down-jitA_<timestamp>_<suffix>`

Formal scope:
- semantic module = natural expert58 down_proj
- implementation = actual JIT variant A
- one selected static instruction per independently replayed shard
- every formal shard must pass A fingerprint guard
- B/unknown processes are non-formal retries
- complete selected static set
- executed/zero partition
- drop=0
- overflow=0
- receiver terminal
- same-process ADDRESS_CONTEXT
- typed membership

If a selected shard overflows:
- exclude that attempt
- recapture only that shard in a fresh recovery root at larger capacity

Use bounded retry policy. Suggested:
- up to 8 natural fresh-process attempts per shard before escalating
- if A becomes unexpectedly unavailable across many shards, diagnose environment drift rather than forcing cuBLAS

No cross-shard global chronology or VA union.

## Stage 6 — formal analysis

Report:
- complete selected static count
- executed / zero
- active-lane event total
- per-executed-shard event min/max/median
- per-shard unique 128B lines min/max/median
- per-shard unique 4K pages min/max/median
- per-shard unique 64K pages min/max/median
- per-shard unique 2M pages min/max/median
- typed event fractions:
  - `EXPERT_DOWN_WEIGHT`
  - `EXPERT_DOWN_INPUT`
  - `EXPERT_DOWN_OUTPUT`
  - `WORKSPACE_IF_PROVEN`
  - `OTHER_OR_UNCLASSIFIED`
- full-scope result

Do not compute:
- cross-shard VA union
- cross-shard chronology
- reuse distance
- cache/TLB causality

## Stage 7 — serial admission

Mandatory:
`FORMAL_ADMISSION_CONCURRENCY=1`

Complete:
`manifest -> transfer -> destination verification -> catalog -> positive ACK`

Only one OLMoE formal run is required in V38.

## Stage 8 — third-lineage authorization

If formal capture + ACK PASS, authorize:

`OLMOE_VARIANT_A_FORMAL_ANCHOR_CLOSED_FOR_THREE_LINEAGE_MOE_CONSUMER`

The handoff must explicitly state:
- OLMoE evidence is conditioned on JIT variant A under the fixed V38 formal protocol
- V36 historical B exists but is not formally characterized
- therefore later consumer may test a 3-independent-lineage descriptive pattern across accepted deployment anchors
- later consumer may NOT claim OLMoE internal-variant invariance

No additional OLMoE operator/scenario should be authorized after this closure unless the later consumer finds a specific scientific gap.

## Optional profiler evidence

NCU/NSYS is optional.
Do not block formal closure for missing profiler evidence.

## Required review pack

Create:
`docs/vm_tlb/review_packs/C16_OLMOE_VARIANT_A_FORMAL_109_V38/`

Include at least:
- `UPSTREAM_V37_AUTHORITY.json`
- `FORMAL_PROTOCOL_VARIANT_PROBES.tsv`
- `VARIANT_A_FUNCTION_IDENTITY.json`
- `VARIANT_A_COMPLETE_STATIC_PATH_AUDIT.json`
- `VARIANT_A_COMPLETE_STATIC_SELECTOR.tsv`
- `VARIANT_A_TYPED_DYNAMIC_AUDIT.json`
- `VARIANT_A_CANARY.json`
- `VARIANT_A_FORMAL_SUMMARY.json`
- `VARIANT_A_FORMAL_SHARDS.tsv`
- `VARIANT_A_ADDRESS_MEMBERSHIP.json`
- `VARIANT_A_ADMISSION_ACK.json`
- `THIRD_LINEAGE_HANDOFF.json`
- `NCU_TYPED_EVIDENCE.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Preferred full PASS:
`C16_OLMOE_VARIANT_A_FORMAL_109_V38_PASS`

Only PASS after:
- A is naturally available under the actual formal protocol
- complete A static selected set is closed
- canary closes
- all formal shards are clean
- admission ACK is positive

## Cleanup / retention

At end:
- release GPU lock
- unload GPU
- remove transient scratch
- no stale NVBit/profiler/CUDA processes
- GPU baseline restored
- retain valid OLMoE node109 replica
- retain useful V36/V38 NVBit JIT introspection tooling

## Git closure

Use node109 existing Git transport. Do not install/configure `gh`.

Complete:
`review pack -> SHA256SUMS -> commit -> push -> canonical git ls-remote verify -> clean worktree -> STOP`

Routine tracer lifecycle, variant retry, selector plumbing, and trace-capacity issues are engineering problems: solve and continue.
