# Remaining C10-B blockers

The following are deliberately still open despite the B2--B7 static source
closure:

| ID | Required before a replay/result claim | Why static closure is insufficient |
| --- | --- | --- |
| B1 | Core compile/link and standard-mode regression | source inspection cannot prove integration or preserve accepted behavior |
| B2--B7 runtime | focused registration/lifecycle/access/fair-arm/generation tests | new directed test sources have not executed |
| B8/F5 | implement C9 physical PWC state, 3×40 entries, 4-way PLRU, pointer payload, port/queue/timing; otherwise retain hard block | historical 128-entry logical PWC is not fair F5 |
| B9 | inspect post-delta translation and cross-layer telemetry output | source field names do not prove emitted continuity or conservation |
| C5 | only after C10-B validation and normal resource approval | C10-A2 did not authorize C5 or any simulator workload |

Additional runtime checks must include reject-to-conventional fallback with no
local hit, all-replica install/revoke, store/atomic conservative routing,
F0/F1/F2/F3/F4/F6/F7/F8/F9 parser paths, H0/F5 failure, exact/sub-entry
shootdown races, and telemetry conservation/backpressure. No KV segmentation,
12K, M5 or new AI-aware mechanism is authorized by this closure.
