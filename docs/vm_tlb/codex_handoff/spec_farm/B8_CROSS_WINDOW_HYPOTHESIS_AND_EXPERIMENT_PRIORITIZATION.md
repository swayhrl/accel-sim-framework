# B8：跨窗口假设与最小信息实验优先级

Goal：`B8_CROSS_WINDOW_HYPOTHESIS_AND_EXPERIMENT_PRIORITIZATION`

状态：`READY_TO_EXECUTE / ANALYSIS_ONLY / SPECULATIVE_DIAGNOSTIC`。

## 1. 目的

B7 已经完成 partial farm evidence synthesis；C7 已经完成 speculative candidate opportunity analysis。B8 的目的不是继续增加实验数量，而是把两边已有证据统一成一套可证伪的研究假设，并给出 Window A terminal、资源恢复后最小但信息量最高的实验集合。

本阶段只做证据综合、假设分解和实验设计。不得把 B7 partial、B2 smoke、C4 bounded replay、C7 geometry/opportunity 任一项升级成 full-workload 或正式性能结论。

## 2. 冻结输入

Window B authoritative input：
- Framework branch：`hrl/vm-spec-farm-v0`
- B7 HEAD：`118ead03268612bc61f613811ae232318d98e581`
- B7 handoff：`docs/vm_tlb/codex_handoff/spec_farm/B7_PARTIAL_FARM_EVIDENCE_SYNTHESIS.md`
- B7 review pack：`docs/vm_tlb/review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B7_PARTIAL_FARM_EVIDENCE_SYNTHESIS/`

Window C external read-only input：
- Framework branch：`hrl/vm-m4b-speculative-v0`
- C7 HEAD：`ea07cb0ec6fb3212c18f3435637f055e1296d737`
- C7 report：`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C7_SPECULATIVE_CANDIDATE_OPPORTUNITY_ANALYSIS.md`
- C4 report：`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C4_BOUNDED_REPLAY.md`

B8 可以用 `git show <sha>:<path>`、临时只读导出或远端 fetch 读取 C7 已提交文件；不得切换、修改、清理或写入 Window C worktree/scratch。

## 3. 硬资源边界

B8 禁止：
- 启动 Accel-Sim / GPGPU-Sim；
- 启动任何 B worker；
- 生成新 trace；
- rebuild simulator；
- 扫描完整大 ROI trace；
- 解压/复制大数据集；
- 修改 Window A/C 进程、文件、优先级、scratch；
- 为了补证据运行 missing smoke/full ROI。

允许：
- 读取已提交 TSV/MD/小型 manifest；
- streaming/offline Python；
- 小型统计、表格和文档；
- 读取远端 C7/C4 已提交证据。

如果某项分析需要大 trace 或真实运行才能成立，必须标为 `NEEDS_RUNTIME_EVIDENCE`，而不是在 B8 中补跑。

## 4. 必须建立的研究假设

至少覆盖以下六类，允许在证据支持下新增，但不得为了数量制造假设。

### H1：prefill 与 decode 的 translation/memory 行为存在结构性差异

当前仅有不同比例 partial：prefill 134/692、decode1 96/740。B7 中 exact-adjacent lane 比例和对象组成存在明显差异，但覆盖位置和比例不匹配。

B8 必须区分：
- 已观测 partial 差异；
- coverage bias；
- 真正需要 matched-prefix / matched-kernel-class / full-ROI 才能验证的命题。

### H2：decode 对 PWC/PTW 路径更敏感

当前强 smoke 信号仅有 `PWC-off/decode1`：PTE request 7→8、IPC -1.0583%。

不得把单 kernel 结果写成 full ROI 结论。需要定义最小验证集合，并说明哪些结果会支持/否定该假设。

### H3：Weight Segment 的上限主要受“可识别 Weight traffic 覆盖率”约束

C7 已显示局部 Segment 机制机会 HIGH、C4 有 512 个真实 Segment hit；但 B7 partial 中 WEIGHT lane 占比有限且 UNKNOWN 很高。

必须把以下链条拆开：
`all translation traffic -> classified WEIGHT -> descriptor covered -> Segment hit -> conventional path actually avoided -> end-to-end performance effect`

每层都要列当前证据、未知项和最小观测量。

### H4：Sub-entry 收益取决于 post-L1 sibling-leaf locality，而不是静态 VA 压缩率

C7 静态前缀有较强 group compression opportunity，但 C4 真正到达 L2 的 occupancy 始终 1/16。

