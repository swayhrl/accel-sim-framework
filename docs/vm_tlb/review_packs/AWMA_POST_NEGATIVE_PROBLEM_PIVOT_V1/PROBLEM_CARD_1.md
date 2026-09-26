# Problem hypothesis 1 — retained predecessor state

Status before diagnostic: `CANDIDATE_DIAGNOSTIC_SUPPORTED`.

## Exact hypothesis

The isolated Q05 replay may materially misstate target cycles because a real
predecessor interval establishes persistent translation and/or L2-data state.
If a specific retained state is causal, matched prefix rows with the same page
overlap and walk count should have cycle direction consistent with the remaining
L2-miss difference.

This is first a simulation/sampling methodology hypothesis. It is not an
architecture mechanism claim and does not authorize fusion.

## Existing matched evidence

- Isolated Q05: 885,681 cycles.
- P1-P34: same target, instructions and CTA, exact boundary snapshot, fresh
  process per row, state carried only through the ordered suffix.
- L1D is flushed at kernel completion; L2 and translation state persist.
- P2/P4 share 49.60% 4K overlap and 128 walks.
- P8/P16 share 99.20% 4K overlap and 16 walks.

## Missing capability and signal

The accepted simulator does not tag scoreboard/scheduler delay with the
producer state that caused it. Available realizable signals are target-entry
page overlap, TLB/PTW counters, and L2 misses. These can falsify a simple
retained-cache/translation explanation but cannot identify an unobserved cause.

## Minimum diagnostic

Use only accepted TSVs. Compute per-row cycle delta, page overlap, walk count,
and L2 misses; then inspect the two equal-overlap/equal-walk pairs. The
hypothesis is rejected as `REJECT_NO_LOCALIZED_CAUSE` if either pair has more
than 1% cycle separation while lower L2 misses fail to predict the faster row.

P1 and P34 are retained as endpoint checks, but this is retrospective existing
evidence, not an independent scientific holdout.

## Cost and promotion boundary

The diagnostic is offline and zero-hardware-cost. Any later architecture would
need explicit finite retained-state metadata and backpressure. No prototype is
authorized unless this diagnostic localizes a repeatable state mediator and a
closest-work-distinct limitation.
