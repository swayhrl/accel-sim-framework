# C12 operator-aware findings (final)

Evidence cutoff: C12 final source commit
`a268aba0d01310294074ded5bb8017e2092394c0`, with 22/22 terminal-PASS arms.

## MEASURED_OPERATOR_FACT

- Compute-list, semantic-header, and simulator-marker alignment remains exact:
  692/692 Prefill and 740/740 Decode1 rows pass. Direct evidence covers 99.86%
  of kernels in each ROI; the residual one kernel per ROI remains `UNRESOLVED`.
  There are no heuristic-sequence assignments.
- FFN has the larger direct Weight footprint versus Attention Projection:
  201,326,592 versus 41,943,040 Prefill lane references and 6,158 versus 1,294
  unique 64 KiB pages; Decode1 is 25,165,824 versus 5,242,880 references with
  the same page counts. Embedding/Output is independently 8,016 pages.
- Prefill F1 versus F2 is now measured: F1 is 455,615 cycles (+0.7197%) slower
  full ROI. Its largest positive exact operator contribution is
  Embedding/Output (+483,963 cycles), while Attention Core, Attention
  Projection, and Other Compute are negative. Decode1 F1 versus F2 is 24,139
  cycles (-0.0698%).
- The complete Prefill F8-over-F7 series is -16,864, +4,615, and +13,085
  cycles at Lseg=5/10/20. At Lseg=20, Attention Projection (+7,307) and
  Embedding/Output (+6,299) are the largest positive deltas. Decode1 is exactly
  zero F8-over-F7 in total and every reported operator class at all Lseg values.
- Segment sensitivity remains concentrated. Prefill F7-L20 versus F0 adds
  7,444,348 FFN and 4,157,697 Embedding/Output cycles; Decode1 adds 870,760
  and 594,778 respectively. At Lseg=5, FFN has the largest benefit in both
  ROIs (-2,728,133 Prefill; -493,157 Decode1).
- F0 translation differs substantially by phase: Prefill has 1,119,527 L1 and
  45,227 L2 TLB misses versus Decode1's 57,947 and 22,220. Direct
  Embedding/Output, FFN, and Attention Projection account for 20,545 / 11,626
  / 3,971 Prefill L2 misses and 8,210 / 6,389 / 4,172 Decode1 L2 misses.
- Decode Weight's zero-L2-hit signature is present in direct Attention
  Projection, FFN, and Embedding/Output, not one operator alone. KERNEL-scope
  `DATA_KV_CACHE` L2 HIT transactions are observed in several
  operator-classified markers: 33,395 in Attention Core, 933,824 in
  Embedding/Output-classified markers, and 120,817 in FFN-classified markers.
- For FFN/Embedding-classified markers, those are only observed
  KV-runtime-range / KV-class Cache transactions in the same marker as the
  direct Weight classification. They do not prove semantic FFN/Embedding KV
  use, cache reuse, or fusion. See `KV_CLASS_TRANSACTION_AUDIT.*`.

## SUPPORTED_OPERATOR_SIGNAL

- Decode1 F7 lowers full-ROI translation walks from 15,691 (F0) to 170 at all
  three Lseg values, while the timing ranges from -1.75% cycles at Lseg=5 to
  +4.26% at Lseg=20. Together with the FFN/Embedding localization, this
  supports—but does not prove—that event suppression alone does not determine
  full-ROI timing.
- Prefill has roughly 48--50 million exact Segment hits/suppressed L2 lookups
  across F7/F8 Lseg points, but changes from a 4.25% improvement at Lseg=5 to
  approximately 21.8% regressions at Lseg=20. This supports a latency-sensitive
  direct Weight-touching subset rather than a universal operator response; it
  is not a counter-to-performance causal claim.
- Sub-entry activity is predominantly Other Compute and Embedding/Output in
  Prefill (about 607k and 158k F8-L20 hits) and Other Compute/Attention Core
  in Decode1 (13,481 and 6,549 hits). The activity exists even where Decode
  F8-over-F7 cycles are exactly unchanged.

## HEURISTIC_ONLY

None. No formal row relies on position in a Transformer block, periodicity,
neighboring kernels, trace filenames, or address-volume thresholds.

## UNRESOLVED

- One kernel per ROI lacks direct parameter and explicit semantic evidence.
- No semantic name meets the frozen direct-evidence bar for RoPE; sin/cos and
  execution order are not promoted to a RoPE label.
- `UNKNOWN` remains an address class and is not renamed Activation or Workspace.
- The retained Decode1 KV interval union has overlapping CREATED/REPLACED
  histories and `UNKNOWN_ACTIVE` end lifetimes. It cannot prove logical tensor
  ownership, direct FFN/Embedding KV consumption, fusion, or a causal cache
  explanation.
