# Paper-opportunity gate

- Gate A: **met**. T2 has 10.36% translation-specific 10/80-to-0/80 headroom under the frozen V1 baseline.
- Gate B: **supporting evidence only**. At modeled 64KiB, T2 touches 134 pages; the busiest 10% of pages carry 54.91% of trace references, and same-page/stride behavior is highly regular.
- Scope: the 4KiB companion is behavioral support, not a hardware page-size claim. Missing temporal/per-PC stall telemetry prevents a burst- or PC-specific mechanism claim.

Result: there is enough structured evidence to justify a separate mechanism-design discussion, but this Goal does not select or implement one.
