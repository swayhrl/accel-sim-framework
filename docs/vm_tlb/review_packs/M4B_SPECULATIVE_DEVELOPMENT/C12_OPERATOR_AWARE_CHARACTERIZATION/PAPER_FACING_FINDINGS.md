# C12 operator-aware findings (interim)

Evidence cutoff: the 20 terminal-PASS arms at C12 source commit
`269c274712f4eeaee15d304033a9e6d61b5b3206`.  `Prefill F1` and
`Prefill F8-Lseg20` are deliberately absent.

## MEASURED_OPERATOR_FACT

- The compute-list, semantic header, and simulator marker index are one-to-one:
  692/692 Prefill and 740/740 Decode1 entries pass.  The complete evidence is
  in `INDEX_ALIGNMENT_AUDIT.tsv`.
- Direct classification is 99.86% of kernels in both ROIs (691/692 Prefill,
  739/740 Decode1); the remaining one kernel per ROI is retained as
  `UNRESOLVED`.  There are no heuristic-sequence rows.  FlashAttention is
  represented by 16 `ATTENTION_CORE` kernels per ROI through its embedded
  `pytorch_flash` semantic name, not its filename.
- Between direct Weight parameter classes, FFN has the larger footprint:
  Prefill FFN versus Attention Projection is 201,326,592 versus 41,943,040
  Weight lane references and 6,158 versus 1,294 unique 64 KiB pages; Decode1
  is 25,165,824 versus 5,242,880 references with the same respective page
  counts.  `EMBEDDING_OUTPUT` is a separate direct class with 8,016 pages, so
  it must not be silently folded into either side of that comparison.
- F0 translation differs strongly by phase.  Prefill has 1,119,527 L1 and
  45,227 L2 TLB misses versus Decode1's 57,947 and 22,220.  At L2, direct
  embedding/output, FFN, and Attention Projection contribute respectively
  20,545/11,626/3,971 misses in Prefill and 8,210/6,389/4,172 in Decode1.
  Direct `OTHER_COMPUTE` is also material in Prefill (7,752 L2 misses), so the
  phase difference is not an attention-only effect.
- Decode1's direct Weight L2 `HIT` count is exactly zero for Attention
  Projection, FFN, and Embedding/Output, while their `MISS` counts are
  660,773, 3,145,728, and 4,231,706 respectively.  This localizes the observed
  near-streaming Weight signature to several direct parameter classes, rather
  than only to Attention Projection.  Norm is a small exception (9,632 hits,
  7,264 misses).
- KV L2 reuse is not exclusive to attention.  Decode1 `ATTENTION_CORE` has
  33,395 hits and 157 misses (99.53% hit/(hit+miss)), but its largest absolute
  hit source is `EMBEDDING_OUTPUT` (933,824 hits, 67,068 misses); FFN also has
  120,817 hits and 19,913 misses.  In Prefill, Attention Projection has 82.60%
  hit/(hit+miss), Attention Core 60.56%, and generic `OTHER_COMPUTE` has the
  largest absolute KV L2 hits (1,005,585).  Reservation failures remain
  separately tabulated and are excluded from these rates.
- Segment latency sensitivity is concentrated, not uniform.  Relative to F0,
  Prefill F7-L20 adds 13,640,954 cycles: FFN contributes +7,444,348,
  Embedding/Output +4,157,697, and Attention Projection +1,716,774.  Decode1
  F7-L20 adds 1,471,105 cycles, led by FFN (+870,760) and Embedding/Output
  (+594,778).  Conversely, at Lseg=5 the F7 improvements are led by FFN
  (Prefill -2,728,133; Decode1 -493,157 cycles).  These are exact per-kernel
  cycle sums, not apportioned ROI cycles.
- F8 sub-entry activity exists even where its incremental timing is negligible.
  In Decode1, F8 and F7 have identical total and per-class reported cycles at
  all Lseg values, although F8-L5 records 25,407 sub-entry hits, led by
  `OTHER_COMPUTE` (13,458) and Attention Core (6,533).  In Prefill, F8 versus
  F7 is -16,864 cycles at Lseg=5 and +4,615 at Lseg=10; its sub-entry hits are
  led by `OTHER_COMPUTE` (~608k) and Embedding/Output (~154k), not Attention
  Projection (~13k).  The pending F8-L20 Prefill row is not inferred.
- Direct parameter names show the same structural repetition in both ROIs:
  layers 0--15 each contain four direct Attention Projection kernels, three
  direct FFN kernels, and two direct Norm kernels.  This is a mapping fact;
  it does not assert layer-invariant performance.

## SUPPORTED_OPERATOR_SIGNAL

- Decode1 F7 reduces translation walks from 15,691 (F0) to 170 at every
  reported Lseg, but the full-ROI outcome ranges from -1.75% cycles at Lseg=5
  to +4.26% at Lseg=20.  Together with the FFN/Embedding concentration above,
  this supports the interpretation that translation-event suppression alone
  does not determine end-to-end timing.  It does not establish a downstream
  causal mechanism.
- Prefill F7 exposes a similar non-monotonic relation: roughly 48--49 million
  exact Segment hits/suppressed L2 lookups are recorded at all three Lseg
  values, while the total is -4.25% cycles at Lseg=5, +1.41% at Lseg=10, and
  +21.83% at Lseg=20.  The measurements support latency sensitivity localized
  in direct Weight-touching FFN/Embedding groups, not a claim that Segment
  lookup counts themselves cause the outcome.

## HEURISTIC_ONLY

None.  No kernel is assigned by sequence position, periodicity, neighbor, or
trace filename.

## UNRESOLVED

- One compute kernel per ROI lacks a direct parameter-range label and an
  explicit semantic-name label; it remains `UNRESOLVED`.
- No embedded name directly establishes a RoPE class under the frozen taxonomy;
  sin/cos or execution order were not promoted to RoPE evidence.
- `UNKNOWN` trace addresses remain an address class only.  They are not called
  activations, workspace, or a model operator.
- This interim pack cannot make the requested Prefill F1-vs-F2 or
  F8-L20-based final comparisons until formal C12 publishes terminal-PASS
  rows for those arms.
