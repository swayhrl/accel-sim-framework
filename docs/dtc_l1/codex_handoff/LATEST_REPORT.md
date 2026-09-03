# Latest Codex Report

Stage: `M4_COMPUTE_BRINGUP`

Status: **STOP — HARD FAILURE: SOURCE-REACHABLE DTC COMPLETION ACCOUNTING**

Core M3 checkpoint: `90cb35d5c4f9511a2eacb9e0e809a2d9c74ecb2c`

Framework M3 implementation/parser checkpoint:
`800fc95fe2b502e30e76ce1cb6de050f6069178e`.

## M3 closeout status

Whole-line OO random-access retirement, line-level Ref Count, merge/wakeup,
active reclamation, O01–O13, IO-vs-OO causal HOL, and the 4x32B sector
extension S01–S09 have passed. Real modes 2/3/4 VecAdd self-checks and strict
provenance parsers are recorded in:

`implementation/M3_OO_SECTOR_EVIDENCE.md`.

M2 recovery evidence remains authoritative historical context in:

`implementation/M2_IO_RESPONSE_RECOVERY_EVIDENCE.md`.

## M4 active HARD stop

The PTX proxy-fence frontend limitation is governed by the current authorized
source-reachability resolution: no PTX fence frontend support or
`membar -> FENCE_OP` mapping was added. Before F00/F01 disposition or any
remaining M4 gate could close, the first provenance-controlled real compute
triplet exposed a new source-reachable failure:

- `PAPER_IO` aborts in `ldst_unit::dtc_l1_io_complete_instruction` at
  `shader.cc:2824`, `pending >= dependencies`.
- `PAPER_OO` aborts in `ldst_unit::dtc_l1_oo_complete_instruction` at
  `shader.cc:3068`, the same invariant.
- `PAPER_BASE` did not finish within the fixed 240-second diagnostic limit.

This failure invalidates M4 compute bring-up and is not eligible for
`SOURCE_UNREACHABLE_NA`. It blocks F00 closure, remaining M4 HARD gates,
workload acceptance, review-pack creation, and M5.

Complete reproduction provenance, compact raw-log/config hashes, and the
explicit no-repair disposition are in:

`implementation/M4_COMPUTE_BRINGUP_FAILURE.md`.

Core source-domain operation observability checkpoint:

`56a9230e4a538b69a30673ebdf66c42526fb324a`

It adds only dynamic Load/Store/Atomic/source-reachable-FENCE_OP counters for
Base/IO/OO comparison. Full Core build and both CTests passed before the
workload attempt; it does not change routing, cache policy, completion, or
fence semantics.

M4 is not accepted. Do not start M5.
