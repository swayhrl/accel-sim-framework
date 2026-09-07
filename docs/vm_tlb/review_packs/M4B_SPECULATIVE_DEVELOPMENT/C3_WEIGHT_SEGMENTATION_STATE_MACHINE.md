# C3：Weight Segmentation 并行状态机

状态：`PASS`（`SPECULATIVE_CANDIDATE`）。仅实现授权的 Weight
Segmentation；没有实现 KV segmentation、12K KV 合成或任何 M5 机制。

每一个未完成的翻译请求在启用 C3 后同时启动 L1 和 immutable Segment lookup。
状态机等待两项原始并行观察都完成：

1. Weight Segment 命中：返回冻结 identity-like SimPA，并丢弃已经完成的 L1
   原始结果。它不会发射 L2 lookup，不会创建/合并 MSHR 或 PWQ，不会启动 walker，
   不会探测 PWC、请求 PTE，也不会填充 conventional L1/L2 TLB。
2. Segment 未命中：复用已完成 L1 的 hit/miss，不会再次占用 L1 port 或 re-probe。
   L1 miss 随后走既有 L2→MSHR→PWQ→walker/PWC/PTE 流程；KV 和 Unknown 也属于
   该路径。
3. 已由 PTW 唤醒的相同 UID 只执行接受的 L1 交付 retry，不会对同一 requester
   发射第二次 Segment lookup。

输出明确区分 `vm_weight_segment_raw_l1_*`（并行观察）和
`vm_weight_segment_effective_l1_*`（真正进入 conventional 路径的结果），并输出每种
下游资源的 `*_suppressed` 计数。对象标签仅选择 Weight descriptor；从不改变 tag、
LRU、cache、路由或调度。

`vm_m4b_weight_segmentation_test` 覆盖：并行 launch、Segment hit 的全部抑制、无
conventional TLB fill、Segment miss 的 L1 复用、PTW retry 不重发 Segment、KV 与
Unknown 正常 paging、边界 crossing 保守 miss、identity SimPA，以及对象归因守恒。
