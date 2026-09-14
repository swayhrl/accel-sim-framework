# Llama S0 exploratory fingerprint findings

Status: `C16_H_LLAMA_S0_EXPLORATORY_FINGERPRINT_V1_READY_FOR_REVIEW`.

The only admitted analysis inputs are two SHA-verified historical M4A captures,
not C16 formal inputs.  `/root/share/c16_recovery_v3` contains the frozen
Llama model asset but no Llama NVBit raw candidate.  The latest G closeout
(`556ab6ca`) independently reports no new formal Llama raw trace, so no row
has been promoted into a C16 canonical scientific table.

For the historical selected PCs, Prefill has 64x the exact-address and 128B
line footprint of Decode1 (131,072 versus 2,048 VAs; 2,048 versus 32 lines).
Both have 32 active lanes, 2B requests, one 128B block per request, and a 1.0
contiguous-lane-pair fraction.  Thus the observed difference is footprint and
concentration, not an observed difference in same-request coalescing proxy.
Decode1's top line covers 3.125% of its lane-address records, versus 0.0488%
for Prefill; its one observed 4KiB bucket covers all selected accesses, versus
Prefill's 64 buckets.  These are set-frequency/address-structure facts only.

No Decode2/3/4 input exists.  Consequently Q2/Q3 (cross-step overlap and its
address-versus-page nature) are `NOT_AVAILABLE`, not zero or inferred.  The
two phase targets have zero cross-capture set overlap, but they are distinct
target functions and process runs, so this supplies no decode reuse claim.

`MEMORY_FINGERPRINTS.tsv` is a reproducible output of
`util/vm_tlb/c16/lane_h/llama_s0_analysis.py`; it preserves `UNKNOWN_RUNTIME`
object attribution and `SET_ONLY` ordering.  `PREFILL_DECODE_COMPARISON.tsv`
states all computed ratios and metric meanings.
