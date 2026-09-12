# POST-FAST64 paper-grade result analysis

Status: `A_PAPER_RESULTS_READY` — `EXISTING_DATA_DERIVED_ANALYSIS` from
immutable `ACCEPTED_FAST64_EVIDENCE` only. The frozen accepted authority is
`hrl/decoupled-l1-fast64-v0@18a68dcccd795f1b6cda75504e9450d00c9cee02`
(`FAST64_COMPLETE_READY_FOR_REVIEW`). This Lane-A package does not modify or
reinterpret any accepted FAST64 result and contains no post-FAST64 simulator run.

## A0 — accepted-input freeze

`generated/A_ACCEPTED_INPUT_MANIFEST.tsv` records the frozen authority, exact
FAST12 membership, and every consumed Stage4/5/6 SHA-256. The generator refuses
to emit output unless those bound hashes match the FAST64.7 input manifest and
the primary cycles reconcile independently to both accepted Stage4 triplets and
Stage5 summary rows.

## A1 — primary performance

`generated/paper_primary_performance.tsv` is the paper-primary Base-normalized
table; Base is exactly 1.0 per workload. The exact accepted GM-FAST12 is IO
**1.326143376x** and OO **1.592062402x**. IO regressions are intentionally
retained: ATAX 0.993064680x, BICG 0.942016955x, and GESUMMV 0.925562007x.
`generated/paper_primary_performance.svg` is a reproducible figure generated
from that table. No leave-one-out statistic is used in primary reporting.

## A2 — Base structural pressure

The raw and denominator-qualified views are respectively
`generated/paper_base_pressure_raw.tsv` and
`generated/paper_base_pressure_normalized.tsv`. They separately preserve PIB
full, true cacheline/all-lines-reserved, Tag-bank conflict, MSHR entry full,
MSHR merge full, and missqueue/downstream full. These are non-exclusive
accumulated counters and are explicitly **not** a stackable 100% distribution.

## A3 — IO to OO mechanism evidence

`generated/paper_io_oo_mechanism.tsv` preserves the raw IO HOL and OO
retirement/reclaim/wakeup counters. Its two specified derived fields are:

```
IO_HOL_SM_CYCLE_FRACTION = io_hol_ready_younger_cycles / (64 * io_cycles)
OO_OOO_RETIRE_FRACTION  = oo_out_of_order_retires / oo_retire_count
```

The arithmetic and metric provenance are recorded per row; neither fraction is
presented as exclusive causal proof. `generated/paper_io_oo_mechanism.svg` is
the plot-ready visualization. ATAX, BICG, and GESUMMV preserve the IO-regression
to OO-recovery contrast, while rows with similar IO/OO behavior remain included.

## A4 — sensitivity presentation

`paper_sens_logical.tsv` uses IO@16 and OO@16 separately; `paper_sens_physical.tsv`
uses IO@32 and OO@32 separately; and `paper_sens_pib.tsv` uses IO@128 and OO@128
separately. The physical table preserves both requested points and modeled
capacities. Its four accepted BICG/GESUMMV 16.5-KiB resource deadlocks are
`NONNUMERIC_BOUNDARY_MARKER` rows with no fabricated performance value; the
accepted numerical Btree 16.5-KiB rows remain numerical. The physical SVG is
generated from numeric points only and its subtitle records that boundary.

## A5 — paper-facing workload interpretation

`generated/paper_workload_explanations.tsv` covers all 12 workloads with
performance, Base pressure, IO HOL, OO retire/reclaim, and traffic evidence.
It explicitly records that Lane A has no `SOURCE_PROVEN` performance-causal
claim and classifies its interpretations as `MEASURED_CORRELATION`; no counter
is promoted to a causal proof.
Gaussian is correctly described as a **modest approximately 1.108x benefit** in
both accepted modes, not as a mechanical non-beneficiary.

## Reproduction

From this Framework worktree run:

```bash
python3 tools/generate_post_fast64_paper_analysis.py
```

The script uses Python's standard library, consumes only committed compact
accepted evidence, writes only `docs/dtc_l1/post_fast64/`, and performs its
hash/membership/Stage4–5 reconciliation checks before generation.
