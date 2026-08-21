# C2P paper-table reproduction status

## Configuration status

`configs/c2p-cache/paper-table.config` is the sole paper-table configuration.
It fixes the explicitly stated configuration fields from Table 1 wherever
Accel-Sim can represent them:

| Paper field | Reproduction setting | Status |
| --- | --- | --- |
| Simulator | Accel-Sim | matched |
| GPU | 64 SM, 1.41GHz | 64 simulator endpoints x 1 SM; 1.41GHz core/ICNT/L2 |
| Scheduling | GTO, four schedulers/SM | matched |
| L1 | 64KiB, 32-way, 128B, 20 cycles | 16 sets x 32 ways x 128B, fixed at 20 cycles |
| L2 | 128 sets, 16-way, 128B, 200 cycles | one Accel-Sim L2 slice per sub-partition, 200-cycle ROP path |
| Memory | 20 partitions, two sub-partitions each | matched |
| C2P | 5120 bits, four encodings, 64 banks x four copies, 128 engines | matched by `c2p.config` defaults |

The L1 table in the manuscript is internally inconsistent: four sets x 32
ways x 128B is 16KiB, not 64KiB. We preserve capacity, associativity, and line
size, yielding 16 sets. The paper does not specify an address hash or L2 set
hash. Accel-Sim's QV100 IPOLY implementation cannot express 20 partitions or
128 L2 sets, so the paper-table overlay uses deterministic consecutive
partition mapping and linear L2 set indexing. These are explicit simulator
adaptations, not claims about the authors' unpublished implementation.

### SM endpoint correction (2026-08-21)

The manuscript describes eight clusters of eight SMs.  In this trace-driven
Accel-Sim model, representing that layout literally as eight
`simt_core_cluster` instances creates an artificial reply/ROP deadlock: the
same Stencil baseline stops with pending stores even after its shared cluster
ejection FIFO is scaled by eight.  A control that preserves all 64 SMs and 20
memory partitions while using 64 one-SM simulator endpoints proceeds through
the same point and into later kernels.  The paper overlay therefore uses
`64 x 1` endpoints.  C2P still searches all 64 peer L1s and retains its
paper-specified C2P transport latencies; only GPGPU-Sim's unrelated cluster
aggregation is avoided.  This is a required functional-model adaptation and
is recorded with the failed 8x8 diagnostic, rather than being presented as a
literal topology match.

ATA and CCD are intentionally different: their paper comparators operate on
eight-SM logical peer groups.  `c2p_cache_comparator_cluster_size=8` makes
that grouping explicit and independent of `gpgpu_n_cores_per_cluster`; this
prevents the 64x1 endpoint adaptation from accidentally reducing ATA tag
lookups or CCD broadcasts to a single L1.  The same explicit logical grouping
also defines C2P/ideal candidate locality ordering.  This avoids silently
changing a paper eight-by-eight topology into a 64-cluster topology merely
because the simulator endpoints are decomposed for forward progress.

### L1 forward-progress correction (2026-08-21)

The capacity-preserving `16 sets x 32 ways` interpretation exposed a
pre-existing GPGPU-Sim forward-progress bug on Parboil SGEMM. The inherited
`-gpgpu_l1_cache_write_ratio 25` policy preferred clean victims globally. At
the failing point, sets 8, 9, and 11 each contained 32 dirty lines while the
cache-wide dirty ratio was below 25%; a miss mapping to set 11 therefore
received `RESERVATION_FAIL` forever even though a dirty victim was available.

`796f2609` keeps the global clean-first rule normally, but evicts that set's
LRU/FIFO dirty line when it is the only way to make progress. The corrected
configuration completes SGEMM in 475,720 cycles, exactly matching an
isolation run that restored the inherited `4 sets x 64 ways` organization
while retaining the paper's 64-SM/20-partition topology. This is a
forward-progress fix, not a geometry substitution.

