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

## FAST64.3 controlled third Base admission and v3 closeout recovery

After the two-row Base ramp and BICG coupled stress remained CPU-active without
cgroup throttling, swap-out, OOM, memory PSI, or unsafe output-space behavior,
the fresh 60-second audit
`/tmp/fast64-post-smallbatch-resource-audit-20260908T172527Z.tsv` returned
`safe_to_launch=YES` for exactly one additional worker.  It observed 17.215
cgroup CPU-core equivalents, 205,771,091,968 bytes cgroup memory headroom,
zero sampled swap-out/OOM/memory PSI/throttling, and 62,715,150,336 bytes
output free space.

The immutable-v2 dispatcher then admitted exactly one additional frozen Base
row, not an IO/OO row:

| item | value |
| --- | --- |
| namespace | `fast64_3_precomputed_dwt2d_base_cap8192_a1_r2` |
| workload/mode | DWT2D / Base |
| CPU / attempt UUID | `11` / `adc75323-a985-4222-bc28-804e4a9dedad` |
| launch | `2026-09-08T17:26:51Z` |
| class | `PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE` |
| identity | Core `bbcbb5e...`; runtime `6a8743b4...`; A1 observer `2c2a6a27...`; Framework execution snapshot `037f008b...` |
| payload | frozen DWT2D `kernelslist.g` SHA-256 `337087fedad435cd92cbd7e0f962f90d567ec9e77038fd8150977b7c6beb7164` |
| lifecycle | atomic START receipt published; CPU-active; narrow initial error scan clean |

The running v2 ATAX/GESUMMV collectors match the normal configuration echo
`-gpgpu_deadlock_detect` as though it were a real deadlock, so they would
false-fail at terminal.  They were not modified while their v2 monitor is
live.  Versioned `collect_fast64_3_base_alias_v3.sh` and
`monitor_fast64_3_base_alias_v3_closeout.sh` instead match actual failure
diagnostics and cover ATAX, GESUMMV, and DWT2D only after each atomic terminal
receipt.  Their pre-terminal regression passed; the v3 monitor has its own
lock and remains pending-only.  This changes neither simulator behavior nor
the R2 frozen closeout closure.

The next fresh 60-second audit at
`/tmp/fast64-post-dwt-resource-audit-20260908T173337Z.tsv` rejected another
admission solely because `swap_so_delta=72`, despite zero sampled OOM,
memory-PSI, and CFS throttling and 207,377,240,064 bytes cgroup memory
headroom.  No Btree or other replacement row was launched.  This is an
operational fail-closed wait, not a FAST64 result failure or a change to the
current nine live jobs.

### DWT2D Base natural terminal — strict-valid but still pre-acceptance

The admitted DWT2D/Base row naturally terminated with exit `0` at
`2026-09-08T17:40:19Z`.  The separate v3 closeout monitor observed its atomic
`RUN_TERMINAL.tsv` and produced compact evidence in
`fast64/generated/fast64_3_dwt2d_base_alias_v3/`; it did not modify the live
v2 monitor or any frozen R2 closeout dependency.  The result is strictly
valid only as physical precomputation:

| item | value |
| --- | --- |
| status | `FAST64_3_BASE_PRECOMPUTED_STRICT_VALID_PENDING_FAST64_1_2_ACCEPTANCE` |
| mode / cap | `PAPER_BASE` / `8192` |
| cycles / instructions | `344,119` / `148,684,429` |
| lower accounting | acquired/released `757,359/757,359`; terminal lower `0` |
| PIB accounting | admits/retires `437,886/437,886`; terminal PIB `0` |
| cap condition | `DTC_L1_lower_cap_full_events=0`; peak outstanding `2048` |
| immutable attempt | UUID `adc75323-a985-4222-bc28-804e4a9dedad`; runner `bf9a84c8...` |
| provenance | Core `bbcbb5e...`; runtime `6a8743b4...`; observer `2c2a6a27...`; execution snapshot `037f008b...` |

The alias-aware v3 collector accepted one canonical timestamped perf stream
and its normal `perf_counter.csv.gz` alias as one epoch.  It records a clean
precise assertion/fatal/deadlock/output-mismatch scan, positive cycle and
instruction progress, exact Base/cap identity, and drained terminal state.
This is **not** a FAST64.3 PASS, a later-stage performance claim, or permission
to launch IO/OO work: it remains governed by FAST64.1 and FAST64.2 acceptance.

The future-only Base structural companion extractor additionally establishes
the source-correct distinction required by FAST64.3 metric completeness.
Core `gpu-cache.h` defines `LINE_ALLOC_FAIL` as all cache lines reserved, while
`DTC_L1_tag_conflicts` remains Tag-bank arbitration only.  From DWT2D's final
canonical perf row it records `1,417,779` conventional L1D cache-line
reservation failures, `346,268` MSHR-entry-full events (cross-checked exactly
against the terminal DTC summary), zero MSHR-merge-full events, and `18,367`
L1D miss-queue/downstream-full events.  The compact companion is
`FAST64_3_DWT2D_BASE_STRUCTURAL_METRICS_V1.json`; it also preserves lower
create/response (`757,359/757,359`) as the Base live-miss lifecycle closure.
This source-backed extraction is a pre-acceptance metric companion, not a
FAST64.3 result promotion.

