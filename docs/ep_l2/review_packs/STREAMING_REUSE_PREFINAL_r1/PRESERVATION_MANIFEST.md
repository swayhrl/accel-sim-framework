# Preservation closeout (prefinal)

The following immutable locations were re-hashed after checkpoint generation with the same sorted, NUL-safe `sha256sum` stream specified at initial capture. Both match the initial manifest exactly.

| Immutable root | Files | Bytes | Initial / recheck content-root SHA-256 | Result |
| --- | ---: | ---: | --- | --- |
| `/workspace/worktrees/accel-sim-ep-l2-motivation/docs/ep_l2/review_packs/MOTIVATION_FIGURES_r1/` | 28 | 143,199 | `4c444e74b7908e4bff5b9ef80f9a7d0530e69a1f1dd1453b3bd147297b3109c7` | MATCH |
| `/workspace/results/ep_l2_motivation/` | 180 | 244,118,782 | `dcd6eb72148178e886eac5778de3670961feeb9ed4cea753ec1a28b3915e2100` | MATCH |

The historical branch `hrl/ep-l2-motivation-v0` was not rebased, force-pushed, changed, or deleted. The extension wrote only to its designated streaming-reuse worktrees and results root. Status: `STREAMING_REUSE_PRESERVATION_PREFINAL_PASS`.

