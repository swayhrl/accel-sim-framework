# V2 implementation and result audit

- V1 remains frozen at `CORRECTNESS_MISMATCH_STOP`; its overlap has no scientific use.
- GNU patch applied the exact authorized two-line scope correction. Runner SHA is `0297e142457ea5ac4ed3d6c37889993fda4168bfcca8392b41d74ba4b698fc0b`.
- PREFILL calls the saved bound original forward. D0–D3 retain two producer streams and the original event DAG.
- Stage 1 passed tokens, 420 call order entries, 336 exact projection identities, module/policy semantics, and kernel name/grid/block inventories.
- B1_V2 overlap occurred in 10/112 windows (544929 ns total).
- Formal completed 24 B0 and 24 B1 samples in 12 complete ABBA blocks.
- B1 is slower: saving -7.217999 ms, speedup 0.911364x.
- Gate and up duration ratios are 1.024772x and 1.193848x.
- Decision: `CONCURRENCY_ACTIVATED_BUT_RESOURCE_CONTENTION_LIMITED`. No NCU or follow-up experiment was launched.
