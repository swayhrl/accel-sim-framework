# SG3 bounded buffering × memory-service plan

This is the complete pre-result C1/C2 registry following the pushed C0 decision `b7cedaef`.  It contains four BICG cells only: two exact reuses, two service-only `Q0M1` attempts, and two queue-plus-service `Q1M1` attempts.  The fixed default DTC GPU-wide lower outstanding cap remains 8192 in every cell.

The selected service delta is exactly `-gpgpu_dram_buswidth 32`; the hash-locked runner must reject any missing echo of both its intended L2 queue and `busW=32`.  C2 is not a queued workload expansion: each GESUMMV cell remains conditional on the stated predeclared 5% gate and coherent service telemetry.  No additional resource point is authorized.
