# Validation

Release build and M0a parser unit tests passed. `git diff --check` passed for frozen Core and Framework simulator candidates. All six ON rows and three OFF controls have normal terminal exit and `COMPLETE_VALID` status. The analyzer re-parsed all six ON rows and passed strict deterministic OFF/ON comparisons of cycles, instructions, B0/L1/DRAM CSV artifacts, terminal invariants, and config-delta evidence.
