# One selected-stage online active-world diagnostic — frozen before candidate timing

Stage: pinned-source `_update_gradient_incremental` (`solver.py:3492–3565`) on B1024 sparse Newton/PYRAMIDAL conditional-graph solves. No other stage or second candidate is allowed.

One current-state list is built at stage entry from `ctx.done` on the GPU, in ascending logical world ID order, with a single device control thread scanning all 1024 flags. There is no host count read, future niter, prerecorded activity trajectory, difficulty sorting or cross-world math. Its list creation and count publication are part of the captured solver graph and formal complete-solver interval.

Selected-stage implementation is a fixed resident-worker mapping for its two dominant inactive-world-grid kernels:

1. `_update_gradient_h_incremental_sparse`: worker index replaces only the launch's world coordinate; each worker loops over active IDs in strides of the fixed pool. The original `slots_per_world`, 32-lane changed-row decomposition, sparse J row order, sign, upper-triangle decode and per-world `atomic_add` algorithm remain unchanged.
2. `_update_gradient_cholesky_blocked_skip_unchanged`: each worker CTA loops over active world IDs; original `block_dim`, tile size, MathDx-disabled blocked factor/solve helper, same-world factor reuse and output formulas remain unchanged.

Other kernels within the selected complete stage (`_update_gradient_zero_grad_dot`, `_update_gradient_grad`, `_padding_h`) stay on the original grid, notably preserving scratch/status writes for completed worlds. Their costs remain included in the complete solver; the candidate need not remap every kernel to reduce the heavy inactive-world launch footprint. The separate `_zero_change_counters`, line search, constraint update, `_solve_done` and graph control are untouched.

Fixed worker count: `min(nworld, 4 × SM_count) = min(1024, 4 × 76) = 304`, from a locked Warp device property query on node109 RTX4080 SM89. This is a deterministic device rule frozen before formal timing; no occupancy or worker sweep is permitted. H launch changes its first grid dimension from 1024 to 304 while keeping the same slot/lane axes; blocked Cholesky launch changes its world grid from 1024 to 304 with identical block/tile configuration. Worker loops still compute every active world and none of the completed-world H/factor work. Zero-active loops are empty.

The patch must be opt-in/default OFF. OFF must reproduce all four accepted B0 boundaries after patch insertion. Directed all-active/some-done/zero-active/no-constraint/iteration-limit canaries and four exact-entry S1 correctness must precede timing. S1 must pass the unchanged R20R3 hard gates: exact entry/constraint coverage/nefc/outer niter and non-LS overflow, capacity/finite/done, frozen qacc/qfrc/Ma/valid-force screens and qfrc source relation; LS bits are recorded but any material alpha/path propagation still fails. No tolerance, solver, EFC/J order, stop predicate or output contract changes. At most two bounded engineering repairs; otherwise the selected diagnostic fails, and there is no fallback stage.

Primary timing, if qualified, is the full `solver.solve` graph including this list/worker organization, all unmodified stage kernels and final recovery. No partial-kernel speedup can decide the science label.
