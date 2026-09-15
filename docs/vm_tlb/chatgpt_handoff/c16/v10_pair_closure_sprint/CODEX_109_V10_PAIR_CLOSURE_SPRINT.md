# C16 V10 — Qwen2.5-7B raw/AWQ pair closure sprint on node109

## Goal

Close, in one bounded producer sprint, the first controlled Qwen2.5-7B BF16-raw vs AWQ **matched semantic module replay deployment comparison**, or prove that the remaining kernel-signature gate is still not losslessly closable and stop spending time on this pair.

This Goal deliberately merges the next producer tasks that would otherwise become several repair/qualification rounds:

1. in-context semantic-module kernel-signature closure;
2. fresh replay-function address-path audits;
3. formal raw + AWQ replay capture and serial Pipeline admission if gates close;
4. matched replay NCU with explicit unit semantics;
5. an actually executable pair gate/comparator;
6. durable offline `tokenizers==0.20.3` wheel handoff for 174-new canonical input validation.

Do not split these into separate rounds unless a hard external dependency makes execution impossible.

## Accepted authority

Producer base / V9 scoped evidence:

`065fbc20a4a44281e301f9bbdcc8482b4fe59db0`

Accepted raw replay authority from V8:

`e1d210d662ece6975648d04f628eb3f9e938117f`

Lane-A static semantic checkpoint authority:

`ef8b5629fc8c10d770bed1c24f68c31cabe9912f`

Matched semantic target is fixed:

`model.layers.0.mlp.down_proj`

Scenario / phase:

`Qwen2.5-7B S2_TEXT B1/T2048/D32, first decode step`

Historical raw/AWQ S2 token files are already proven byte-identical and must remain unchanged.

## Scientific boundary

The intended success label is:

`MATCHED_SEMANTIC_MODULE_REPLAY_DEPLOYMENT_COMPARISON`

This is a **deployment-level comparison**, not pure quantization causality. Raw and AWQ may differ in:

- weight representation;
- activation dtype;
- kernel implementation;
- upstream hidden-state numeric values.

They must match in:

- Qwen2.5-7B semantic family;
- historical 2048-token input sequence;
- first-decode step identity;
- layer 0;
- `mlp.down_proj` semantic role;
- logical input shape `[1,1,18944]`;
- each side's in-context-vs-replay semantic equivalence;
- each side's in-context-vs-replay kernel-signature qualification;
- each side's complete global-address-path formal closure.

Do **not** require raw and AWQ to execute the same CUDA kernel name. Different deployment kernels are expected.

Do **not** require raw/AWQ module input tensor hashes to be equal. Record them and classify the difference as `NATURAL_DEPLOYMENT_STATE_DIVERGENCE`.

## P0 — Freeze V9 and verify prerequisites

Before new GPU work:

- verify V9 pack hashes;
- verify current branch/base identity;
- verify exact raw and AWQ model revisions;
- verify exact common historical S2 token-file SHA and 2048 parsed IDs;
- verify raw first decode token and AWQ first decode token; require the same token ID for this pair gate;
- verify V9 raw and AWQ module replay bitwise PASS;
- record raw/AWQ module input dtype and output dtype explicitly (V9 omitted this for the pair contract).

Do not mutate V8/V9 packs or old formal raw.

## P1 — Bounded in-context kernel-signature closure

The remaining blocker is **not** that raw and AWQ use different kernel families. The blocker is whether each dedicated replay uses the same kernel implementation as that exact semantic module call in the real first-decode context.

Use at most the following two qualification methods. Do not keep inventing new methods after both fail.

### Method A — exact module wrapper + NVTX + synchronize

For RAW and AWQ independently:

1. execute the real accepted first-decode path;
2. wrap the exact live `model.layers.0.mlp.down_proj.forward` call, not a launch occurrence;
3. push a unique NVTX range immediately before the original module forward;
4. invoke the original forward unmodified;
5. `torch.cuda.synchronize()` before closing the NVTX range so the module-launched kernels complete inside the qualification range;
6. verify wrapped execution preserves the unwrapped module output bit-for-bit;
7. capture NSYS with CUDA API + NVTX correlation;
8. enumerate every CUDA kernel attributable to exactly that one semantic module invocation.

The synchronization is allowed **only for signature qualification**. Do not use this wrapped run as performance/NCU evidence.