`monitor_fast64_3_base_structural_companion_v1.sh` is a separate future-only
observer for ATAX, GESUMMV, DWT2D and GEMM.  It waits for both an atomic Base
terminal receipt and the corresponding already-strict alias-aware JSON before
calling the structural extractor once.  The DWT2D companion remains preserved;
the live rows have no companion output.  Its static/once regression passed and
the detached monitor writes only its explicit log.  It cannot signal, launch,
collect Base validity, or modify the active v3/v4 Base collectors or frozen R2
closure.

The subsequent review-time 60-second audit
`/tmp/fast64-post-review-r2-fullwave-resource-audit-20260908T174003Z.tsv`
again rejected a new worker fail-closed because `memory_psi_avg10=0.01`.
It observed zero sampled swap-out/OOM/throttling, 205,547,999,232 bytes
cgroup headroom and 62,614,523,904 bytes output free, but no new worker was
admitted.

### GEMM Base controlled replacement admission — active, pending

DWT2D's natural terminal justified a new, independent 60-second admission
measurement.  `/tmp/fast64-post-dwt-terminal-resource-audit-20260908T174330Z.tsv`
returned `safe_to_launch=YES` for exactly one worker: zero sampled
swap-out/OOM/memory PSI/CFS throttling, 246 candidate physical cores,
207,427,174,400 bytes cgroup headroom and 62,598,434,816 bytes output free.
The immutable-v2 dispatcher then admitted only the next nonredundant Base row:

| item | value |
| --- | --- |
| namespace | `fast64_3_precomputed_gemm_base_cap8192_a1_r2` |
| workload/mode | GEMM / Base |
| CPU / attempt UUID | `11` / `4b62ba62-9ee3-41ed-8a67-402172e594fa` |
| launch | `2026-09-08T17:45:33Z` |
| class | `PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE` |
| identity | Core `bbcbb5e...`; runtime `6a8743b4...`; A1 observer `2c2a6a27...`; Framework execution snapshot `037f008b...` |
| payload | frozen GEMM `kernelslist.g` SHA-256 `fd9a9430fc95eb0af4c73b9710db271f8e32bff4ea2f5dd08a4e8e17c9b02057` |
| lifecycle | atomic START receipt present; CPU-active; initial precise failure scan clean |

The active v3 Base monitor has a fixed three-row scope and is not changed.
Future-only `collect_fast64_3_gemm_base_alias_v4.sh` and
`monitor_fast64_3_gemm_base_alias_v4_closeout.sh` instead cover this one new
namespace.  Their static regression passed; the monitor observes only its
atomic terminal receipt and cannot modify a simulator, the v3 monitor, or the
frozen R2 closure.  GEMM remains physical precomputation only until the
FAST64.1 and FAST64.2 gates pass.

The first detached v4 monitor inherited a closing caller stdout pipe.  Its
next `tee` write therefore exited before a second poll; GEMM itself remained
CPU-active, had no terminal receipt, and was never signalled.  A short
read-only two-second-poll reproduction proved the monitor loop correct.
The exact already-committed v4 bytes were then relaunched in a separate session
with stdout/stderr redirected to `/dev/null`; its explicit log remains the
only monitor output channel.  It survived a complete 120-second poll and
wrote the subsequent wait record at `2026-09-08T18:03:47Z`.  This is a
controller-lifecycle repair only, not an evidence collection, result change,
or modification of any frozen R2 dependency.

### GEMM/Base natural terminal — strict-valid precompute

GEMM/Base naturally exited `0` at `2026-09-08T23:15:14Z`. Its independent
future-only v4 monitor observed the atomic terminal receipt and produced
compact alias-aware evidence in `generated/fast64_3_gemm_base_alias_v4/`.
The sole immutable attempt is `4b62ba62-9ee3-41ed-8a67-402172e594fa` with
runner `bf9a84c8...`; identity is Core `bbcbb5e...`, runtime `6a8743b4...`,
A1 observer `2c2a6a27...`, execution snapshot `037f008b...`, Base config
`1a016e3c...`, and frozen GEMM payload. The precise failure scan is clean;
one canonical perf epoch is normalized from the normal alias.

| condition | observed value |
| --- | ---: |
| cycles / instructions | `2,662,394` / `739,246,080` |
| lower acquired / released | `16,813,388 / 16,813,388` |
| PIB admits / retires | `12,599,296 / 12,599,296` |
| final lower / PIB | `0 / 0` |
| lower-cap-full / peak | `0 / 2,048` |
| line allocation / MSHR-entry / miss-queue events | `114,099,368 / 0 / 49,091` |

The compact structural companion preserves Tag-bank conflicts (`25,214,976`)
as a separate diagnostic category. GEMM is
`FAST64_3_BASE_PRECOMPUTED_STRICT_VALID_PENDING_FAST64_1_2_ACCEPTANCE` only:
it is not a FAST64.3 result promotion, a triplet result, or authorization to
launch additional Base work.

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

## Future-only FAST64.4 triplet validator preflight

`validate_fast64_triplet_v1.py` is prepared but is not connected to a live
dispatcher, monitor, or acceptance transition.  It consumes only three
already strict-parsed compact JSON summaries and requires Base/IO/OO mode
identity, common workload/payload/Core/Framework identity, common trace-list
identity, equal dynamic instruction-domain progress, and source-mode terminal
drain/conservation.  Its formal invocation additionally requires immutable
attempt receipts plus common runtime and observer identities.  A synthetic
immutable fixture based on the existing NN telemetry triplet passes, while a
one-instruction OO mismatch fails closed.  The only PASS string it can write
is `FAST64_TRIPLET_STRICT_VALID_PENDING_STAGE_ACCEPTANCE`; it cannot confer
FAST64.2, FAST64.3, or FAST64.4 acceptance.
