# C10-A：低资源架构模型实现

Goal：`C10A_ARCHITECTURE_MODEL_IMPLEMENTATION_LOW_RESOURCE`

状态：`READY_TO_EXECUTE / IMPLEMENTATION_ALLOWED / NO_FULL_REPLAY`。

## 1. 目的

C9 已冻结 v1 架构并给出唯一结论：`ARCHITECTURE_READY_FOR_MODEL_IMPLEMENTATION`。C10-A 的目标是把 C9 的架构决定真正落到 Framework/Core 模型、配置、manifest、telemetry 与 focused validation 中，同时严格保护仍在运行的 Window A。

C10-A **允许修改 Core functional model**，这是相对 C0-C9 的重要权限变化；但本轮不授权 full Accel-Sim build、连续 Llama replay、C5、12K/KV segmentation/M5。

本轮完成后必须 STOP 等独立审阅。不得自动进入 C10-B 或 C5。

## 2. authoritative 输入与起点

Framework：
- repo：`swayhrl/accel-sim-framework`
- branch：`hrl/vm-m4b-speculative-v0`
- C9 HEAD：`04be2899a19b1fe756956dbe5e459494ae1da8df`

Core：
- repo：`swayhrl/gpgpu-sim`
- branch：`hrl/vm-m4b-speculative-v0`
- **必须从且仅从**冻结 SHA `c21137bcb86010215c008292f272aacefac175d3` 开始本轮 functional delta。

必须先阅读：
- `docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C9_SEGMENT_SUBENTRY_ARCHITECTURE_DECISION/ARCHITECTURE_DECISION_RECORD.md`
- `.../WEIGHT_SEGMENT_ARCHITECTURE_SPEC.md`
- `.../SUBENTRY_EQUAL_BIT_BUDGET.md`
- `.../FAIR_BASELINE_POLICY.md`
- `.../C10_IMPLEMENTATION_REQUIREMENTS.md`
- C8 model-risk register 与 C3/C4/C7 evidence boundary。

Window A 只读外部参考：
- progress-review branch：`hrl/vm-llm-m4b-c3-progress-review-20260907`
- early C4 SHA：`2e491abec2afb0c745ca26aae0d86f8f35ad096b`

A evidence 只能作为 observability 方法学参考。不得访问 A 私有 worktree/scratch/process，不得把 A 的 cycles/IPC/counter 数值作为 C10-A 参数校准或 pass target。

## 3. 资源与隔离硬边界

Window A 当前仍有 `prefill-paper` simulator-heavy 长跑。C10-A 必须保持低资源。

禁止：
- full Accel-Sim/GPGPU-Sim build；
- full Llama/prefill/decode replay；
- C5；
- 生成/解压/扫描完整大 trace；
- 高并发编译；
- 大规模 hash/copy；
- 操作 Window A/B 的 worktree、scratch、process、priority、cgroup；
- synthetic 12K KV、KV segmentation、M5。

允许：
- source/code 修改；
- Python/static validators；
- 小型 deterministic unit/model tests；
- 若主机无持续 swap、且有明确小目标，可用 **单进程 / `-j1`** 的 translation-only focused compile/test；
- existing tiny unit target 的增量编译。

若某验证只能通过 full simulator build 才能完成，记录为 `DEFERRED_TO_C10B_FULL_BUILD`，不要在 C10-A 偷跑 full build。

普通代码/测试问题必须尽力 debug：`reproduce -> root cause -> repair -> focused rerun`。不要因为第一次 compile/test 失败就把工程问题升级成架构 blocker。

## 4. 全局不变量

1. C10-A mode/profile 关闭时，历史 standard VM/TLB behavior 必须保持原样。
2. 新 candidate 与公平 baseline 必须显式 opt-in；不得静默改变默认配置。
3. 所有用于 Segment 与 conventional paging 对比的受注册 Weight 页必须看到**相同的 VA->PA mapping**。
4. `OBJECT_WEIGHT` 永远不能再决定 Segment eligibility；它只能用于 telemetry。
5. Segment hit 不能凭空 identity-map `ppn=vpn`。
6. lower L2/PTW 只能在 L1 与 Segment 都 miss 后发起。
7. no duplicate side effect / no duplicate completion / no repeated Segment probe on requester retry。
8. 新 telemetry 不得反馈改变 functional behavior。
9. 历史 768-group sub-entry 仅保留为 historical speculative artifact；任何新 official fair profile不得把它叫 equal-cost。