The earlier apparent `2^32`-cycle failure was a deadlock formatting bug: it
printed unsigned `gpu_tot_sim_cycle - gpu_sim_cycle`. The detector had actually
fired after about 500,000 cycles in the current kernel. The diagnostic now
prints the counters separately; the two speculative timestamp-widening
commits were explicitly reverted (`c100f127`, `2a0b2204`).

## Canonical paper16 v7 campaign (in progress, 2026-08-21)

The final directional-reproduction dataset is the explicit 16-entry manifest
`configs/c2p-cache/paper16_workloads.tsv`, replayed into
`hw_run/c2p-paper16-v7-20260821` with all seven
`baseline`/`oracle`/`ideal`/`c2p`/`ata`/`ccd`/`ring` modes. A separate
`hw_run/c2p-paper16-l2-50-v7-20260821` root runs the same selected inputs at
50-cycle L2 latency for R0/R1 and S0/S1 classification. Gaussian is `_s_256`
(838 MiB trace tree) and Hotspot1 is the 1024-sized trace (994 MiB); neither
historical Gaussian-16 nor Hotspot-512 numbers below are final evidence.

The selected complete trace-tree sizes are: Btree 773 MiB, DWT2D 404 MiB,
Gaussian 838 MiB, Hotspot1 994 MiB, LUD 1.5 GiB, NN 2 MiB, CUTCP 11 GiB,
MRI-Q 1.7 GiB, SGEMM 2.1 GiB, Stencil 3.5 GiB, 2DConvolution 803 MiB,
3mm 2.8 GiB, ATAX/BICG 228 MiB each, GEMM 1.1 GiB, and GESUMMV 302 MiB.
Each output mode retains resolved configuration, trace/config/binary hashes,
backend and frontend commits, full log, and summary. Final analysis accepts
only this v7 root after seven-mode, L2-50, oracle-timing, and
remote-hit/L2-avoidance strict gates pass.

Earlier bundles below remain diagnostic history. They are not mixed into v7
aggregates or used to claim agreement with the paper.

### Default-BF refactor equivalence check

The later Figure-13 support parameterized the formerly fixed 5,120-row
Snapshot Matrix without changing its default `m5120-k4` mapping. An isolated
replay of the canonical Btree C2P input against the refactored backend and
rebuilt frontend completed in 229,052 cycles, exactly equal to the v7 C2P
summary. Every pre-existing summary field was equal; the only new fields were
the four CCD classification counters, all zero in a C2P-mode replay. This is
the behavioral regression proof for using the parameterized default in the
separate CCD/Figure-13 campaigns.

The same isolated refactored binary was also replayed in canonical Btree
**baseline** mode.  Its 234,962 cycles, 227,116,937 instructions, 1,420,865
total L2 accesses, and 1,310,865 global-read L2 accesses exactly match v7.
Across the complete self-contained summary, the only differences were again
the four newly added CCD classification fields, each zero.  Thus the two
provenance families used while resuming the long v7 campaign (`5ad465ec` and
the default-equivalent `5efa3d56`) have direct baseline and C2P evidence; the
analyzer still requires identical resolved configuration hashes for each mode
and records the exact source/binary hashes per run.

### Figure-13 parameterized-bank correction

The first non-default Figure-13 launches exposed a real model bug.  The
parameterized Snapshot Matrix correctly changed its physical row count, but
the request-side bank arbiter still computed `row / 80`, the original default
rows-per-bank value.  This silently modeled the wrong bank contention for
`m2048-k2` and `m3072-k3`; `m9216-k5` could index a bank beyond the 64-bank
arbiter and segfault.  Those launches were terminated before producing any
`summary.txt`, and are explicitly excluded from all analysis.

GPGPU-Sim commit `04962526` derives the bank from
`16 + snapshot_bf_rows_per_bank` and asserts the 64-bank bound.  A rebuilt
Accel-Sim front end then completed a Btree `m9216-k5` directed replay with a
normal exit marker, 179,144 remote hits exactly matching avoided L2 requests,
and complete Snapshot TP/FN/FP/TN counters.  All four m/k points were
restarted from the rebuilt binary afterward.  The Figure-13 analyzer also
checks the final generated configuration: the directory label `mX-kY` must
equal the resolved logical Snapshot rows and total hash count before a point
is admitted.

