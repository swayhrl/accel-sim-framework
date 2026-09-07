# C8：硬件代价与模型风险审计

Goal：`C8_HARDWARE_COST_AND_MODEL_RISK_AUDIT`

状态：`READY_TO_EXECUTE / ANALYSIS_ONLY / SPECULATIVE_CANDIDATE`。

## 1. 目的

C7 已经给出 Weight Segment = HIGH、Sub-entry = MEDIUM 的 analytical opportunity。但 C7 回答的是“有没有机会”，没有回答“这个模拟模型是否对应一个合理、可实现、可公平比较的 GPU translation hardware design”。

C8 的唯一目标是对当前冻结 candidate 做硬件可实现性、代价、公平性和模型风险审计，明确哪些机制已经在模拟器中建模，哪些只是 architecture assumption，哪些必须在未来实现/实验中补齐。

本轮禁止继续增加 candidate 功能，也禁止用分析结果自动修改 Core。

## 2. 冻结输入

Framework：
- branch：`hrl/vm-m4b-speculative-v0`
- C7 evidence HEAD：`ea07cb0ec6fb3212c18f3435637f055e1296d737`
- C7：`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C7_SPECULATIVE_CANDIDATE_OPPORTUNITY_ANALYSIS.md`
- C3：`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C3_WEIGHT_SEGMENTATION_STATE_MACHINE.md`
- C1：`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C1_SUBENTRY_SEMANTICS_AUDIT.md`
- C4：`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C4_BOUNDED_REPLAY.md`

Core frozen implementation：
- repo：`swayhrl/gpgpu-sim`
- branch：`hrl/vm-m4b-speculative-v0`
- SHA：`c21137bcb86010215c008292f272aacefac175d3`

C8 可以只读检查当前 Framework/Core source、配置和已提交文档；不得修改 Core，禁止生成新的 functional commit。

## 3. 硬资源边界

禁止：
- rebuild Accel-Sim/GPGPU-Sim；
- 启动 simulator；
- C5 replay；
- 生成/扫描完整大 trace；
- 新 benchmark；
- synthesis/PPA 重负载；
- 修改 Window A/B worktree/process/scratch；
- 修改 Weight Segment/Sub-entry 实现。

允许：
- `git show` / source inspection；
- 小型 symbolic/analytical cost model；
- streaming 读取小型配置/telemetry；
- 生成 TSV/MD/轻量 Python 脚本。

## 4. Weight Segment：必须审计的硬件问题

### W1 Descriptor representation

从当前实现出发，明确一个硬件 descriptor 至少需要哪些字段：
- address/base/limit 或等价 range 表达；
- address-space / ASID / context identity 是否需要；
- physical mapping information 是否需要；
- valid/protection/page-size/permission 等是否需要；
- 是否真的可以只靠 immutable `[start,end]` 得到正确 physical translation。

不要直接把当前 C++ `range(start,end)` 当成完整硬件 descriptor。

给出符号位宽公式和当前 one-descriptor example 的最低 storage estimate。任何无法从现有架构事实确定的字段明确标为 `REQUIRED_BUT_UNMODELED`。

### W2 Lookup topology / comparator cost

当前软件实现顺序遍历 range vector 不是硬件结构。

至少比较：
- single/few parallel range comparators；
- banked descriptor table；
- hierarchical/prefix/range-indexed lookup；
- per-SM / per-cluster / shared placement。

对每种方案讨论 comparator width/count、fanout、port/throughput、storage replication、lookup latency 和更新复杂度。

不要给没有工艺依据的面积/功耗绝对数；可以给 comparator-bit、entry-bit、lookup-port 等可复核 proxy。

### W3 Throughput and parallel-L1 contract

C3 模型对 eligible request 并行发 L1 + Segment lookup。审计：
- 每周期可能有多少 translation lookup；
- Segment engine 需要什么吞吐才能不引入新 queue/backpressure；
- 10-cycle latency 是否只是 model parameter；
- 如果吞吐不足，需要 queue/arbiter/replication 时当前模拟是否遗漏；
- L1 与 Segment 谁先完成、等待两者的策略是否会伤害 L1-hit request。

给出至少一个 throughput/latency break-even 风险表，不把 C7 的解析 latency lower bound 当成实际 pipeline 证明。

### W4 Correct physical translation risk

重点审当前 `identity-like SimPA` / `ppn = vpn(...)` 的语义。

回答：
- 它在当前 simulator/runtime 假设下为什么能工作；
- 真实 GPU VM 中 Weight VA→PA 是否必然 identity-like；
- 若物理页不连续、迁移、重映射、UVM oversubscription、压缩/保护存在，descriptor 需要增加什么映射信息；
- 是否需要 segment base physical + offset、segment page table、版本/epoch 等。

若当前模型绕过了真实 page-table mapping，必须明确标为 `HIGH_MODEL_RISK`，不能只因为功能测试 PASS 就视为硬件可实现。

### W5 Context / ASID / lifecycle

审计：
- context switch；
- 多进程/多模型；
- ASID；
- address-space reuse；
- allocation/free；
- model load/unload；
- page migration/remap；
- TLB shootdown/invalidation；
- descriptor install/remove/update；
- ordering / stale descriptor prevention。

当前 immutable map 可以作为研究 simplification，但必须写清它依赖的 software/runtime contract。

### W6 Classification provenance

C7/B7 联合结果表明 object attribution completeness 是重要未知项。

