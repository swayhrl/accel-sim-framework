# Simulator L2/writeback scope requalification

Current status: `COMPLETE_TRAFFIC_RESPONSE_NO_CYCLE_GAIN`.

## Source audit (`VERIFIED_CODE`)

The accepted config uses:

`S:2048:128:16,L:B:m:L:X,A:192:4,32:0,32`

with eight memory channels and two subpartitions per channel. Thus the modeled
L2 has 16 instances, 128-byte lines, 2048 sets/instance and 16 ways, totaling
64 MiB and 524,288 lines.

The existing writeback path is real:

1. `tag_array::probe` chooses a legal LRU/FIFO victim subject to the existing
   dirty-line eligibility rule.
2. `tag_array::access` exports block address, dirty byte/sector masks and
   modified size in `evicted_block_info`.
3. `data_cache` allocates an `L2_WRBK_ACC` `mem_fetch` and places it in the
   finite miss/lower-memory queue.
4. the memory subpartition and DRAM model account writeback requests through
   ordinary queues and `n_wr_bk`/DRAM write statistics.

The narrow implementation points are therefore victim selection,
`evicted_block_info`, and the existing writeback enqueue function. No DRAM
latency/bandwidth, cache capacity, port, queue or translation parameter changes.

The PRE hook is `gpgpu_sim::launch`, before any CTA/L2 access. The POST hook is
`gpgpu_sim::set_kernel_done`. Formal use is restricted to the admitted single
context/stream-0 ordered sequence. Runtime checks enforce serialized launch,
exact ordered names, unique runtime UIDs, matching completion UIDs, and complete
PRE/POST consumption.

## Completed qualification

- accepted pre-implementation VM/controller regressions: 3/3 PASS;
- candidate post-implementation regressions: 3/3 PASS;
- ten transient-policy directed tests: 10/10 PASS;
- complete unified binary build: PASS;
- default-OFF accepted T2 smoke: exact 93,079 cycles, 43,357,696 instructions,
  1,216 CTAs, 411,008 unique UIDs, untranslated/unobserved zero;
- no transient output when selector/diagnostics are absent;
- strict producer/node164 hashes: review pack 29/29, traceg 18/18 and ordered
  kernelslist PASS;
- exact trace header/native-binding/lifetime identity and A/B/X0/X1 address
  intersections PASS;
- PRE/POST integrated default-OFF, explicit-none, O1-no-overlap and M1-no-overlap
  smokes all preserve the exact accepted T2 signature and terminal quiescence.

## Formal B0 scope qualification (`VERIFIED_RUN`)

The full 18-kernel replay passes every frozen identity, correctness, coverage and
quiescence gate:

- 15,374,861 total cycles, 6,195,889,164 instructions and 46,860 CTAs;
- 194,132,409/194,132,409 translated admissions across 18 ordered kernel UIDs,
  with untranslated, unobserved and duplicate application all zero;
- 150,408,736 target-region accesses and 3,770,353 transient admissions;
- 2,531,000 real L2 writeback transactions totaling 323,967,936 bytes;
- 2,530,987 target-region writebacks totaling 323,966,336 bytes;
- 5,061,999 modeled 64-byte DRAM writeback commands totaling the same
  323,967,936 bytes; regular DRAM writes are zero;
- 4,315,826 modeled DRAM read commands / 276,212,864 bytes;
- complete final drain in 192 cycles with GPU active, L2-writeback active,
  max-limit hit and deadlock all zero; all eight DRAM latency queues,
  translation MSHRs/PWQ/walkers and the controller outstanding-writeback count
  are zero.

The L2 transaction count is not multiplied by a presumed full-line size:
modified-sector byte masks make one transaction partial in this replay. The
controller byte sum exactly equals the DRAM 64-byte command sum.

The 323.968 MB decimal B0 writeback total is about 6% below the accepted
346.03 MB logical-write, 344.72 MB Native NS-family and 346.92 MB R101R1-B0
anchors. This is the same phenomenon and order of magnitude, with the remaining
difference bounded by simulator line/sector behavior and modeled cache traffic;
no cache, DRAM, translation or platform parameter was tuned to obtain it.

Therefore the simulator is qualified for this bounded L2/writeback experiment.
Exact receipts are in `BASELINE_L2_ACCOUNTING.tsv` and the node164 formal B0
directory.

## O1 semantic-direction gate

Formal O1 passes all identity, coverage, correctness and full-drain gates.
At software-declared region death it drops 2,505,858 resident dirty lines /
320,749,824 bytes. Actual L2/DRAM writeback falls from 323,967,936 bytes in B0
to 25,582,784 bytes, a 298,385,152-byte (92.1033%) directional reduction.
Reserved skips are zero.

This passes Gate A: the admitted simulator/input exposes resident dead-dirty
writeback-elimination opportunity aligned in direction with the Native D1
phenomenon. O1 remains an `ORACLE_ZERO_COST_SCAN`; its 0.9145% cycle response
is not an attainable hardware-performance claim and its drop bytes cannot be
added directly to saved writeback because the scan changes later residency and
traffic. Exact receipts are in `O1_ORACLE_RESULTS.tsv` and node164 formal O1.
The fixed finite M1 is now the only mechanism under performance evaluation.

## M1 disposition

The finite M1 passes every formal gate and preserves full terminal liveness.
It reduces writeback by 92.0887% and modeled cycles by 0.5027% versus B0.
Thus the simulator scope remains qualified and the mechanism has a real
traffic response, but the response does not meet the preregistered 5%
performance gate. C0/H0 are not triggered.
