# C12 operator-aware characterization — final review pack

## Status

`C12_OPERATOR_AWARE_COMPLETE_READY_FOR_REVIEW`

This finalization consumed the read-only C12 source commit
`a268aba0d01310294074ded5bb8017e2092394c0`, whose formal final report is
`C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW` with 22/22 terminal `PASS` arms.
All 22 `ARM_STATUS.tsv`/`ARM_RESULTS.tsv` rows passed the frozen Framework,
Core, binary, ROI trace, registration, and raw-log-SHA checks before analysis.
No simulator replay was launched and no C12 asset was changed.

Final-review reparse acceptance is also closed: all 15,752 kernel markers
across the 22 arms contain exactly one explicit `gpu_sim_cycle`, and every
arm's per-kernel sum equals both formal `gpu_tot_sim_cycle` and its immutable
validation value. The 302 cumulative `vm_*` metrics actually used for
per-kernel attribution pass snapshot continuity, monotonicity, delta-to-final,
and numeric validation closure over 216,232 metric snapshots.

## Continuation identity check

The existing 692/740 alignment and trace scans were reused, then rechecked.
The two F0 compute-list SHA-256 values remain `a40d683…6e6f` (Prefill) and
`b6c42e…0dc` (Decode1). Regenerated canonical trace-scan, parameter-range, and
object-range TSV SHA-256 values are byte-identical to the interim artifacts.
The runtime sidecar SHA-256 values are `8b605b8b…839a` (Prefill) and
`7a07d671…aa7` (Decode1), recorded in `PROVENANCE.md`. Thus the final arm
extension did not alter the proven trace/header/marker or Weight-layout
namespace.

## Final 22-arm completion

The formerly missing Prefill comparisons are now present in
`OPERATOR_ARM_DELTAS.tsv` and `ARM_OPERATOR_CHARACTERIZATION.tsv`:

| Comparison | Full-ROI cycle result | Exact operator-level observation |
| --- | --- | --- |
| Prefill F1 vs F2 | 63,302,886 → 63,758,501 (+0.7197%) | Embedding/Output +483,963 cycles is the largest positive component; this is attribution, not causal proof. |
| Prefill F8-L20 vs F7-L20 | 76,131,192 → 76,144,277 (+0.0172%) | Attention Projection +7,307 and Embedding/Output +6,299 cycles are the largest positive components. |
| Decode F8-L20 vs F7-L20 | 36,035,731 → 36,035,731 (0%) | Every reported operator-class cycle sum is identical, despite 25,197 exact sub-entry hits. |

Prefill F8 is now complete at Lseg=5/10/20: versus F7 its full-ROI deltas are
-16,864 (-0.0282%), +4,615 (+0.0073%), and +13,085 (+0.0172%) cycles.
Decode's corresponding F8-over-F7 deltas are exactly zero at all three Lseg
points. All Segment/Sub-entry activity remains reported separately from
performance claims in `LSEG_OPERATOR_SENSITIVITY.tsv`.

## Key final findings

- Direct classification is retained: 691/692 Prefill and 739/740 Decode1
  kernels are direct; one per ROI is `UNRESOLVED`, and there are no heuristic
  rows. The 16 FlashAttention kernels per ROI are `ATTENTION_CORE` by their
  embedded semantic name.
- FFN has more direct Weight footprint than Attention Projection in both ROIs
  (6,158 versus 1,294 unique 64 KiB pages). Embedding/Output is separately
  larger at 8,016 pages; it is not folded into either class.
- Final Segment latency sensitivity remains concentrated in direct FFN and
  Embedding/Output. At Lseg=20, F7 adds 7,444,348 FFN and 4,157,697
  Embedding/Output cycles in Prefill, and 870,760 / 594,778 in Decode1.
- The new KV-class audit establishes same-kernel **address-range** conjunctions
  in Decode1, not semantic ownership. Twenty-one direct-FFN kernels and one
  direct Embedding/Output kernel have both a direct Weight hit and trace
  references inside the selected KV runtime range. Their exact KERNEL-scope
  cache rows are documented in `KV_CLASS_TRANSACTION_AUDIT.tsv`; the sidecar
  range contract has overlapping historical/replaced intervals and
  `end_phase=UNKNOWN_ACTIVE`, so it cannot establish that FFN or embedding
  semantically consumes model KV Cache or that a kernel fusion occurred.

## Review entry points

- `PAPER_FACING_FINDINGS.md` answers the required questions in four evidence tiers.
- `CONSERVATION_AUDIT.md` proves F0 additive closure and final-arm admission.
- `KV_CLASS_TRANSACTION_AUDIT.md` states the narrowly supported interpretation
  of FFN/Embedding KV-class cache transactions.
- `KERNEL_OPERATOR_MAP.tsv`, `ARM_OPERATOR_CHARACTERIZATION.tsv`, and
  `OPERATOR_ARM_DELTAS.tsv` provide row-level evidence.