## 5. 建议实施分段与 checkpoint

每完成一个 coherent 子段，做 owner/语义检查、focused test、显式路径 staging 和 checkpoint commit。禁止 `git add .` / `git add -A`。

推荐顺序：

### C10A-0 Admission / baseline lock

- 核对 Framework `04be2899...`、Core `c21137bc...`；
- 确认工作树无未解释修改；
- 记录 baseline file/blob identity；
- 列出预计修改文件；
- 创建 C10-A review pack skeleton 与 input provenance。

本段不修改 functional semantics。

### C10A-1 Real-PA registered mapping backend

实现 C9 v1 注册与映射合同：

- versioned privileged-registration artifact，不复用 object map；
- descriptor/extent 至少包含：`asid, epoch, va_base_vpn, va_limit_vpn, pa_base_ppn, read_only, mapping_class, valid/install outcome`；
- 只描述完整 64KiB 页；partial endpoint page 保守 conventional paging；
- physically non-contiguous allocation 拆成多个 maximal contiguous extents；
- overlap、非只读、无法 pin、extent count > N=8、invalid ASID/epoch 等注册失败必须是**原子全回退**，不能 prefix 部分有效；
- ordinary page/PTE backend 对已注册 Weight pages 必须返回同一个 non-identity-capable PPN mapping，使 conventional path 与 Segment path 可一致性比较；
- 未注册地址/历史 mode 保持旧 backend behavior。

必须有至少一个 non-identity PA test，例如 `VA VPN != PA PPN`。

### C10A-2 Local N=8 Segment tables + lifecycle

按照 C9：

- 每 translation/L1 cluster 一份 local replica；
- nominal `N=8` slots，单 provisioned ASID；
- 一次本地 L1 admission 同拍发起本地 Segment lookup；
- 每 table accept contract = 1 lookup/cycle；
- nominal 无 queue；若实际调用路径能在同 cycle 对同 cluster 多次发起，必须显式统计 port denial/backpressure，并安全保持请求，不得覆盖；
- install/revoke 采用 pinned immutable inference epoch；
- ASID + 16-bit epoch；epoch wrap 需 quiesce/reuse rule；
- install 只有所有 replica 成功后才 valid；revoke 后不得出现 stale hit；
- context mismatch、epoch mismatch、store/atomic/non-read-only/boundary crossing 全部 conventional fallback。

不得用软件 vector 顺序扫描的成本语义冒充硬件 table；即使内部 C++ 容器实现方便，也必须通过固定 N/port/latency contract 暴露硬件模型。

### C10A-3 `HIT_FIRST / MISS_JOIN`

替换 frozen wait-both 行为。

要求：

- L1 与 Segment 并行 launch；
- L1 hit 先到：可立即拥有 requester completion，不应等待慢 Segment；
- Segment hit 先到：可立即拥有 requester completion，并抑制 conventional lower translation；
- L1 miss + Segment pending：等待 Segment；
- Segment miss + L1 pending：等待 L1；
- 只有双方 miss 后才允许 L2 lookup；
- late result 不得二次完成请求；
- 若 late L1/Segment 也提供 mapping，模型应做一致性检查；mapping/permission 不一致是 correctness error/assert，不是 winner heuristic；
- requester PTW retry / completed-delivery 不可重复 launch Segment；
- Segment hit 不填 conventional L1/L2 TLB；Segment miss 按既定路径复用已有 L1 observation。

需要有显式 join-token / owner state 或等价清晰机制；禁止靠隐式轮询产生 repeated probe。

### C10A-4 Parameterized latency / port telemetry

