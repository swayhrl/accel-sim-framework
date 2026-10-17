# SIM_RTL_TIMING_GAP — first changed-path controller prototype

Authority f1980a84, §§0/1/4/5. Specification is the **finite P1** path of
Core9bd30ed913c5058b5d952fbeb2e67cb5e4644b3f (joint producer binaryfb67448d),
not any Ideal branch. Original paper H0 Core7b8e6ac7 has fixed B16/U slots and
P1; the joint source adds S64 partition helpers/local-quota/P2/Ideal wiring,
without selecting those diagnostics here. S64 uses Lane1's integrated range
1024/80/64. B16 remains1024/128/16. Unified has1168 dynamic-role slots, same
bank class for resident landings. All mode parameters are elaboration constants.

This is **controller + real access datapath** cost, not whole L2 or a cycle
match to the simulator. Functionally included: stable Tag→physical handle,
physical role/Tag-owner/pin/sector metadata, generation checks, bounded aligned
landing selection, WAD address CAM, pending replacement and stable victim,
real byte-enable1024-bit data movement/static copy, in-place U ownership,
shared128B read/copy latch, real4-bank P1 grants, WB FIFO/data snapshot,
lower_accept free and later generation-qualified set_done. No historical stats
or symbolic-version integers stand in for payload bytes.

Externally reused, **excluded cost unknown, not zero**: native Tag/address
comparison/LRU/dirty byte mask, Line-MSHR issue/merge and ordinary response
policy, existing request/NoC/lower queues, interconnect, DRAM and GPU. The
`native_ready` input is a held resource approval; only `native_commit` changes
native Tag ownership. Request Tag identity is captured once, not re-probed.
`req_addr`/`req_victim_addr` are native line addresses (128B aligned). Traditional
Tag lookup must validate hit identity; `fill_protect_be` is the native dirty
byte mask, not a reconstructed symbolic version. That traditional state needs
its own implementation/cost if the design is later integrated into a full L2.

## Explicit pipeline / throughput differences

- This first hardware prototype has a **serialized frontend transaction** and
  one response snapshot. With no stalls: read admissionE0, bank readE1,
  synchronous SRAM return capturedE2, response handshakeE3, next admissionE4
  (II4). A write admitsE0, writes/commitsE1, acknowledgesE2, next admissionE3
  (II3). These are chosen implementation boundaries, NOT measured extra
  latency required by an allocator, and NOT a proposal to add one cycle to all
  simulated hits. The simulator can service its eligible native frontend once
  per physical GPU cycle and models granted array access without this macro
  latency. Full frontend/return-queue throughput matching is outstanding.
- Static dirty: E0 reserveWAD/staging; E1 source read; E2 latch;
  E3 staging write; E4 approved incoming write/Tag commit; E5 acknowledgement.
  Source ft_access can reserve/read on its first call and can do staging write
  plus incoming write on distinct banks in a later same physical cycle. This
  controller serializes those phases even across different banks. Copy is
  never collapsed, but timing is not identical.
- WB read uses one real bank service, synchronous return, then the common
  copy/read latch→WB output snapshot. The extra output register phase and
  shared latch conflicts are explicit. WB packet data remains stable through
  lower backpressure; the payload is freed only on output valid&&ready. WAD
  remains until set_done, independently of the now reusable slot.
- Three finite clients (fill/frontend/WB) arbitrate round-robin per bank.
  Simulator's vector/arrival-sequence oldest-ready policy is not reproduced.
  Hardware has bounded fairness among these clients; simulator timing/order
  claims cannot be assigned to it. Independent banks can actually grant
  simultaneously; no bank can serve two operations in a P1 cycle.
- Dynamic landing/WAD search is a combinational priority encoder/CAM over
  full capacity, explicitly mapped and timed. There is no free unlimited
  hardware search and no hidden extra allocation pipeline stage. A failing
  critical path is reported, not fixed by relaxing U's clock.
- Native approval occurs **before** destructive incoming byte writes, so
  abort can free reservations without restoring old payload bytes. The C++
  symbolic rollback can restore its saved sidecar after native failure. Our
  interface requires held prechecks/commit approval; no claim of equivalence
  for an arbitrary late native failure after destructive writes is made.

SRAM wrapper is4×292×1024, synchronous1RW with128 byte enables. Its1-cycle
functional read model is a declared assumption; there is no matching macro
Liberty in this flow. Controller STA constrains exposed RAM input/output
ports with the same0.10ns interface budgets as other ports. That is not a
measured RAM delay, and controller WNS cannot imply full-hit latency/Fmax.
No SPEF/placement: this is netlist STA only. At1132MHz, target0.883392226ns;
exploration2ns is separately reported on the SAME mapped netlist/constraints.

Before marrying these costs to simulated performance: review/close or model
these frontend, SRAM-return, copy, WB, arbitration and native-approval gaps.
Lane1 owns any minimal default-off SIM timing adaptation/release. No running
simulator was modified. Until then this is first-version feasibility/cost of
the disclosed RTL boundary, not proof that the current SIM throughput has
this area/frequency. P2/U_CAP16 are not synthesized here; a final P2 claim
requires matching real extra-port/bank implementation and cost.

## First functional qualification correction

The initial byte-functional suite omitted same-edge external-pin acquisition
against a destructive frontend admission. A new actual compiled regression
reproduced old-red: op0 req_ready=1 and pin_ready=1, so a victim could acquire
a pin after its unpinned precheck on that same IDLE edge. The corrected RTL
excludes only a pin to the selected old payload when req_fire occurs for
install/write/invalidate. An already blocked request still permits existing
pin decrements; unrelated payload pins remain concurrent. The integration
suite covers dirty/clean replacement, write, invalidate, unrelated pin and
exact rollback/reference drain. This is an RTL admission correction, not a
change to the finite simulator mechanism or its accepted evidence. Initial
pre-correction mappings were stopped and cannot serve as final costs.
