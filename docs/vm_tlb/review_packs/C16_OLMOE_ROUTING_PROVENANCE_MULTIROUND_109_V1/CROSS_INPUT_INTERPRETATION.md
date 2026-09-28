# Cross-input interpretation

Producer-side bounded decision: `PERIOD11_REPRODUCED_ACROSS_INPUT_FAMILIES`.

Prospective P_TEXT Layer1 lag11 exceeds shuffle p95 and the same predeclared Layer1 criterion holds for at least one alternative input family.

| Prompt | Strongest full-prompt token lag(s) | Layer1 dominant routing lag | Layer1 lag11 above shuffle p95 | Layers with lag11 above p95 |
|---|---|---:|---|---:|
| P_TEXT | [11] | 22 | True | 16 |
| P_CODE | [32] | 16 | False | 0 |
| P_STRUCTURED | [14] | 14 | False | 0 |
| P_PROSE | [9] | 1 | True | 3 |

All comparisons are descriptive for one model across four fixed prompt families. Above-p95 refers to the preregistered marginal-preserving temporal shuffle, not a p-value. Expert IDs are never mixed across layers. No cache, timing, full-model speedup, or population-language claim is made.