Segment latency 必须参数化，nominal = 10 cycles，mandatory sensitivity points = 5/10/20。

不要在 C10-A 跑 workload sensitivity，但配置/manifest 必须能表达这些点。

至少加入/保留以下 bounded aggregate telemetry：

Segment front-end：
- lookup attempted / accepted；
- port denial/backpressure；
- completion；
- hit/miss；
- reasoned fallback（ASID/epoch/rights/boundary/no descriptor/table overflow 等）；
- configured `Lseg`；
- install/revoke outcome。

Completion ordering：
- L1-first owner；
- Segment-first owner；
- both-miss；
- miss-join wait cycles；
- late-result discard；
- consistency mismatch fault/assert。

Conventional translation：
- 保留 L1/L2 service、MSHR alloc/merge/full/wait、PWQ、walker、PWC、PTE wait/DRAM 等已有 telemetry。

Cross-layer：
- 新 profile 必须继续输出/兼容现有 memory-hierarchy telemetry，能在未来关联 translation source 与 L1D/L2/DRAM/queue outcome。

A early C4 已观察到 paper 相对 generic 在 miss/MSHR-full 下降时仍可能因 PTE memory wait、requester wait 和 memory-queue pressure 更慢。因此 C10-A 不能只证明“TLB miss 少了”；必须确保未来 C10B/C5 可回答压力是否转移到下游 memory hierarchy。

### C10A-5 Fair sub-entry profiles

实现 C9 official accounting/profile：

- standalone fair sub-entry：`G=96`, 16-way, 6 sets, 16 leaves/group, 64KiB-only；
- charged combined Segment+sub-entry：`G=32`, 16-way, 2 sets；
- set/hash 必须基于实际 `G/16` sets，不得仍假定 48 sets；
- `G % 16 == 0` validation；
- base-tag/leaf fill、group replacement、leaf invalidate、empty-group free、ASID/global flush、generation-race stale-fill discard 与 C9 spec 一致；
- timing 不得继续静默继承 80-cycle exact L2 作为“物理事实”；至少将 sub-entry hit/fill latency 参数/manifest 分离或明确标为 provisional model point。

历史 768-group profile可以保留用于 old-evidence reproducibility，但必须带 `HISTORICAL_UNFAIR_SPECULATIVE` 或等价标签，不能被 C10/C5 official arm selector 选中。

### C10A-6 Fair baseline/config plumbing

至少把 C9 F0-F9 的配置/manifest contract 固化到能够被后续 C10B 执行：

- F0 baseline exact；
- F1 G96 sub-entry；
- F2 bit-matched exact；
- F3 charged exact-capacity sweep；
- F4 leaf-capacity diagnostic；
- F5 equal-budget PWC alternative；
- F6 2MiB diagnostic；
- F7 charged Segment + exact；
- F8 Segment + G32 sub-entry；
- F9 bit-matched exact comparator。

C10-A 不要求运行这些 full arms，但必须使每个 arm 的 actual bit budget、capacity、associativity、page-size class、Segment replica count、latency point、port model能进入 manifest/telemetry。

若 F5 physically-interpretable PWC state/port model 实现超出已有小模型可安全完成的范围，不得用旧 128-entry software PWC 冒充 fair F5。应实现必要 state contract 或明确标 `F5_MODEL_IMPLEMENTATION_INCOMPLETE_C10B_BLOCKER`，并继续完成其他独立部分；不要停止整个 C10-A。

## 6. Focused tests / mutations

C10-A 不允许 full regression，但必须尽可能建立低资源定向验证。

至少覆盖：

### Mapping/registration
- non-identity PA；
- contiguous multi-page extent；
- >8 extents atomic fallback；
- overlap reject；
- wrong ASID；
- stale epoch；
- partial endpoint page；
- write/atomic reject；
- conventional PTE mapping == Segment mapping。

### Ordering
- L1 hit before Segment；
- Segment hit before L1；
- L1 miss then Segment hit；
- Segment miss then L1 hit；
- both miss -> exactly one L2 launch；
- late result no duplicate completion；
- mapping mismatch catches error；
- retry does not re-probe Segment。

