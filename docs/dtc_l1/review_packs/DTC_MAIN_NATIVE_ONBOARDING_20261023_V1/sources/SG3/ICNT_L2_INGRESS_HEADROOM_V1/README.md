# ICNT->L2 ingress-headroom review pack

Status: `CLOSED_ALL_FOUR_ROWS_STRICT_PASS`.

This is the final, pre-registered four-row BICG check.  G changes only the
first partition-queue field from 64 to 256.  H makes that same change on top
of accepted E's detailed-DRAM 2x service probe.  All rows use default DTC
lower outstanding cap 8192 and the frozen Core/runtime/trace identity.

Final bounded decision: `ICNT_L2_INGRESS_PRESSURE_NOT_CAPACITY_LIMITED`.
Ingress-only G is +0.16% (IO) and -1.71% (OO) versus exact default; the H
increment over accepted E is -0.87% (IO) and +0.38% (OO).  Thus the large
source-defined ingress-stall counter is not evidence that this FIFO's 64-entry
capacity is the dominant performance limiter for BICG under this identity.

See `SOURCE_ANCHORS.md`, `R5_REGISTRY_RESULTS.tsv`, `VALIDATION_SUMMARY.md`,
and `OPEN_ISSUES.md`.  No other resource family was launched.
