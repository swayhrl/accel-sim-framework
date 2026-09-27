# C16_E1_M1F_REAL_TRACE_ACTIVATION_CANARY_V1

Qualification: `M1F_REAL_TRACE_ACTIVATION_QUALIFIED_V1`.

This pack establishes that the three frozen real C16 kernels traverse oracle
target recognition, the frozen stable selector, and the existing M1 hard
admission path. It does not authorize a full timing run.

| kernel | class | selected / target unique lines | selected / target simulator L2 accesses | successful protected fills | hard denials |
|---:|---:|---:|---:|---:|---:|
| 4490 | 1 | 4752 / 265216 | 35241 / 1969155 | 4752 | 0 |
| 5232 | 15 | 4744 / 265216 | 35176 / 1969721 | 4744 | 0 |
| 5921 | 28 | 4698 / 265216 | 34556 / 1951033 | 4698 | 0 |

The trace scanner counts active-lane address and 128-byte line-reference
proxies. Simulator admission counters count modeled L2 transactions. These
denominators are intentionally reported separately. Repeated accesses explain
any reference-weighted versus unique-line fraction difference.

N0 and N1 are exact frozen-versus-instrumented 50,000-cycle real-prefix
neutrality checks. N2 cycle values are activation evidence only and are not a
performance comparison. Lane 4 results were not read or used.
