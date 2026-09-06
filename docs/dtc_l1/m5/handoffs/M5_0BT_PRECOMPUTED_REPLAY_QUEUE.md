# M5.0BT — returned-trace precomputed replay queue

Status: **ACTIVE — PRECOMPUTED_PENDING_STAGE_ACCEPTANCE**

This is an acquisition-scheduling record under the researcher-authorized
pipelined replay policy.  It does not change logical stage ordering: T3 must
still pass before its successor, and M5.0BT must satisfy every HARD gate before
M5.0C.  No row below is a formal result until natural terminal, strict parsing,
trace-consumption, correctness, accounting and review gates close.

## Admission

The following payloads had hardware checker PASS, immutable bundle PASS,
archive SHA PASS, copyback PASS and SIM_HOST internal `SHA256SUMS` plus
controller `valid_bundle()` PASS before launch.

| workload | bundle ID | immutable bundle root |
| --- | --- | --- |
| ATAX | `3ef882957eeca84f9e600fc65342493e29e63e071fe816ca10d5cbb2d210c075` | `/workspace/m5-trace-immutable/atax/atax` |
| GEMVER | `779b051990d34d0abf03f378960e5ad28d501cae7b2b9b2833df4375e5d23200` | `/workspace/m5-trace-immutable/gemv/gemv` |
| MVT | `8b96abe81eed02a614014401cb074ff9d57abd3dc6ba72260167050679ca4f3a` | `/workspace/m5-trace-immutable/mvt/mvt/mvt` |

Each triplet uses exactly one workload-local immutable `kernelslist.g`, Core
`120978646e4c8bae2707ddfc6b31512a4a0c76c8`, runtime Framework
`554743644bfd3fc28fac13bc1b78fc9f9fa6ba4f`, and the frozen ratio-zero formal
config family (`PAPER_BASE_16KB`, `PAPER_IO_16KB`, `PAPER_OO_16KB` plus
SM7 trace config).  No diagnostic statistics overlay is present.

## Resource admission and live rows

At admission the host had 512 logical CPUs, two NUMA nodes, approximately
141 GiB `MemAvailable`, negligible swap-in/out, and low disk iowait.  The
three live T3 workers measured approximately 3.2 GiB RSS each.  The first
one-minute health sample of the returned-trace rows measured a 6.66 GiB p95
RSS, retained approximately 112 GiB `MemAvailable`, and showed no swap-in or
fatal/assert/deadlock signature.  Nine newly launched formal workers therefore
form a 12-worker formal pool; the isolated four-worker stats-light study
remains outside formal accounting.  CPUs 48--56 are distinct physical cores
and avoid the diagnostic cores 40--47.

| workload | mode | CPU | simulator PID | output root |
| --- | --- | ---: | ---: | --- |
| ATAX | Base | 48 | 943020 | `/workspace/m5-precomputed-returned-80sm-cap10240-20260906/atax/base` |
| ATAX | IO | 49 | 943210 | `/workspace/m5-precomputed-returned-80sm-cap10240-20260906/atax/io` |
| ATAX | OO | 50 | 943414 | `/workspace/m5-precomputed-returned-80sm-cap10240-20260906/atax/oo` |
| GEMVER | Base | 51 | 943598 | `/workspace/m5-precomputed-returned-80sm-cap10240-20260906/gemver/base` |
| GEMVER | IO | 52 | 943770 | `/workspace/m5-precomputed-returned-80sm-cap10240-20260906/gemver/io` |
| GEMVER | OO | 53 | 944175 | `/workspace/m5-precomputed-returned-80sm-cap10240-20260906/gemver/oo` |
| MVT | Base | 54 | 944237 | `/workspace/m5-precomputed-returned-80sm-cap10240-20260906/mvt/base` |
| MVT | IO | 55 | 944255 | `/workspace/m5-precomputed-returned-80sm-cap10240-20260906/mvt/io` |
| MVT | OO | 56 | 944267 | `/workspace/m5-precomputed-returned-80sm-cap10240-20260906/mvt/oo` |

The output directories contain no committed raw logs, traces, binaries, or
datasets.  On natural terminal each row is parsed and checked independently;
only a complete same-payload triplet may enter a later reuse decision.