The repaired Btree runs now completed at all four points.  The repaired
default `m5120-k4` replay is a second default-preservation check: every
pre-existing v7 C2P summary field is bit-for-bit equal, and the only four new
fields are zero-valued CCD counters.  Thus the dynamic-bank correction changes
only non-default bank mapping/arbitration as intended; it cannot perturb the
main default-C2P performance data.

The same `m5120-k4` byte-for-byte comparison has also completed for the
substantially different Parboil SGEMM trace.  Every pre-existing primary-C2P
summary field again matches the v7 run; the only additions are the same four
zero-valued CCD counters.  Together with the Btree and LUD comparisons, this
checks default preservation across three independent workload families rather
than inferring it solely from the directed Btree replay.

### Target-probe headroom diagnostic

The partial v7 aggregate showed that Btree's realized remote-hit count was
well below its accept-time oracle opportunity count. To distinguish Snapshot
filtering from finite target-side arbitration, the diagnostic-only
`btree_target_probe_headroom.config` changed **only** the target-probe FIFO
from 32 to 256 entries and the escape timeout from 32 to 4,096 cycles. It kept
the default Snapshot geometry, engines, remote tag/return timing, and baseline
hierarchy unchanged. This result is deliberately outside the canonical v7
aggregate.

| Btree C2P run | Cycles | Remote hits | Probe-timeout fallbacks | Query-queue bypasses |
| --- | ---: | ---: | ---: | ---: |
| canonical v7 (32 entries / 32 cycles) | 229,052 | 161,628 | 438,570 | 132,808 |
| headroom diagnostic (256 entries / 4,096 cycles) | 233,788 | 211,944 | 69 | 759,549 |

More target-side headroom removes nearly all timeout fallback and raises
remote hits by 31.1%, but it makes the application 2.1% slower and causes a
5.7x increase in query-queue bypasses. Thus unlimited target waiting is not a
valid performance fix: it retains requests long enough to congest the finite
query path. The canonical finite escape is therefore retained while the final
report identifies target contention/timeout as a genuine model-and-input
sensitivity, rather than mislabeling it as Snapshot false-negative error or
tuning it away.

## Formal Btree six-mode bundle (2026-08-21)

The retained Rodinia 3.1 Btree trace is the first workload run through the
complete `baseline`/`oracle`/`ideal`/`C2P`/`ATA`/`CCD`/`RING` bundle after the
Snapshot refresh correction. Each mode has a copied executable, resolved
configuration, hashes, simulator log, and summary under the ignored
`hw_run/c2p-paper-table-results/btree_formal_r1` directory. The strict
summarizer verified that oracle leaves baseline timing unchanged and that every
remote hit avoids exactly one L2 request.

| Mode | Cycles | Change vs baseline | Remote hits | Main interpretation |
| --- | ---: | ---: | ---: | --- |
| baseline | 252,592 | — | 0 | reference timing |
| oracle | 252,592 | 0.00% | 0 | 699,085 exact peer opportunities from 1,685,582 L1 misses |
| ideal | 229,027 | -9.33% | 205,707 | exact candidate discovery reference |
| C2P | 237,809 | -5.85% | 154,748 | finite Snapshot filtering retains 75.2% of ideal remote hits |
| ATA-like | 243,092 | -3.76% | 75,407 | four aggregate-tag requests/cluster/cycle still has high tag-access traffic |
| CCD-like | 252,861 | +0.11% | 0 | the weak predictor finds no useful sharing on this trace |
| RING-like | 262,862 | +4.07% | 33,691 | serialized chip-wide discovery dominates its limited hits |

