# R17 execution-readiness checklist

Date: 2026-09-30. Preparation-only gate.

## Source work complete

- [x] Round16 closed issues are not reopened.
- [x] Direct-neighbor screen covers CAGRA/Jasper-class traversal capability.
- [x] cuVS stable v26.08.01 source authority pinned.
- [x] Stable/current low-query routing compared.
- [x] Q1 AUTO->MULTI_CTA source behavior understood.
- [x] MULTI_CTA CTA-count formula bound.
- [x] Redundant width=1/2 points removed from draft.
- [x] Persistent SINGLE_CTA boundary bound.
- [x] Dynamic batching separated from isolated-Q1 semantics.
- [x] Official cuVS-bench search knobs/timing inspected.
- [x] Public GloVe-100 upstream generation authority checked.

## Required before scientific timing

- [ ] Exact cuVS runtime/package receipt on node109.
- [ ] Driver/CUDA/RTX4080/SM89 receipt.
- [ ] Local GloVe-100 HDF5 SHA256/shape/dtype receipt.
- [ ] Stable normalization/conversion receipt.
- [ ] Prepared base/query/ground-truth hashes.
- [ ] Unit-normalization sanity check.
- [ ] Durable node164 source and any node109 replica identity.
- [ ] Dataset terms/redistribution note.
- [ ] One frozen CAGRA index identity.
- [ ] Recall@10 qualification before performance selection.
- [ ] Discovery/holdout split materialized without holdout timing.
- [ ] Preallocated output/workspace behavior verified.
- [ ] AUTO->MULTI_CTA identity receipt for Q1.

## Requires user approval

- [ ] Formal node109 CUDA timing.
- [ ] NSYS/NCU.
- [ ] Alternative execution harness.
- [ ] Holdout opening.
- [ ] Any 174/Accel-Sim work.
- [ ] Any mechanism/hardware proposal.

Stop before GPU if input authority, metric/ground-truth semantics, stable runtime, or the surviving novelty boundary fails.

State: `SOURCE_READY_INPUT_SOURCE_READY_LOCAL_RECEIPTS_PENDING_EXECUTION_NOT_AUTHORIZED`.
