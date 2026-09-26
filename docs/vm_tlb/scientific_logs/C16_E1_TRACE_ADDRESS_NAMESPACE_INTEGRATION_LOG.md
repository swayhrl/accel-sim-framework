# C16 E1 Trace Address Namespace Integration Log

The accepted 109 D1-D3 bounded trace at `df0d0484875ec62f2b2f0c4aaf03f9d904328528` was consumed without payload modification. Durable manifest `db3bdbb...ab389` closes 9062 artifacts and 114,926,148,782 bytes; node164 admission and positive ACK are PASS.

Real addresses selected by the producer for layers 0, 14 and 27 were replayed in single-kernel, early-terminating `ADDRESS_INTEGRATION_CANARY_ONLY` runs. Each address remained numerically identical through trace parsing, instruction operands, coalesced access creation, mem_fetch construction, L2 entry and the oracle lookup. Oracle activation was true only for up_proj qweight target regions. The initial L0 run exposed and repaired a sector-fill protected-metadata accounting defect; the hard occupancy recount caught it, and a directed sector regression now locks the fix.

All 28 exact regions are 128-byte aligned, disjoint, 33,947,648 bytes each, and observed at least once in qualified D2 trace artifacts. The sidecar is a deterministic identity generation bound to the complete D1-D3 manifest. This qualifies namespace integration only; no C16 performance comparison or budget sweep was executed or authorized.
