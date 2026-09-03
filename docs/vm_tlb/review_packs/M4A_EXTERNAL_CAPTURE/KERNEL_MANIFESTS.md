# Kernel manifests

Raw rank0 traces and raw/full `kernelslist.g` are retained inside both archives.
The reproducible classifier reports prefill 724 and decode1 772 `COMPUTE`, with
zero `NCCL_COLLECTIVE`, `MEMCPY`, and `UNKNOWN_OTHER`; derived compute-only lists
are byte-identical to the corresponding full lists. No raw trace was deleted.
