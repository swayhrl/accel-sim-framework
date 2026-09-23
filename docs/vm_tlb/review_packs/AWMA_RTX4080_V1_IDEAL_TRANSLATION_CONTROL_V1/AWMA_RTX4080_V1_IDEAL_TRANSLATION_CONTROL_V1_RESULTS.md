# RTX4080/V1 ideal-translation control: result and stop record

Status: `STOP_SEMANTIC_CONTRACT_NOT_CLOSED`.

All three authorized ideal points completed with exit code zero. They preserve
the expected instruction totals and unique translated UID totals, have zero
untranslated/unobserved accesses and zero ready-application duplicate attempts,
and report zero modeled lookup, MSHR, PWQ, walker, PTW/PWC/PTE service state.

| target | C_10_80 | C_0_80 | C_ideal | S_L1 | S_ALL |
| --- | ---: | ---: | ---: | ---: | ---: |
| T0 | 527896 | 496170 | 446880 | 0.060098959 | 0.153469623 |
| T1 | 665802 | 664805 | 715636 | 0.001497442 | -0.074848078 |
| T2 | 93079 | 83439 | 83713 | 0.103567937 | 0.100624201 |

`S_L1=(C_10_80-C_0_80)/C_10_80` and
`S_ALL=(C_10_80-C_ideal)/C_10_80`.

T1 is slower under the purported ideal control than under accepted V1 10/80.
T2 is slower than accepted 0/80. This is incompatible with the required
diagnostic contract that removes only translation service while preserving the
V1 downstream order and non-translation memory behavior. The current patch
suppresses V1 prelaunch translation in order not to use future information; the
result demonstrates that this changes scheduling behavior. These three runs are
therefore diagnostic evidence, not accepted ideal-control performance results.

Do not interpret `S_ALL-S_L1` as a PTW time fraction. No further workloads,
mechanisms, or parameter sweeps were launched.
