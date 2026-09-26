# Context-prefix diagnostic decision

Decision: **REJECT_NO_LOCALIZED_CAUSE**.

The retrospective diagnostic preserves the accepted seven-row matrix and does
not rerun simulation.

## Primary matched contrasts

- P2/P4 have identical 49.5987% 4K overlap and 128 walk starts. P2 is 2.835%
  faster and also has fewer L2 misses, so this pair is directionally consistent
  but does not distinguish the full cause.
- P8/P16 have identical 99.1973% 4K overlap and 16 walk starts. P8 is 3.290%
  faster even though P16 has 2,723 fewer L2 misses. This is the preregistered
  falsifier.

Across P1-P34, L2 misses have Pearson correlation 0.0821 and Spearman
correlation -0.1429 with cycles. Page overlap/walk count have moderate opposite
correlations, but the saturated matched pair shows that they are not a
sufficient localized mediator.

P1 is also slower than isolated Q05 despite fewer walks and fewer L2 misses.
P34 confirms that almost-complete page overlap alone does not select the best
cycle response.

The accepted context replay remains useful methodology evidence: isolated
kernel replay can differ materially from a real-prefix replay. It does not,
however, expose a specific realizable hardware limitation. Scoreboard,
scheduler, and unobserved cache state cannot be attributed to the producer with
the existing counters. Generic fusion is closest-work-covered and is not
inferred from these data.

No tiny prototype, matched mechanism control, or holdout run is authorized.
