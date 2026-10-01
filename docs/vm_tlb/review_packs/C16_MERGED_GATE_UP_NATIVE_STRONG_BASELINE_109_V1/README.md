# C16 merged gate/up native strong baseline — Lane 7

Authority, environment isolation, checkpoint identity, 28-layer canonical AWQ identity, runtime backend selection, token identity, shape checks, and finite checks closed successfully. The B2 runtime selected the mature Marlin merged path.

The frozen FP16 tolerance failed for a bounded subset of gate/up/down occurrences. The contract therefore stopped before formal timing. Canary wall values and kernel traces are retained as non-inferential diagnostic evidence only; no B0/B2 speedup or merge benefit is claimed. Three earlier engineering attempts were aborted and their locks released; consequently the single-outer-lock-across-goal requirement was not met, although the cumulative 86-second GPU budget remained below 480 seconds.
