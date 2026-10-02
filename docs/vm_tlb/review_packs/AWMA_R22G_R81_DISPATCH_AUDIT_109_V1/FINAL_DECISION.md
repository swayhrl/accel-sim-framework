# Final decision

`R22G_R81_DISPATCH_NOT_JUSTIFIED_FROM_EXISTING_EVIDENCE`

RULE_U01 is favorable in the accepted matched head-region data before dispatch
cost, with median reductions of 7.17%, 4.37%, and 6.09% for C0/C1/H0. However,
the online path does not produce the required union fraction before head
execution. Deriving it requires a new CPU union reduction over legal IDs or a
new mask OR/popcount operation on every step. That cost is outside the accepted
A0/A3 timing and has no accepted measurement.

Consequently the deployable net time is `UNKNOWN`. It is not legal to set the
dispatch cost to zero, infer it from A2's compound timing, or call the
retrospective head-region reduction a complete-generation speedup. One bounded
future mixed-dispatch validation is specified but not executed. No hardware
claim follows.
