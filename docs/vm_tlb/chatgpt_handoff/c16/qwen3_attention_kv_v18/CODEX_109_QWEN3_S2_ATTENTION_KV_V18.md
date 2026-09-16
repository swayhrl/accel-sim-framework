# CODEX GOAL — C16 Qwen3-8B S2 Attention/KV Qualification + Formal Closure V18 (node109)

## IMPORTANT EXECUTION MODE

Execute this task in GOAL MODE. This is not a planning/review-only request.

Carry the complete authorized S2 workflow through target qualification, exact replay/signature validation, fresh path audit, formal capture/admission/ACK, profiling, evidence closure, commit/push, then STOP.

Do not stop after census, environment checks, state capture, or replay if downstream stages remain executable.

## Authorities

Producer evidence authority:
- branch lineage: Qwen3 V12/V15 producer
- producer evidence-closure commit: `ac4420f81dfafbe03b96e1bda63b4af31fe77f6a`
- review pack: `docs/vm_tlb/review_packs/C16_QWEN3_8B_EVIDENCE_CLOSURE_109_V15/`

Cross-lineage analysis authority:
- commit: `2405be223c4d55c0101f9700ea9b3ab1b19dd64f`
- review pack: `docs/vm_tlb/review_packs/C16_QWEN3_CROSS_LINEAGE_174NEW_V17/`

Exact model:
- `Qwen/Qwen3-8B`
- revision `b968826d9c46dd6066d109eabc6255188de91218`
- BF16 only

Exact S2 input:
- V13 exported validated payload `qwen3-8b__S2_TEXT.json`
- payload SHA256 `5913c573054d23a444477394a60f3f280311325e81175663b4ae2abd5ef6aafb`

Runtime baseline:
- `/data/c16/env/c16-qwen3-v14`
- transformers 4.51.0
- tokenizers 0.21.0
- huggingface-hub 0.30.2
- torch 2.5.1+cu124

Existing accepted MLP anchor is immutable and must not be recaptured or re-admitted.

## Scientific motivation from V17

The matched first-decode layer0 `mlp.down_proj` comparison is already informative enough to move to an orthogonal path:

- Qwen2.5 RAW: 243 static MREF, 193 executed / 50 zero, 51,387,392 active-lane events.
- Qwen3: 243 static MREF, 129 executed / 114 zero, 100,667,392 active-lane events.
- Per-executed-shard median events: 344,064 vs 786,432.
- Per-shard page/line distributions are broadly similar in shape; absolute VA is not comparable.

V17 contains one stale expected tuple for Qwen2.5 (`243/0`) even though accepted raw and prior V11 consumer evidence contain ZERO_EXECUTION_PROVEN shards. Treat the durable raw manifest/accepted consumer evidence as authority; do not turn this stale expectation into a scientific blocker.

The purpose of V18 is therefore NOT another MLP linear. It is to qualify and close a materially distinct first-decode layer0 attention/KV memory target in S2.

## Scope

Required scenario: `S2_TEXT`, first decode, layer0.

Semantic parent scope:
`model.layers.0.self_attn`

Target must be a memory path that is materially distinct from the existing MLP `internal::gemvx` anchor and is losslessly attributable to KV-backed data.

Preferred target roles, in order:
1. attention-score Q/K core operation that reads cached K;
2. attention-value P/V core operation that reads cached V;
3. another attention-core/cache operation only if it is demonstrably KV-backed and materially distinct.

Do NOT select q_proj/k_proj/v_proj/o_proj merely because they are easy to bind if they reduce to the already-characterized BF16 GEMV family and add no new memory-path information.

At most TWO formal targets may be admitted in V18: one K-oriented and one V-oriented target, only if both independently satisfy all gates below and are materially distinct. One well-qualified target is sufficient for V18 PASS.

S3 is NOT part of this V18 execution. Do not start long-context S3 here.

## P0 — Producer readiness and authority binding

Verify before GPU work:
- exact model revision/assets;
- exact S2 payload hash;
- V15 producer pack hashes;
- V17 cross-lineage authority commit is readable;
- pinned Qwen3 environment remains usable;
- NVBit / NSYS / NCU / SASS tools available;
- formal admission global policy remains `FORMAL_ADMISSION_CONCURRENCY=1`.

Do not redownload or replace model weights.

## P1 — Build exact PRE-ATTENTION first-decode state

Important: existing `/data/c16/qwen3_runtime_v14/layer0_first_decode_state.pt` is a down_proj-oriented capture and contains layer0 KV after the first-decode layer0 execution (length 2049). Do NOT misuse that post-update cache as the pre-attention replay authority.

Using the exact already-qualified streaming method:
1. exact 36-layer S2 prefill with true hidden/position/KV propagation;
2. derive the true next token;
3. before layer0 first-decode `self_attn` mutates its cache, capture the exact pre-attention state required for replay:
   - current layer0 hidden input;
   - layer0 K/V cache at pre-decode length 2048;
   - position/cache_position/attention-mask state;
   - rotary/position embedding inputs or equivalent exact state;
   - relevant module weights;
4. capture the in-context `self_attn` output and any required returned cache state.

Persist hashes, shapes, dtypes, byte counts and script/runtime identity.

Fail closed on state ambiguity.

## P2 — Semantic attention census, without launch-order inference

Run an in-context kernel census scoped by an explicit NVTX range for first-decode layer0 `self_attn`.

Within that scope, establish operator/role identity without using launch order alone.

Preferred binding methods:
- operator/module-specific NVTX ranges;
- PyTorch operator instrumentation / dispatch-based ranges;
- minimal source-level wrapper of the installed Qwen3 eager-attention implementation, only if math is unchanged and equivalence is proven.

