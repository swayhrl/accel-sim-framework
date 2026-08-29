# EP-L2 Target Baseline v0 — Resolved Decisions and Gate Register

## Status

The owner decisions below resolve the source-audit questions against Core
`32f9b8d52490044f487c14811121ed0368e48a48`.  They freeze Target Baseline v0
only; they do not authorize Unified borrowing, RO no-MSHR, TVD hits or graphics
borrowing.  C1–C3 are authorized, with a mandatory semantic stop after C3
directed tests.

The audit does freeze these **non-negotiable constraints** for the next
implementation review:

* Do not encode target MSHRs as `A:128:32`: that creates 4,096 fixed target
  positions instead of 256 globally shared descriptors.
* Do not implement the long-lived descriptor pool by setting
  `m_miss_queue_size=256`: current `m_miss_queue` is a short lower-issue FIFO.
* Do not use existing L2CHARV1 fields with changed EP-L2 meanings.
* B0-Legacy and B0-Banked remain static-partition baselines.  No RO no-MSHR,
  TVD hit, Unified borrowing or graphics bypass borrowing belongs in either.

## Frozen owner decisions

| ID | Status | Frozen decision |
|---|---|---|
| OPEN-01 | RESOLVED | Keep sector-L2: 128-B line with four 32-B sectors. Resident Tag/Payload/WAD and line MSHR are 128-B-block indexed; sector valid/dirty and pending/issued masks are retained. |
| OPEN-02 | RESOLVED | A descriptor stays allocated until its requester response has successfully entered L2→ICNT. It is not freed at Fill or lower issue, and does not wait for SM architectural completion. |
| OPEN-03 | RESOLVED | Keep DRAM→L2 FIFO at 64 per slice; independently keep DRAM internal ReturnQ at 192 per channel. Instrument both. |
| OPEN-04 | RESOLVED | 850 MHz is primary. 1 GHz is a headroom sensitivity only. |
| OPEN-05 | RESOLVED | L1 keeps verified QV100 resource semantics: 512 MSHRs × 8 merge cap, MissQ 16, 4 banks, 20 cycles, write-through/on-miss/lazy-fetch and 32-B port. Only capacity changes to 64 KiB. Add L1 blocker statistics later in C7. |
| OPEN-06 | RESOLVED | Disable adaptive L1 associativity; fix 4 sets × 128 ways × 128 B and assert association is invariant across kernels. |
| OPEN-07 | RESOLVED | Allocate WAD before destructive dirty-victim mutation; release at the writeback `mem_fetch`'s memory-partition `set_done()` completion. |
| OPEN-08 | RESOLVED | One 256-entry long-lived descriptor pool exists. Current `m_miss_queue` remains a distinct 128-entry lower-issue staging queue and cannot be named MissQ in EP-L2 reporting. |
| OPEN-09 | RESOLVED | Begin B0 with explicit `payload_id + generation` lower-response identity for resident/bypass traffic, reserving the detached-response interface. |
| OPEN-10 | RESOLVED | B0-Legacy uses separate Resident-1024 and Bypass-128 1R1W RAMs. Resident hit/WB-read use read; fill/write-hit use write; bypass fill/read use its write/read; atomic is ordered read then write. |
| OPEN-11 | RESOLVED | B0-Banked uses 4×288 banks, one arbitrary 128-B operation/bank/cycle, oldest-ready sequence arbitration, retry for losers and no mechanism-specific priority. Atomic remains read then write. |
| OPEN-12 | RESOLVED | Fix ICNT→L2=64, L2→ICNT=64, DRAM→L2=64/slice, L2→DRAM=128/slice and ReturnQ=192/channel. Preserve corrected-baseline NoC/credit/lower-read-credit behavior. |
| OPEN-13 | RESOLVED | Add independent `EPL2B0V1`: fixed per-L2-cycle occupancy samples, exact event blockers, 5K windows, application plus kernel-launch-UID snapshots; kernel boundary snapshots counters only. |

## Source-audit outcome by implementation layer

| Work item | Can proceed now? | Reason |
|---|---|---|
| C1 — create target configuration overlays | Complete | `tests/ep_l2/b0_legacy_850.config` freezes the geometry, queues and 850-MHz primary point; `b0_legacy_1ghz.config` is sensitivity-only. |
| C2 — fixed 64-KiB L1 | Complete | Core disables adaptive reassociation in the overlay and asserts `4 × 128 × 128B` at initialization and invariant associativity at every kernel CTA calculation. |
| C3 — shared persistent descriptor model | Complete; stop point reached | Core implements 128 line entries plus a global 256 descriptor pool, 32/address cap, sector masks, and L2→ICNT commit-time release. All mandatory directed checks pass. |
| C4 — WAD | Deferred until C3 review | The release event is frozen, but C4 is out of this execution slice. |
| C5 — B0-Legacy / B0-Banked payload RAM model | Deferred until C3 review | RAM semantics and bank arbitration are frozen, but C5/C6 are out of this execution slice. |
| C6 — directed tests and `EPL2B0V1` instrumentation | Design only | Test/instrumentation schema follows the resolved lifetime and arbitration contracts. |
| Target characterization / 850-vs-1G decision | No | Must not run until B0 directed invariants pass and the unresolved resource scopes are manifested. |

## Review-ready implementation plan after C3 review

Only C1–C3 are authorized now.  After their directed tests pass and semantic
review accepts their ownership/lifetime behavior, the remaining sequence is:

1. Add Framework-only B0 configuration overlays and a manifest validator.
   It must record both SHA/branch pairs and every resolved queue scope.
2. Add a Core `line_mshr[128]` plus a single `descriptor_pool[256]` whose
   allocator enforces global and per-address bounds.  Keep the existing
   lower-issue FIFO separate.  Directed tests: 129th distinct-line block,
   257th descriptor block, 33rd same-address block, and no free at lower
   issue.
3. Add an explicit B0 payload model behind static roles.  First Legacy
   1024+128 1R1W, then Banked 4×288; no dynamic borrowing.  Test grant limits,
   conflicts and no payload leak.
4. Add WAD with mandatory allocation before dirty-victim mutation.  Test WAD
   full without partial mutation and same-address lower-read hazard through the
   chosen completion event.
5. Add a distinct `EPL2B0V1` producer/parser and terminal invariants.  It
   reports line-MSHR, descriptor, payload-role, WAD, bank and L1 blockers
   without altering L2CHARV1 definitions.
6. Only after directed tests and source/manifest review pass, run B0-Legacy
   and B0-Banked target characterization.  The 1-GHz subset is a sensitivity,
   not a mechanism result or an automatic primary choice.

## Explicitly deferred

The following remain out of scope for this branch until a target-baseline
closeout and an explicit follow-up decision: RO pending replacement, RO
no-MSHR functional behavior, TVD serve-in-place/promotion, Unified dynamic
borrowing, graphics bypass borrowing, and any paper-performance conclusion.
