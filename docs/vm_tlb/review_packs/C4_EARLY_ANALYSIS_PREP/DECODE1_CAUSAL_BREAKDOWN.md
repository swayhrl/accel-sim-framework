# Decode1 paper-versus-generic causal breakdown

## OBSERVED_TERMINAL_FACT

Evidence: `decode1-generic` and `decode1-paper`, both terminal and provenance
bound in `INPUT_PROVENANCE.tsv`.

- Generic: 32,812,575 cycles, 125.8222 IPC.
- Paper: 34,438,514 cycles, 119.8818 IPC: **1.049552×** generic cycles.
- Paper lowers L1-TLB misses (57,926 vs 69,483), L2-TLB misses (22,408 vs
  23,805), and translation-MSHR full events (130,257 vs 2,301,691).
- PTE requests/responses are nearly unchanged (15,786/15,786 vs
  15,798/15,798); PWC hits are identical (46,978), while PWC misses are 95 vs
  104.
- The fixed configured lookup latencies are unchanged: L1=10 and L2=80 cycles;
  PWQ-full is zero for both profiles.

## SUPPORTED_MECHANISM_SIGNAL

Paper nevertheless has higher PTE memory-wait cycles (6,560,190 vs 4,835,001;
1.3568×) and requester-MSHR-wait cycles (9,552,488 vs 9,065,536; 1.0537×).
Its total requester latency is nearly the same (774,521,844 vs 773,733,827).
These terminal counters rule out a simple "more TLB misses / more MSHR full"
explanation and identify PTE-memory and delivery/wait timing as candidates for
the remaining causal chain.

The lightweight queue summary provides a further bounded signal. `*_total` is
the sum of sampled queue occupancy, not a transaction count. Dividing by its
`samples`, paper versus generic records mean occupancy of 2.3230 vs 0.00558
for L2→DRAM and 1.9740 vs 0.13694 for ICNT→L2. Both profiles reach the same
queue high-water marks (64, 64, 1, 63 for the four recorded directions).
This supports investigation of sustained backpressure rather than a claim of
different queue capacity.

## UNRESOLVED_CAUSAL_GAP

The existing evidence does not attribute the additional 1,625,939 cycles to a
specific request class, bank, row, cache victim, or source instruction. The
early pass deliberately does not full-scan the large L1D/L2/DRAM tables while
`prefill-paper` is consuming the formal host. Full C4 must correlate
translation source × L1D/L2 outcome with queue occupancy and native memory
statistics. No change is made to C3 telemetry or the running simulator to
force an answer.
