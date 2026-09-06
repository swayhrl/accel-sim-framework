# M5 SIM_HOST statistics-light audit

Status: `ACTIVE_DIAGNOSTIC`, never a formal performance identity.  This audit
does not change a running replay, Core mechanism, cache/memory model, trace,
or result registry.

## Purpose and fixed diagnostic identity

The BICG T2 immutable trace is replayed through the existing trace frontend
with the existing runtime binary, Core SHA, 80-SM, cap-10240, ratio-zero and
`PAPER_BASE` model.  The originally requested `-gpgpu_max_cycle 2000000`
round is retained only as a source-classification probe; it cannot reach the
normal DTC drain boundary and is never a formal M5 result.  The admissible
host-cost comparison is the separately launched, isolated, natural-terminal
four-variant replay round.

The first attempt used an invalid assumed trace subdirectory and therefore
exited before replay with `Unable to open file`.  It is preserved at
`/workspace/m5-hostdiag-bicg-80sm-cap10240-2m-20260906/`, is not evidence.
The next cutoff round shared its working directory and is
`INVALID_OUTPUT_NAMESPACE`; the isolated r3 cutoff reproduction and the r4
natural-terminal round use distinct per-variant directories and physical
cores.

| variant | added observer-only settings | CPU |
| --- | --- | --- |
| A0 | formal defaults: runtime stat `500`, memlatency `14`, PTX-line `1` | r3: 40; r4: 44 |
| A1 | runtime stat `500000` | r3: 41; r4: 45 |
| A2 | A1 + PTX-line report `0` | r3: 42; r4: 46 |
| A3 | A2 + memlatency `0` | r3: 43; r4: 47 |

All listed CPUs are distinct physical cores on NUMA node 0, with respective
SMT siblings 256 CPUs away, and none is shared with another diagnostic row.
`numactl` is not installed, so no memory-policy claim is made.  The live
formal T3 workers retain their original unrestricted affinity and are never
changed by this audit.

## Source-backed dependency table

| setting | source path | work performed | M5 parser/formal dependence | audit disposition |
| --- | --- | --- | --- | --- |
| `gpgpu_runtime_stat=500` | `gpu-sim.cc`: sample-frequency condition; `abstract_hardware_model.cc:PerfCounter::print_counters` | every 500 cycles serializes all registered counters, opens gzip append, writes a row, and closes gzip | `parse_dtc_l1_summary.py` reads terminal `key = value` counters, not the CSV | A1 tests a sparse cadence; A0 quantifies the observer cost |
| `enable_ptx_file_line_stats=1` | `ptx-stats.cc` | gates only final `gpgpu_inst_stats.txt` writing; update routines still mutate the file-line map when disabled | no parser field or M5 metric consumes this report | A2 can suppress end report, but is not assumed to remove collection cost |
| `gpgpu_memlatency_stat=14` | `mem_latency_stat.cc`, `dram_sched.cc` | gates per-request latency histograms, bank logs and final latency reporting | no M5 parser field consumes its latency tables; DTC/L1/L2/traffic terminal counters are compared independently | A3 is permitted only if full same-cutoff equivalence holds |

`gpgpu_memlatency_stat` has a source hazard that prevents treating decimal 14
as a proven independent `0x2|0x4|0x8` contract: `memory_config` declares the
field as `bool` (`gpu-sim.h`), while `reg_options` registers its address as
`OPT_INT32` (`gpu-sim.cc`) and `option_parser_register` dereferences that
address as `int` (`option_parser.cc`).

| requested bit in decimal 14 | source-backed meaning | disposition |
| --- | --- | --- |
| `0x2` | `GPU_MEMLATSTAT_MC`; the sole bit-test found, gating end-of-run MC reporting in `mem_latency_stat.cc` | observer report only; no M5 parser field consumes it |
| `0x4` | named as “queue logs” in the option help text, but no `0x4` constant or active bit-test is present in this source tree | unsupported independent-contract assumption |
| `0x8` | no definition or consumer found | unsupported independent-contract assumption |

Generic latency bookkeeping, MRQ latency accumulation, and final latency
printing use a nonzero truth-value test.  This is an observer-statistics type
mismatch, not a demonstrated DTC timing result.  No subset mask will be
adopted on assumption: A0/A3 first establish the actual host/result behavior,
and a source repair would require a separate Core change and regression scope.

## Measurement and acceptance

### Forced-cutoff disposition

The requested initial `2,000,000`-cycle cutoff was exercised in A0--A3.  It
is not a valid DTC result boundary: `gpgpu_sim::active()` returns false as
soon as the cycle condition is reached, without waiting for the normal
cluster/memory/interconnect drain.  At final statistics,
`shader_print_dtc_l1_stats()` correctly asserts `total.admits ==
total.retires` (and Base PIB occupancy zero).  All four first-round rows
therefore reached exactly `gpu_tot_sim_cycle = 2000000` and then terminated
with that assertion because the second BICG kernel remained live.  The first
round also shared a working directory and is additionally
`INVALID_OUTPUT_NAMESPACE`; its files are retained only as failure evidence.

