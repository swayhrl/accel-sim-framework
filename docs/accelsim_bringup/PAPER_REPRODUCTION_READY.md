# Paper Reproduction Readiness

The current pipeline is ready for bounded baseline and future variant plumbing:

1. Discover and lock prior workload evidence.
2. Map locked rows to available Accel-Sim traces.
3. Run a baseline experiment matrix.
4. Parse stats with fixed modes.
5. Compare only fields approved by the equivalence matrix.
6. Package local reports and logs into a review pack.

Not ready:

- Mascar and MeDiC mechanisms are not implemented in Accel-Sim.
- Paper-level config equivalence is not proven.
- NVBit trace generation requires a visible GPU and is not validated in CPU-only environments.

To add a paper-specific variant, create a variant config, run A13 with `ACCELSIM_A13_VARIANTS=baseline,<variant>`, and compare stats only through the A11 equivalence matrix.
