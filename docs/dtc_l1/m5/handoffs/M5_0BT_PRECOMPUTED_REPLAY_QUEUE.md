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

## Post-repair identity supersession (2026-09-06T10:49+08:00)

This historical queue used Core
`120978646e4c8bae2707ddfc6b31512a4a0c76c8`.  It is retained as acquisition
and diagnosis evidence only; it cannot produce a formal M5 result after the
source-correct lower-candidate-queue repair in Core
`15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`.  The repair's full source and
invalidation evidence is
`docs/dtc_l1/implementation/M5_PRECOMPUTED_LOWER_CREATE_QUEUE_FAILURE.md`.

The pre-repair ATAX IO/OO and MVT IO/OO rows naturally exposed the exact
bounded-candidate-queue assertions in `shader.cc` (IO line 2972, OO line
3241).  They are preserved as `OBSOLETE_SOURCE_REPAIR_REQUIRED`, never as
failed workload correctness or formal performance rows.  The pre-repair ATAX
Base, GEMVER Base/IO/OO, and MVT Base workers remain non-destructively live as
diagnostic/progress anchors, but their natural terminal counters must not be
registered as formal due to the Core identity mismatch.

The repaired-Core ATAX and BICG triplets are separately manifested in
`M5_REPAIRED_CORE_REPLAY_JOB_MANIFEST.tsv`; GEMVER and MVT repaired-Core
triplets are queue-eligible only after a naturally released, recalibrated
SIM_HOST worker slot.  Thus no historical row is silently relabelled, no
valid live process is disturbed, and every later formal triplet retains one
same-bundle, same-payload, frozen-config, repaired-Core identity.

## SpMV repaired-Core pipelined acquisition (2026-09-06)

The exact SpMV payload subsequently reached archive/copyback/local-immutable
PASS under receipt `d8790ea7279aa79345650ffaafc61835187d8b1e6c4b10a6e6e2cc24891db270`.
Its current repaired-Core A0 Base/IO/OO acquisition began without waiting for
the independent 2MM physical capture, using Core `15cfa76e...`, runtime
Framework `dc7836c4...`, binary `3e71cb...`, and the frozen 80-SM/cap-10240/
ratio-zero configs.  The three isolated rows use CPUs 61/62/63 and output
roots `/workspace/m5-spmv-repaired-precompute-80sm-cap10240-20260906/{base,io,oo}`.
Each has consumed its immutable first `.traceg` header with empty stderr.

They are `PRECOMPUTED_PENDING_STAGE_ACCEPTANCE`, not formal results.  They
must naturally terminate and satisfy strict parser, trace-consumption,
application, accounting and review gates before later reuse.  Their full
identity rows are in `M5_REPAIRED_CORE_REPLAY_JOB_MANIFEST.tsv`.

### SpMV PAPER_IO terminal sub-row (2026-09-06)

The repaired-Core SpMV `PAPER_IO` acquisition row has naturally terminated
with `/usr/bin/time` exit status zero.  It remains a **single precomputed row**
and is not a formal result or a triplet PASS: its matching Base and OO rows are
still live at this observation.

The immutable trace frontend consumed all 50 expected invocation headers and
all 50 `Processing kernel` entries.  Strict parsing passed under Core
`15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`, Framework runtime
`dc7836c484544b78d143837bbbb40ecbabb15aee`, the frozen IO config
`7acb4914...`, and the SpMV bundle
`d8790ea7279aa79345650ffaafc61835187d8b1e6c4b10a6e6e2cc24891db270`.
The compact local strict summary has SHA-256
`05ea2e854a1e0a977571a42d4a9070a51b34267239994256f0db9b5890f273bf`.

| terminal check | value |
| --- | ---: |
| simulated cycles / instructions | `658,328` / `96,963,600` |
| IO lower create / issue / response | `1,329,938` / `1,329,938` / `1,329,938` |
| lower credit acquire / release / final outstanding | `1,329,938` / `1,329,938` / `0` |
| completion dependency count / closed | `4,518,800` / `4,518,800` |
| final IO PIB / inflight | `0` / `0` |
| lower-create-queue-full stalls | `0` |

No assertion, fatal, deadlock, or output-mismatch signature was found.  The
separate hardware-capture checker evidence remains bound by
`M5_0BT_SPMV_CAPTURE_CLOSEOUT.md`; no application checker is inferred from
this replay terminal event.  The manifest state is therefore
`PRECOMPUTED_TERMINAL_STRICT_PASS`, pending same-payload Base/IO/OO closure
and the later stage/review acceptance decision.

### SpMV same-bundle triplet strict closeout (2026-09-06)

All three SpMV rows have now naturally terminated with exit status zero.  Each
strict-parses, consumes exactly 50 immutable trace invocation headers and 50
`Processing kernel` entries, and has no assertion, fatal, unclassified
deadlock, or output-mismatch signature.  The Base/IO/OO rows share the same
Core, Framework runtime, source/input/tracer identity and bundle recorded in
the manifest; the source-domain dynamic identity is exact:

| source-domain field | Base | IO | OO |
| --- | ---: | ---: | ---: |
| instructions | 96,963,600 | 96,963,600 | 96,963,600 |
| dynamic loads | 722,500 | 722,500 | 722,500 |
| dynamic stores | 18,700 | 18,700 | 18,700 |
| dynamic atomics / source-reachable fences | 0 / 0 | 0 / 0 | 0 / 0 |

The Base `m4_source_completions` and `m4_observation_retires` remain zero by
the documented PAPER_BASE no-sidecar contract; these are not source-domain
trace differences.  IO and OO each close those DTC completion/retire counters
at 18,700.  Strict lifecycle closure is:

| mode | cycles | lower/conservation closure | final lifecycle state |
| --- | ---: | --- | --- |
| Base | 765,542 | lower acquire/release `3,859,653/3,859,653`; PIB admit/retire `741,200/741,200` | PIB and lower outstanding zero |
| IO | 658,328 | lower create/issue/response `1,329,938/1,329,938/1,329,938`; dependency `4,518,800/4,518,800` | PIB, inflight and lower outstanding zero |
| OO | 638,856 | lower create/issue/response `1,323,449/1,323,449/1,323,449`; dependency `4,518,800/4,518,800` | PIB, inflight, active refs and lower outstanding zero |

The Base/IO/OO strict-summary SHA-256 values are respectively
`383c82ce5eb6e76b55b6613db7b910fa22d4671fc701aed7d90d46c846bb65a1`,
`05ea2e854a1e0a977571a42d4a9070a51b34267239994256f0db9b5890f273bf`, and
`7a5f6e4a706926e1d8e6261fca6b8ce0b7c698b420e8d8e931802e2664dfa2d5`.
The rows are now `PRECOMPUTED_SAME_BUNDLE_TRIPLET_STRICT_PASS`.  This makes
the exact repaired-Core SpMV triplet reusable only after the relevant M5.0BT
and later stage review gate; it does not register a formal result or advance
M5.0BT/M5.0C.