The independently isolated r3 repetition retains the cutoff solely to
reproduce this source-backed classification.  It is not eligible for a
performance claim.  The admissible host-cost A/B is the complete, natural
terminal BICG trace replay: it preserves the existing DTC drain assertions
and gives every observer variant the same complete workload.  No assertion is
weakened, bypassed, or reclassified as an observer difference.

For each row record wall/user/system time, maximum RSS, output bytes,
runtime-CSV bytes and terminal diagnostic state.  Compare all terminal
`key = value` counters common to A0 and each candidate, with only documented
observer outputs excluded; in particular compare simulated cycles/instructions,
DTC PIB and lower acquire/release/current state, cache/L2 traffic, and
allocation/MSHR/lower-pressure counters.  A candidate needs an independent
same-placement A0-versus-best repeat before it can be proposed for future
formal rows.  Existing T2 results retain their original configuration identity.

Hardware `perf` cannot attach in this container: `perf_event_paranoid=4` and
the process lacks `CAP_PERFMON`; no security sysctl is changed.  The direct
wall-clock A/B is therefore the admissible host measurement.

## Researcher-authorized non-candidate retirement (2026-09-06)

The researcher authorized recovery of workers consumed by candidates that can
no longer affect a stats-light adoption or repaired-Core result.  Before any
signal, their PID/PGID, argv identity, output namespace, CPU/wall time,
resident memory, compressed CSV/stdout sizes, and error scan were snapshotted.
All output namespaces remain preserved; no result registry entry was made.

| row | PID / PGID | preserved namespace | disposition | reason |
| --- | --- | --- | --- | --- |
| A2 | `795048` / `795044` | `/workspace/m5-hostdiag-bicg-80sm-cap10240-natural-r4-20260906/A2` | `RESEARCHER_ABORTED_NONCOMPETITIVE_STATS_CANDIDATE` | PTX-line suppression had no observed advantage over A1 and is not needed for the required decision. |
| A3 | `795055` / `795052` | `/workspace/m5-hostdiag-bicg-80sm-cap10240-natural-r4-20260906/A3` | `RESEARCHER_ABORTED_NONCOMPETITIVE_STATS_CANDIDATE` | No observed advantage over A1; it also carries the documented memlatency type-contract risk. |

At the snapshot both rows had about 1:58 CPU time, approximately 2.41 GiB
RSS, empty stderr, and no active fatal/assertion/deadlock/output-mismatch
signature.  `SIGTERM` was delivered only to the two isolated time-wrapper
process groups (`795044`, `795052`); both groups exited.  No `SIGKILL` was
used and A0/A1 Base were not signaled.

The released physical CPUs 46 and 47 now host the explicitly authorized,
natural-terminal repaired-Core BICG confirmation pair:

| row | PID | CPU | namespace | identity |
| --- | --- | --- | --- | --- |
| BICG PAPER_IO A1 | `1512229` | 46 | `/workspace/m5-statslight-confirm-bicg-repaired-core-80sm-cap10240-20260906/io-a1` | Core `15cfa76e...`, runtime SHA `3e71cb...`, immutable BICG trace, 80-SM/cap10240/ratio-zero, only `gpgpu_runtime_stat=500000` added. |
| BICG PAPER_OO A1 | `1512240` | 47 | `/workspace/m5-statslight-confirm-bicg-repaired-core-80sm-cap10240-20260906/oo-a1` | Same as IO except frozen PAPER_OO config. |

These rows are active observer-only confirmations, not a stats-light adoption
or formal result.  They require natural terminal, strict parser, terminal
drain/accounting, and full M5-consumed counter equivalence against their
respective repaired-Core A0 rows.

## Concurrent repaired-Core observation (2026-09-06T12:19+08:00)

The independent repaired-Core BICG `PAPER_OO` A0 replay has naturally ended
with exit status zero.  Strict parsing succeeds under Core
`15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`, Framework
`dc7836c484544b78d143837bbbb40ecbabb15aee`, the immutable BICG trace bundle,
and the frozen 80-SM/cap-10240/ratio-zero `PAPER_OO` configuration.  It is a
post-repair T2 candidate, not a stats-light decision: its paired A1 observer
run (PID `1512240`) and the repaired A0 Base/IO triplet members remain live.
No observer setting has been adopted and no formal registry entry was made.

The resulting A0 OO closure is exact: 8,764,792 simulated cycles, 158,601,216
instructions, lower create/issue/response `17,827,090/17,827,090/17,827,090`,
completion dependencies `18,350,080/18,350,080`, final PIB/inflight/active
refs/lower outstanding all zero.  This provides a clean terminal reference
for the later A0-versus-A1 equivalence comparison, but no comparison is made
before A1 naturally terminates.
