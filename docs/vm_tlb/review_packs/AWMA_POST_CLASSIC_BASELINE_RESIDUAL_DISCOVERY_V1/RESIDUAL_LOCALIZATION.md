# Residual localization

The strong reference retains material modeled translation headroom. The
directly established causal response is localized to the L1 lookup path, which
is 95.4--99.8% hit-dominated across the seven targets, not to a remaining
coalescing opportunity.

The fixed 0/80 contrast exceeds the preregistered 1% gate on
T0, T2, A2. T1 moves in the opposite direction, showing that
lower lookup latency is not a monotonic scheduling improvement. The
intervention changes only modeled L1-TLB lookup latency; L2 remains 80 cycles,
grouping and finite ports are unchanged, and correctness closes.

Across the seven strong-reference targets, L1 hits dominate physical launches
(see `STRONG_BASELINE_RESIDUAL_MATRIX.tsv`). MSHR allocations/PTW starts are
small relative to L1 launches and PWQ-full is zero, although repeated MSHR-full
events remain visible on SPLITKV/A1/A2 and are reported without being relabeled
as physical work. No matched capacity intervention establishes those retries as
material headroom in this stage; LATPC already covers multi-VPN MSHR compression
and ISCA 2018 covers instruction-aware walk scheduling. H2's exact head-loses-
to-nonhead-prelaunch event is impossible under the verified reverse scan.

Level-1 Observatory replays are exact-neutral and retain large translation-not-
ready exposure alongside scheduler/cache/interconnect pressure. The reference
prelaunch path applies READY results outside the Observatory head-ready hook,
so its printed `translation_ready=0` is an instrumentation boundary—not an
absence of completed translations. These totals are localization context, not
additive cycle fractions. Level 2 and zero-all-
translation were not run: the matched L1-only intervention already identifies
the service level, and additional diagnostics would not distinguish a new
mechanism.

The reference applies a READY result in the same simulator call, so READY to
address-apply delay is zero by model/source contract. Per-access apply-to-cache-
admission latency is not paired by Level 1 and remains `NOT_PAIRED_IN_LEVEL1`;
it is not needed to locate the observed 0/80 response.
