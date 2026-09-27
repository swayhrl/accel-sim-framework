# Final decision

V1R2 backend gate: `R54_V1R2_GREEDY_BACKEND_QUALIFIED`.

R54 scientific state: `R54_HOST_RUNTIME_COST_NOT_ARCH_LOCALIZED_V1`.

The strong P2-D512 arm has a stable measured 6.58% production overhead on 4096 tokens and 6.31% on 2048-token holdout. The D2048 P2 arm is 1.57% above P0. The measured D512 D2D copy duration (1.27 ms discovery; 0.67 ms holdout) is much smaller than the end-to-end gap (10.33 ms; 4.92 ms), while per-layer host scheduling and source-reuse events dominate. Restore costs about 0.11–0.12 ms incrementally relative to ~151 ms of avoided prefix recompute. No qualified GPU-local >=5% residual is isolated.

No NCU profile or architecture review manifest was produced. No node174 or Accel-Sim was run.
