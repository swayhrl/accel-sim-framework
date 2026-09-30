# Final decision — R101R5 Native post-L1 downstream realism

**`NATIVE_POST_L1_DOWNSTREAM_SUPPORT_NOT_OBSERVED`**

## Exact target facts before interpretation

All three rows are the second recurrence (0-based occurrence 1) of the accepted natural L512 five-step HiMuon map, selected from the same NVTX range as the accepted NCU run. Counts below are NCU *warp instructions*, not simulator memory requests; L1/TEX values are 32-byte sectors. Percentages are `smsp__warp_issue_stalled_*_per_warp_active.pct`, i.e. percentages of active warp-cycles, and are not normalized shares of only failed issue attempts. L2/DRAM values are NCU Mbyte. The complete precision and full stall composition are in the TSVs.

| Exact target (accepted launch ID; grid/block) | ordinary LDG/LD | ordinary STG/ST | LDGSTS | L1/TEX global load/store sectors | L2 requested; DRAM R/W MB | dominant issue facts |
|---|---:|---:|---:|---:|---:|---|
| XXT (6; 2816×1×1 / 128×1×1) | 0 | 50,688 | 506,880 | 6,488,064 / 811,008 | 233.807; 16.426 / 3.136 | math-pipe 56.87%; wait 9.18%; long scoreboard 8.80%; LG 0.77% |
| BA (7; 2816×1×1 / 128×1×1) | 25,344 | 50,688 | 506,880 | 6,893,568 / 811,008 | 246.800; 21.431 / 3.070 | math-pipe 51.21%; long scoreboard 12.63%; wait 9.43%; LG 0.79% |
| BMM-add (8; 16×44×1 / 128×1×1) | 45,056 | 45,056 | 428,032 | 6,488,064 / 720,896 | 231.060; 46.148 / 13.326 | math-pipe 71.26%; wait 10.20%; long scoreboard 3.41%; LG 0.65% |

Eligible warps per active cycle were 0.220748 / 0.237463 / 0.157958 for XXT / BA / BMM-add. Active-warp occupancy was 23.71% / 23.79% / 15.82% of peak. MIO throttle was 2.69% / 2.78% / 1.36%; short scoreboard 2.73% / 3.37% / 0.10%; barrier 8.13% / 8.69% / 3.93%. These are counter observations, not fresh primary runtime measurements. Cache and clock control remained `none`, matching accepted R101 profiling policy; uncontrolled-cache/clock warnings are preserved in the raw logs. Each selected kernel required 11 NCU internal replay passes.

SASS-PC SourceCounters were available. For the sampled long-scoreboard reason, XXT had 646 samples (642 at two `BAR.SYNC.DEFER_BLOCKING` PCs); BA had 861 (684 at two `BAR.SYNC` PCs, 133 at `SEL`); BMM-add had 403 (325 at two `BAR.SYNC` PCs). This localizes the sampled *stalled PC*, not the originating memory request. LG-throttle samples were sparse (74 / 62 / 37), mostly on `LDGSTS` and `LDGDEPBAR`, not on an ordinary `LDG` instruction. Math-throttle sampling concentrated on `HMMA` PCs (4,165 / 3,710 / 8,401 total samples). The per-PC rows and classification rules are in `SOURCE_PC_ATTRIBUTION.tsv` and `SOURCE_PC_SUMMARY.json`; source CSVs remain in durable raw.

## Bounded conclusion

All three exact targets are dominated by math-pipe throttle, while ordinary global LDG is absent or small relative to LDGSTS, and LG throttle is below 1% of active warp-cycles in each. BA's 12.63% long-scoreboard signal is real but not dominant and its sampled PCs do not isolate ordinary LDG/ST downstream service. The large L1/TEX global-load sector counts cannot be treated as ordinary-LDG evidence because LDGSTS execution is substantial. Ordinary stores and L2 traffic exist, but the issue/PC evidence does not make ordinary LDG/ST post-L1 pressure a dominant native limitation across these kernels.

This matches the handoff's **NOT_OBSERVED** decision rule: three targets consistently exhibit stronger nonmatching compute/barrier/wait limitations and weak ordinary-LDG/ST downstream issue evidence. It does not prove absence of all memory cost, disprove the simulator's local 8.31% response, or identify an exact L1/ICNT/L2 component. A scoreboard stall is not ICNT proof; LSU/LG throttle is not an L1/L2/ICNT localization. Simulator P1 served 1,126,400 ordinary LDG reads and 2,342,912 writes but zero LDGSTS; simulator request counts and these NCU warp-instruction counts are different units and are not compared numerically.

No R101 mechanism, extra counter search, synthetic ICNT benchmark, new trace, graph-timing refresh, 174 simulation, or next round was initiated. Lane E/G remain STOP.
