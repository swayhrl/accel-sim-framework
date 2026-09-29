# Final decision

Decision:

`R101R2_O2_MEMORY_SERVICE_HEADROOM_PRESENT`

## Input and context gate

The deterministic zero-copy input uses original zero-based launch indices 3-8,
accepted sidecar ordinals 4-9 and immutable trace members 3580-3585. It
preserves all 44 L512 tiles and the admitted A/B/X0/X1 generation/lifetime
sequence.

B0 and O2 context kernels 1-3 match exactly:

- end cycle: 2,976,829;
- instructions: 1,217,463,296;
- CTAs: 7,040;
- L1D accesses/misses/reservation failures:
  3,469,312 / 3,347,858 / 38,535,562;
- L2 accesses/misses/reservation failures:
  29,964,261 / 3,582,086 / 21,787;
- DRAM read/write/writeback commands:
  1,419,398 / 0 / 392,701;
- pre-ROI lifecycle hash: `c11eff45e7bbc37f`.

O2 schedules no service transaction in the context iteration.

## B0_CONTEXT2 qualification

B0 completes the exact six-member view with 6/6 coverage, 2,434,926,592
instructions and 14,080 CTAs. Translation, duplicate-application, controller,
writeback and terminal-drain gates all pass. Normal memory service is present.

B0 measured ROI cycles are:

`5,962,148 - 2,976,829 = 2,985,319`.

The B0 ROI has 29,964,036 L2 accesses, 2,907,857 L2 misses, 745,169 DRAM
reads and 1,082,945 DRAM writeback commands. This is structurally close to the
accepted FULL5 iteration1 slice (29,964,036 L2 accesses, 2,906,049 L2 misses,
743,361 DRAM reads and 1,093,138 writeback commands). No platform parameter was
tuned.

## O2_CONTEXT2 result

O2 preserves all six kernel instructions/CTAs and activates only at derived
kernel 4. In the measured ROI it services:

- 27,594,656 qualified reads;
- 1,126,400 ordinary LDG reads;
- 26,468,256 LDGSTS reads through the existing pending-LDGSTS/DEPBAR path;
- 2,342,912 qualified writes;
- 883,028,992 read request bytes;
- 74,973,184 write request bytes.

The exactly-once identity closes:

`qualified = scheduled = one-cycle-ready = retired = 29,937,568`.

Atomic, unsupported, dead, partial, multi-region, invalid-range, duplicate,
latency, stale-token and outstanding counters are all zero. Non-oracle normal
hierarchy activity remains: measured ROI adds 26,473 L2 accesses and 3,209
DRAM reads.

O2 measured ROI cycles are:

`4,107,499 - 2,976,829 = 1,130,670`.

Improvement:

`(2,985,319 - 1,130,670) / 2,985,319 = 62.1256555832%`.

This exceeds the preregistered 5% gate.

## Repeat and prohibited scope

The result is outside the 3%-7% near-threshold band, so no repeat is allowed or
needed. FULL5, O3, holdout, scratchpad/DSMEM mechanisms, parameter sweeps and
new 109 capture were not run.

## Interpretation boundary

O2 is `ORACLE_ONE_CYCLE_UNBOUNDED_SERVICE`, not hardware. It has no service
capacity/bandwidth limit and charges one modeled cycle only from service
admission to response READY; existing response/writeback/dependency arbitration
remains. It does not establish implementability, cost, energy, RTX4080 speedup,
FULL5 performance or novelty.

The result does establish material transient memory-service headroom in this
matched CONTEXT2 simulator screen while retaining global instructions,
coalescing, dependencies, compute, kernel decomposition and CTA scheduling.
A later bounded local-handoff mechanism requires separate ChatGPT authorization.
No mechanism is promoted automatically.

## Postprocessing recovery

Both simulator processes completed rc=0, stderr=0 and 6/6 coverage. The
formal-at-run summarizer failed before writing summaries because it interpreted
the atomic in-flight directory name as the arm; it also contained an extra
O2-L1D-growth gate not required by the Goal. The raw command/log/rc/stderr bytes
were not modified. A hash-bound recovery summarizer fixed only those
postprocessing rules, produced all-pass summaries, and atomically promoted both
directories. `ORCHESTRATION_RECOVERY.json` records before/after hashes and
confirms no simulator rerun.
