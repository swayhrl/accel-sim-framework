# Open issues and boundaries

- Runtime-range matching is conservative observed-range provenance, not exact
  per-instruction tensor-lifetime attribution.
- `UNKNOWN` access coverage is not relabelled as activation or workspace.
- NCCL raw evidence is retained. The permanent FULL_RANK0 versus
  COMPUTE_ONLY_TP_PARTITION decision is `DEFER_TO_M4B_INTEGRATION`.
- Parser startup is compatibility evidence, not a performance simulation.
- This stage neither merges Track A nor changes Core. Future integration must
  use the accepted final Track-A M1–M3 baseline rather than the frozen parser
  compatibility Core.
