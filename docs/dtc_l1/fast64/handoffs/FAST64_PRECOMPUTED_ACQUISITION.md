# FAST64 Pending Precomputed-Acquisition Checkpoint

Status: **ACTIVE — NO LATER STAGE PASS CLAIMED**

This checkpoint records physical acquisition authorized by the throughput
update while retaining the strict logical order
`FAST64.1 -> FAST64.2 -> FAST64.3 -> ...`.

## Authority and live FAST64.1 r1 rows

- `MECHANISM_BEHAVIOR_ANCHOR`:
  `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`.
- Formal instrumented Core: `bbcbb5e7565417102087bc80b14c349b4e568c05`.
- r1 execution snapshot Framework source: `037f008b330eb230353b60edf126d6be9f45afdc`.
- Runtime SHA-256:
  `6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041`.
- A1 observer SHA-256:
  `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`.

The seven r1 qualification rows remain live and untouched: BICG Base/IO/OO at
8192, BICG IO/OO at 1048576, and GESUMMV IO at 8192/1048576.  No terminal,
parser, accounting, or FAST64.1 PASS claim is made here.

## FAST64.2 forced-stress diagnostic — terminal, gate unsatisfied

| item | value |
| --- | --- |
| namespace | `fast64_2_precomputed_bicg_io_stress_cap1048576_pib1_a1` |
| workload/mode | BICG / IO |
| status | `PRECOMPUTED_FAST64_2_DIAGNOSTIC_PENDING_FAST64_1_ACCEPTANCE` |
| formal Framework launch source | `5ee236f9452cd09145ab275c530c34f263a1c2e4` |
| Core | `bbcbb5e7565417102087bc80b14c349b4e568c05` |
| high-cap config SHA-256 | `f2de27d772e667f475c0e01a41c77c6ce66084cdcb76122ce2f58266b28b3015` |
| overlay transformation | only `-gpgpu_dtc_l1_io_pib_entries: 256 -> 1`; final global cap remains 1048576 |
| source meaning | the Core bounds the IO lower-create candidate queue by this mode PIB setting before physical allocation; the two controls are source-coupled |
| terminal | natural exit `0` at `2026-09-07T16:42:35Z` |

The overlay is diagnostic only, never a performance aggregate.  It has natural
termination, zero terminal state, and lower conservation, but records zero IO
lower-create-queue-full stalls and therefore cannot close FAST64.2.  The
source-backed semantic incompatibility and required researcher decision are
recorded in `FAST64_2_FORCED_STRESS_SEMANTIC_GATE.md`.  The external overlay
provenance is
`/workspace/fast64-runs/overlays/FAST64_IO_CAP1048576_STRESS_PIB1.config.PROVENANCE.tsv`.

## FAST64.3 Base acquisition — terminal but pending

| item | value |
| --- | --- |
| namespace | `fast64_3_precomputed_nn_base_cap8192_a1` |
| workload/mode | NN / Base |
| status | `PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE` |
| Framework launch source | `0de11045e191d8a50e8de1d2e5e2a59cd3df65bc` |
| Core | `bbcbb5e7565417102087bc80b14c349b4e568c05` |
| config SHA-256 | `1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde` |
| frozen trace-list SHA-256 | `6b5e83e43dc74ae1b23312e1772d19a774b6c7397740c1bc1e0f572db77f8664` |
| terminal | natural exit 0; wall 8.86 s; RSS 450560 KiB |
| strict evidence | `/workspace/fast64-runs/validated/fast64_3_precomputed_nn_base_cap8192_a1.summary.json` |
| cycles / instructions | 6,985 / 1,284,872 |
| accounting | lower acquired/released 10,691/10,691; terminal lower and PIB occupancy 0; lower-cap-full 0 |

Strict validation passed its trace sequence, source identity, natural-exit,
failure scan, parser, and terminal-accounting checks.  It remains pending and
cannot become an accepted FAST64.3 row until all relevant FAST64.1/2 HARD
gates pass.

## Resource decision

The controlled first ramp reached 18 active simulator workers (the seven r1
rows, preserved older anchors, the stress row, and NN before it terminated).
At admission, the cgroup had a 384-CPU quota and 256-GiB memory limit, but the
host had only about 40-GiB `MemAvailable`, swap essentially exhausted, output
space about 62-GiB, and high shared load.  No sampled swap I/O, iowait,
cgroup OOM, or new error signature occurred.  No further ramp is authorized
until fresh capacity shows that throughput and memory/output headroom remain
safe.

The first dispatcher inherited its launch lock into the detached child; this
was corrected in Framework `0de11045...` with a new migration lock and fd
closure.  No duplicate namespace was created and no live row was perturbed.
