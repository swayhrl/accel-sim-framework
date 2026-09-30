# FFN timeline scientific identity recovery

## Decision

`IDENTITY_RECOVERED_FROM_ACCEPTED_AUTHORITY`. The accepted operator-family producer, its independent consumer, the source-bound model/input constants, the immutable historical snapshot, and the recorded NCU session jointly select one execution identity. No old GUD84 rerun was used or requested.

## Recovered identity

The workload is `Qwen/Qwen2.5-7B-Instruct-AWQ@b25037543e9394b818fdfca67ab2a00ecc7dd641` at the exact `/data/c16/models/.incoming/...` path in the accepted runner. It consumes the frozen 2048-token S2 text vector (`0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9`), without runtime tokenization, in batch 1. One prefill builds a 2048-token cache; greedy D0-D3 feed `[23578, 11, 323, 3950]` with past lengths 2048-2051. The accepted `CONTROL_GUD84` condition executes 28 layers × gate/up/down in the natural order: 84 calls per phase, 420 including prefill, and 336 measured decode projection occurrences. Seven fresh producer processes and the independent consumer agree on order, tokens, input/output hashes, and shapes.

The runtime is the accepted CPython 3.10.12 / torch 2.5.1+cu124 / Transformers 4.46.3 / AutoAWQ 0.2.7.post3 environment on the RTX 4080 (CC 8.9, 76 SM). The accepted NCU session directly records the interpreter, command, host, GPU, and `CONTROL_GUD84`; the platform authority supplies the UUID and driver. The FFN backend is `WQLinear_GEMM`, `fuse_layers=False`, with FP16 activations.

## Provenance and inference boundary

`SCIENTIFIC_IDENTITY_RECOVERY.tsv` separates direct fields from deterministic recovery. Derived entries are limited to consequences fixed by source plus hash-closed artifacts: the 2048 vector reconstructed from the archived 39-token source rule, context lengths, quantization fields, combined platform identity, and payload values recovered through an accepted immutable-manifest SHA. There are no `UNKNOWN` required fields. In particular, a name like “Qwen AWQ” was never used to guess a missing value.

The attention backend is bound operationally as the automatic Qwen2 selection of the exact frozen Transformers/config tuple; the runner has no attention override. Lane7 must not replace it with an explicit alternate backend. Environment variables not present in the accepted command are not invented; Lane7 must record its environment and stop if it introduces a semantic override.

## Authorization scope

The old proposal remains byte-identical at SHA256 `5ad0f920f133a8679aa4053cbcfd4096b8a3b573e90f4b05d985c3c41e6b8e65` and remains `PROPOSED_NOT_AUTHORIZED`. The new contract SHA256 is `b6b6b36a71eb6ce092b4bd28d55de037fec5911074fe3f93ddb3e0ede7e8a7cd`. It authorizes only one OFF/ON neutrality pair and one lightweight formal NSYS `cuda,nvtx` capture under the established GPU lock. It does not authorize NCU, NVBit, SASS, oracle work, Accel-Sim, a timing campaign, or any model/input/backend/policy change.

The observational delta is frozen at commit `e44571e59ef716be76c67aef013c7835f6b158be`, patch SHA256 `bdffcd5bf135fd9db310973828f51de23976fb45e558ed9ba5cc7cfc2a9bcbeb`, and resulting runner SHA256 `ad922629a9898c01400a165b2f6565659f1c6e422784c10bc1d013265c45b5fb`. It preserves the original gate→activation→up→multiply→down expression order, adds only semantic NVTX/correlation ranges, and is admissible only if the OFF/ON canary preserves output tokens, all occurrence hashes/shapes, natural call order, policy semantics, and CUDA kernel sequence.
