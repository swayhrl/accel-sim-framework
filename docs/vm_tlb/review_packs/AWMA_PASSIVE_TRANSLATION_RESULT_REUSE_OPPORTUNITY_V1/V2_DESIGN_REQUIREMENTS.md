# V2 design requirements

Opportunity characterization supports a future V2 design, but V2 is **not**
implemented here.

Minimum reasonable memo capacity: **1 entry** per live memory
instruction/accessq. One entry captures 100% of observed 4-entry hits on every
target; larger capacities add storage without additional observed opportunity.

Any future V2 must provide:

- zero proactive physical lookup and zero owner speculation;
- zero waiting and zero future information;
- an exact no-opportunity path preserving OFF lookup/admission behavior;
- finite instruction-local lifetime with deterministic bounded replacement;
- ASID/VPN/page-size/generation/access-compatible identity and verified PPN;
- exactly-once translation application and preserved logical UID;
- bounded storage and lookup ports with explicit contention;
- no cross-instruction/warp/CTA/kernel persistence;
- no second-TLB semantics: this is a short-lived result handoff memo only;
- OFF-by-default operation and complete controller/memo quiescence gates.
