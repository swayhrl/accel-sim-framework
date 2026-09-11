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

The original hash-pinned V1 dispatcher correctly fails closed after the active
Core worktree advanced to Core-41: its specified observational Core is
`f2836ea1...`, so it must not silently validate the changed worktree.  The
future-only V2 dispatcher
`util/dtc_l1/dispatch_fast64_6_gesummv_physical16p5_diagnostic_v2.sh` preserves
the same observational Core/binary/config/trace contract but validates
`f2836ea1...` in a clean detached worktree.  Both IO and OO V2 dry runs pass.
It refuses an existing namespace and requires both `--dispatch` and an
explicitly supplied safe CPU; it cannot modify the active Core-41 worktree or
create a formal result.

The companion parser
`analyze_fast64_6_physical16p5_diagnostic_v1.py` only accepts the
post-deadlock `DTC_L1_IO_DEADLOCK` or `DTC_L1_OO_DEADLOCK` source print.  It
records IO FIFO/partial-allocation state separately from OO ownership/refcount
state and explicitly refuses to assign IO semantics to OO.  A future
diagnostic remains `NONFORMAL_DIAGNOSTIC_NOT_RESULT`; its sole purpose is to
distinguish reserve/physical allocation, pending read/response, and reclaim.
Until then these attempts remain failed evidence and cannot be used for
FAST64.4, FAST64.5, FAST64.6, or any normalized sensitivity curve.

## V2 diagnostic acquisition active (2026-09-11)

After the V3 admission audit passed two additional workers (no sampled swap
activity, memory PSI, OOM or CFS throttling; 83.9 GiB projected
`MemAvailable` after admission), the committed V2 dispatcher was dry-run
verified and launched exactly once per mode in fresh namespaces:

| mode | CPU | UUID | namespace | status |
| --- | ---: | --- | --- | --- |
| IO | 0 | `5a6b4eeb-1563-49f5-8af0-a20ded38fc3c` | `fast64_6_gesummv_physical16p5_io_coref283_diag_v2` | `NONFORMAL_DIAGNOSTIC_NOT_RESULT`, active |
| OO | 7 | `ac6c1a27-7980-4cdc-85c1-64974a536b76` | `fast64_6_gesummv_physical16p5_oo_coref283_diag_v2` | `NONFORMAL_DIAGNOSTIC_NOT_RESULT`, active |

Each namespace has an atomic START receipt binding observational Core
`f2836ea1...`, binary `361aada1...`, immutable runner `bf9a84c8...`, A1,
scientific Framework `037f008b...`, the literal original GESUMMV payload and
its respective frozen physical-16.5-KiB config.  These are diagnostic only:
their terminal analyzer output may classify source state but cannot relabel
the preserved formal failures or create a FAST64 result.
