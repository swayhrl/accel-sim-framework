# Validation summary

Status: **M0A_INTERIM_REVIEW_READY** — not final PASS.

The candidate is frozen and pushed. Completed rows have normal simulator exit,
valid B0 parsing/invariants, M0a schema parsing, source/config contracts, and
lossless raw logs. The three required OFF/ON controls have equal terminal
cycles/instructions with the approved one-bit configuration delta.

The live `scan` M0a-ON job is intentionally excluded from completed metrics
until normal exit, parser completion, and final analysis. It has not been
disturbed. Final M0a readiness additionally requires the final strict analyzer
comparison of parsed B0/L1/DRAM terminal fields and all accepted final-pack
artifacts.
