# Formal decode1

## PASS — durable G3 checkpoint

The completed formal run is `m4a-llama-decode1-20260903T004138Z` at capture
Framework `c79f4469c6a2befa59e4c4efcd3c885dc2259a81`. It used the frozen local
snapshot of `meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`,
real TP=4, BF16, batch 8, input sequence 64, output tokens 3, and rank0-only
NVBit. Model load, TP initialization, flat-weight binding, and warmup remained
outside the profiler-controlled decode1 ROI.

- Raw rank0 traces retained: 772 `*.trace.xz`.
- Postprocessed traces retained: 772 `*.traceg.xz`.
- Raw/full `kernelslist.g` SHA256:
  `734674fa079cfc72ae1ea9b78bd7d31e86179612e21f7a6b5eba94e86ad3fd72`.
- Embedded-header audit supersedes the filename-only count: 740 COMPUTE and 32
  `NCCL_COLLECTIVE`, with no observed direct MEMCPY or UNKNOWN entry.
- Metadata: one contiguous Weight allocation and 128 real KV events; no
  synthetic KV. Runtime-range coverage is reported by M4A merge-prep rather
  than inferred from access patterns.

The archive is retained locally at
`/workspace/m4a-rented-host-pilot/formal-decode1/m4a-llama-decode1-20260903T004138Z.tar.zst`.
Its SHA256 is
`5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad`; archive,
tar, and internal `SHA256SUMS` checks pass. It must not be recaptured.
