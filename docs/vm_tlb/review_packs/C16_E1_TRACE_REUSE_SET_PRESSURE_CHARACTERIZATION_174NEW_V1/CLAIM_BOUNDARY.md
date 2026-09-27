# Claim Boundary

## Permitted evidence labels

The formal analysis may report only the following dynamic quantities:

- `TRACE_ADDRESS_REFERENCE`: a decoded active-lane address reference from the
  qualified trace grammar.
- `128B_LINE_REFERENCE_PROXY`: one or more 128-byte lines touched by such an
  address and its opcode-derived width.
- `SET_CONFLICT_REFERENCE_PRESSURE_PROXY`: accepted-mapper placement of those
  line-reference proxies onto the RTX4080-model L2 subpartition/set geometry.

Static qweight placement may be called `STATIC_ACCEPTED_CORE_MAPPER_OUTPUT`.
The accepted mapper must be source-direct from Core
`a2322069b9701597db7019080b5b54d29518e3a2` and the config with SHA-256
`de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`.

For a layer-L reuse gap, “non-target” is layer-relative: it excludes only
layer L's qweight. Traffic to the other 27 qweight regions remains intervening
pressure. An all-28-targets-excluded quantity must say so explicitly.

## Prohibited claims

This goal must not describe any proxy as:

- actual L2 traffic, requests, transactions, hits, misses, fills, or writebacks;
- observed LRU state, eviction, residency, protection, or admission denial;
- simulator timing, speedup, slowdown, cycles saved, or performance ranking;
- proof of undocumented RTX4080 hardware address mapping or microarchitecture;
- proof that B8, B16, B24, or BFULL will perform best;
- a result from coalescing, L1 filtering, or cache simulation unless a separately
  named and validated proxy is later added without replacing the base evidence.

No full GPGPU-Sim timing replay, GPU/NVBit/NCU run, new trace collection,
oracle-mechanism modification, or automatic B8/B24/BFULL launch is authorized.

## Boundary between this lane and future timing

Future B16 timing evidence may be interpreted only after independently binding
its exact build, config, trace, mechanism counters, and run receipt. The four
pre-registered interpretation branches are hypotheses/checklists, not current
conclusions. Proxy evidence may explain a timing result but cannot substitute
for one.
