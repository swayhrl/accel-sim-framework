# Required final C3 closeout column semantics

When C3 reaches terminal closeout, do not label a count derived from
`^Processing kernel ` markers simply as `completed_kernels`. Those markers
mean **`processing_kernel_markers` / `started_kernels`**, not independently
proved completion.

The final closeout must either rename the column to
`processing_kernel_markers` (preferred) or retain `completed_kernels` only
with an adjacent explicit explanation of that marker semantics. Terminal
completion must remain established separately by all of:

1. `simulator_exit_status = 0`;
2. marker count equals the immutable kernel-list count;
3. telemetry-kernel-record count equals that list count; and
4. the formal parser/summary gate passes.

This is a forward closeout requirement, not a retroactive rewrite of existing
run manifests.
