# Window C — SPECULATIVE M4B DEVELOPMENT 当前交接

结论：`C0-C4 PASS；C5 SKIPPED_POLICY；C6 closeout；C7/C8 analysis-only 完成；C9 design-only 完成`。历史实现与结果继续标记 `SPECULATIVE_CANDIDATE`，sub-entry 保持 `REFERENCE_APPROX_SUBENTRY_16`，不得作为 target paper 精确复现或正式性能结论。

## 冻结身份

| 项目 | SHA / 状态 |
|---|---|
| Framework branch | `hrl/vm-m4b-speculative-v0` |
| C9 architecture SHA | `04be2899a19b1fe756956dbe5e459494ae1da8df` |
| C8 evidence SHA | `468fe62ddc1c4d1786133072b540e52e0d8bdc23` |
| C4 tested runtime anchor | `5dd4501a51720a959129860b72988a6961b07477` |
| Core pre-C10-A frozen functional SHA | `c21137bcb86010215c008292f272aacefac175d3` |
| original Framework branch point | `eb18c43c516bdcd52c164969df10d97b895f45f1` |
| original Core branch point | `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd` |

C0-C4 已有 18 个定向测试、bounded real replay 和 Weight Segment C4 telemetry。C7 将 Weight Segment 评为 HIGH analytical opportunity、Sub-entry MEDIUM；均不是性能结论。

## C8 architecture gate

C8 的唯一 C5 gate：

`ARCHITECTURE_DECISION_REQUIRED`

原因：
- current Segment hit 使用 identity-like `ppn=vpn`，没有真实 PA mapping；
- `OBJECT_WEIGHT` 是 simulator metadata，不是可信硬件安装来源；
- Segment table port/bank/queue/latency 及 parallel-L1 ordering 未定义；
- descriptor context/lifecycle/migration/shootdown 未定义；
- current 768-group sub-entry 最多可容纳 12,288 leaves，对 768 exact entries 不是同预算比较。

因此不得在资源恢复后直接重启 C5。

## External A evidence context

Window A progress checkpoint：`73d25ebbdd96833ee1ddb8ea42b9017cefbceb75`。

Window A early C4 analysis：`2e491abec2afb0c745ca26aae0d86f8f35ad096b`，位于专用 progress-review 分支。它只作为方法学/observability 参考，不是 C candidate 的参数校准输入。

A early C4 的 decode terminal 分析进一步显示：paper 相比 generic 的 L1/L2 miss 与 MSHR-full 更少，但 cycles 更高；同时 PTE memory-wait、requester-MSHR-wait 与部分 memory-hierarchy queue occupancy 更高。因此未来 C 模型/报告必须保留 queue/backpressure/latency/stall 以及 cross-layer memory outcome，不能只用 TLB hit/miss 判断收益。A/C 数值不得合并，也不得据此调参匹配比例。

## C9 architecture decision（完成）

C9 在 Core `c21137bc...` 完全冻结、无 build/simulator/C5/trace 的条件下完成设计收敛。
唯一决定是：`ARCHITECTURE_READY_FOR_MODEL_IMPLEMENTATION`。

冻结 v1 设计为：privileged runtime/driver 注册、真正 `PA_base + (VA-VA_base)` 的物理连续 64KiB Weight extents；每 translation cluster 一个总 8-slot、单 provisioned-ASID 的本地复制 table；`HIT_FIRST / MISS_JOIN` completion；5/10/20 参数化 Segment latency；pinned immutable inference epoch。object map 仅 telemetry。non-contiguous extent 拆 descriptor，admission 失败则原子回退 conventional paging。

sub-entry 采用明确 C9 accounting ABI：66,000-bit 64KiB exact baseline 对应 standalone `G_equal_bit=96` group。35 个 N=8 Segment replica 的 37,800 bits 全额收费，故 equal-budget combined 为 32 groups。F0-F9 公平政策包含 exact、expanded/bit-matched exact、PWC、2MiB、leaf-capacity diagnostic、Segment 和 combined，历史 768-group candidate 永不作为 equal-cost arm。

完整 C9 architecture spec 与 C10 requirements 位于：
`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C9_SEGMENT_SUBENTRY_ARCHITECTURE_DECISION/`。

## C10-A authorized next stage

现授权低资源实现阶段：

`C10A_ARCHITECTURE_MODEL_IMPLEMENTATION_LOW_RESOURCE`

执行文档：
- `docs/vm_tlb/codex_handoff/spec_m4b/C10A_ARCHITECTURE_MODEL_IMPLEMENTATION_LOW_RESOURCE.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C10A_ACCEPTANCE_MATRIX.md`

C10-A **允许从 Core `c21137bc...` 开始修改 functional model**，实现 C9 已冻结的 real-PA registration/mapping、N=8 local Segment table、`HIT_FIRST / MISS_JOIN`、lifecycle/telemetry、G96/G32 fair sub-entry 以及 F0-F9 config/manifest plumbing。

但在 Window A simulator-heavy 长跑仍存在期间，C10-A 严格禁止 full build、full replay、C5、12K/KV segmentation/M5。仅允许 source 修改、static validator、小型 unit/model test，以及资源健康时单进程 focused compile/test。重资源 build/regression 留给后续独立 C10-B。

C10-A 完成后必须 commit/push 并 STOP 等独立审阅，不自动启动 C10-B/C5。