C2P’s direct Figure-14-style actual-probe distribution (excluding
zero-probe no-candidate fallbacks) is P90/P95/P99 = 2/3/6 probes for completed
remote hits and 4/5/10 for fallbacks after one or more probes. The hit P90 is
consistent with the paper’s low-candidate trend; the miss distribution is
higher than the paper’s group average, so it is recorded as a Btree-specific
model/input difference rather than tuned away. This trace is not asserted to
be the authors’ input, and the simplified far-L1 network remains an explicit
limitation.

An initial comparator launch failed before simulation because the paper overlay
was accidentally passed as a complete configuration and therefore lacked the
QV100 base cache definitions. It produced no `summary.txt`; the completed
bundle above was rerun with the same full QV100 base, trace overlay, and paper
overlay used by its core four modes. Only the completed bundle is used here.

The same strict campaign now also contains DWT2D, LUD, Gaussian-16, NN, and
the retained Parboil MRI-Q variant. DWT2D is a second positive C2P point
(-1.81%, 4,381 remote hits); LUD has only a near-neutral -0.01% change despite
1,628 remote hits. Gaussian-16 and MRI-Q are zero-opportunity controls with
C2P costs of +0.10% and +0.27%, respectively. NN has zero remote hits but a
-0.53% schedule-sensitive change, so it is retained only as a diagnostic and
is not counted as a C2P benefit. MRI-Q's paper `mri` variant is unspecified,
therefore this result is not used as a direct paper-table row.

## Earlier diagnostic runs

A full DWT2D four-mode smoke completed with this configuration before the
continuous-refresh correction:

| Mode | Cycles | Relevant check |
| --- | ---: | --- |
| baseline | 76,093 | static L1; no adaptive resize |
| oracle | 76,093 | baseline timing unchanged |
| ideal | 74,971 | 4,673 remote hits and avoided L2 requests |
| C2P | 74,574 | 4,378 remote hits and avoided L2 requests |

The smoke establishes that the table configuration can run; it is not a
paper-level performance data point because its DWT2D input trace has not been
shown to match the authors' input and trace generation. It is retained only as
a pre-correction diagnostic and will be rerun before any cross-workload
conclusion.

A four-mode Gaussian (`_s_16`) R0 control also completed under the same
paper-table configuration:

| Mode | Cycles | L1 misses | Peer opportunities | Remote hits |
| --- | ---: | ---: | ---: | ---: |
| baseline | 173,970 | n/a | n/a | n/a |
| oracle | 173,970 | 513 | 0 | 0 |
| ideal | 174,152 | 513 | 0 | 0 |
| C2P | 174,152 | 513 | 0 | 0 |

This is deliberately a no-benefit control, not an attempted paper match.  It
shows that when the trace has no redundant peer line, finite C2P does not
invent a remote hit: the observed query/update cost is 182 cycles (0.10%).
The oracle invariant and one-remote-hit/one-avoided-L2-request invariant both
passed.

The selected Hotspot-512 trace is not yet a refreshed paper-table result. Its
old baseline log reported a misleading value near `2^32` because of the
deadlock formatting bug described above; it is not evidence of a timestamp
wrap. It will be rerun with the forward-progress correction before any
comparison mode is accepted.

The similarly small NN trace is also zero-opportunity (0 remote hits), but
its finite-query modes finish in 7,850 cycles versus the 7,892-cycle baseline.
That is not reported as a C2P benefit: delaying no-candidate misses in the
finite C2P query queue changes their lower-memory injection pattern and can
smooth congestion.  An A/B implementation which accepted a query only when
the baseline lower port was free made the effect larger (7,795 cycles), so it
was rejected.  This is a calibration finding: use an input known to be the
paper's R0S1 class before comparing the reported R0S1 overhead, and retain
the queue's finite buffering as part of the modeled mechanism.

## Workload availability and staging cost

The paper lists 24 workloads. Six Rodinia, four Parboil, and six PolyBench
names have matching local source traces or retained archive members: 16/24
workload names are therefore practical to stage now. The current paper
experiment's Rodinia BFS is **not** a substitute for the paper's ISPASS BFS.

