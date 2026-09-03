# Formal prefill

## PASS — durable G3 checkpoint

The completed formal run is `m4a-llama-prefill-20260902T182016Z` at Framework
`c79f4469c6a2befa59e4c4efcd3c885dc2259a81`. It used the frozen local snapshot
of `meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`, real
TP=4, BF16, batch 8, input sequence 64, output tokens 3, and rank0-only NVBit.
Model load, TP initialization, flat-weight binding, and warmup remained outside
the profiler-controlled prefill ROI.

- Raw rank0 traces retained: 724 `*.trace.xz`.
- Postprocessed traces retained: 724 `*.traceg.xz`.
- Raw/full `kernelslist.g` SHA256:
  `1ac8a5c2496491be41af6305673b34a661175c15754a438fc740ca2d2449c971`.
- Classifier result: 724 `COMPUTE`, 0 `NCCL_COLLECTIVE`, 0 `MEMCPY`, and 0
  `UNKNOWN_OTHER`; the raw list remains in the bundle.
- Metadata validator: one contiguous Weight allocation, 128 real KV events,
  no synthetic KV; trace-address coverage is correctly reported as unavailable
  (all coverage counters zero), not inferred.

The archive is retained locally at
`/workspace/m4a-rented-host-pilot/formal-prefill/m4a-llama-prefill-20260902T182016Z.tar.zst`.
It has SHA256
`f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181`; the
remote and local values matched, the local archive was rechecked after the
AutoDL balance shutdown, and zstd/tar integrity plus internal `SHA256SUMS`
verification pass. The shutdown is an infrastructure interruption after G3,
not a capture failure; this prefill must not be recaptured.
