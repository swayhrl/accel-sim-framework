# T1 retrospective validation

Status: `PASS`

The unified observatory replays the exact accepted T1 payload/index for
10/80, 0/80, and ideal.  It preserves cycles, instructions, CTAs, UID
coverage, mapping, and correctness gates.

| mode | cycles | READY cycle peak | READY->admission mean | admission 32-cycle peak | L1 reservation fail | LDST resource stall | avg ICNT->memory latency | legacy W0_Idle | new no-active | instruction p90 | CTA p90 | last data DRAM completion |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10/80 | 665802 | 69 | 3.940080 | 846 | 3850 | 3716553 | 841.0 | 7845947 | 151193 | 597751 | 653280 | 628461 |
| 0/80 | 664805 | 69 | 6.480338 | 904 | 367023 | 3790685 | 1214.0 | 8892778 | 128299 | 587803 | 638362 | 613365 |
| ideal | 715636 | 1216 | 25.925711 | 2432 | 1825599 | 4161666 | 2100.0 | 12391742 | 61312 | 653515 | 702233 | 684412 |

## Gate results

- semantic_cycles: `TRUE`
- work_identity: `TRUE`
- ready_burst: `TRUE`
- admission_burst: `TRUE`
- l1_pressure: `TRUE`
- icnt_latency: `TRUE`
- accepted_scheduler_idle: `TRUE`
- instruction_tail: `TRUE`
- cta_tail: `TRUE`
- dram_tail: `TRUE`

## High-level consistency

The unified interface recovers the accepted high-level location:
`downstream temporal burst/backpressure`.  Ideal produces an earlier and
larger READY release burst, a larger short-window admission burst, more
L1/resource pressure, longer ICNT latency, a higher accepted legacy
scheduler-idle aggregate, and later
instruction/CTA/data-DRAM tails while logical
work remains identical.

Differences from the T1-specific pack are expected and explained:
the old observer retained full per-cycle vectors.  Accepted `W0_Idle`
combines idle/control-hazard states and rises in ideal; the new exclusive
`no_active_work` predicate is narrower and falls because ideal retains
active-but-blocked warps.  They are reported side by side, never equated.
The unified observer otherwise uses fixed online windows,
a source-predicate exclusive scheduler taxonomy, and bounded Level-2
reservoir quantiles.  Level-3 progress and READY latency remain exact.

This retrospective validates location and mediators.  It does not create a
new causal experiment or upgrade the prior manual attribution into an
automatic root-cause claim.
