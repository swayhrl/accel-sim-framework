# FAST64.6 — GESUMMV physical-16.5-KiB terminal-failure record

Status: **PRESERVED TERMINAL FAILURE — NOT A RESULT; SOURCE-STATE
CLASSIFICATION PENDING**

This record preserves the two exact frozen physical-16.5-KiB GESUMMV attempts
separately from retained FAST64.6 precompute results.  It does not alter the
frozen sensitivity roster, claim a stage result, or authorize a mechanism
change.

| mode | UUID | terminal UTC | exit | raw namespace |
| --- | --- | --- | ---: | --- |
| PAPER_IO | `8a6207ac-b653-4c4f-afb5-d298e8a91bcd` | `2026-09-10T19:49:11Z` | 1 | `/workspace/fast64-sensitivity-v1/fast64_sens_v1_gesummv_physical16p5_io` |
| PAPER_OO | recorded in the original v1 launch receipt | `2026-09-10T19:28:47Z` | 1 | `/workspace/fast64-sensitivity-v1/fast64_sens_v1_gesummv_physical16p5_oo` |

Both runs bind formal repaired Core `95ccdb7a...`, runtime `462d105c...`, A1
observer, scientific Framework `037f008b...`, the immutable-v2 runner and the
frozen GESUMMV payload.  The IO manifest specifically records
`FAST64_SENS_PHYSICAL_16p5KB_IO`, SHA `475b8eab...`; its terminal receipt is
atomic and exit status is `1`.

## Observed, not inferred

The IO stdout contains the simulator deadlock detector at local cycle
`37,997,199` (global cycle `4,256,917,296`) after 52,801 no-writeback cycles.
The dump shows an empty L1D MSHR, miss queue, and response FIFO for the printed
core.  The pre-existing OO attempt also reached the deadlock detector.  These
facts are sufficient to exclude either attempt from the strict-pass registry.

They are **not** sufficient to label either failure
`EXPECTED_RESOURCE_DEADLOCK`: the current formal deadlock dump does not print
the mode-equivalent DTC physical-pool ownership/free-line state required to
prove a circular undersized-pool condition.  No timeout, host slowdown, or
lower-cap-full observation is used as a substitute.

## Next ordinary action

When a resource-safe slot exists, run a hash-pinned, diagnostic-only replay
under the observational Core descendant that prints the missing ownership
state.  It must preserve the exact GESUMMV payload/config and be labeled
`NONFORMAL_DIAGNOSTIC_NOT_RESULT`.  Its sole purpose is to distinguish the
source transitions reserve/physical allocation, pending read/response, and
reclaim.  Until then these attempts remain failed evidence and cannot be used
for FAST64.4, FAST64.5, FAST64.6, or any normalized sensitivity curve.
