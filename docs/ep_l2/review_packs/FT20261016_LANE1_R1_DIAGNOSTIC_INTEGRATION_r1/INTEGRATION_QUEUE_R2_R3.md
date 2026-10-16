# R2/R3 integration intake after R0

Authority: review_r2 aec01450. R0 Core is 126394be46b15f55b9756d43eb9ca9a9baae1c84; its primary release, binary and config contract remain independent of this queue. Lane 2/3 write their production adapters in their own worktrees against this exact executable R0, then provide minimal patches and production tests. Lane 1 performs final sequential integration and conflict checks; Lane 5 independently qualifies each new feature/vector.

Lane 2 new bounded publication f38632c2 announces actual R0 production-wiring candidate c9666ae6 and tests in progress, superseding its earlier module-only checkpoint. No new qualified adapter/test pack is consumed yet. Its follow-up owns actual victim/Tag routing, extra lookup cycle, shared WAD authority, reachable dirty-inflight reads, response commit, same-handle promotion and epoch hooks. Actual served sectors/bytes must be distinct from matched lower/DRAM savings. No automatic FULL claim follows module PASS.

Lane 3 currently consumed Framework bfa193e7 / Core ddedbf0f: shared-store adapter only, without independently qualified production dispatch. Its follow-up owns actual Tag generation, lower/return/ICNT/epoch certificate routing, distinct detach/MSHR-bypass bits and production tests. Keep whole-commandlist closed-world certificates and negative empty FWT coverage; no redefinition of oracle scope.

R1 diagnostic integration is Core be651ccf on R0, adding IDEAL_REFERENCE and optional constructor/metadata paths. Expected eventual patch conflicts are gpu-cache.h enum and constructor/allocation declarations plus gpu-cache.cc/l2cache frontend dispatch. Resolve by preserving named roles and default-OFF behavior; never infer enum ordinals, add a second payload/WAD allocator, or silently enable diagnostic options in implementation vectors. Do not substitute the old Lane 5 RO Core57801b42 module PASS for a later producer-runtime gate.

R2/R3 stay unqualified until exact adapter source/test receipts are available. They do not delay Lane 5 R0 experiments or the separately qualified R1 matched baseline.
