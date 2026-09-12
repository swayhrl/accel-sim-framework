# C16-4.4 Memory-Only Observer Audit

Decision: **NO_GO** for this C16 round. Full tracer fallback is retained unchanged.

## Gate result

| Required GO condition | Current result |
|---|---|
| Full-tracer vs memory-only event output bit/exact on a tiny real fixture | NOT_RUN — no real G NVBit capture and no implemented memory-only NVBit producer |
| Same target filter and terminal semantics | NOT_PROVEN |
| No program/timing perturbation beyond qualified full tracer scope | NOT_PROVEN |
| Output materially smaller | NOT_MEASURED |

The local parser includes `compare_memory_only_events()`, which compares canonical opcode/access kind, 32-bit active mask, width, lane IDs, lane addresses, order, and terminal state. Its directed fixture proves that a future candidate is rejected for one-bit/field differences. It is a schema test, not a hardware qualification.

## Why NO_GO is the safe decision

The frozen full tracer's `inst_trace_t` and host receiver serialize instruction metadata, masks, width, and compressed address payload together. A memory-only producer would change device injection, channel payload, host emission, filtering, terminal handling, and tool-version compatibility. Without a tiny real-GPU paired capture, any claim that its addresses/masks/widths or perturbation are equivalent would be unsupported.

## Re-entry conditions

Only G may provide a versioned, target-filtered tiny paired fixture with fixed full-tracer and memory-only manifests/SHA256 values, terminal receipts, exact canonical comparison, output-size measurement, and perturbation receipt. If all GO conditions then pass, the mode must be default-off and full tracer stays available as fallback. Until then C16 uses the existing full tracer path.
