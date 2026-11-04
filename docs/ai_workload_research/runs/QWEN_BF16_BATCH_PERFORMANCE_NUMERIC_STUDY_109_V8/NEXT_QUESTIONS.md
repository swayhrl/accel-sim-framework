# Falsifiable next-stage questions (no execution authorized by this archive)

1. **Memory supply versus shared control cost.** With the same strong dense path and numerical observations held fixed, does31-step incremental latency scale with memory-clock/achieved-DRAM bandwidth while SM-clock is held fixed? Weight-supply dominance predicts stronger response to memory supply; launch/control dominance predicts a residual insensitive to that axis. Requires an independently approved isolated experiment and actual bytes/clock evidence. The V8 conditional602GB/s estimate is not a measurement.

2. **Per-token graph/control residual.** How much of roughly318ms B1 incremental time remains after independently measuring graph replay/control time and actual data movement? LP_NONE removes about4ms but leaves R near1.033. A measurement of kernel/graph/node execution,CPU/device idle intervals and hardware memory bytes could reject a launch-only or bandwidth-only explanation. A tool metric alone must not replace full-request measurements.

3. **Where upstream numerical divergence starts.** First-token B1/B2 hidden states already differ before lm_head,while CPU normalization of captured logits reproduces the returned delta. A small separately tagged layer-boundary/attention-versus-MLP diagnostic with fixed inputs could localize the first divergent activation. A later FP32-head-only control could test head amplification but cannot by itself correct already divergent hidden states. The0.125 grid alone is not a kernel root cause.

4. **Prefix-cache numerical contract.** Warm cache changes A01's first token relative to reset cold,despite valid model/input/runtime identity;withinwarm B1/B2 sequences diverge atposition10. Does shape-matched recomputation or a stronger precision reference preserve the greedy margin? This is a numerical-quality/serving contract question,not evidence of new cache hardware.

These questions are not hardware mechanism candidates or PPA claims. Ordinary batching,Graph execution,logprob elision and prompt-cache reuse are existing software capabilities. No V9,profiling,clock change,new compression,RTL or simulator is launched.
