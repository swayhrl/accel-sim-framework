# A1/A2 nonsharing regression attribution

Status: `SUPPORTS_PROACTIVE_OWNER_PATH_AS_NONSHARING_REGRESSION_MEDIATOR`

## Matched-control result

A1 and A2 are the same exact GEMV identity, grid/block, decode step, frozen
candidate policy, and both have `READY share = 0`.  Their principal external
difference is context/history.

| target | OFF cycles | candidate cycles | response | extra admissions | extra LDST resource stalls |
|---|---:|---:|---:|---:|---:|
| A1 | 114123 | 112023 | -1.840% | 76752 | 76752 |
| A2 | 117698 | 125427 | +6.567% | 1100032 | 1100032 |

For both contexts the candidate's extra coverage admissions equal its extra
source-enum LDST resource stalls exactly.  The magnitude differs by 14.33x:
A1 adds only 76752, while A2 adds 1100032.  This is the central
source-supported mediator link.

## Controller and reuse boundary

- READY-shared members: `0` for A1 and A2.
- fallback members: `116032` for both.
- duplicate physical lookup requests: `116032` for both.
- member owner wait and head blocking: `0` for both.
- owner attempts/retries are nearly equal across contexts; the divergent result
  is downstream retry/readmission amplification, not reusable-result delivery.

Therefore no performance response is attributed to result reuse.

## Differential downstream response

A1 candidate reduces L1 reservation failures, L2 reservation failures,
scoreboard dependency, structural blockage, and requester latency; its progress
milestones move earlier, producing the 1.840% improvement.

A2 candidate adds 1100032 repeated admissions/resource stalls, increases L1
reservation failures by 3431592,
raises average ICNT-to-memory latency from 8040 to
9075, and increases scheduler dependency and
eligible-structural blockage.  Instruction/CTA p90 and the kernel tail move
later, producing the 6.567% regression.

## Temporal relationship

The A2 candidate Top-K 512-cycle windows form a real simulator-cycle sequence:

1. translation not-ready plus eligible-structural concentration near cycles
   5632--9215;
2. READY/admission plus ICNT/DRAM queue concentration near 10240--12799;
3. L1 reservation-pressure concentration near 15872--16895 (with later repeats);
4. scoreboard-dependency concentration near 28672--31231;
5. later cumulative instruction/CTA progress and kernel completion.

This temporal order supports propagation through the listed mediators; no single
aggregate counter is called a causal decomposition.  Exact low-throughput
progress Top-K windows and time-windowed repeated-admission attempts are not
exposed by Observatory V1 and remain `NOT_AVAILABLE`; aggregate repeated
admission counts and bounded Level-1 progress milestones are used instead.

## Level-3 decision

Level 3 was not run.  Level 1 and Level 2 already distinguish the matched A1/A2
chain and close the required observed locations/mediators.  Level 3 would add
READY-to-successful-admission latency and DRAM boundaries, but it cannot add a
time-windowed view of the earlier repeated-admission attempt counter or identify
the physical context/history trigger.  Running it would therefore add cost
without resolving the remaining question.

## Decision

`SUPPORTS_PROACTIVE_OWNER_PATH_AS_NONSHARING_REGRESSION_MEDIATOR`

The proactive owner path creates no READY reuse in either context.  In A2, its
retry/readmission amplification propagates into downstream memory pressure and
scheduler/progress delay; A1 is the matched control showing the same policy with
small amplification and net benefit.

V2 design requirements only (not implemented here):

- no extra proactive physical lookup when no reusable result exists;
- no added retry/readmission amplification;
- no waiting and no future information;
- the no-opportunity path should approach frozen OFF semantics.

The physical context/history condition that turns similar owner attempts into a
14.33x larger downstream amplification remains unresolved.  This stage changes
no mechanism and runs no V2.
