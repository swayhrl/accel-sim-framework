# Metadata validation

Both sidecars are `m4a-allocation-sidecar-v1`: one rank0 contiguous Weight
range (1,012,011,008 bytes) and 128 runtime-observed KV events. KV records carry
layer, K/V component, prefill/decode step, created/replaced state, range/size,
and lifetime. Address-to-trace coverage remains quantified as unavailable (zero
counters), never guessed. `SYNTHETIC_KV` is absent.
