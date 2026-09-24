# AWMA C1 delivery-bandwidth diagnostic V1

Stage: `AWMA_C1_DELIVERY_BANDWIDTH_DIAGNOSTIC_V1`

Accepted parent:
`hrl/awma-174-literature-guided-mechanism-exploration-v1 @
4cf2ee8294fbf761f735ae7089313a048ba0066b`.

## Question and frozen boundary

This phase asks only whether T2's accepted one-slot C1 regression is mainly
caused by serializing shared-result delivery/application to one member per
cycle. T0 is the high-sharing positive control; A1 is correctness smoke.
T0/T2 remain discovery data, not holdouts.

The following Phase 1 semantics are frozen:

- same-page legality key and grouping;
- front-most resident owner selection;
- suppression of member physical translation lookup service;
- READY ownership and one logical UID/downstream effect per member;
- downstream admission/order semantics;
- frozen RTX4080 platform, V1 frontend, trace identities and 10/80 VM overlay.

The only functional intervention is a second finite delivery/application slot
shared by all cohorts of one resident memory instruction in a cycle. The
implementation accepts only `1` or `2`; it cannot select 4/8 or unlimited
broadcast. Default remains one slot, preserving Phase 1.

The second slot represents an additional bounded result-delivery mux/write
opportunity. It adds no translation cache, MSHR, walker, lookup port, future
trace knowledge or free translation service. This pass does not estimate its
layout/timing cost beyond declaring that duplicated delivery resource.

## Predeclared evidence and decision rule

Accepted one-slot evidence is reused without rerun:

| Target | OFF cycles | C1 one-slot cycles | One-slot response |
|---|---:|---:|---:|
| T0 | 527,896 | 487,624 | -7.6288% cycles |
| T2 | 93,079 | 94,034 | +1.0260% cycles |

New execution is limited to:

- A1 C1 two-slot correctness smoke at 10/80;
- T0 C1 two-slot at 10/80;
- T2 C1 two-slot at 10/80.

Support for the serialization explanation requires all correctness gates,
physical lookup requests and L1 probes within 1% of the corresponding one-slot
result, and either:

- T2 becoming non-regressing relative to OFF; or
- the T2 excess cycles above OFF shrinking by at least 50% from the one-slot
  excess of 955 cycles.

Otherwise this phase rejects the claim that one-slot delivery serialization is
the main cause and stops without 4-slot/8-slot exploration.

Observational-only counters record configured slots, shared owners/deliveries,
post-service backlog cycles, backlog member-cycles, cycles where all slots were
used while backlog remained, and maximum post-service backlog. They do not
alter arbitration or completion.

## Correctness gates

Before AI replay, the final source must pass the C1 legality/unit test and the
accepted timing, pending-retry and runtime controller regressions. A1 must then
close instruction/CTA identity, full unique UID coverage, zero
untranslated/unobserved, zero duplicate application, and empty
lookup/READY/MSHR/PWQ/walker/candidate state.

## Results

The configuration and decision rule above were committed to the working pack
before any Phase 2 replay. Execution waited until the concurrent Lane B matrix
finished and the resource gate observed three CPU-idle samples at or above
20%.

All A1/T0/T2 two-slot runs are terminal and pass instruction/CTA identity,
full unique-UID translation coverage, zero untranslated/unobserved, zero
duplicate application, and empty lookup/READY/MSHR/PWQ/walker/candidate state.

| Target | OFF cycles | 1-slot cycles | 2-slot cycles | 2 vs 1 | 2 vs OFF |
|---|---:|---:|---:|---:|---:|
| A1 | 875,138 | 863,057 | 850,291 | -1.4792% | -2.8392% |
| T0 | 527,896 | 487,624 | 505,859 | +3.7396% | -4.1745% |
| T2 | 93,079 | 94,034 | 94,034 | 0.0000% | +1.0260% |

Physical translation suppression is effectively held constant. T0 changes
from 393,499 to 393,525 lookup requests (+0.0066%) and from 369,387 to 369,413
L1 probes (+0.0070%). T2 is exact at 282,838 lookup requests, 279,190 L1
probes, 1,218 L2 probes, 132,544 owners and 132,544 shared deliveries in both
arms. All values are within the predeclared 1% matching criterion.

The new observational counters show:

| Target | Backlog cycles | Backlog member-cycles | Full-slot cycles with backlog | Max backlog |
|---|---:|---:|---:|---:|
| A1 | 13,312 | 13,312 | 13,312 | 1 |
| T0 | 1,179,104 | 6,901,312 | 1,179,104 | 13 |
| T2 | 0 | 0 | 0 | 0 |

T2 has no post-service delivery backlog with two slots and shows exactly no
cycle improvement. Its excess above OFF remains 955 cycles, so the shrink
fraction is 0%, below the predeclared 50% threshold. This directly rejects the
claim that one-slot delivery serialization is the main cause of the accepted
T2 regression.

T0 confirms that the mechanism remains active at high sharing, but widening
delivery is not monotonically beneficial: two slots are 3.74% slower than one
slot while still 4.17% faster than OFF. The high T0 backlog says finite
delivery remains saturated, but this single causal intervention does not
justify parameter tuning or a wider sweep.

Decision:
`DOES_NOT_SUPPORT_ONE_SLOT_DELIVERY_SERIALIZATION_AS_MAJOR_T2_CAUSE`.

## Implementation and validation summary

Changed Core paths are limited to `vm_translation.{h,cc}`, `shader.cc`, and
the directed C1 test, published as `CANDIDATE_CORE.patch`. Default one-slot
behavior is unchanged. Phase 2 adds the `1|2`-only runtime selector, a second
finite delivery opportunity, and observational backlog counters.

The final source passes the Phase 1 C1 legality/unit test plus the accepted TLB
timing, pending-retry, and runtime validation regressions in OFF and refill
protection modes. The unified Phase 2 build and patch dry-run also pass.

Open issue: the T2 regression remains unattributed by this diagnostic. This
phase does not start 4-slot/8-slot runs, further timing/order experiments,
baseline promotion, or independent validation. T0/T2 remain discovery data.
