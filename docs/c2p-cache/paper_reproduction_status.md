# C2P paper-table reproduction status

## Configuration status

`configs/c2p-cache/paper-table.config` is the sole paper-table configuration.
It fixes the explicitly stated configuration fields from Table 1 wherever
Accel-Sim can represent them:

| Paper field | Reproduction setting | Status |
| --- | --- | --- |
| Simulator | Accel-Sim | matched |
| GPU | 64 SM, 1.41GHz | 8 clusters x 8 SM; 1.41GHz core/ICNT/L2 |
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

A full DWT2D four-mode smoke completed with this configuration:

| Mode | Cycles | Relevant check |
| --- | ---: | --- |
| baseline | 76,093 | static L1; no adaptive resize |
| oracle | 76,093 | baseline timing unchanged |
| ideal | 74,971 | 4,673 remote hits and avoided L2 requests |
| C2P | 74,574 | 4,378 remote hits and avoided L2 requests |

The smoke establishes that the table configuration can run; it is not a
paper-level performance data point because its DWT2D input trace has not been
shown to match the authors' input and trace generation.

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
| Rodinia 3.1 | b+tree, dwt2d, gaussian, hotspot1, lud, nn | available as retained full traces | selected inputs range from 356KiB to 773MiB; larger alternatives reach 1.5GiB |
| Parboil | cutcp, mri, sgemm, stencil | available in `parboil.tgz`/retained staging; exact `mri` variant must be declared | selected members are about 11GiB, 1.7GiB, 2.1GiB, and 3.5GiB |
| PolyBench | 2DConvolution, 3mm, atax, bicg, gemm, gesummv | available in `polybench.tgz` | 0.783 + 2.718 + 0.222 + 0.222 + 1.034 + 0.295 = 5.274GiB total |
| ISPASS | BFS, LIB, LPS, RAY | source exists in the retained AccelWattch artifact, but no matching pre-generated trace tree is staged | trace generation or a compatible public trace release is required |
| Pannotia | color_max, fw_block, mis, pagerank | no local trace tree | trace generation or a compatible public trace release is required |

The retained artifact containing ISPASS source is 36.9GiB and contains a
14.4GiB compressed Volta trace collection, but individual traces for the four
paper cases have not yet been indexed or validated. Pannotia source is small
to obtain, but trace volume cannot be stated credibly until exact graph/input
sizes and tracing parameters are fixed. Generating either missing suite with
NVBit requires access to a compatible NVIDIA GPU; without one, the practical
route is to find a public trace release and validate its provenance.
