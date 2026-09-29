# R101R2 CONTEXT2 memory-service oracle - 174 V1 report

Stage: `AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_V1`

Final state: `R101R2_O2_MEMORY_SERVICE_HEADROOM_PRESENT`

## Purpose

The accepted R101 transient-L2 experiment removed about 92% of writeback,
71% of DRAM reads and 19% of L2 misses but improved cycles by only 0.50%.
This round asks a stronger upper-bound question: how much measured-ROI headroom
remains if legal live A/B/X transaction service takes one modeled cycle while
global instructions and execution organization remain?

O2 is `ORACLE_ONE_CYCLE_UNBOUNDED_SERVICE`, not a hardware mechanism.

## Input

`R101_L512_NS_CONTEXT2_EXECORG_V1` is a deterministic zero-copy view of the
accepted FULL5 input:

- source zero-based indices 3-5: context iteration;
- source zero-based indices 6-8: measured iteration;
- six immutable members 3580-3585;
- all 44 L512 tiles;
- accepted A/B/X0/X1 addresses, generations and PRE/POST lifetimes;
- no normalization member and no trace-byte modification.

Initial state is the accepted state after normalization ordinal 3: X0
generation1 live; A/B/X1 dead. Full trace-v5 decoding found zero ATOMIC/RED or
unsupported measured transient records. LDGSTS is explicitly supported as a
global READ using the simulator's existing pending-LDGSTS/DEPBAR completion
path.

## Implementation and correctness

The O2 hook is after VM translation and frontend/coalesced observation but
before L1D/interconnect admission. Qualified transactions never access normal
L1/L2/DRAM.

Admission at cycle t becomes response-ready at t+1. Loads retain the existing
global writeback client, operand collector, scoreboard and LDGSTS depbar path.
Stores retain normal sector ACK accounting. Service capacity and queue size are
unbounded by design.

Validation completed:

- 18 policy/direct tests;
- 14 source integration-hook checks;
- three accepted VM regressions and accepted transient policy tests;
- default-absent and explicit-none exact T2 equivalence;
- positive 6xT2 integration with real reads/writes and closed exactly-once
  equations;
- exact Core patch reproduction;
- isolated cold build and frozen binary/library;
- six-member authoritative decode and zero-copy samefile checks.

## Matched context

B0 and O2 are exact through context kernel 3:

- end cycle 2,976,829;
- 1,217,463,296 instructions;
- 7,040 CTAs;
- identical L1D/L2/DRAM cumulative counters;
- lifecycle hash `c11eff45e7bbc37f`;
- zero O2 qualification/scheduling/retirement.

## B0 qualification

B0 completes 6/6 coverage with normal hierarchy service and all
translation/controller/writeback/full-drain gates passing.

Primary ROI:

`2,985,319 cycles = end(kernel6) 5,962,148 - end(kernel3) 2,976,829`.

The B0 ROI L2-access count exactly matches the corresponding accepted FULL5
iteration1 slice; L2 misses and DRAM reads are within 1,808 commands, and
writeback remains structurally close. No platform tuning was used.

## O2 result

O2 completes 6/6 coverage with identical instructions/CTAs and all
semantic/exactly-once/terminal gates passing.

Measured-ROI accounting:

- qualified reads: 27,594,656;
- qualified LDG: 1,126,400;
- qualified LDGSTS: 26,468,256;
- qualified writes: 2,342,912;
- qualified bytes: 958,002,176;
- scheduled = ready = retired: 29,937,568;
- violations, duplicates and outstanding: zero.

Primary ROI:

`1,130,670 cycles = end(kernel6) 4,107,499 - end(kernel3) 2,976,829`.

Improvement is 62.1256555832%, well above the preregistered 5% gate. The result
is outside the 3%-7% repeat band, so no repeat was run.

## Decision and boundary

This L2 CONTEXT2 screen establishes material transient memory-service headroom
under an intentionally optimistic oracle while keeping global instructions,
coalescing, dependencies, compute, kernel decomposition and CTA scheduling.

It does not establish a realizable buffer, service bandwidth, hardware cost,
energy, RTX4080 speedup, FULL5 response, holdout generalization or novelty. A
bounded local producer-consumer handoff requires a separately authorized later
round.

FULL5, O3, scratchpad/DSMEM mechanisms, sweeps, holdout and new 109 capture were
not run.

## Engineering recovery

Both formal simulations completed successfully. Their first summarization
failed before emitting summaries because the tool inferred arm identity from
the atomic temporary directory, plus one non-preregistered O2 L1D-growth gate.
Hash-bound recovery modified only postprocessing, preserved command/log/rc/
stderr bytes exactly, wrote recovery receipts and atomically promoted all-pass
B0/O2 summaries. No simulator rerun occurred.

## Evidence

Review pack:

`docs/vm_tlb/review_packs/AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_174_V1/`

Durable root:

`/root/share/mnt164/huangrulin/awma_r101r2_context2_memory_service_174_v1/`
