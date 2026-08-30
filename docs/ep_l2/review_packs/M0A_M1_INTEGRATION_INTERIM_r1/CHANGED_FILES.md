# Changed files

Core integration is the exact M0a telemetry delta applied to M1: `gpu-cache.h`, `gpu-sim.cc`, `l2cache.h`, and `l2cache.cc`.

Framework integration adds M0a OFF/ON overlays, parser/analyzer/runner tooling, mode-feature provenance, and the corresponding tests. No Framework simulator runtime-source file changes from the M1 Framework base. No functional payload, RO, TVD, adaptive, or headroom implementation was added.
