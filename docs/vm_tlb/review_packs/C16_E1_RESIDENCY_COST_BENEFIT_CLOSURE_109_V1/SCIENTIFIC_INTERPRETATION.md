# C16 E1 residency cost/benefit closure interpretation

Stage label: `RESIDENCY_OFFSET_LOCALIZED`.

All four budgets preserve material local up_proj benefit across all 28 layers, strongest at the full request. No budget reaches a positive whole-decode result beyond dispersion or the 2% system gate.

The non-overlapping top-level decomposition qualifies at every budget: median unexplained residual stays within roughly 0.006–0.025 ms, below the 0.10 ms closure limit. At full budget, direct up_proj saving is about 0.576 ms, but gate/down slow by about 0.177 ms and measured self-attention slows by about 0.534 ms; norm timing improves by about 0.074 ms and final stages are negligible. MLP top-level saving is close to the total FFN projection saving, so MLP internal work is not the main missing offset.

Representative NCU confirms up_proj duration improvement at 16 MiB and full budget. L0 self-attention NCU changes are small and do not reproduce the large native aggregate slowdown across 28 layers, so the localization is semantic aggregate evidence rather than a unique per-kernel mechanism claim.

The former negative residual is now largely assigned to directly measured categories, especially self-attention at full budget, with little unexplained remainder. This supports mechanism revision around measured interference/cost rather than immediate simulator implementation or an unexplained-cache claim. No simulator or trace work was run.
