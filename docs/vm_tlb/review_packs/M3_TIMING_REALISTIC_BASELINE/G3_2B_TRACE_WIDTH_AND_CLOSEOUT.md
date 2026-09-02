# G3-2B — generic trace-width extension and G3-2 closeout

Status: `PASS — STOP FOR CHATGPT REVIEW BEFORE G3-3/PWC`

## Scope and provenance

| Item | Value |
| --- | --- |
| Core accepted predecessor | `a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9` |
| Core G3-2B/G3-2 closeout | `965bd8e188175731c31cabfef6c3bdeb7c59e1fd` |
| Framework handoff read | `f8a272b9b6d59f25b0a2ba8a35ee0b207ec58b64` |
| Model status | `MODELING_DECISION`: generic trace/backend width, not a commercial-SM86 or target-paper VA claim |
| Generic runtime width | 56 bits |
| Retained paper-facing configuration | 49 bits, directed-tested only |

The historical `stash@{0}` was neither restored, popped, nor dropped.  The
G3-2 path was reconstituted as a reviewable commit on the accepted G3-1 source
anchor.  No PWC/G3-3, segmentation, sub-entry, migration, UVM, MCM, ASID
expansion, page-size-policy change, SimVA rewrite, or SimPA rewrite is part of
this closeout.

## Frozen address contract

The raw/coalesced trace transaction remains `SimVA`.  Generic resident data
mapping remains identity-like, so `SimPA == SimVA` numerically.  The generic
backend now accepts a configured width up to 56 bits; a key outside that width
is rejected by `supports_key()` and the real PTE address path asserts that
predicate rather than masking, truncating, canonicalizing, or modulo-mapping
the address.

For the default 56-bit configuration:

```text
application SimPA range: [0, 2^56)
PTE physical range:     [2^56, 2^56 + 2^46)
PTE requirement:        4 levels × 2 page classes × 2^(56-16) × 8B = 2^46 B
```

The PTE endpoint is overflow-checked, the application limit covers all valid
56-bit identity-like SimPA values, and the ranges are disjoint.  The flat,
per-level/full-VPN PTE identity is a generic plumbing model only; it is not a
PWC-locality or paper-exact hierarchy claim.

## Width and namespace validation

[G3_2B_VALIDATION.tsv](G3_2B_VALIDATION.tsv) contains expected-versus-actual
machine-checkable results.  Highlights:

- 49-bit G3-1 cross-page-size collision proof remains PASS.
- 56-bit backend accepts former offender `0xfffdc0000000c0`, preserves it as
  both identity-like SimVA/SimPA, and accepts `2^56-1`.
- A 57-bit key is explicitly rejected before a PTE address is created; the
  actual PTE path retains an assertion on that rejection.
- All 8 `(64KB/2MB × level0..3)` min/max namespaces are pairwise disjoint in
  both the retained 49-bit proof and new 56-bit proof.

## TRACE_ENCODING_OBSERVATION (non-blocking)

The complete default-configuration BFS replay reached all 49,048 global
transactions and recorded exactly 12 coalesced VM-hook transactions at or
above `2^49`.  Every one is listed in
[TRACE_ENCODING_OBSERVATION.tsv](TRACE_ENCODING_OBSERVATION.tsv).  The table
records the coalesced `SimVA` derived from the raw trace path; G3-2A preserves
the direct raw lane evidence for the first case
`0x00fffdc0000000cd -> 0xfffdc0000000c0`.

Observed facts only:

- all 12 have bits `[63:56]=0x00`, `[55:49]=0x7f`, and bit 48 set;
- none matches ordinary 49-bit sign/canonical extension;
- five distinct lower-49-bit values occur; no two distinct observed coalesced
  raw/global SimVA values collapse to one lower-49-bit value;
- all remain raw/coalesced generic SimVA in this baseline.

This is labeled `TRACE_ENCODING_OBSERVATION`, not an adapter design and not
authorization to rewrite generic addresses.  A later paper-specific trace
adapter may evaluate it separately.

## Real PTE L2/DRAM integration

PTE reads use distinct `PTE_ACC_R` traffic, are constructed physical and
translation-bypassing, bypass shader L1D, inject through a real cluster
terminal, consume request/response interconnect and L2/lower-memory resources,
and terminate at the walker.  The response association retains the PTE request
identity by `mem_fetch` UID because L2 can align its working address.

The standalone two-walker directed test proves four levels/walk, out-of-order
response identity, no early completion, exact 8/8 request/response accounting,
and zero misassociation.  Integrated evidence is in
[G3_2B_RUNTIME_SUMMARY.tsv](G3_2B_RUNTIME_SUMMARY.tsv):

- isolated one-kernel LUD cold replay: 4/4 PTE requests/responses, all DRAM,
  zero misassociation, final MSHR/PWQ/walker occupancy all zero;
- complete default BFS: 28/28 PTE requests/responses, 20 DRAM and 8 L2-only,
  L2 `PTE_ACC_R` hit/miss `8/20`, zero misassociation, and final quiescence;
- small-TLB diagnostic pressure replay crossed the former offender and
  produced 4,936 PTE accesses alongside application L2 traffic, 4,920 L2-only
  and 16 DRAM completions, with zero misassociation.  It was intentionally
  bounded at 180 seconds during kernel 9, so it is resource-path evidence—not
  the complete BFS acceptance run.

No PTE request re-enters normal translation; PTE response, MSHR, PWQ, walker,
waiter, and store/atomic replay invariants remain covered by the directed M2
and G3-2 test suite.

## Regression and transparency summary

All M1/M2/G3 directed tests listed in the validation matrix pass after a full
Core+Framework release build.  LUD VM_DISABLED and VM_IDEAL_IDENTITY have the
identical 10-kernel cycle sequence and final total (`139766` cycles).  The real
PTE LUD run finishes normally (`141588` cycles) with its timing difference
explained by explicit PTE traffic; it has no non-quiescent translation state.
Complete 56-bit BFS also exits normally and includes the former offender.

## Remaining boundary

G3-2 is closed.  Do **not** start G3-3/PWC: current PTE identities do not yet
model hierarchy-prefix/PTE-sharing locality.  The next task requires a separate
ChatGPT architecture specification and review.