必须把：
`raw page locality -> L1 filtering -> L2-arriving leaf/group occupancy -> group fill/replacement -> performance`
分层，并定义未来要记录的动态指标。

### H5：page size / TLB capacity / PWC 等基础 VM 参数可能比当前 speculative candidate 更重要

不能因为已有 Segment/Sub-entry idea 就只做 confirmation experiments。

至少保留对：
- PWC size；
- 2MiB diagnostic；
- VM-disabled / ideal-identity；
- L1/L2 TLB capacity；
- walker/PTW pressure
的反证/替代假设。

### H6：对象归因完整性本身是关键研究风险

B7 partial 中 UNKNOWN 很高。必须判断 UNKNOWN 可能来自：
- object map 不完整；
- trace/address provenance 不足；
- 真正非 Weight/KV traffic；
- phase coverage bias。

不得把 UNKNOWN 自动重新分配给 Weight/KV。若需要运行或新的 runtime instrumentation，列为后续实验，不在 B8 中实现。

## 5. 输出格式：Hypothesis → Evidence → Falsifier → Observable → Minimum Experiment

建立：

`docs/vm_tlb/review_packs/VM_SPECULATIVE_EXPERIMENT_FARM/B8_CROSS_WINDOW_HYPOTHESIS_AND_EXPERIMENT_PRIORITIZATION/`

至少包含：
- `README.md`
- `INPUT_PROVENANCE.tsv`
- `HYPOTHESIS_MATRIX.tsv`
- `EVIDENCE_CONFLICTS_AND_LIMITS.md`
- `MINIMUM_INFORMATION_EXPERIMENT_SET.tsv`
- `RESUME_PLAN_AFTER_A_TERMINAL.md`
- `FINAL_REPORT.md`

`HYPOTHESIS_MATRIX.tsv` 每行至少包含：
- hypothesis_id
- hypothesis
- current_supporting_evidence
- current_counter_evidence
- evidence_scope
- confidence
- falsifier
- required_observable
- minimum_experiment
- estimated_resource_class
- decision_if_positive
- decision_if_negative

## 6. 最小信息实验集合

不要复制 B7 的 1321 项 resume list。B8 必须从中抽取一个小集合，目标是最大化“区分假设”的信息增益。

建议目标规模：约 8–20 个第一批实验/校准项；若证据充分可更少。

每个实验必须说明：
- 它区分哪几个 hypothesis；
- 为什么不能被已有实验替代；
- 预计资源等级；
- 必须等待 Window A terminal 还是只需主机 no-swap gate；
- 成功/失败/无差异分别意味着什么。

第一批应优先考虑 B7 已建议的低资源 decode smoke（PWC finite-32/512/ideal、2MiB diagnostic、VM-disabled、ideal-identity）以及 B1 miner peak-RSS 校准，但允许经过跨窗口证据审阅后调整顺序。

不要把 C5 full replay 塞进第一批低资源 smoke；它应作为候选验证的独立后续层级。

## 7. 反确认偏差要求

最终计划必须至少包含：
- 能证伪 Weight Segment 价值的实验；
- 能证伪 Sub-entry 价值的实验；
- 能发现传统 PWC/TLB/page-size 方案更优的实验；
- 能判断 object attribution 不足导致误判的实验。

若一个实验无论结果如何都只会被解释为“支持当前 idea”，则实验设计不合格。

## 8. 证据标签

所有 B8 输出保持：`SPECULATIVE_DIAGNOSTIC`。

必须保留原标签：
- B7 `REAL_PARTIAL/SMOKE_ONLY/PLANNED_ONLY/STATIC_ONLY/MISSING`；
- C7 `ANALYTICAL_OPPORTUNITY_ONLY`；
- C candidate `SPECULATIVE_CANDIDATE` / `REFERENCE_APPROX_SUBENTRY_16`。

不得生成 `FORMAL`、`FULL_ROI_PASS`、`PAPER_REPRODUCED`、`SPEEDUP_PROVEN` 等升级标签。

## 9. 完成标准

B8 PASS 需要：
1. 输入 SHA/路径全部绑定且可追溯；
2. 六类核心 hypothesis 全部覆盖；
3. 每个 hypothesis 有 counter-evidence/falsifier；
4. 明确区分 partial/smoke/opportunity/runtime；
5. 输出最小信息实验集，不是简单排序所有缺口；
6. 第一批实验数量受控且可解释；
7. 无 simulator/build/trace/new-worker；
8. Window A/C untouched；
9. 提交并 push 后停止。

本轮只负责“决定后续最值得跑什么”。不要在 B8 结束时自动启动任何实验。