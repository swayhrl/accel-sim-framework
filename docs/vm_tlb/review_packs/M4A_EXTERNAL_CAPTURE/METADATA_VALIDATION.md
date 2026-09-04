# Metadata validation

Both sidecars are `m4a-allocation-sidecar-v1`: one rank0 contiguous Weight
range (1,012,011,008 bytes) and 128 runtime-observed KV events. KV records carry
layer, K/V component, prefill/decode step, created/replaced state, range/size,
and lifetime. M4A merge-prep supersedes the old zero-counter placeholder with a
full trace-format-aware streaming address scan. Its result is explicitly
runtime-range matching—not exact per-instruction tensor-lifetime attribution—
and uses prefill step 0 only for prefill and prefill step 0 plus decode step 1
for decode1. `SYNTHETIC_KV` is absent.