Record normalized signature components at minimum:

- kernel/function name;
- code object/module identity where available;
- grid;
- block;
- count/order within the exact semantic invocation;
- relevant CUDA API/cublas correlation if present.

Run the dedicated replay under the same signature census and compare.

A side passes when the exact semantic in-context invocation and dedicated replay have the same deterministic kernel-signature set/tuple for repeated runs.

### Method B — API/correlation bounded escalation

Only if Method A remains ambiguous:

- use CUDA API / cuBLAS / profiler correlation scoped by the exact semantic wrapper to disambiguate the kernel(s);
- still identify by the semantic module call, never by global launch order;
- perform one bounded diagnostic implementation, not an open-ended profiler campaign.

### Hard decision gate after P1

If either side still cannot be losslessly bound after Method A + Method B:

- emit `PAIR_KERNEL_SIGNATURE_UNRESOLVED_AFTER_BOUNDED_ESCALATION`;
- keep V9 semantic module replay evidence accepted;
- emit no formal pair bundles;
- do not try a third isolation technique;
- skip P2–P4 formal pair work;
- still execute P5 runtime bridge and close the review pack;
- STOP this pair line after commit/push.

This fail-closed outcome is acceptable and should trigger moving the GPU mainline to the next model rather than another raw/AWQ repair round.

## P2 — Fresh replay address-path audits

Execute only if P1 closes for both sides.

Audit the **actual V10 dedicated replay kernel(s)** independently for RAW and AWQ.

Important: do not inherit V8's `141 direct + 18 LDGSTS + 5 control` counts onto V10. V8 audited a different candidate function and V9 raw dedicated replay reports `internal::gemvx BF16`; therefore V10 must derive fresh static sets from the exact replay code object.

For every replay kernel involved in the exact module invocation:

- enumerate all direct GLOBAL MREF static indices;
- audit `LDGSTS` / global-to-shared source operands using the qualified exact-SASS operand rule;
- separate memory-control instructions such as `LDGDEPBAR` from address-bearing paths;
- audit any other special address-bearing path;
- freeze the complete static set and static-set SHA;
- prove executed vs `ZERO_EXECUTION_PROVEN` partitions.

If the exact module invocation legitimately consists of more than one address-bearing kernel, formal coverage is the closed set of those semantically bound kernels; do not collapse them into one fake stream.

## P3 — Formal matched replay capture

Execute only if P1 and P2 close.

For RAW and AWQ separately:

- replay the exact captured first-decode module input;
- use the exact live module object / weights from the accepted deployment;
- capture same-process `ADDRESS_CONTEXT`;
- record explicit tensor/object ranges for replay-local semantic objects.

RAW object map should include, where losslessly known:

- `model.layers.0.mlp.down_proj.weight`;
- input activation;
- output activation;
- `UNKNOWN_RUNTIME` for anything else.

AWQ object map should include, where losslessly known:

- qweight;
- qzeros;
- scales;
- bias if present;
- input activation;
- output activation;
- `UNKNOWN_RUNTIME` for anything else.

Do not promote event attribution merely because a range exists; join actual event VAs to same-process ranges losslessly.

For each frozen static path:

- deterministic shard capture;
- terminal complete;
- zero overflow/drop;
- executed or `ZERO_EXECUTION_PROVEN`;
- independent artifact hashes;
- set-level only semantics.

Formal admission is serial only:

`FORMAL_ADMISSION_CONCURRENCY = 1`

Admit one side, wait for Pipeline ACK, then admit the other.

No cross-deployment absolute-VA comparison.
No cross-shard temporal stream.
No cross-shard reuse distance.

## P4 — Matched module NCU + executable pair gate

### NCU

Capture NCU for the exact dedicated module replay on both RAW and AWQ using the same declared replay/cache policy.

Required metrics:

- L1/TEX bytes metric;
- L2 bytes metric;
- DRAM bytes metric.

Export in a form that retains **explicit metric units**. Normalize to base bytes only when the source unit is explicitly proven. If unit semantics remain unavailable, preserve raw display value and mark non-comparable; never guess.

Record raw `.ncu-rep` SHA, export SHA, metric name, metric unit, replay mode, cache-control, kernel signature, grid, block.

### Executable pair gate

