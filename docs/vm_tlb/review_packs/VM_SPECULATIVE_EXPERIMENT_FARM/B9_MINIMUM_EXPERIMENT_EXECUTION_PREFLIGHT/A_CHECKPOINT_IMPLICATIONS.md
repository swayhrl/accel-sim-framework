# A checkpoint implications for B9

**Evidence label: `SPECULATIVE_DIAGNOSTIC`**

The only A input was committed checkpoint
`73d25ebbdd96833ee1ddb8ea42b9017cefbceb75`, read with `git show`. It is
external supporting evidence, not a B baseline and not numerically poolable
with B.

At that checkpoint seven A arms were terminal and `prefill-paper` was running.
For terminal decode evidence, disabled and ideal both recorded 10,938,651
cycles / 377.4279 IPC. Generic recorded 32,812,575 cycles / 125.8222 IPC;
paper recorded 34,438,514 cycles / 119.8818 IPC. Paper nevertheless had fewer
reported L1/L2 TLB misses than generic (57,926/22,408 versus 69,483/23,805)
and near-equal PTE requests. Thus lower miss counts do not imply a better
cycle/IPC outcome.

B9 consequently requires E01--E06 to retain cycles/IPC together with TLB,
MSHR/PWQ, walker, PWC, PTE DRAM/wait, and object observables. It does not
infer an A performance prediction for B, does not cancel B-local disabled or
ideal control validation, and excludes running `prefill-paper` from all B9
comparisons. A checkpoint provenance also records that some completed decode
arms predated later Framework documentation/exporter commits while simulator
binary/Core/trace-list hashes were unchanged; that distinction is not used to
claim B compatibility.
