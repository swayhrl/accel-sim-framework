# W/V850 performance frontier

All rows below are actual accepted ON points, same Source78/32x8/L100/DRAM850. OFF controls do not add independent cache configurations. Numeric output remainsUNKNOWN; source/trace/kernel/protocol completion follows existing acceptance.

|Input|S|W-only|Clean-only|Dirty-only|BothWV|Best mechanism in this scope|
|---|---:|---:|---:|---:|---:|---|
|FWT|181827|181635|181441|179267|178951|bothWV|
|GEMM|558588|558957|553632|570129|550642|bothWV|
|Stencil|5242939|5240684|UNKNOWN|UNKNOWN|4768893|WV; F4769712 slightly slower|
|3MM|1696618|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|F1669413; not V-only proof|
|Scan|2162540|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|S; F2224142 regresses|
|Conv32x8|331234|UNKNOWN|UNKNOWN|UNKNOWN|UNKNOWN|S; F335088 regresses|

FWT clean-only serves0 Victim reads while occupying439658554CLEAN slot-ticks; dirty-only serves88103reads including3280dirty-forward. Both serves88069reads,3312dirty-forward and still finishes316cycles before dirty-only. Removing clean therefore does not automatically accelerate; standalone-class metrics cannot be subtracted to assign combined-mode contributions.

GEMM clean-only serves592450Victim reads; dirty-only serves0reads despite306732787dirty slot-ticks and runs570129cycles. Both serves609858reads with only9dirty installs and finishes2990cycles before clean-only. The default both policy already suppresses most useless standalone dirty retention; uniform lowCLEAN quotas can sacrifice valuable reuse.

StencilWV serves4930426reads and lowerscycles9.00%vsW. 3MM Fserves1147507reads. Their final directory populations total8192entries (64x128); that is terminal occupancy evidence, not proof directory capacity is the critical path. Scan serves5584reads over16316924436combined retentionticks, while its lower scheduler pressure remains large. Conv has44974reads and actual WAD wait populations.

Current gaps that affect structure selection: both-mode clean-vs-completed-dirty service split isNOT_INSTRUMENTED; dirty area mixesinflight mandatory andcompleted optional time; terminal live entries are censored; no unique unserved-entry lifetime/reclaim-value denominator. Directory saturation event population and bank-color-local optional allocation opportunity need actual sameevent evidence before strong bottleneck claims. Existing bank_wait and B0 blockage sums are not exclusive GPU cycles. Do not rescan enormous Trace to fill these gaps.

Full exact identities, pointrefs and perpopulation values are in the JSON/CSV and ACCEPTED_850_SMALL_EVIDENCE.json. Newly accepted GEMM DIRTY_ONLY_ON was appended from its own official point; OFF570129 was not substituted.
