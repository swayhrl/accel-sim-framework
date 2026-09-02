# Route-E NCCL kernel preservation policy

The exact paper treatment of TP collectives is unavailable. Therefore raw
rank-0 ROI files are immutable capture evidence: no script deletes, rewrites,
or replaces them. After postprocessing,
`classify_kernels.py --kernelslist <raw>/kernelslist.g --output-dir <derived>`
creates all of the following:

- `full-kernel-manifest.json`: original order, raw name, classification rule,
  and raw-list SHA-256;
- `compute-only-kernelslist.g`: a derived diagnostic list only;
- `classification-command.txt`: reproducibility record.

Rules classify names matching `nccl`, `allreduce`, `all_gather`,
`reduce_scatter`, or `broadcast` (case insensitive) as `NCCL_COLLECTIVE`;
nonempty remaining lines are `COMPUTE`; empty/comments are `UNKNOWN_OTHER`.
M4A-C decides parser compatibility and keep/exclude/report-both policy after a
tiny trace, without recapturing raw ROI evidence.
