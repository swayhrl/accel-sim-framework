# CODEX_NEXT_STAGE — Track A

## Status

`M1_M3_VM_BASELINE_CLOSEOUT`: **PASS / ACCEPTED**.

Accepted final Core:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Accepted Framework evidence before this review update:

`47dde5767af8d30b892c7d63d932455644b7cf3a`

Track A has completed G3-4A, G3-4B, G3-5A, G3-5B, G3-CLOSEOUT and the M1-M3 macro closeout.

## Current authorization

**STOP / HOLD.**

There is no additional Track-A implementation target at this time.

Track B is still executing `M4A_MERGE_PREP` on the frozen formal LLM traces. Wait for its ChatGPT review before any A/B integration or M4B work.

## Frozen integration anchor

Any future integrated VM/LLM branch must use this Core as its starting VM baseline:

`swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Do not replace it with Track B's old frozen parser Core; that old Core exists only as trace-format compatibility evidence.

## Do not execute now

Do not:

- merge Track B into Track A;
- create the final A/B integration branch unless explicitly authorized;
- start M4B;
- implement Segmentation;
- implement L2-TLB sub-entry/coalescing;
- inject synthetic KV;
- add page faults/migration/UVM/MCM;
- broaden to multi-ASID claims;
- retune the accepted generic M1-M3 baseline in anticipation of LLM results.

## Next expected handoff

After Track B reports `M4A_MERGE_PREP_PASS_READY_FOR_INTEGRATION` and ChatGPT independently accepts it, ChatGPT will issue a new integration-stage specification covering approximately:

1. creation of a fresh Framework integration branch from accepted Track A;
2. selective import/merge of B-owned LLM capture utilities, docs and immutable trace provenance;
3. preservation of A-owned final `CURRENT_STATE.md` / `CODEX_NEXT_STAGE.md` semantics during merge;
4. exact binding of formal prefill/decode1 archive hashes and derived semantic kernel lists;
5. replay/parser compatibility against the final accepted M1-M3 Core;
6. LLM baseline translation characterization before Segmentation;
7. only after that gate, M4B paper reproduction work.

Until then, remain stopped.
