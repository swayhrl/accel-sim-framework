# FAST64 Pending Precomputed-Acquisition Checkpoint

Status: **ACTIVE — NO LATER STAGE PASS CLAIMED**

This checkpoint records physical acquisition authorized by the throughput
update while retaining the strict logical order
`FAST64.1 -> FAST64.2 -> FAST64.3 -> ...`.

## Authority and current immutable FAST64.1 R2 wave

- `MECHANISM_BEHAVIOR_ANCHOR`:
  `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`.
- Formal instrumented Core: `bbcbb5e7565417102087bc80b14c349b4e568c05`.
- R2 execution snapshot Framework source: `037f008b330eb230353b60edf126d6be9f45afdc`.
- Runtime SHA-256:
  `6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041`.
- A1 observer SHA-256:
  `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`.

Historical r1 rows are superseded/nonformal.  The current seven-row R2 wave
uses the SHA-addressed immutable runner and has two natural terminals (BICG
Base@8192 and BICG IO@8192); BICG OO@8192, BICG IO/OO@1048576, and GESUMMV
IO@8192/1048576 remain live and untouched.  The frozen R2 closeout controller
is waiting for all seven receipts; no FAST64.1 PASS claim is made here.

## FAST64.2 forced-stress diagnostic — terminal, gate unsatisfied

| item | value |
| --- | --- |
| namespace | `fast64_2_precomputed_bicg_io_stress_cap1048576_pib1_a1` |
| workload/mode | BICG / IO |
| status | `FAST64_2_HIGH_CAP_NEGATIVE_CONTROL` |
| formal Framework launch source | `5ee236f9452cd09145ab275c530c34f263a1c2e4` |
| Core | `bbcbb5e7565417102087bc80b14c349b4e568c05` |
| high-cap config SHA-256 | `f2de27d772e667f475c0e01a41c77c6ce66084cdcb76122ce2f58266b28b3015` |
| overlay transformation | only `-gpgpu_dtc_l1_io_pib_entries: 256 -> 1`; final global cap remains 1048576 |
| source meaning | the Core bounds the IO lower-create candidate queue by this mode PIB setting before physical allocation; the two controls are source-coupled |
| terminal | natural exit `0` at `2026-09-07T16:42:35Z` |

The overlay is diagnostic only, never a performance aggregate.  It has natural
termination, zero terminal state, and lower conservation, and records zero IO
lower-create-queue-full stalls exactly as required for the preserved high-cap
negative control.  It cannot close FAST64.2 by itself.  Researcher-authorized
positive coupled-stress construction is recorded in
`FAST64_2_FORCED_STRESS_SEMANTIC_GATE.md`.  The external overlay provenance is
`/workspace/fast64-runs/overlays/FAST64_IO_CAP1048576_STRESS_PIB1.config.PROVENANCE.tsv`.

## FAST64.2 BICG coupled fallback — active, pending

| item | value |
| --- | --- |
| namespace | `fast64_2_precomputed_bicg_io_coupled_cap512_pib1_a1_r2` |
| workload/mode | BICG / PAPER_IO |
| controls | global cap `512`; source-coupled IO PIB entries `1` |
| class | `PRECOMPUTED_FAST64_2_COUPLED_STRESS_PENDING_FAST64_1_ACCEPTANCE` |
| execution source | `037f008b330eb230353b60edf126d6be9f45afdc` |
| Core / runtime / observer | `bbcbb5e...` / `6a8743b4...` / `2c2a6a27...` |
| CPU / attempt UUID | `9` / `24e4fff0-e2c5-4832-b8d6-fec5ae911249` |
| lifecycle | START receipt present; simulator CPU-active; initial failure scan clean |

The explicit 60-second admission evidence is
`/tmp/fast64-future-precompute-audit-20260908T164959Z-for-f2-recheck.tsv`:
it passed exactly one worker with zero sampled swap-out/OOM/memory PSI.  This
row is the researcher-authorized BICG fallback after NN's strict negative
pressure result.  It remains pending until natural terminal, strict collection
and FAST64.1 acceptance; it has no FAST64.2 PASS or performance-result claim.

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

## FAST64.3 Base acquisition — active, pending

| item | value |
| --- | --- |
| namespace | `fast64_3_precomputed_atax_base_cap8192_a1_r2` |
| workload/mode | ATAX / Base |
| status | `PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE` |
| execution snapshot Framework source | `037f008b330eb230353b60edf126d6be9f45afdc` |
| review checkpoint commit | `7691a09851c201870c788bc95df1802bacf82954` |
| Core / runtime / observer | `bbcbb5e...` / `6a8743b4...` / `2c2a6a27...` |
| immutable attempt | CPU 0; UUID `2e51d286-4483-45fd-8795-dd19fcd413c4`; START receipt present |
| admission evidence | `/tmp/fast64-future-precompute-audit-20260908T153334Z.tsv`: one worker safe; zero sampled swap-out/OOM/memory PSI |
| lifecycle | active; initial assertion/fatal/deadlock/output-mismatch scan empty |

This is the single small Base ramp authorized by the post-R2 audit.  It has no
claim beyond physical acquisition, and it must naturally terminate then pass
strict validation before any later-stage reuse decision.

The frozen A1 observer's final `-gpgpu_runtime_stat 500000` value parses as a
500,000-cycle sampling frequency with runtime-stat flag zero.  Source shows
that this deliberately suppresses human-readable runtime-stat output while
still calling `perf_counters.print_counters()` at each 500,000 simulated-cycle
boundary.  Before its first perf boundary, host CPU-time progress was the only
ATAX liveness evidence.  The observer/config remains frozen throughout the
ramp.