If instrumentation changes output, reject it.

Record candidate kernels with:
- semantic operation role;
- kernel/function name;
- grid/block;
- count/occurrence;
- relevant tensor shapes;
- whether it is merely q/k/v/o GEMV or an attention-core/cache path.

## P3 — KV materiality gate

A formal candidate must have direct evidence that the selected operation reads KV-backed storage in the same process.

For each candidate, bind live storage ranges at the target call, including as applicable:
- pre-existing K cache;
- pre-existing V cache;
- updated/returned K/V tensors;
- any repeated/expanded view that shares the same underlying storage;
- query/output activations.

The candidate is qualified only if address evidence can be losslessly joined to the KV-backed range for the claimed role.

For this V18 target, `UNKNOWN_RUNTIME` is NOT enough to call the target `ATTENTION_KV`. If KV attribution cannot be proven, do not promote that candidate as the formal attention/KV target.

## P4 — Exact replay equivalence

Construct an exact replay for the selected semantic attention scope using the captured pre-attention state.

Required:
- exact model/revision/weights/runtime;
- exact hidden input;
- exact pre-decode KV state;
- exact position/cache state;
- exact output equivalence for the replayed semantic scope.

Prefer bitwise equality. If the framework makes bitwise equality impossible, do not silently weaken the gate; report the exact numerical behavior and block formal promotion unless an existing authority explicitly permits a weaker threshold.

## P5 — In-context vs replay signature gate

For every formal candidate, prove the selected in-context and replay implementations match in all relevant signature fields, including:
- semantic role;
- kernel/function identity;
- grid/block;
- static implementation/library identity;
- target occurrence binding.

No launch-order semantic inference.

A signature mismatch blocks that candidate.

## P6 — Fresh static global-address-path audit

For each qualified candidate, enumerate fresh SASS/static instructions for that exact Qwen3 implementation.

Classify independently:
- DIRECT GLOBAL MREF;
- LDGSTS GLOBAL_SOURCE;
- other address-bearing global paths;
- control-only instructions such as LDGDEPBAR.

Do not reuse the MLP static set or any Qwen2 static set.

Formal completeness remains:
`executed + ZERO_EXECUTION_PROVEN = complete fresh address-bearing static set`.

Unexpected/uninstrumented address-bearing path => BLOCKED for that candidate.

## P7 — Formal capture and serial admission

For each qualified candidate:
1. close all local shards first;
2. require drop=0 and overflow=0;
3. verify static membership/path classification/context receipts;
4. acquire/use global formal-admission serialization;
5. admit exactly one run at a time;
6. wait for positive remote ACK before any second admission.

`FORMAL_ADMISSION_CONCURRENCY=1` is mandatory.

If one target closes successfully and a second optional target fails qualification, preserve the first and record the second as scoped optional evidence. Do not invalidate the required first target.

Do not overwrite prior MLP raw/catalog evidence.

## P8 — NCU

Profile the exact qualified replay target with:
- application replay;
- cache-control none;
- requested L1/L2/DRAM byte metrics.

Make one bounded attempt to export explicit metric value + unit using an NCU page/CSV mode that actually exposes the unit column.

If units remain unavailable, preserve raw/display values and mark unit/comparability gap. Do not infer or convert units. NCU unit ambiguity alone does not invalidate otherwise closed formal evidence.

## P9 — Review pack

Create:
`docs/vm_tlb/review_packs/C16_QWEN3_S2_ATTENTION_KV_109_V18/`

Include at minimum:
- `AUTHORITY_BINDING.json`
- `PRE_ATTENTION_STATE_CAPTURE.json`
- `ATTENTION_KERNEL_CENSUS.tsv/json`
- `TARGET_QUALIFICATION.tsv/json`
- `KV_RANGE_BINDING.json`
- `REPLAY_EQUIVALENCE.json`
- `SIGNATURE_GATE.json`
- `STATIC_PATH_SUMMARY.json`
- formal shard/capture summary and shard index for every admitted target;
- Pipeline verify/admit/ACK receipts;
- `NCU_METRICS.tsv`
- `FINAL_DECISION.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Hash-close the complete pack.

## Allowed final decisions

- `C16_QWEN3_S2_ATTENTION_KV_109_V18_PASS`
- `C16_QWEN3_S2_ATTENTION_KV_109_V18_PASS_WITH_SCOPED_EVIDENCE`
- `C16_QWEN3_S2_ATTENTION_KV_109_V18_BLOCKED_<specific_gate>`

A PASS requires at least ONE materially distinct, exact-replay-qualified, signature-qualified, KV-attributed formal target with complete fresh path closure and positive Pipeline ACK.

Do not use PASS_WITH_SCOPED_EVIDENCE to hide failure of the required first target.

## Forbidden shortcuts

- no S3 execution in V18;
- no model/revision/precision/backend substitution;
- no synthetic hidden/KV state;
- no launch-order semantic inference;
- no reuse of MLP/Qwen2 static sets;
- no formal claim based only on UNKNOWN_RUNTIME;
- no second admission before first ACK;
- no cross-process absolute-VA comparison;
- no invented cross-shard/global chronology or reuse distance;
- no duplicate recapture/re-admission of the existing MLP anchor.

## Completion

Suggested implementation branch:
`hrl/c16-qwen3-s2-attention-kv-109-v18`

Execute autonomously through the entire Goal. Commit/push the final PASS/scoped/BLOCKED review pack and report:
- branch;
- HEAD;
- decision;
- selected semantic target role(s);
- replay/signature status;
- static-path counts;
- formal shard closure + ACK;
- NCU status;
- key evidence gaps.

Then STOP.