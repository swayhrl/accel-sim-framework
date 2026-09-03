# Latest Codex Report

Stage: `M4_COMPUTE_BRINGUP`

Status: **READY_FOR_M5_REVIEW**

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

## M4 completion-accounting recovery closed

The first provenance-controlled 2DConv triplet exposed a source-reachable DTC
completion failure.  It was recovered under the authorized R4C procedure:

- R4C.0--R4C.2 established Category C duplicate DTC completion for UID 15888
  at PC `0x148`; no conventional pending-write consumption occurred.
- Core `a33ffa87ed4d31d9725b693ea4f822ad1ed1c330` gates IO/OO completion on
  full PIB-reference admission, carries the registered count through a
  production exactly-once ledger, and retains all pending/scoreboard asserts.
- Final-source 2DConv PAPER_IO/PAPER_OO both pass with correct output and
  strict request/dependency/credit/PIB/inflight/ref drain.
- The separate Base rerun is `SLOW_BUT_PROGRESSING`, not deadlocked.

Complete cause, source proof, final log/config hashes, and regression results
are in `implementation/M4_COMPLETION_ACCOUNTING_RECOVERY_EVIDENCE.md`.

## M4 final closeout

All active M4 HARD gates now pass under the authorized frozen-source boundary.
The review pack is `review_packs/M4_COMPUTE_BRINGUP/`.

- Five provenance-resolved Base/IO/OO compute triplets have exact matching
  source-domain Load/Store/Atomic/FENCE_OP counts.
- Store, same-address atomic, architectural `.cg` bypass, IO HOL, OO
  ready-younger retirement, lifecycle closure, parser, and CTest gates pass.
- F00A--F00D pass. F01--F03 are explicitly `SOURCE_UNREACHABLE_NA`: the PTX
  frontend cannot produce the existing dynamic proxy-fence path. No PTX fence
  support was added and `membar` was not mapped to `FENCE_OP`.

M5 is not begun and remains unauthorized. Stop at this handoff state.