Fold the Lane-A comparator implementation gap into this Goal. Implement an actual executable comparator/gate; do not write hard-coded PASS test rows.

The gate must reject if any required field/gate is missing or incompatible:

Common:

- historical token canonical/file authority;
- first decode token ID;
- semantic layer;
- semantic role;
- logical input shape;
- phase.

RAW:

- exact revision;
- semantic in-context module output identity;
- dedicated replay bitwise equivalence;
- in-context-vs-replay kernel-signature PASS;
- fresh path coverage closure;
- Pipeline ACK.

AWQ:

- exact revision;
- exact deployment identity;
- semantic in-context module output identity;
- dedicated replay bitwise equivalence;
- in-context-vs-replay kernel-signature PASS;
- fresh path coverage closure;
- Pipeline ACK.

NCU comparison is allowed only when metric descriptors and unit semantics are compatible.

Unit tests must actually invoke the comparator and include at least:

- missing token;
- token mismatch;
- first-decode token mismatch;
- layer mismatch;
- role mismatch;
- logical shape mismatch;
- missing raw replay equivalence;
- missing AWQ replay equivalence;
- missing raw signature gate;
- missing AWQ signature gate;
- invalid raw coverage/ACK;
- invalid AWQ coverage/ACK;
- incompatible NCU unit/descriptor;
- deterministic positive case.

Success label only if the executable gate returns PASS on real evidence:

`MATCHED_SEMANTIC_MODULE_REPLAY_DEPLOYMENT_COMPARISON`

Otherwise emit the precise scoped reason and do not fabricate a pair conclusion.

## P5 — Offline tokenizers runtime bridge to 174-new/node164

This side task is mandatory regardless of the pair outcome.

V9 already proved:

- `tokenizers==0.20.3` works in `/data/c16/env/c16-awq-v6`;
- exact cached wheel exists:
  `/data/c16/wheelhouse/c16-g-cp310-cu124/tokenizers-0.20.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl`;
- wheel SHA256:
  `1fd9fee817f655a8f50049f685e224828abfadd436b8ff67979fc1d054b435f1`;
- network was not used.

Publish this exact wheel as a durable offline runtime asset for 174-new via the existing 109 -> hrl174new -> node164 transfer path.

Use `.partial`, independent destination SHA verification, no overwrite.

Suggested durable namespace:

`/root/share/mnt164/huangrulin/c16_ai_workload/assets/wheels/tokenizers/0.20.3/`

Record a receipt containing:

- source path;
- destination path;
- size;
- SHA256;
- Python ABI/platform tag;
- source node;
- destination verification;
- network_used=false.

Do not attempt the full 42-binding validation on 109 if the six canonical tokenizer assets are not locally available. The purpose of P5 is to remove the 174-new blocker cleanly in one transfer, not to copy six model archives to 109.

## Stop conditions / anti-waste rules

- Maximum two methods for in-context signature isolation: Method A, then Method B. No third method.
- Do not retrofit semantic identity onto old accepted AWQ function-level bundles.
- Do not reuse V8 static path counts for V10 replay functions.
- Do not start Qwen3/DeepSeek inside this Goal.
- Do not create formal bundles if signature qualification is unresolved.
- Do not admit more than one formal bundle at a time.
- Do not recapture accepted historical inputs.
- Do not retokenize historical S2.
- Do not make whole-model performance/cache/TLB claims from module replay.

## Output

Commit/push a hash-closed review pack:

`docs/vm_tlb/review_packs/C16_QWEN25_7B_PAIR_CLOSURE_109_V10/`

Include at least:

- `FINAL_DECISION.json`
- `PAIR_GATE_INPUT.json`
- `PAIR_GATE_RESULT.json`
- `PAIR_GATE_TEST_RESULTS.tsv`
- `RAW_IN_CONTEXT_SIGNATURE.json`
- `RAW_REPLAY_SIGNATURE.json`
- `AWQ_IN_CONTEXT_SIGNATURE.json`
- `AWQ_REPLAY_SIGNATURE.json`
- `SIGNATURE_GATE.tsv`
- fresh static-set/path-audit indexes if P2 executes
- formal trace/ACK indexes if P3 executes
- matched NCU index/values if P4 executes
- `TOKENIZERS_WHEEL_TRANSFER_RECEIPT.json`
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Then STOP.
