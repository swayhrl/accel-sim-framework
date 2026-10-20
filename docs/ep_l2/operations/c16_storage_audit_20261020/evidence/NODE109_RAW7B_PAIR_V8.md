# CODEX 109 Goal — C16 Qwen2.5-7B Raw Paired Layer Replay V8

Fresh branch/worktree on node109.

Suggested branch: `hrl/c16-qwen25-7b-raw-paired-replay-109-v8`.

Read `CURRENT_SCOPE_AND_GATES.md` first and execute in GOAL MODE.

## P0 — Consume accepted authorities

Use:
- raw7B exact model `Qwen/Qwen2.5-7B-Instruct@a09a35458c702b33eeacc393d103063234e8bc28`;
- AWQ exact model `Qwen/Qwen2.5-7B-Instruct-AWQ@b25037543e9394b818fdfca67ab2a00ecc7dd641`;
- accepted AWQ V6/V7 evidence listed in scope;
- raw7B readiness and helper fixes from the accepted 174-new authorities.

Bring only needed helper changes from `cd74256d698d9949d222703db8bb077a3581792a` into this branch; do not overwrite accepted producer evidence.

## P1 — Close AWQ V7 NCU numeric export

Without recapturing if reports are intact:
- export numeric `l1tex__t_bytes`, `lts__t_bytes`, `dram__bytes` for the accepted Prefill AWQ dequant and Decode fused GEMM reports;
- retain report SHA, exact command, cache-control none, application replay semantics;
- archive/receipt the `.ncu-rep` files or explicitly record their immutable long-term location;
- produce compact TSV consumable on node174-new.

## P2 — Pair input authority

Independently parse the exact token ID arrays for raw7B historical S2 and the AWQ V6 executed S2 input.

Compute a common canonical token-sequence hash using one documented serialization.

If the sequences are identical, close `COMMON_HISTORICAL_PAIR_SEQUENCE`.

If they differ:
- preserve both historical authorities unchanged;
- verify raw7B embedding/vocab/token-id compatibility with the exact AWQ executed sequence;
- freeze `QWEN25_7B_RAW_AWQ_PAIR_S2_V1` as a new PROSPECTIVE pair authority by adopting the exact AWQ-executed 2048 token IDs for raw7B;
- no tokenizer invocation and no source-text reconstruction is required for this adoption;
- record clearly that raw7B historical S2 is not being rewritten.

Fail closed if the AWQ exact executed sequence cannot be recovered byte-for-byte or is invalid for raw7B.

## P3 — Bind a semantic AWQ pair anchor

The accepted V6 `DECODE_FUSED_GEMM` function-level target is not sufficient for a pair unless a unique semantic module/layer is proven.

Instrument the exact AWQ V6 deployment with deterministic module-level NVTX or an equivalent zero-semantic-change range mechanism around WQLinear modules. Re-run the exact pair input and decode path under NSYS only.

Bind the accepted formal target to:
- decoder layer id;
- exact linear role (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, or `down_proj`);
- decode step / launch context;
- input/output shape;
- kernel signature/grid/block if useful for correlation.

If and only if the existing target cannot be mapped losslessly, choose one explicit module (prefer a representative MLP linear in an ordinary decoder layer), add semantic range binding, and formalize at most ONE replacement AWQ decode-linear target. Serial Pipeline admission only.

The accepted Prefill dequant target is AWQ-specific overhead and does not require a raw kernel twin; retain it as AWQ-only evidence.

## P4 — Raw7B semantic layer streaming

Build an isolated raw7B BF16 replay environment. Do not destabilize accepted Qwen0/AWQ environments.

Implement Mode A semantic layer streaming for the exact pair input:
- exact archived BF16 weights;
- original Qwen2.5 layer implementation;
- exact attention/position/cache semantics;
- no quantization, pruning, approximation, synthetic hidden state, or standalone GEMM substitution;
- load only required layer tensors from checkpoint shards;
- hold inactive weights host-side;
- preserve per-layer KV/state as needed across decode.

For the matched semantic target, freeze `TARGET_LAYER_STATE` with at least:
- model/revision/runtime deployment identity;
- pair input authority SHA;
- phase and decode step;
- layer id and semantic linear role;
- incoming hidden-state bytes/hash;
- position/cache identity;
- target-layer past KV/state bytes/hash when applicable;
- exact target layer weight identities;
- RNG state if relevant.

## P5 — Mode B exact target-layer replay

Restore the target state and exact layer weights, execute the full target layer in the same implementation path, and compare against the Mode A reference.

Record bitwise equality where achieved; otherwise record max-abs/max-rel error and a justified tight tolerance. Do not proceed to formal profiling if equivalence fails.

Use NSYS to prove the matched raw semantic linear kernel(s) and record implementation differences from AWQ.

## P6 — Raw formal target

For ONE matched raw semantic linear target:
- freeze exact function/code object/launch selector;
- run full-function address-path census;
- separate direct GLOBAL MREF, LDGSTS/global-to-shared, other address-bearing paths, and control-only instructions such as LDGDEPBAR;
- capture all required address-bearing static paths to terminal closure;
- require overflow/drop = 0 and same-process ADDRESS_CONTEXT;
- serial Pipeline admission and ACK.

Best allowed coverage label: `ALL_DETECTED_GLOBAL_ADDRESS_PATHS_COVERED_SET_LEVEL`.

Do not fabricate direct+LDGSTS temporal ordering or a unified absolute VA stream.

## P7 — Paired NCU canary

If P3–P6 pass, collect application-context NCU for the matched raw semantic target with the same three accepted metrics and equivalent cache-control semantics. If the existing AWQ NCU target is not the exact semantic pair anchor, collect a small semantically-bound AWQ NCU canary for the anchor; do not broaden the campaign.

## Tests and regressions

- raw7B layer selective-loader tests including bytes/dtype/shape fail-close;
- target-state deterministic hash test;
- Mode A/Mode B replay equivalence test;
- pair-input canonical hash test;
- existing RTX3090 Q2 exact CPU regressions if shared parser/analysis code is touched;
- review pack SHA closure.

## Review pack

Create `docs/vm_tlb/review_packs/C16_QWEN25_7B_RAW_PAIRED_REPLAY_109_V8/` with at least:
- `FINAL_DECISION.json`
- `PAIR_INPUT_AUTHORITY.json`
- `AWQ_SEMANTIC_TARGET_BINDING.json`
- `RAW7B_DEPLOYMENT_IDENTITY.json`
- `TARGET_LAYER_STATE_RECEIPT.json`
- `REPLAY_EQUIVALENCE.json`
- `RAW_TARGET_PORTFOLIO.tsv`
- `RAW_ADDRESS_PATH_AUDIT.tsv`
- formal index/ACK evidence if admitted
- compact AWQ V7 NCU numeric export and report receipt
- paired raw NCU index if qualified
- `OPEN_ISSUES.md`
- `SHA256SUMS`

Allowed success labels:
- `C16_QWEN25_7B_RAW_PAIRED_REPLAY_109_V8_PASS`
- `..._PASS_WITH_SCOPED_EVIDENCE`

If semantic equivalence or pair-input/semantic-target binding cannot be closed, stop with an explicit scoped gap rather than inventing comparability.

Commit/push and STOP.
