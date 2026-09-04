# Route-E NCCL kernel preservation policy

The exact paper treatment of TP collectives is unavailable. Raw rank-0 ROI
files are therefore immutable capture evidence: no script deletes, rewrites,
or replaces them. Semantic classification uses
`classify_kernels.py --kernelslist <raw>/kernelslist.g --trace-dir <raw>
--output-dir <derived>` and produces a `semantic-full-kernel-manifest.json`
containing original order, raw entry, trace path, embedded semantic name,
classification, and raw-list SHA-256; a `compute-only-kernelslist.g`
diagnostic derivative; an `nccl-only-kernelslist.g` diagnostic derivative; and
a reproducible command record.

For each kernel record, classification reads exactly one embedded
`-kernel name = ...` header—not the opaque `kernel-*.traceg.xz` filename.
Names matching `nccl`, `allreduce`, `all_gather`, `reduce_scatter`, or
`broadcast` (case insensitive) are `NCCL_COLLECTIVE`; direct Memcpy records
are `MEMCPY`; missing, malformed, or duplicate headers are `UNKNOWN_OTHER`; a
valid remaining semantic kernel name is `COMPUTE`. The derived compute-only
list excludes NCCL, MEMCPY, and UNKNOWN_OTHER while preserving original order.

The frozen formal prefill and decode1 raw lists each have 32 header-confirmed
`ncclDevKernel_AllReduce_Sum_bf16_TREE...` records. The earlier filename-only
`0 NCCL` result is historical-invalid for semantic interpretation; raw evidence
is unchanged. The permanent FULL_RANK0 versus COMPUTE_ONLY_TP_PARTITION policy
is `DEFER_TO_M4B_INTEGRATION`.
