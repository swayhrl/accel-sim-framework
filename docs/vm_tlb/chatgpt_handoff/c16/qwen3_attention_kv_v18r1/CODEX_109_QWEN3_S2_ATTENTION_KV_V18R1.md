# CODEX GOAL — C16 Qwen3-8B S2 Attention/KV V18R1 replay-contract repair and continuation

## IMPORTANT — GOAL MODE
Execute this task in GOAL MODE. Do not stop after diagnosing or fixing replay. If the repaired replay gate passes, continue automatically through signature qualification, fresh static-path audit, formal capture, serial Pipeline admission/ACK, NCU, and review-pack closure.

This is a continuation of the same V18 scientific target, not a new target/campaign.

Base blocked producer HEAD:
`f201a6699cdbd998fad40c2b0b329a1d36ff0dcc`

Existing accepted state:
- exact Qwen3-8B revision `b968826d9c46dd6066d109eabc6255188de91218`
- exact V2 S2 payload SHA256 `5913c573054d23a444477394a60f3f280311325e81175663b4ae2abd5ef6aafb`
- existing pre-attention state and same-process K/V range capture are valid unless a hash mismatch is found
- no Attention/KV formal bundle has been admitted yet
- existing MLP formal admission must not be repeated

## Root-cause correction
Transformers 4.51.0 `Qwen3Attention.forward()` accepts `past_key_value` (singular), not `past_key_values`.

The V18 replay script called `l.self_attn(..., past_key_values=cache, ...)`. Because `Qwen3Attention.forward()` also accepts `**kwargs`, this typo is silently accepted while the real `past_key_value` parameter remains `None`; the restored 2048-token KV cache is therefore not consumed.

Treat V18's `bounded_methods_exhausted=true` as invalidated by this implementation error. Preserve the old BLOCKED pack as immutable history; do not delete or rewrite it.

## P0 — API-contract proof before GPU replay
In the pinned `/data/c16/env/c16-qwen3-v14` environment:

1. Use `inspect.signature(Qwen3Attention.forward)` and persist the exact signature.
2. Assert `past_key_value` is a named parameter.
3. Assert the old replay source contains `past_key_values=cache` and record that as the V18 root-cause evidence.
4. Patch the replay to pass `past_key_value=cache`.
5. Do not change model/revision/input/precision/backend/semantic target.

Produce `V18_REPLAY_ROOT_CAUSE.json`.

## P1 — Corrected exact replay gate
Reuse the hash-closed V18 pre-attention state first; do not recapture by default.

For the corrected replay:
- restore exact K/V tensors;
- assert cache seq length before call is exactly 2048;
- call layer0 `self_attn` with `past_key_value=cache`;
- pass the exact position/cache position and attention mask represented by the V18 state;
- assert cache seq length after call is 2049;
- compare output against captured in-context self-attn output;
- record bitwise equality, max_abs, input/output SHA, K/V SHA, before/after cache length.

Also run a negative-control replay with no effective cache (or the old typo behavior) and record its output SHA/max_abs. If it reproduces the old V18 failed output SHA `7d4977da2ec398228c16e9819a1f70714599f7ccb3274cdbaada3a01591f44dd`, record this as causal confirmation that the old blocker was an API-binding error.

Expected repaired gate: bitwise equal and `max_abs=0`.

If corrected replay still fails, allow exactly one bounded evidence-recovery recapture of the actual `self_attn` kwargs at the pre-hook boundary, including:
- hidden_states
- attention_mask
- `past_key_value` preexisting layer0 K/V
- cache_position
- exact position_embeddings cos/sin tensors

Replay those captured kwargs verbatim with the correct singular parameter. If this still fails, emit `BLOCKED_REPLAY_EQUIVALENCE_AFTER_API_FIX` and STOP.

## P2 — Attention/KV material target qualification
If replay passes, continue immediately.

The formal target must be materially distinct from q/k/v/o projection GEMV/linear kernels.

The pinned Qwen3 eager attention core performs:
- Q x K^T score read path
- softmax
- attention_weights x V value read path

Use NVTX/NSYS census plus same-process KV ranges to identify one or at most two kernels/static sets whose dynamic addresses are losslessly attributable to captured K and/or V storage.

Do not bind by launch order.
Do not call a projection kernel an Attention/KV target.
Do not accept `UNKNOWN_RUNTIME` as proof of KV materiality.

Preferred order:
1. K-backed score/read target
2. V-backed value/read target only if separately material and losslessly bindable

At least one qualified KV-backed target is required for PASS.

## P3 — Signature gate
For every qualified target:
- compare in-context vs direct replay implementation/kernel signature;
- require same qualified implementation family/signature for formal replay use;
- preserve grid/block and relevant library/runtime identity.

Mismatch => fail closed for that target.

## P4 — Fresh global-address-path audit
For each qualified implementation, enumerate fresh SASS/static instructions.

Classify independently:
- direct GLOBAL MREF
- LDGSTS GLOBAL_SOURCE
- control-only such as LDGDEPBAR
- any other address-bearing special path

Never reuse Qwen2/Qwen3-MLP static sets.

Closure rule: every address-bearing static instruction must be either executed/captured or `ZERO_EXECUTION_PROVEN`.

Unexpected/uninstrumented address-bearing path => BLOCKED.

## P5 — Formal capture/admission
`FORMAL_ADMISSION_CONCURRENCY=1`.

For the first required qualified Attention/KV target:
1. complete all local shards first;
2. require terminal closure and drop=0/overflow=0;
3. preserve same-process ADDRESS_CONTEXT/KV range attribution;
4. acquire global admission lock;
5. verify/admit once;
6. wait for positive remote ACK before any optional second target.

Do not repeat the existing MLP admission.

A second K/V target is optional and only allowed if materially distinct and already qualified.

## P6 — NCU and compact fingerprint
Profile the exact qualified replay target with application replay and cache-control none where supported.

Export durable metric values and explicit units if available. If unit semantics remain unresolved, preserve raw display values and mark non-comparable; do not infer units.

Create a compact per-target memory fingerprint without inventing cross-shard chronology, cross-path reuse distance, or cross-process VA relations.

## P7 — Final review pack
Expected pack:
`docs/vm_tlb/review_packs/C16_QWEN3_S2_ATTENTION_KV_109_V18R1/`

Include at least:
- `V18_REPLAY_ROOT_CAUSE.json`
- corrected replay-equivalence receipt
- KV materiality/target qualification
- signature gate
- fresh static-path summary/index
- formal shard/closure summary
- Pipeline verify/admission/ACK receipt
- NCU receipt/export
- final decision
- open issues
- SHA256SUMS

Allowed decisions:
- `C16_QWEN3_S2_ATTENTION_KV_109_V18R1_PASS`
- `..._PASS_WITH_SCOPED_EVIDENCE`
- `..._BLOCKED_REPLAY_EQUIVALENCE_AFTER_API_FIX`
- `..._BLOCKED_KV_TARGET_QUALIFICATION`
- other specific fail-closed blocker if required

Required first target failure must not be hidden as scoped PASS.

Commit/push final branch and STOP only after full Goal completion or a genuine fail-closed blocker.