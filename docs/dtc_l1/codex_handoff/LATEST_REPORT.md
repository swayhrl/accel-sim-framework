# Latest Codex Report

Stage: `M5.0B_WORKLOAD_RECOVERY`

Status: **M5 BLOCKED — RESEARCHER_DECISION_REQUIRED**

## Stop record — frozen 16 KiB conventional-L1 dirty-set deadlock

M5.0B cannot continue. Canonical Parboil CUDA JDS SpMV reproduces a real
deadlock in both PAPER_BASE and LEGACY with the frozen 16 KiB, 128B-line,
four-way L1 geometry. The LEGACY control excludes DTC PIB/Tag behavior.

- Corrected source-reachable `cudaFuncCachePreferL1`/`PreferShared` variants
  now use the same frozen 16 KiB geometry; the exact corrected replay still
  fails, so that earlier configuration-fidelity omission is not causal.
- Fatal-state evidence shows no L1D MSHR, no L1 miss-queue item, no memory or
  interconnect traffic, but an L1 latency-queue load retry with all four ways
  of its target set `MODIFIED`.
- `tag_array::probe` returns `RESERVATION_FAIL` because the inherited SM7
  `gpgpu_l1_cache_write_ratio=25` policy does not yet permit a modified victim.
  The retry remains at L1 latency-queue stage zero, so its dependent
  pending-write/scoreboard state cannot retire.

This is a source-reachable conventional-L1 policy ambiguity at the researcher-
frozen geometry. Do not change the dirty-victim ratio, reinterpret
write-through `MODIFIED` state, enlarge the L1, disable deadlock detection, or
weaken pending-write/scoreboard assertions without a researcher decision.

Evidence is pushed:

- Core `2f99d81422649242ae4a328767a4848de92a1c3e`
  (`debug(l1): capture fatal dirty-set deadlock state`)
- Framework `a5b1084520a8d06ef032469e538a545c8c6f8fe4`
  (`docs(m5): record frozen 16KiB L1 deadlock evidence`)
- Full causal record: `implementation/M5_ISSUE_LOG.md`, M5-T005.

The user-requested parallel jobs have not been interrupted; their outputs are
diagnostic only and cannot advance M5 while this HARD gate is unresolved. M5,
including M5 review, must not proceed.

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

## M5.0A anchor closed

M5 now runs only on dedicated M5 branches. Branch ancestry, a Release Core
build, all three DTC CTests, and LEGACY/Base/IO/OO VecAdd sentinels pass. The
M4 LEGACY/IO/OO cycle sentinels match exactly. Runtime/toolchain/config hashes,
the resumable identity registry, safe initial concurrency, and raw-log index
are recorded in `m5/FORMAL_ANCHOR.md` and `m5/handoffs/M5_0A_ANCHOR.md`.

Active work is M5.0B recovery and source verification of all ten thesis compute
workloads. No formal paper performance figure has been claimed yet.
