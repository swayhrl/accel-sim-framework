# Service suppression to performance response

Every measured target reduces L1 translation launches, but runtime response is
not linear or universal.

- Measurable positive responses occur on T0, T1, A2 and both Pair-C contexts,
  alongside substantial redundant-L1 suppression. Downstream-pressure
  attribution is limited to targets with accepted Observatory columns; Pair-C
  has no such columns and receives no pressure explanation.
- SPLITKV has only a very small positive response; COMBINE and independent
  REDUCE are exactly cycle-neutral despite substantial suppression. Their
  translation work is largely hidden behind other execution/memory work at
  the modeled scale.
- T2 and A1 regress even with zero follower head-block. Accepted Observatory
  evidence shows schedule/cache-pressure and progress-tail perturbations that
  can offset the service benefit; it does not identify a root cause.
- Accepted `S_L1/S_ALL` exists only for T0/T1/T2 and is reported verbatim.
  No sensitivity is invented for other targets. The mixed signs—especially
  T2 and T1's negative `S_ALL` ideal response—rule out a simple linear causal
  model between suppressed requests and cycles.

The paper-level observation is therefore bounded: pre-L1 coalescing reliably
removes modeled translation service on the measured targets; speedup appears
when that service is exposed on the critical schedule, remains hidden when
other work dominates, and can be offset by schedule perturbation.