| Paper suite | Paper workloads | Local status | Trace staging size |
| --- | ---: | --- | --- |
| Rodinia 3.1 | b+tree, dwt2d, gaussian, hotspot1, lud, nn | available as retained full traces | canonical v7 selections range from 2MiB (NN) to 1.5GiB (LUD) |
| Parboil | cutcp, mri, sgemm, stencil | available in `parboil.tgz`/retained staging; exact `mri` variant must be declared | selected members are about 11GiB, 1.7GiB, 2.1GiB, and 3.5GiB |
| PolyBench | 2DConvolution, 3mm, atax, bicg, gemm, gesummv | available in `polybench.tgz` | 0.783 + 2.718 + 0.222 + 0.222 + 1.034 + 0.295 = 5.274GiB total |
| ISPASS | BFS, LIB, LPS, RAY | source exists in the retained AccelWattch artifact, but no matching pre-generated trace tree is staged | trace generation or a compatible public trace release is required |
| Pannotia | color_max, fw_block, mis, pagerank | no local trace tree | trace generation or a compatible public trace release is required |

The retained artifact containing ISPASS source is 36.9GiB and contains a
14.4GiB compressed Volta trace collection.  Its complete member list was
stream-indexed without extracting trace payloads (6,722 members); it contains
Rodinia BFS but none of ISPASS BFS/LIB/LPS/RAY.  It therefore cannot supply
any of the four paper ISPASS points. Pannotia source is small to obtain, but
trace volume cannot be stated credibly until exact graph/input sizes and
tracing parameters are fixed. Generating either missing suite with NVBit
requires access to a compatible NVIDIA GPU; without one, the practical route
is to find a public trace release and validate its provenance.

### Trace-discovery record (2026-08-20)

Two public sources were checked specifically for replay-compatible artifacts:

- Accel-Sim's [published trace index](ftp://ftp.ecn.purdue.edu/tgrogers/accel-sim/traces/1.1.0.trace.summary.txt)
  contains only Cutlass, DeepBench, Parboil, PolyBench, Rodinia 2.0/3.1, and
  Ubench suites.  It publishes neither ISPASS nor Pannotia traces.
- The canonical [ISPASS 2009 benchmark repository](https://github.com/gpgpu-sim/ispass2009-benchmarks)
  supplies CUDA source for BFS, LIB, LPS, and RAY, but no NVBit/Accel-Sim
  `kernelslist.g` trace release.  It is therefore a future trace-generation
  input, not a runnable trace source.

For the other missing suite, [Pannotia CUDA CTE](https://github.com/lashhw/pannotia-cte)
is a source-level candidate, and gem5 publishes a HIP port plus input datasets.
Neither is compatible with Accel-Sim replay without compiling a CUDA variant
and collecting a new NVBit trace.  No compatible public trace package was
found in this discovery round.  This negative result is intentional: the
experiment must not substitute algorithm names or non-NVBit traces for the
paper workloads.

## Recorded repository checkpoints

The C2P model and the paper-table experiment harness are intentionally kept
in two repositories.  Both named branches were pushed on 2026-08-20 and are
the only remote publication points for this work:

| Component | Pinned branch and commit | Remote branch |
| --- | --- | --- |
| Accel-Sim configuration, runner, and experiment records | `hrl/c2p-cache-exp-v0` at `98dbb0c` | `swayhrl/accel-sim-framework:hrl/c2p-cache-exp-v0` |
| GPGPU-Sim C2P mechanism | `hrl/c2p-cache-v0` at `2a0b2204` | `swayhrl/gpgpu-sim:hrl/c2p-cache-v0` |

Large trace files and four-mode run directories stay under ignored `hw_run/`.
Each completed bundle nonetheless contains a copied binary, resolved config,
trace/config hashes, full simulator log, and compact summary, as specified in
`experiment_execution.md`.
