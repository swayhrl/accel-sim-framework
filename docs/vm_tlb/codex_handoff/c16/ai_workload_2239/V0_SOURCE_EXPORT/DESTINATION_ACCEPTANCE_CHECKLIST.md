# Destination acceptance checklist (prepared only; not executed)

## Exact next starting entry

After this source-export branch is pushed, the destination Docker must first
fetch and check out the final commit on
`hrl/c16-ai-workload-2233-to-2239-handoff-v0`, then read this directory in the
following order:

1. `SOURCE_STATE.md`
2. `ARTIFACT_TRANSFER_MANIFEST.tsv`
3. `STORAGE_TRANSFER_PLAN.md`
4. `UNKNOWN_PROVENANCE.md`

It must then create a **new destination receipt** that binds its actual external
storage mount.  It must not reuse `/data/c16` or any source Docker path by
assumption.

## Gates for the later destination phase

- [ ] Verify destination Git commit and clean working tree.
- [ ] Record actual destination mount/ownership/free capacity in a new receipt.
- [ ] Reconcile every planned storage row with source and destination
  size/SHA; copy-not-move only.
- [ ] Verify model identity/revision and frozen-input four-hash binding without
  invoking a tokenizer; do not claim the model is already present until this
  succeeds.
- [ ] Rebuild or verify CPython/PyTorch/CUDA/NVBit/NCU independently.  Do not
  inherit Python, CUDA binding, NVBit build, environment variables, or model
  cache from source by convention.
- [ ] Keep 3090 historical records separately namespaced and use them only for
  explicitly authorized comparison.
- [ ] Preserve R4 as mechanism-only/non-authoritative.

This checklist intentionally does not launch a GPU workload, profiler, tracer,
model, or destination copy action.
