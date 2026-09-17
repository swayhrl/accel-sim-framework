# C16 DeepSeek-V2-Lite Persistent MLA Typed-Dataflow Qualification + Conditional Formal Capture — node109 V26

## Execution mode

Execute this task in **GOAL MODE** using the normal node109 Linux producer workflow.

This is a continuation of the accepted DeepSeek S2 lineage. Do not redo V23R1 MLA/MoE anchors and do not run S3 automatically.

Use node109's existing Linux Git workflow. Do not install/configure `gh`. Do not use a Windows mirror.

Suggested implementation branch:

`hrl/c16-deepseek-v2-lite-persistent-mla-109-v26`

## Accepted upstream authority

DeepSeek producer branch/head:

`hrl/c16-deepseek-v2-lite-s2-producer-109-v23r1`

`baf892ced6d66cbacabb995caf095e5280995097`

Accepted model:

`deepseek-ai/DeepSeek-V2-Lite@604d5664dddd88a0433dbae533b7fe9472482de0`

Accepted S2 input authority:

- payload SHA256 `2ca11cff95f13bcdd0efcb3f5b2d6c0b8f7e30c9e67492d6b291362c09ff6935`
- token-matrix SHA256 `14009279ed85b3de1f2510df84a3a8b2ba7a0d35f00c79d250d8e0e47cff63df`
- token count `2048`
- no retokenization

Accepted V23R1 MLA anchor:

`layer0.self_attn.kv_b_proj`

Evidence class:

`KV_B_EXPANSION_LATENT_READ`

This is explicitly **not** a persistent-KV-cache direct-read claim.

Accepted V23R1 MoE anchor is out of scope except as already-closed lineage evidence.

174-new V24 independent consumer classified the unresolved MLA persistent-cache question as:

`PERSISTENT_MLA_CACHE_IS_MULTI_OBJECT_OR_DERIVED_TARGET_REQUIRES_GPU_TYPED_DATAFLOW`

Treat that as the question to resolve, not as a preselected answer about which CUDA kernel is correct.

## Scientific objective

Determine the actual persistent MLA decode-cache representation and its first defensible GPU memory-read path under the exact S2 deployment.

The Goal should answer:

1. What objects are persisted across decode steps?
2. Is persistent state one object or multiple typed objects?
3. Which downstream semantic operations consume those persisted objects directly?
4. Which accesses are derived-buffer reads rather than persistent-cache reads?
5. Can one or more clean persistent-cache direct-read semantic anchors be formalized on S2?
6. If yes, capture/admit them in this same Goal; if no, stop with a typed scientific conclusion rather than forcing a target.

Do not assume the answer is compressed-latent-only, expanded-K/V, or ordinary MHA K/V.

## Stage 0 — authority and GPU preflight

Revalidate only the necessary accepted authorities:

- model/revision/file-set/per-file SHA authority
- runtime/backend versions
- exact accepted S2 state artifacts needed for replay
- S2 input hashes
- GPU identity/baseline

Use current C16 identity policy: exact file-set/per-file SHA and semantic/runtime identity are hard gates; aggregate directory bytes are derived sanity metadata.

Before CUDA/profiler work:

- inspect `nvidia-smi`
- inspect `/data/c16/locks/c16_gpu_campaign.lock`
- acquire lock normally
- never kill/bypass another scientific workload

## Stage 1 — reconstruct persistent MLA state across decode

Use exact semantic execution/state replay, preferably reusing accepted V23R1 layer-streaming infrastructure.

Instrument at least two adjacent decode states where persistence can be proven, e.g. cache-before and cache-after update, without changing the canonical S2 semantics.

For the earliest practical MLA layer, record every cache-relevant tensor/object with:

- semantic name from runtime/source path
- shape/dtype/stride
- storage pointer/range in the same process
- tensor/content SHA where practical
- alias relationships
- lifetime across decode steps
- whether it is appended/updated/replaced
- whether it persists after the layer returns

Build an evidence-backed typed graph. Labels may include, only when proven by runtime/source and storage evidence:

- compressed latent / `kv_a`-derived state
- positional/RoPE state
- expanded/derived K or V
- persistent cache component A/B/...
- current-token transient state
- attention-core operand

Do not call an object persistent merely because it is named `cache` in source; require cross-step lifetime/state evidence.

## Stage 2 — downstream consumer mapping

For every proven persistent component, determine the first downstream operation(s) that consume it.

Use source/runtime hooks + NVTX/NSYS/signature evidence to map:

`PERSISTENT_OBJECT -> semantic operator -> CUDA kernel/function`

For each candidate distinguish:

- direct persistent-object read
- read after an explicit derived/materialization transform
- mixed kernel reading persistent + transient/weight objects
- no clean isolatable direct read

Do not use launch order as object identity.

## Stage 3 — target selection policy

Prefer at most **two** persistent-cache anchors if the runtime truly needs multiple persistent objects.

Target class priority:

1. clean direct read from a proven persistent compressed/latent cache object;
2. clean direct read from a second proven persistent positional/RoPE or companion cache object if architecturally required;
3. if direct read is inseparable from a mixed kernel, an explicitly typed mixed persistent-cache consumer may be accepted only if same-process object membership can quantify the persistent portion losslessly;
4. derived-buffer-only paths must remain `DERIVED_BUFFER_READ`, not direct-cache evidence.

Do not force a single-object story if persistent MLA state is genuinely multi-object.

If no clean direct/mixed target exists, emit:

`NO_CLEAN_PERSISTENT_MLA_CACHE_DIRECT_READ_TARGET_IN_CURRENT_RUNTIME`

with evidence and stop before formal capture.

## Stage 4 — exact replay/signature gate

