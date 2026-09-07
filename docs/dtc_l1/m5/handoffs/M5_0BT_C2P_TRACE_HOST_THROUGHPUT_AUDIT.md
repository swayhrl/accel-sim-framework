# M5.0BT C2P trace and host-throughput audit

Status: **DIAGNOSTIC_EVIDENCE_ONLY; NO FORMAL-PAYLOAD SUBSTITUTION; NO
RUNNING-JOB CHANGE**.

Date: 2026-09-07.

## Question and boundary

This read-only audit addresses why a historical C2P ATAX replay reported
approximately 2,466 simulated cycles/s while the live exact-M5 ATAX
`PAPER_IO` replay's completed first kernel reported approximately 280
simulated cycles/s.  It changes no Core behavior, formal configuration,
workload input, trace, result registry, or active process.

The answer is not that the same trace became nine times slower.  The C2P and
M5 traces are different workload payloads: they have different source/ABI,
launch geometry, dynamic instruction stream, trace identities, platform
configurations, and Core/Framework commits.  C2P material may be useful for a
strictly isolated **nonformal host diagnostic**, but cannot enter a M5 formal
Base/IO/OO row or be mixed into a M5 triplet.

## Immutable identities

| field | historical C2P ATAX oracle | current M5 ATAX exact capture/replay |
| --- | --- | --- |
| trace location | `accel-sim-decoupled-l2/.../polybench-atax/NO_ARGS/traces` | `/workspace/m5-trace-immutable/atax/atax/traces` |
| Core / Framework | `f0724ce9...` / `91240349...` | Core `15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9`; active Framework branch |
| trace provenance | C2P trace SHA-256 `b6dcd0e3807bd71449d2283f97ba43a91868cb761e7b4924dd3d3063340a94ba` | NVBit-v1.8 bundle `3ef882957eeca84f9e600fc65342493e29e63e071fe816ca10d5cbb2d210c075` |
| source / capture identity | historical C2P artifact | PolyBench `5584aaa7...`; source SHA-256 `5966799837bce3d7fce603c7876f78c2c1bc487f97f590bf242e28ab2acbd230`; capture-binary SHA-256 `fb69cf3d...` |
| final platform | 64 SM (`gpgpu_n_clusters 64`) | 80 SM; global lower cap 10,240; ratio zero |
| observer baseline | runtime-stat 500; memlatency-stat 14; PTX line stats 1 | same three baseline settings in the live A0 run |

The M5 trace contract requires the source/input, `TRACE_BUNDLE_ID`, capture
result, `kernelslist.g`, traceg set, tracer, config, Core, Framework and
parser identities to be recorded together.  A workload name alone is not a
payload identity.  This is why a C2P trace cannot replace an M5 trace for a
formal performance result.

## Direct trace evidence

| kernel-1 property | C2P | M5 | M5 / C2P |
| --- | ---: | ---: | ---: |
| mangled kernel ABI | `_Z12atax_kernel1PfS_S_` | `_Z12atax_kernel1iiPfS_S_` | source/ABI differs |
| grid | `(16,1,1)` | `(128,1,1)` | 8.0x CTAs |
| block | `(256,1,1)` | `(32,8,1)` | 256 threads/CTA in both |
| total launched threads | 4,096 | 32,768 | 8.0x |
| traceg bytes | 118,289,012 | 1,233,217,485 | 10.43x |
| simulated instructions | 71,380,992 | 638,582,784 | 8.95x |

Across both kernels the C2P traceg set is 238,280,936 bytes while the M5 set
is 2,444,457,882 bytes (10.26x).  The M5 capture manifest freezes two
`(128,1,1) x (32,8,1)` invocations and `NX=NY=4096`; the C2P provenance does
not supply this M5 source/input/capture identity.

## Rate decomposition

The two available measurements do not have identical boundaries: C2P is a
natural full-two-kernel run, while M5 is the naturally completed first kernel
of a still-live IO process.  They are sufficient to reject an apparent
nine-fold host regression, but not to attribute every residual host cycle to
a particular source routine.

| measurement | C2P full run | M5 IO kernel-1 |
| --- | ---: | ---: |
| simulated cycles | 35,613,481 | 23,732,355 |
| simulated instructions | 145,666,048 | 638,582,784 |
| observed wall seconds | 14,439 | 84,863 (launch to kernel-1 terminal report) |
| simulated cycles/s | 2,466.3 | about 279.7 |
| simulated instructions/s | about 10,088 | about 7,525 |
| simulated IPC | 4.09 | 26.90 |

`cycles/s = simulated-instructions/s / simulated-IPC`.  Thus the observed
8.82x cycles/s ratio decomposes approximately into 6.58x more simulated work
per M5 cycle and only 1.34x lower host simulated-instruction throughput.  The
larger launch and trace stream are the dominant established cause of the
cycles/s difference.  The remaining 1.34x is compatible with, but does not
by itself apportion, 80-versus-64 SM per-cycle work, different Core/DTC
lifecycle work, trace parsing/format costs, and ordinary host placement/cache
effects.

## Factors ruled out or bounded

- The live M5 IO process has remained CPU-active at about 99.6% CPU.  The
  read-only host sample recorded zero I/O wait and no swap-in/out; there is no
  evidence that I/O wait explains the large rate difference.
- Both runs use the same old observer baseline (`runtime_stat=500`,
  `memlatency_stat=14`, PTX file-line stats enabled).  It cannot explain the
  cross-campaign baseline gap.
- The independently repeated BICG IO A0/A1 same-CPU test changed only
  `runtime_stat` from 500 to 500000 and was parser-visible exactly equivalent;
  it improved wall time only 1.0066x.  A1 is therefore worthwhile for future
  triplets, but cannot account for an 8.82x difference.
- No claim is made that DTC itself is responsible for the residual host
  instruction-throughput difference.  The compared Core versions and payloads
  are not controlled for that attribution.

## Reviewable next diagnostic, if approved

Run no experiment on the live ATAX processes.  If further apportionment is
needed, use an isolated nonformal namespace and an identical simulated-cycle
cutoff to form a small host-only matrix:

1. C2P trace with its recorded C2P configuration/binary, 64 SM;
2. the same C2P trace through the current trace frontend/80-SM configuration,
   explicitly labelled nonformal; and
3. the current M5 exact trace on the same CPU placement and observer identity.

For each row record cycles, instructions, host wall/user time, CPU placement,
RSS, trace bytes consumed, and parser-visible architectural counters.  Do not
compare these rows as scientific DTC performance results.  The matrix can
separate 64-to-80-SM tick cost, trace-density/parser cost, and residual
Core-path cost without changing the formal payload contract.  It must not run
until it is shown not to contend with an active formal gate, and it must not
promote C2P data into M5 result tables.
