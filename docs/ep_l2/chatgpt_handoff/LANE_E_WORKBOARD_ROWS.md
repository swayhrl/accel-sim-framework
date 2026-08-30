# Lane E workboard rows to install

Lane E Codex must fetch the latest `docs/ep_l2/coordination/PARALLEL_WORKBOARD.md` and append these rows if their IDs do not already exist. Preserve all other lane fields and ChatGPT review conclusions.

```markdown
| MSHR256-AUDIT | Lane E | Audit/generalize Line-MSHR256 support | Keep descriptor semantics fixed; ensure allocator + line occupancy telemetry/p95/window state represent >128 exactly; prove MSHR128 equivalence if source changes | directed + vectorAdd + convolution | frozen Lane-B candidate | TODO | — | `hrl/ep-l2-mshr-causality-v0` | PENDING | Observation/parameterization-only changes only; exact MSHR128 equivalence required. |
| MSHR256-2X2 | Lane E | Descriptor × Line-MSHR causal 2x2 on convolution | Existing D256/M128 + D512/M128; new D256/M256 + D512/M256; B0-Banked only | convolutionSeparable | MSHR256-AUDIT; D512 child promotion waits for `D512_PREFLIGHT_PASS` | TODO | — | `/workspace/results/ep_l2_line_mshr_causality/` | PENDING | Determine whether the 931,416 D512 Line-MSHR-full blocks are performance-causal or downstream-limited. |
| MSHR256-CONTROL | Lane E | Near-threshold negative control | D512 spmv MSHR128->256 only; MSHR128 has max125 but exact full-block=0 | spmv | MSHR256-AUDIT; promotion waits for `D512_PREFLIGHT_PASS` | TODO | — | `/workspace/results/ep_l2_line_mshr_causality/` | PENDING | Material response would weaken a simple exact-full-block causal interpretation and requires investigation. |
```

Lane E completion status is `LINE_MSHR_CAUSALITY_PROBE_COMPLETE`; do not mark any row `DONE` merely because a speculative D512 child locally finishes.
