# M5.0BT — Capture/replay pipeline scheduling admission

Status: `CAPTURE_AND_REPLAY_PIPELINED`; this is a scheduling admission, not a
T2 PASS or a `TRACE_FORMAL_PATH_VALID` verdict.

## Researcher scheduling authority

Exact physical-GPU capture and SIM_HOST trace replay are independent pipelines.
After a trace replay passes the basic structural-health gate, AutoDL capture
continues sequentially while replay remains logically ordered by its T2/T3
HARD gates. A captured bundle is not a formal result until its own identity,
terminal, parser and accounting gates pass.

## Live replay audit

At the audit, the only live simulator was BICG `PAPER_BASE`:

| field | evidence |
| --- | --- |
| PID / topology | `290969`; PPID `1`, PGID/SID `290969`; launched 2026-09-06 02:01:09 UTC |
| executable / argv | `/tmp/dtc-l1-m5-t2-clean-build.7tN1Dz/accel-sim.out`; `-trace /workspace/m5-trace-immutable/bicg/traces/kernelslist.g -config PAPER_BASE_16KB.config -config SM7_QV100/trace.config` |
| output / payload | `/workspace/m5-t2-bicg-80sm-cap10240-20260906/base`; immutable BICG trace bundle, not an application/PTX execution payload |
| frozen identity | Core `120978646e4c8bae2707ddfc6b31512a4a0c76c8`; runtime Framework `554743644bfd3fc28fac13bc1b78fc9f9fa6ba4f`; Base config SHA-256 `0f99ae3b7d3a81f813ba0ac9b24fab5fa57474f323bf655b0c56f73fb6d225d9` |
| trace identity | `TRACE_BUNDLE_ID=ae7f9dbd07e2da471b6e218d160b7446c710872cd85797e54bd58b42708e8a33`; `kernelslist.g` SHA-256 `6d277910149236df31f19532ac68e09415416b603e44094316f95028bdf9ba3a`; traceg-set SHA-256 `ba3bb3cb5796ca757cea548ab919d59426f70efc1d687090509308b59d9aedb3`; NVBit-v1.8 |
| frontend proof | argv supplies immutable `kernelslist.g`; stdout records that trace path, then `Processing kernel` and `Header info loaded` for both ordered `.traceg` invocations. No PTX application command is passed to the simulator. |
| resource state | 99.4% CPU, 2,506,752 KiB RSS, `Rs`; no fatal/assert/deadlock/output-mismatch/trace-corruption/missing-address-or-opcode signature |
| two-point progress | over 90 seconds, current-kernel `gpu_sim_cycle` advanced `33,182,550 -> 33,316,550` and `gpu_sim_insn` `54,363,616 -> 54,570,624`: about 1,489 cycles/s and 2,300 instructions/s |
| classification | `TRACE_REPLAY_HEALTHY_PROGRESSING` |

The same immutable BICG bundle was used by all three T2 modes. Base now
naturally terminated at `50,303,549` cycles / `158,601,216` instructions and
strict-parsed with PIB admit/retire `3,145,984/3,145,984`, lower
acquire/release `19,175,277/19,175,277`, and final PIB/lower `0/0`. IO and OO
had already naturally terminated and strict-parsed with their final
lower/inflight/PIB (and OO active-reference) states zero. The complete T2
review pack is `review_packs/M5_0BT_T2_BICG/`; T2 is `PASS`, admitting T3 but
not closing M5.0BT/Q1.

## Capture queue and admission repair

The AutoDL V100 queue resumes with GESUMMV (`gesu`) first. Its first start
correctly exposed a controller-only storage-admission defect: the heavy-pilot
receipt defines `working_headroom_bytes` as the complete raw/grouped/archive
working set, but the gate added those components again. Framework
`14be71c7968f0fb5bc1e021cf40eda41d8314171` fixes the gate to validate
`working_headroom_bytes * safety_factor`, preserves BICG binding and live free
space checks, and adds fail-closed regression coverage for the stale summed
projection. The actual heavy-pilot receipt remains BICG-bound and admits
55,353,177,980 bytes against 101,565,759,488 available bytes.

After that repair, an isolated AutoDL control checkout at `14be71c7` started
the GESUMMV controller under an exclusive capture lock. Its first GPU attempt
correctly remains preserved as `RETRY_READY`, with no bundle/archive/result:
the pinned source initializes CPU `tmp`/`y` to zero but copies uninitialized
host buffers to additive CUDA accumulators, yielding 1,964 checker mismatches.
This is a source-backed, workload-local initialization defect, not a trace or
replay verdict. The frozen source is never modified. The capture build now
requires an exact-byte checked source copy that replaces only those two device
copies with zero initialization, records the original/prepared hashes and
replacement map in `source_repair`, and refuses GESUMMV capture provenance if
that record is absent. The next attempt is therefore a new exact repaired
capture; the failed raw attempt is neither postprocessed nor bundled. BICG and
2DConv immutable bundles were not recaptured.

The corrected GESUMMV capture is now `ARCHIVE_PASS`, source checker PASS and
locally copyback-SHA/internal-bundle revalidated. It carries the audited
`GESUMMV_ZERO_DEVICE_ACCUMULATORS` provenance and is eligible for T3 only
after this T2 closure. The capture queue has independently advanced to ATAX.
