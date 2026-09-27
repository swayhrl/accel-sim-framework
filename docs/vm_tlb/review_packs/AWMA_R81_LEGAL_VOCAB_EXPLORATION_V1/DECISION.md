# R81 decision

State: `R81_SOFTWARE_OPPORTUNITY_NO_ARCH_CLAIM`.

The strongest qualified known-capability baseline was A0, a BF16 vendor dense head with XGrammar masking and singleton support shortcut. A1 used a FlashSampling-style greedy fused tile adaptation; A2 used Kestrel-style indexed union gather; A3 was a fixed direct-index ragged prototype. All four arms selected exactly the same tokens and stop positions for every C0, C1 and H0 request; 12/12 authored outputs satisfied their JSON schemas.

| Cohort | Steps retained | Union > half vocabulary | A0 full generation median (ms) | A3 median (ms) | A3 vs A0 |
| --- | ---: | ---: | ---: | ---: | ---: |
| C0 shared | 78 | 63 | 611.0 | 633.1 | +3.62% |
| C1 heterogeneous | 72 | 63 | 555.7 | 561.2 | +0.98% |
| H0 holdout | 57 | 47 | 445.4 | 442.1 | -0.73% |

The median legal union was 147,068 of 151,936 rows (96.8%) in all three cohorts. On the pre-registered sparse stratum (union <1% vocabulary), A3's summed head-region time was 53.4%, 45.3% and 44.8% below A0 for C0, C1 and H0. On broad states (union >50%), A3 was 27.5%, 7.1% and 6.7% slower. All timesteps were retained. The local sparse response is real within the authored fixture; it did not yield a reliable complete-generation improvement. A2 indexed union regressed substantially because union often approached the full head and its gather/metadata remained on the path.

This identifies a bounded software opportunity to choose among already known dense and direct-index organizations from the current legal set. It does not establish an architectural need or deployment-wide gain. The authored B4 fixture is not a production distribution; task-answer accuracy and logprob-serving semantics were not evaluated. A1 is a greedy adaptation, not a reproduction or upper bound for the published FlashSampling kernel.

C0's first formal complete-generation bundle had unexplained A0/A1 latency outliers and is retained in raw as `C0_ATTEMPT0_HIGH_VARIANCE`; one exact same-configuration paired repeat is the primary C0 timing. C1 and H0 were not rerun. Neither Kestrel's indexed head nor FlashSampling's fused-selection ability is claimed as new. No NCU profile was admitted because there was no remaining registered mechanism question that would change this software-first conclusion.