For each retained target:

- freeze exact persistent source object(s) and any required current-token/transient state
- construct the smallest exact semantic replay that preserves the target operation
- fresh-process replay where useful
- prove output equivalence to in-context execution
- prove source/destination alias relations
- establish exact function/grid/block signature
- capture same-process `ADDRESS_CONTEXT`

Do not synthesize cache tensors or replace runtime semantics with a mathematically similar microkernel.

## Stage 5 — fresh SM89 static/address-path audit

For each retained target:

- freeze exact function/code object
- enumerate all direct GLOBAL MREF instructions
- independently audit LDGSTS/GLOBAL_TO_SHARED
- audit any other address-bearing special path
- classify load/store/atomic semantics
- derive source-address registers from actual SASS when generic callback operand semantics are insufficient

Reuse the known-good V20/V23R1 warp-regsource tracer scaffold where applicable:

`/data/c16/qwen3_runtime_v14/v20/tools/v20_warp_regsource.so`

Clear inherited `C16_*` and `CUDA_INJECTION64_PATH` for fresh tracer processes.

## Stage 6 — typed dynamic canaries

Before formal capture, prove at least one executed static MREF for each retained target whose dynamic addresses join the intended persistent object range in the same process.

Also prove terminal close, drop=0, overflow=0 and correct occurrence/full-scope behavior.

Classify failures explicitly:

- `TRACE_SELECTOR_ALIGNMENT_FAILURE`
- `ADDRESS_EXTRACTION_OR_OPERAND_SEMANTICS_FAILURE`
- `SCOPED_CAPTURE_ONLY`
- `PERSISTENT_OBJECT_JOIN_FAILURE`

Do not convert a proven-executed operation into `ZERO_EXECUTION_PROVEN` because a selector is broken.

## Stage 7 — conditional formal capture

If and only if one or more persistent-cache targets pass all qualification gates, complete formal capture in this same Goal.

For each retained target:

- capture complete frozen static address-bearing set
- fresh output root
- clear inherited CTA slicing selectors
- same-process `ADDRESS_CONTEXT`
- terminal close
- drop=0 / overflow=0
- explicit executed vs `ZERO_EXECUTION_PROVEN` partition
- independent local decode/object-join audit

Then transfer/admit serially.

Hard rule:

`FORMAL_ADMISSION_CONCURRENCY=1`

For multiple retained persistent components:

`target A local close -> transfer -> verification -> admission -> positive ACK -> target B`

Do not start S3 in this Goal.

## Stage 8 — interpretation

Produce an evidence-bounded typed result describing:

- actual persistent MLA cache object topology
- object lifetimes and update semantics
- direct-read target(s), if any
- derived-buffer paths
- static/path structure
- dynamic object-membership fractions
- per-shard 4K/64K/2M page and 128B-line distributions
- active-lane events
- full-scope status
- bounded NCU status if collected

Do not construct cross-shard chronology, cross-replay VA union, reuse distance, or cache/TLB causality.

## Stage 9 — S3 authorization decision

Only after persistent S2 semantics are resolved, choose one typed outcome:

### If a clean persistent direct-read anchor is formally accepted

`DEEPSEEK_PERSISTENT_MLA_ANCHOR_READY_FOR_S3_LONG_CONTEXT`

This authorizes a later same-target S2->S3 context-scaling Goal, not S3 execution inside V26.

### If persistent state is multi-object and two clean anchors are accepted

`DEEPSEEK_MULTI_OBJECT_PERSISTENT_MLA_ANCHORS_READY_FOR_S3`

### If only mixed/derived access is defensible

`DEEPSEEK_PERSISTENT_MLA_DIRECT_READ_NOT_AVAILABLE_USE_TYPED_DERIVED_PATH`

### If evidence remains ambiguous

emit a specific blocker and do not authorize S3.

## Required review pack

Create:

`docs/vm_tlb/review_packs/C16_DEEPSEEK_V2_LITE_PERSISTENT_MLA_109_V26/`

Include at minimum:

- `UPSTREAM_AUTHORITY.json`
- `PERSISTENT_CACHE_OBJECTS.tsv`
- `PERSISTENT_CACHE_LIFETIME_AUDIT.json`
- `MLA_PERSISTENT_TYPED_DATAFLOW.json`
- `CONSUMER_CANDIDATE_MATRIX.tsv`
- `TARGET_SELECTION.json`
- `REPLAY_SIGNATURES.json`
- `STATIC_PATH_AUDIT.json`
- `DYNAMIC_CANARY_AUDIT.json`
- `FORMAL_TARGETS.tsv` if any
- `FORMAL_SUMMARY.json` if any
- `ADMISSION_ACKS.json` if any
- `NCU_TYPED_EVIDENCE.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_AUTHORIZATION.json`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Suggested PASS forms depend on evidence, e.g.:

- `C16_DEEPSEEK_V2_LITE_PERSISTENT_MLA_109_V26_PASS_WITH_DIRECT_ANCHOR`
- `...PASS_WITH_MULTI_OBJECT_ANCHORS`
- `...PASS_NO_DIRECT_READ_TARGET`

Do not use a direct-anchor PASS unless formal raw receives positive ACK.

## Git/cleanup

Use node109's existing Git transport/authentication; do not install `gh`.

After scientific closure:

- commit only Goal-owned changes
- push actual HEAD
- verify canonical repo and nonempty `git ls-remote` SHA
- require local HEAD == remote SHA
- clean worktree
- release GPU lock
- verify no profiler/DeepSeek CUDA process remains
- verify GPU baseline
- STOP

Fail closed only on a real scientific/evidence blocker. Do not stop after source inspection or target discovery while downstream bounded qualification remains executable.
