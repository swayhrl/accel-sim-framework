# Top remaining problems

## 1. Gate/up sibling concurrency - continue with the existing contract

This is the only candidate that clears all three gates.

- **Whole-decode headroom is explicit:** the accepted gap-preserving no-contention ceiling saves 7.732849 ms, or 7.8931% of the 97.970144 ms decode GPU wall, for an ideal 1.0857x speedup.
- **Strong kernels do not directly solve it:** Marlin, QUICK, FLUTE and vLLM AWQ/Marlin optimize a projection kernel or its dispatch. They do not schedule the logically independent gate-to-SiLU branch concurrently with up before Mul.
- **A minimal validation is already defined:** `C16_FFN_TIMELINE_HEADROOM_QUALIFICATION_174NEW_V2/LANE7_FFN_GATE_UP_CONCURRENCY_NATIVE_CONTRACT.json` freezes two streams, events, unchanged kernels/layout/quantization, exact outputs, timing and stop conditions.

No new 109 contract is generated here. The pre-existing contract is sufficient and this Goal remains CPU-only.

## 2. No second candidate qualifies

The second slot is intentionally empty.

- Perfect intra-FFN gap removal is only a 2.9602% whole-decode ceiling, overlaps candidate 1, and graph/persistent dispatch is established software territory.
- Reduction removal is a 0.7808% zero-cost ceiling; accepted split1 removes reduction but regresses M1 up by 41.3% and M1 down by 413.3%. Grouped/swizzled mapping already closes the larger-M split/reuse branch.
- The 6.25% M-tile fill is a valid attribution metric, not a legal batch-1 elapsed-time oracle. Marlin/vLLM AWQ-Marlin/QUICK/FLUTE/FlashDecoding++ directly guard a new kernel story.
- W4 memory-service headroom is not identifiable from bytes plus long-scoreboard percentages, and attention service fields are absent. Missing data remains `UNKNOWN`; this screen does not create a profile solely to fill the table.

Therefore the ranked continuation set has cardinality one, not two.
