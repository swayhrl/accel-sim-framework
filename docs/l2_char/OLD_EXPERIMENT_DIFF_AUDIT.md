# Old Decoupled-L2 fork audit

This is an audit note, not a porting plan.  The old core branch changes ten
files relative to `03c1fe44` and adds Decoupled-L2 implementation files.  None
of those files is merged into `hrl/l2-char-baseline-v1`.

| Area | Old-branch change | Corrected-baseline disposition |
|---|---|---|
| `decoupled-l2-cache.*` | AAD/token/decoupled timing backend. | Explicitly excluded. |
| `gpu-sim.*` | Backend selector plus deadlock-progress/diagnostic edits. | Selector excluded; deadlock correction audited separately. |
| `l2cache.*` | Backend dispatch, queue gating, diagnostics. | Only conventional request-aware fixes may be independently reimplemented. |
| `gpu-cache.*` | Dirty-victim fallback, windowed-rate fix, diagnostics. | Dirty-victim and windowed-rate corrections are eligible as focused patches. |
| `shader.cc` | Related experimental behavior. | Excluded unless independently required by a conventional-L2 regression. |

The old diff is therefore a source of small, reviewable correctness references
only.  It is not a source branch for this baseline.