C8 需区分：
- simulator object map 用于 telemetry/classification；
- 真硬件如何知道一段 VA 是 Weight；
- driver/runtime/compiler/programmer annotation 的候选接口；
- map 构建、验证、权限、安全问题。

不得假设硬件天然知道 Weight/KV 类型。

### W7 Multi-model / multi-tenant scalability

给出 descriptor count 从 1 增加到 N 时：
- storage scaling；
- comparator/lookup scaling；
- per-context isolation；
- replacement/partition；
- worst-case lookup throughput。

至少分析 1、4、16、64 descriptors 的 symbolic scaling，不需要真实综合。

## 5. Sub-entry：必须审计的硬件问题

### S1 Actual storage accounting

不要只用“16 leaf/group”描述优势。给出当前 reference approximation 相对 exact-page L2 TLB 的 storage accounting：
- group tag；
- 16 leaf valid bits；
- 每 leaf translation/PPN/state bits；
- replacement metadata；
- object-attribution bits若仅 telemetry则不要计入真实硬件；
- 组数/way 数。

区分：`simulator data structure` 与 `minimum hardware state`。

### S2 Lookup and fill complexity

审计：
- base-tag compare；
- leaf select；
- hit critical path；
- existing-group leaf fill；
- group replacement；
- invalidation/shootdown；
- superpage interaction；
- ASID/context。

C1 当前拒绝 2MiB+sub-entry，需要说明这是否只是第一版限制，还是硬件语义根本冲突。

### S3 Capacity/fair-budget comparison

C7 显示 static compression 高，但 full Weight range 仍可能超过 768 groups。

建立公平比较：在相同或近似 storage budget 下，对比：
- exact-page L2 TLB 增容；
- sub-entry group design；
- PWC 增容；
- page-size/2MiB 策略。

这里的目的不是预测性能，而是防止 sub-entry 因“用了更多真实存储位/更复杂 lookup”获得不公平优势。

## 6. Fair-comparison matrix

建立至少以下 candidate：
- current paper/baseline translation hierarchy；
- extra L2 TLB capacity；
- extra PWC capacity；
- larger-page/2MiB diagnostic；
- Sub-entry；
- Weight Segment；
- Sub-entry + Weight Segment。

每个 candidate 给出：
- added state bits / symbolic formula；
- comparators/lookup structures；
- ports/throughput requirements；
- assumed latency；
- software/runtime support；
- current simulator modeled?；
- missing hardware behavior；
- fairness caveat。

不要在没有真实 PPA flow 的情况下给出伪精确面积或能耗数字。

## 7. 风险分类

每项机制/假设必须归类：
- `MODELED_AND_REASONABLE`
- `MODEL_ASSUMPTION_NEEDS_VALIDATION`
- `REQUIRED_BUT_UNMODELED`
- `HIGH_MODEL_RISK`
- `ARCHITECTURE_DECISION_REQUIRED`

并给出：
- 为什么；
- 对当前 C4/C7 结论影响；
- 最小补证据方式；
- 是否必须在正式论文/下一实现轮前解决。

## 8. 必须重点回答的最终问题

1. Weight Segment 目前更像可实现 architecture，还是 simulator shortcut？
2. 哪些最小硬件/软件契约补齐后它才成为可信 architecture？
3. 10-cycle Segment latency/并行吞吐假设是否有足够依据？
4. identity-like translation 是否高风险？如何改成更真实的 mapping model？
5. Sub-entry 在公平 storage budget 下是否仍值得继续？
6. C5 full replay 前有没有必须先修正的 model assumption？如果有，不要直接授权 C5。
7. 哪些问题只影响论文表达，哪些会实质改变性能结论？

## 9. 输出

建立：
`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C8_HARDWARE_COST_AND_MODEL_RISK_AUDIT/`

至少包含：
- `README.md`
- `INPUT_PROVENANCE.tsv`
- `WEIGHT_SEGMENT_HARDWARE_MODEL.md`
- `SUBENTRY_HARDWARE_MODEL.md`
- `FAIR_BUDGET_COMPARISON.tsv`
- `MODEL_RISK_REGISTER.tsv`
- `SOFTWARE_RUNTIME_CONTRACT.md`
- `C5_PRECONDITION_DECISION.md`
- `FINAL_REPORT.md`

可以增加轻量计算脚本，但不得生成/修改 candidate implementation。

## 10. C5 gate conclusion

最终必须选择且仅选择一个：
- `C5_READY_WHEN_RESOURCES_HEALTHY`
- `C5_READY_WITH_EXPLICIT_MODEL_CAVEATS`
- `C5_MODEL_FIX_REQUIRED_BEFORE_REPLAY`
- `ARCHITECTURE_DECISION_REQUIRED`

这只是决定未来 C5 前置条件，不允许 C8 自动启动 C5。

## 11. 完成标准

C8 PASS 需要：
1. Core `c21137bc` 保持完全冻结；
2. 无 simulator/build/trace/full scan；
3. Weight Segment W1-W7 全覆盖；
4. Sub-entry S1-S3 全覆盖；
5. 有公平 budget comparison；
6. identity-like mapping、classification provenance、ASID/lifecycle 被显式审计；
7. 风险有分级、影响和补证据方法；
8. C5 gate 给出明确结论；
9. Window A/B untouched；
10. commit/push 后 STOP 等待独立审阅。

保持 `REFERENCE_APPROX_SUBENTRY_16` / `SPECULATIVE_CANDIDATE`，不得把 analytical audit 升级为正式性能或论文精确复现结论。