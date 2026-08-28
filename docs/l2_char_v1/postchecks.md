# Instrumentation v1 closeout postchecks

This closeout uses only small directed traces and production
`memory_partition` fixtures.  It does **not** run a broad workload sweep or
change simulated L2 behavior.

| Check | Result | Evidence |
|---|---|---|
| C0 build / diff check | PASS | Core and framework rebuilt; both `git diff --check` commands pass. |
| C1 frozen vs char-off | PASS | After removing unavoidable build-banner and newly registered option echo rows, 5,710 original-output rows are byte-identical. |
| C2 char-off vs char-on | PASS | 5,709 production-output rows are byte-identical after removing config echo and `L2CHARV1`; both arms: 6,895 cycles / 13,568 instructions. |
| C3 queue class conservation | PASS | `L2CHARV1|INVARIANT` validates MissQ and L2→DRAM class sums every sample; dirty-WB fixture ends with class sum zero. |
| C4 causal denominator | PASS | Directed DataPort arm: eligible 1,300, blocked 930, requests/episodes 30; P4 arm additionally records MSHR-new 268/272 and MissQ 132/272 blocked cycles. |
| C5 all-reserved set | PASS | 1-set/2-way production fixture reaches `max_reserved_ways_any_set=2`, `cycles_any_set_all_reserved=180`, then real `LINE_ALLOC_FAIL` for 180 cycles before retry completes. |
| C6 MSHR lifetime | PASS | Production new-miss+merge fixture reaches merge depth 2; pending lifetime 101, held response-drain lifetime 118, final tracker/invariant empty. |
| C7 WB accounting | PASS | Dirty-WB arm: 16 generated WBs / 512 B; MissQ-WB and L2→DRAM occupancy return to zero with invariant pass. |
| C8 fill blocking | PASS | Two real returns: fill eligible 33, fill blocked 31; final response and resource state drain cleanly. |
| C9 ROP→input | PASS | One-entry production ICNT→L2 FIFO: ROP eligible 184, blocked 180, then drains without a ROP policy change. |
| C10 DRAM causality | PASS | P5A reports return-path blocked read (`dram_issue_returnq=1`, `dram_read_returnq=1`); P5B reports production credit 223 and scheduler 262 issue contexts, with progress-credit return/no leak. |
| C11 windows | PASS | 16-cycle directed window run emits 384 monotonic windows for 6,123 samples; final window has 3 samples and per-window WB sum is 16, matching the final cumulative count. |
| C12 percentiles | PASS | Deterministic histogram unit test passes exact nearest-rank P50/P95/MAX/AVG. |

## Timing-neutrality and host cost

The common pressure trace was run with the frozen corrected baseline, with
characterization disabled, and with the standard 5K-window configuration.
The C1/C2 comparisons above preserve simulation behavior exactly.  A local
host measurement was 1.14 s char-off and 1.30 s char-on (about 14% slowdown,
same 286,720 KiB peak RSS); this is within the 25–30% engineering target.

## Parser / artifact checks

`python3 util/l2_char/tests/test_parser.py` passes.  Parsing the final
directed raw log emits `summary.csv`, `slice.csv`, `window.csv`, and
`manifest.json`; the parser retains the final terminal snapshot rather than
combining per-kernel snapshots.

## Limits and stop condition

V1 observes the conventional baseline; it does not add an independent WBQ,
physical SRAM-bank model, queue resizing, resource sensitivity, or any
LateBind/Decoupled mechanism.  Directed holds are default-off verification
hooks and are not enabled for future characterization experiments.  After
the review pack is created, this branch stops here: broad workload sweeps
must start from a separately reviewed/frozen instrumentation point.
