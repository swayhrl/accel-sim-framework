# M5 SIM_HOST statistics-light audit

Status: `ACTIVE_DIAGNOSTIC`, never a formal performance identity.  This audit
does not change a running replay, Core mechanism, cache/memory model, trace,
or result registry.

## Purpose and fixed diagnostic identity

The BICG T2 immutable trace is replayed through the existing trace frontend
with the existing runtime binary, Core SHA, 80-SM, cap-10240, ratio-zero and
`PAPER_BASE` model.  Every row stops at `-gpgpu_max_cycle 2000000`; this is a
host-cost cutoff, not natural completion and never a formal M5 result.

The first attempt used an invalid assumed trace subdirectory and therefore
exited before replay with `Unable to open file`.  It is preserved at
`/workspace/m5-hostdiag-bicg-80sm-cap10240-2m-20260906/`, is not evidence, and
the corrected independent namespace is
`/workspace/m5-hostdiag-bicg-80sm-cap10240-2m-r2-20260906/`.

| variant | added observer-only settings | CPU |
| --- | --- | --- |
| A0 | formal defaults: runtime stat `500`, memlatency `14`, PTX-line `1` | 32 |
| A1 | runtime stat `500000` | 33 |
| A2 | A1 + PTX-line report `0` | 34 |
| A3 | A2 + memlatency `0` | 35 |

CPUs 32--35 are distinct physical cores on NUMA node 0 (their SMT siblings
are 288--291) and none is shared with another diagnostic row.  `numactl` is
not installed, so no memory-policy claim is made.  The live formal T3 workers
retain their original unrestricted affinity and are never changed by this
audit.

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
address as `int` (`option_parser.cc`).  The documented `0x2` MC reporting test
exists, but the generic bookkeeping paths use a truth-value test; no source
use for an `0x8` behavior was found.  This is an observer-statistics type
mismatch, not a DTC timing result.  No subset mask will be adopted on
assumption: A0/A3 first establish the actual host/result behavior, and a
source repair would require a separate Core change and regression scope.

## Measurement and acceptance

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
