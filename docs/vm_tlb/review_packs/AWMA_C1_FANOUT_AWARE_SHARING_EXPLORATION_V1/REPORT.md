# AWMA C1 fanout-aware sharing exploration V1

Stage: `AWMA_C1_FANOUT_AWARE_SHARING_EXPLORATION_V1`

Accepted parent:
`AWMA_C1_T2_OWNER_WAIT_RETRY_ATTRIBUTION_V1 @
82b82282d0a7b048d39c976304d2cabc03c341fa`.

Frozen parent conclusion:
`SUPPORTS_OWNER_WAIT_HEAD_BLOCKING_AS_MAJOR_T2_REGRESSION_CAUSE`.

## Fixed discovery mechanism

The only configuration in this phase is `MIN_COHORT_SIZE=4`:

- legal same-page cohort size below 4: use the frozen baseline V1 translation
  path for every access and create no C1 owner/member dependency;
- legal cohort size at least 4: use accepted one-slot C1 semantics unchanged.

Grouping legality, owner choice, READY ownership, delivery width, downstream
memory behavior, RTX4080/V1 platform, traces and 10/80 overlay are frozen.
Default source behavior remains accepted C1 with threshold 2; threshold 4 is
explicitly opt-in. Source validation accepts only 2 or 4, preventing a hidden
2/3/4/5/8 sweep.

## Threshold provenance

The threshold is selected from discovery evidence:

- accepted T2 C1 contains 132,544 cohorts, all size 2, and regresses 1.026%;
- accepted T0 C1 contains 364,256 cohorts, all size at least 4
  (227,680 size 4; 768 size 5–8; 135,808 size 9–16), and reduces cycles 7.63%.

Therefore 4 is a diagnostic separator for these already-consulted targets,
not an independently validated or paper-derived parameter.

## Bounded execution and decision rule

After A1 correctness smoke, only T0/T1/T2 at 10/80 are run. OFF and accepted
C1 values are reused; neither is rerun. Required outputs include the complete
cohort histogram, gated/shared cohort counts, lookup/L1/L2 service, owner
wait/head blocking, admissions/re-admissions, cycles and all terminal gates.

The fixed candidate is labeled
`FANOUT_AWARE_SHARING_PROMISING_DISCOVERY` only if:

- every point passes correctness and quiescence;
- T0 preserves at least 75% of accepted C1's absolute cycle saving over OFF;
- T1 remains faster than OFF;
- T2 improves over accepted C1 and lies within 0.25% of OFF.

Otherwise the result is not supported and the phase stops. No alternate
threshold is run in either case.

## Results

A1 and all three discovery points are terminal with full logical UID coverage,
zero untranslated/unobserved, zero duplicate application, and empty
lookup/READY/MSHR/PWQ/walker/diagnostic state. A1 exactly reproduces accepted
C1 at 863,057 cycles, with 12,800 size-4 cohorts shared and none gated.

| Target | OFF cycles | Accepted C1 | Fanout-4 | Fanout-4 vs OFF | Finding |
|---|---:|---:|---:|---:|---|
| T0 | 527,896 | 487,624 | 487,624 | -7.6288% | 100% of C1 saving retained |
| T1 | 665,802 | 653,485 | 656,682 | -1.3698% | remains beneficial |
| T2 | 93,079 | 94,034 | 93,079 | 0.0000% | exact OFF behavior restored |

The gate activates exactly where intended:

| Target | Size-2 | Size-3 | Size-4 | Size 5–8 | Size 9–16 | Gated cohorts | Shared cohorts |
|---|---:|---:|---:|---:|---:|---:|---:|
| T0 | 0 | 0 | 227,680 | 768 | 135,808 | 0 | 364,256 |
| T1 | 21,888 | 0 | 21,888 | 55,296 | 430,784 | 21,888 | 507,968 |
| T2 | 132,544 | 0 | 0 | 0 | 0 | 132,544 | 0 |

T0 is bit-for-bit equal to accepted C1 in cycles, admissions, lookup requests,
L1/L2 probes, owner count and shared deliveries. T2 is bit-for-bit equal to OFF
in those same observables and has zero owner wait/head block. This is the
intended intervention: size-2 accesses never enter C1 rather than entering and
later falling back.

T1 remains 1.37% faster than OFF while gating its 21,888 size-2 cohorts. It is
0.49% slower than accepted C1 and retains 74.04% of accepted C1's absolute
cycle saving. T1 admissions rise by only 607 versus accepted C1 while all
correctness gates remain closed.

Decision: `FANOUT_AWARE_SHARING_PROMISING_DISCOVERY`.

This result is frozen at threshold 4. No threshold 2/3/5/8 comparison, further
parameter tuning, additional target, or automatic baseline promotion is run.
The threshold was derived from T0/T2 discovery evidence, so confirmation must
wait for a representative test set or a new trace selected independently of
this evidence.

Implementation changes are limited to a `2|4`-only opt-in cohort-size gate and
observational gated/shared cohort counters. Default accepted C1 behavior is
unchanged. The mechanism adds no cache, MSHR, walker, translation port, future
trace knowledge, or free service; it simply declines to create the C1
dependency for cohorts below the fixed threshold.