That first interval is now present and gzip-valid: the immutable ATAX perf
stream records 500,000 and 1,000,000 simulated cycles with 386,656 and
675,008 simulated instructions, respectively.  At a host observation after
the second point, the single ATAX worker had accumulated about 770 host CPU
seconds; this establishes conservative launch-to-observation lower bounds of
about 1,299 simulated cycles/s and 877 simulated instructions/s. During the
same observation, all five R2 simulator processes retained approximately
99.4--99.5% CPU.  This is a host-throughput/ramp observation, not a formal
performance result.

The required post-ramp 60-second admission audit at
`/tmp/fast64-future-precompute-audit-20260908T154840Z-post-atax.tsv` then
returned `safe_to_launch=NO`: it saw zero OOM/memory PSI/throttling and ample
headroom, but `swap_so_delta=103`.  The next Base worker was therefore not
launched.  A later fresh audit must again pass before any expansion.

An independent future-only strict collector is prepared for this exact ATAX
namespace.  It requires immutable receipts, exact identity, Base lower-credit
and PIB conservation, drained terminal state, and positive simulated
cycle/instruction progress; its result remains
`PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE`, never a FAST64.3 PASS substitute.

## Resource decision

The controlled first ramp reached 18 active simulator workers (the seven r1
rows, preserved older anchors, the stress row, and NN before it terminated).
At admission, the cgroup had a 384-CPU quota and 256-GiB memory limit, but the
host had only about 40-GiB `MemAvailable`, swap essentially exhausted, output
space about 62-GiB, and high shared load.  No sampled swap I/O, iowait,
cgroup OOM, or new error signature occurred.  No further ramp is authorized
until fresh capacity shows that throughput and memory/output headroom remain
safe.

## Controlled second Base admission (2026-09-08T15:53:37Z)

The next independent, post-ATAX-1.5M-cycle, 60-second audit is retained at
`/tmp/fast64-future-precompute-audit-20260908T155148Z-after-atax15m.tsv`.
It authorizes exactly one worker (`safe_to_launch=YES`): sampled swap-out,
cgroup OOM, memory PSI and CPU throttling were all zero; cgroup memory
headroom was 194,155,401,216 bytes and output free space was
61,786,910,720 bytes.  This is a new measurement, not a relaxation of the
prior swap-out rejection.

Only one new future-only immutable-v2 row was dispatched:

| item | value |
| --- | --- |
| namespace | `fast64_3_precomputed_gesummv_base_cap8192_a1_r2` |
| workload/mode | GESUMMV / Base |
| classification | `PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE` |
| CPU | 3 |
| launch UTC | `2026-09-08T15:53:37Z` |
| attempt UUID | `c4d6d35e-23ad-4466-b578-ed1f00eb2ee9` |
| execution snapshot Framework source | `037f008b330eb230353b60edf126d6be9f45afdc` |
| Core / runtime / observer | `bbcbb5e...` / `6a8743b4...` / `2c2a6a27...` |
| runner | SHA-addressed immutable-v2 `bf9a84c8...` |

The START receipt is present; initial process inspection finds the simulator
CPU-active and the assertion/fatal/deadlock/error scan empty except for the
printed deadlock-detection configuration description.  No FAST64.1 R2
process, R2 closeout controller, frozen R2 config, parser, validator,
collector, manifest or trace config was opened or changed.  This row has no
formal result or stage-promotion meaning until it reaches natural terminal and
the relevant FAST64.1/FAST64.2 gates pass.

The separate future-only collector
`util/dtc_l1/collect_fast64_3_gesummv_base_alias_v2.sh` is ready for this exact
namespace.  It is not part of the frozen R2 closure.  Its static syntax check
and intentional pre-terminal invocation both passed: before a
`RUN_TERMINAL.tsv` it exits fail-closed and creates neither an output directory
nor a result artifact.  After natural terminal it will require immutable
receipts and identity, `PAPER_BASE`/8192 configuration identity, lower-credit
and PIB conservation, drained final state, positive progress and a clean
failure scan; even then its only possible result label remains
`PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE` until the governing gates pass.

The future-only `monitor_fast64_3_precompute_closeout_v2.sh` is also prepared
for these two active namespaces.  It has a dedicated lock and observes only
the atomic terminal receipt; after that it runs the corresponding strict
collector once and checks for its compact evidence.  Before terminal it writes
only a monitor wait record.  It cannot launch, signal, restart or alter a
simulator, cannot modify the frozen R2 chain, and cannot promote FAST64.3.

## Future formal dynamic-pool path (prepared; not invoked)

The existing generic dynamic pool reads the legacy mutable trace runner and is
therefore not an acceptable launcher for future long formal rows.  It is not
modified, because no current row needs it.  The separately versioned
`dispatch_fast64_precomputed_row_v2.sh` and
`run_fast64_dynamic_pool_v2.sh` instead use the read-only SHA-addressed v2
runner and atomic receipts, validate the Core/runtime/A1 observer/scientific
config and trace-config identities, and alias-strict-validate every terminal
before its CPU slot is refilled.  They enforce that only Base may carry the
pre-FAST64.2 pending classification and require the later `FAST64_2_REPAIR_PASS`
artifact for post-FAST64.2 IO/OO acquisition.  Their dry-run regression creates
no namespace and demonstrates early-IO refusal.  These are future-only files:
they do not replace or modify any R2 closeout dependency, current process or
stage acceptance.

The first dispatcher inherited its launch lock into the detached child; this
was corrected in Framework `0de11045...` with a new migration lock and fd
closure.  No duplicate namespace was created and no live row was perturbed.