### Table/lifecycle
- N=8 capacity；
- 9th extent causes atomic registration fallback；
- one accept/cycle contract；
- install/revoke and stale descriptor；
- context switch/ASID mismatch conservative fallback。

### Sub-entry
- G96 = 6 sets；
- G32 = 2 sets；
- sibling leaf fill；
- group replacement；
- leaf invalidate；
- stale fill after generation change；
- 2MiB config rejected for sub-entry v1。

### Fairness/manifest
- old 768-group cannot be selected as official fair arm；
- F0-F9 bit/capacity metadata matches C9 formulas；
- 5/10/20 Segment latency values visible；
- Segment replica bits are charged。

如果已有 mutation/test infrastructure 能低资源运行，应增加能捕获：identity mapping 回归、wait-both 回归、OBJECT_WEIGHT 再次控制 eligibility、unfair 768-group official selection、duplicate lower launch 等错误的 mutation/checker。

## 7. 编译/验证策略

优先级：

1. Python/static schema validators；
2. translation-only/unit test source；
3. 已有小 target 的 `-j1` focused compile/test；
4. full simulator build **DEFER 到 C10-B**。

在每次允许的 focused compile 前检查主机：MemAvailable、swap activity、iowait。若 A 主运行仍健康但系统出现持续 swap-in/out，则立即停止 C10-A compile/test，只保留 code/static work；绝不碰 A。

代码实现完成但 full-link 尚未验证时，状态可以是 `IMPLEMENTED_FOCUSED_VALIDATION_PASS_FULL_BUILD_DEFERRED`，这不是实现失败。

## 8. Review pack

建立：
`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C10A_ARCHITECTURE_MODEL_IMPLEMENTATION_LOW_RESOURCE/`

至少包含：
- `README.md`
- `INPUT_PROVENANCE.tsv`
- `CHANGED_FILES.md`
- `IMPLEMENTATION_MAPPING.md`
- `REGISTRATION_AND_PA_MAPPING.md`
- `HIT_FIRST_MISS_JOIN_IMPLEMENTATION.md`
- `SEGMENT_TABLE_AND_LIFECYCLE.md`
- `SUBENTRY_FAIR_PROFILE_IMPLEMENTATION.md`
- `FAIR_ARM_CONFIG_MATRIX.tsv`
- `TELEMETRY_SCHEMA_DELTA.tsv`
- `FOCUSED_TEST_MATRIX.tsv`
- `RESOURCE_AND_VALIDATION_LOG.md`
- `KNOWN_DEFERRED_C10B.md`
- `FINAL_REPORT.md`

Core 与 Framework 每个 functional/document checkpoint SHA 都要记录。

## 9. 提交纪律

- 明确路径 staging；禁止 `git add .`、`git add -A`；
- 每个 coherent functional segment 后 checkpoint commit，避免一大坨不可回退修改；
- 文档/测试与对应实现一起更新；
- push Framework 与 Core `hrl/vm-m4b-speculative-v0`；
- 不 force push；
- 确认远端 HEAD 与本地一致。

## 10. STOP / 状态

C10-A 最终必须报告一个明确状态：

- `C10A_IMPLEMENTED_FOCUSED_VALIDATION_PASS_FULL_BUILD_DEFERRED`
- `C10A_IMPLEMENTATION_PARTIAL_WITH_NAMED_BLOCKERS`
- `C10A_ARCHITECTURE_CONTRADICTION_REQUIRES_DECISION`

第三项只用于 C9 spec 本身出现无法同时满足的真实架构矛盾；普通代码 bug、测试 bug、工具 bug 不属于该项，必须尽力修复。

即使第一项 PASS，也必须 STOP。不要自动启动：
- full build/regression；
- C10-B；
- C5；
- 任何 full Llama replay；
- 12K/KV segmentation/M5。

本轮目标是：**把 C9 architecture 高质量地落到可审的模型代码，并把重资源验证留给 A terminal 后的下一轮。**
