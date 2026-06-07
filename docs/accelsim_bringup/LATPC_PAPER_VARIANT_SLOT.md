# LATPC Paper Variant Slot

A16 creates a paper-specific LATPC variant slot for baseline-vs-variant plumbing.

Scope:

- Select one LATPC paper workload with an existing Accel-Sim trace.
- Create `baseline` and `latpc_noop` variants.
- Run both variants with identical simulator binary, trace, config, and simulator arguments.
- Compare parsed stats to validate no-op equivalence.

Non-goals:

- Do not implement LATPC.
- Do not reproduce LATPC speedup.
- Do not validate the full 24-workload paper campaign.
- Do not generate traces unless a GPU is explicitly available and enabled.
