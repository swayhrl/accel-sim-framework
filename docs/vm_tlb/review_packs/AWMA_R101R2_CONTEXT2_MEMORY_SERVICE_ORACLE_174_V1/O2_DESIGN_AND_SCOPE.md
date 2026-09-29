# O2 design and scope

Working mode: `O2_TRANSIENT_1C_SERVICE_ORACLE`.

Required label: `ORACLE_ONE_CYCLE_UNBOUNDED_SERVICE`.

## Placement

The hook is after a coalesced `mem_access_t` has completed normal VM
translation and frontend observation, but before any L1D access or interconnect
push. Thus a qualified transaction does not access or update normal L1/L2/DRAM
state.

Classification uses original SimVA and the admitted region/generation
descriptor, not translated SimPA.

## Activation

Derived kernels 1-3 are context and must use the normal hierarchy. Completion
of kernel 3 applies its accepted POST deaths. Kernel 4 applies its accepted PRE
producer activation and begins the measured ROI. Only kernels 4-6 can qualify.

The selector is opt-in/default OFF:

`AWMA_R101R2_TRANSIENT_SERVICE_MODE=none|oracle_1c`.

Existing transient-L2 replacement mode remains `none`; O2 cannot combine with
O1/M1.

## Service model

A legal ordinary global READ or WRITE that is fully contained in one current
live A/B/X region is allocated as the original coalesced transaction and placed
in an unbounded per-LDST-unit queue.

- admission at cycle t;
- response becomes READY at exactly t+1;
- load then uses the existing global-memory writeback client, operand collector,
  pending-write accounting and scoreboard release;
- store uses the existing reply/store-ack path with the baseline sector-token
  count;
- response/writeback arbitration after service readiness remains modeled.

There is no oracle service bandwidth or queue limit. No additional response or
writeback port is created.

## Fail-closed semantics

Measured-ROI region-targeting ATOMIC, unsupported opcode/type, multi-region,
partial-region, zero-size or overflow access increments a semantic-violation
counter and follows the normal hierarchy. Any nonzero formal violation yields
`R101R2_O2_SEMANTICS_NOT_QUALIFIED`.

Dead/stale-generation or pre-activation accesses follow the normal hierarchy.
Non-transient accesses are unchanged.

## Accounting and quiescence

Required identities:

`qualified reads + qualified writes = scheduled = one-cycle ready = retired`

and:

- duplicate completion = 0;
- latency violation = 0;
- outstanding oracle transactions = 0;
- context-iteration qualified transactions = 0;
- unsupported measured transactions = 0.

Terminal drain includes both existing memory activity and outstanding oracle
entries.

## Claim boundary

One-cycle service is measured from service admission to response READY.
Dependency/writeback completion may occur later through preserved arbitration.
The result bounds transient memory-service cost only; it retains global
instructions, coalescing, dependencies, kernel launches, CTA scheduling and
compute.
