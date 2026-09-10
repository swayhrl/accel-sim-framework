# C12 Operator-Aware Characterization Goal

Status: `AUTHORIZED_CONCURRENT_READ_ONLY_ANALYSIS`

本窗口与正在运行的 C12 C5 full-ROI 矩阵并行，但职责完全不同：**只做离线、只读、算子/Kernel 级 characterization，不改变 C12 的任何模拟输入、运行状态或证据。**

目标不是立刻提出新机制，而是回答：

> Prefill / Decode 内部不同算子（Attention projection、Attention core、FFN/MLP、Norm/RoPE/Other）在 Weight/KV/地址翻译/Cache 行为上到底有什么差异？C12 中 Segment/Sub-entry/PWC 的收益或退化主要来自哪些算子？

最终希望把现有“阶段 × 数据对象”结论推进到：

> `推理阶段 × 算子类型 × 数据对象 × 翻译/Cache机制`

---

## 0. 分支、工作树与只读边界

Framework analysis branch：

`hrl/vm-m4b-operator-aware-v0`

该分支基于 C12 checkpoint 07：

`269c274712f4eeaee15d304033a9e6d61b5b3206`

正在运行的正式 C12 branch：

`hrl/vm-m4b-speculative-v0`

**禁止在正式 C12 worktree 中工作。**建议建立独立 worktree：

`/workspace/worktrees/accel-sim-vm-m4b-operator-aware`

Core 保持只读，不创建/切换新的 Core 实验分支：

`57bb71ecd015b6ec0ab32e45b0815e5beaf69172`

冻结 C12 execution identity：

- Framework functional/config anchor: `d64408a97d76a320a6d49468653d416e33677af8`
- Core: `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- linked binary SHA-256: `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`
- Prefill compute-only trace SHA-256: `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f` (692 kernels)
- Decode1 compute-only trace SHA-256: `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc` (740 kernels)
- Prefill registration SHA-256: `6ae0e18cc3bba29871002c4ff1877052489740163424723a845ead45c4a5f4b0`
- Decode1 registration SHA-256: `3dc77c1f348028ba7b8abfef3dc6c4cffa0c9678f003bc23bdc9158d62762b48`

当前 C12 状态：20/22 terminal PASS；剩余 Prefill F1、Prefill F8-Lseg20 正在运行。**本窗口只能消费 terminal PASS arm；不得读取中间性能并将其当正式结果。**

### 严格禁止

- 不得启动 `accel-sim.out` 或任何 C12 simulator replay；
- 不得向 C12 live worker / scheduler / finalizer 发送 signal；
- 不得修改、移动、覆盖 C12 raw log / validation sidecar / trace / config / registration / binary；
- 不得修改 Window A/B；
- 不得修改 Core architecture；
- 不得把 operator heuristic 结果写回 C12 正式 review pack；
- 不得用 filename 猜 semantic kernel name；
- 不得把 `UNKNOWN` 自动改名为 Activation。

如果需要新增分析脚本，只能放在本 analysis branch，并保证对输入只读。

---

## 1. 必须先读的已有证据

### C12 / C11

- `docs/vm_tlb/codex_handoff/spec_m4b/C12_C5_FULL_ROI_FAIR_PERFORMANCE_GOAL.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C12_ACCEPTANCE_MATRIX.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C12_RESULT_SCHEMA.tsv`
- `docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE/ARM_STATUS.tsv`
- `docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE/ARM_RESULTS.tsv`
- `docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE/C12_CACHE_BEHAVIOR_FINDINGS.md`
- `docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE/FAILURE_RETRY_AUDIT.md`

### M4A semantic / metadata foundation

- `docs/vm_tlb/review_packs/M4A_MERGE_PREP/SEMANTIC_KERNEL_CLASSIFICATION.md`
- `util/llm_trace_capture/classify_kernels.py`
- `docs/vm_tlb/llm/METADATA_SCHEMA.md`
- `util/llm_trace_capture/llama_tp_workload.py`

已知 semantic classifier 是从每个 trace 的 embedded `-kernel name = ...` 读取真实 kernel 名：Prefill raw 724 = 692 COMPUTE + 32 NCCL；Decode1 raw 772 = 740 COMPUTE + 32 NCCL。C12 使用的是对应 692/740 compute-only 列表。

### C4 workload characterization foundation

- `docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/TRACE_LOCALITY_OFFLINE.tsv`
- `docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/OBJECT_VM_STATS.tsv`
- `docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/L1D_L2_OBJECT_SUMMARY.tsv`
- `docs/vm_tlb/review_packs/M4C_C3_C4_FINAL_CLOSEOUT/CROSS_LAYER_TRANSLATION_L1D_L2.tsv`
- `util/vm_tlb/analyze_m4c_trace_locality.py`

这些可作为解析/统计方式参考，但**C12 的性能比较只能使用同 ROI 的 C5 F0 作为 baseline**。

---

# 2. OA0 — Provenance 与可观测性审计

在任何 operator 统计前，先建立：

`OBSERVABILITY_AUDIT.md`

必须回答：

1. C12 compute-only trace list 与 semantic compute-only list 是否是同一文件内容/同一 SHA；
2. simulator 的第 `i` 个 processing-kernel marker 是否可以无歧义映射到 compute-only trace list 第 `i` 项；
3. 每个 trace 文件是否仍包含且仅包含一个 embedded semantic kernel name；
4. allocation sidecar 的 Weight flat-buffer base、`weight_layout` parameter offset/size 与 trace 使用的 SimVA 地址命名空间是否可直接比较；
5. C12 raw log 中哪些指标是：
   - `EXACT_PER_KERNEL`：可精确归属到 kernel；
   - `TRACE_DERIVED`：可由离线 trace 精确统计但不是运行时性能；
   - `FULL_ROI_ONLY`：只能保留 full-ROI，禁止强行下钻到 kernel；
6. 是否存在 kernel fusion / multi-parameter access，导致一个 kernel 同时触及多个模型子层参数。

如果第 2 或第 4 项不能证明，**不要猜测映射**。先尽可能从已有 manifest、sidecar、raw trace/header、C4 object-attribution 路径中解决；确实无法证明时记录 evidence 并限制对应分析，不把普通工程定位问题当最终 blocker。

输出：

- `INDEX_ALIGNMENT_AUDIT.tsv`
- `OBSERVABILITY_AUDIT.md`
- `PROVENANCE.md`

---

# 3. OA1 — 建立可审计的 Kernel → Operator 映射

必须以 `C12_OPERATOR_AWARE_OPERATOR_TAXONOMY.md` 为唯一 taxonomy contract。

核心原则：**direct evidence 与 heuristic 必须分开。**

优先证据顺序：

1. `DIRECT_PARAMETER_RANGE`：kernel 的真实 trace 地址落入 `weight_layout` 某个 parameter range；
2. `DIRECT_SEMANTIC_NAME`：embedded kernel name 本身明确指向某类算子；
3. `MIXED_DIRECT`：一个 kernel 有多个互相冲突/跨类的 direct parameter range；
4. `HEURISTIC_SEQUENCE`：只靠执行序列、邻近 kernel 或模型结构推断；
5. `UNRESOLVED`。

### Weight parameter range 方法

从 runtime allocation sidecar 读取：

- flat Weight allocation SimVA base；
- `weight_layout.tensors[].name`；
- `offset_bytes`；
- `size_bytes`；
- shape/dtype。

建立每个参数精确 SimVA range：

`[flat_base + offset_bytes, flat_base + offset_bytes + size_bytes)`

离线扫描每个 compute trace 的全局访存地址，记录它实际触及哪些 parameter range。

**这里做语义分类用的是 trace SimVA 与 runtime sidecar 的 Weight layout；不要把 C5 modeled PA offset 当成 operator semantic 证据。**

### 输出

`KERNEL_OPERATOR_MAP.tsv`

每个 compute kernel 必须有一行，即使最后是 `UNRESOLVED`。

同时输出：

`OPERATOR_COVERAGE.tsv`

至少按 ROI 给出：

- kernel count coverage；
- instruction-weighted coverage（仅当 instruction exact per-kernel）；
- memory-reference-weighted coverage；
- cycle-weighted coverage（仅当 cycle exact per-kernel）；
- DIRECT / HEURISTIC / UNRESOLVED 各自占比。

**不得为了提高 coverage 强行分类。**

---

# 4. OA2 — F0 operator-aware baseline characterization

先只对两个 ROI 的 C5 F0 做算子级 baseline；F0 是本窗口所有性能解释的锚点。

按 operator class / operator group 聚合可用指标。

至少尝试覆盖：

### 执行贡献

- kernel count；
- instructions；
- cycles / ROI cycle share（仅当 `EXACT_PER_KERNEL`）；

### 数据对象

- Weight / KV / UNKNOWN trace references；
- 各自 unique 64KiB pages；
- Weight parameter bytes/ranges touched；

### 地址翻译

- L1 TLB accesses/misses；
- L2 TLB accesses/misses；
- PTW starts；
- PTE requests / L2-only / DRAM；
- translation requester latency；

仅对 raw log 中确实可精确 per-kernel 归属的指标聚合。若某项只有 full-ROI，总结为 `FULL_ROI_ONLY`，不要拆。

### Cache / memory

- Weight/KV 的 L1D/L2 hit/miss；
- reservation fail（单列，不混进 hit/(hit+miss)）；
- L2 replacement，如果能精确归属；
- L2 queue / native memory latency，如果能精确归属。

所有 rate 必须由聚合后的 numerator/denominator 重新计算；**禁止平均 per-kernel rate。**

输出：

- `F0_OPERATOR_CHARACTERIZATION.tsv`
- `F0_OPERATOR_OBJECT_SUMMARY.tsv`
- `F0_OPERATOR_TRANSLATION_SUMMARY.tsv`
- `F0_OPERATOR_CACHE_SUMMARY.tsv`

---

# 5. OA3 — 机制级 operator response

对当前 terminal PASS arm 做 operator-aware 对比；不得消费 PENDING arm。

当前 Decode1 11/11 已闭合，可以先完成 Decode 全矩阵。

Prefill 先分析已有 PASS，等待 C12 最后两个点自然完成后补齐。

必须保留 C12 的核心公平比较：

- F1 vs F2：Sub-entry-only vs near-budget exact；
- F5 vs F0：physical PWC vs F0；
- F7-L5/L10/L20 vs F0：Segment-only latency sensitivity；
- F8-L5/L10/L20 vs F0：Segment+Sub-entry latency sensitivity；
- F8 vs F7 at same Lseg：Sub-entry 在 Segment 上的增量；
- F8-L10 vs F9：低预算下隔离 Segment 增量；
- Prefill vs Decode：阶段差异。

如果 cycles 可以 exact per-kernel：输出各 operator 的 cycle delta / speedup contribution。

如果 cycles **不能** exact per-kernel：禁止构造 operator speedup；改为输出机制活动的 operator attribution，例如 Segment hits、L2/PTW suppressed、subentry hits、translation slow-path reductions，并保持 full-ROI speedup 单独展示。

输出：

- `ARM_OPERATOR_CHARACTERIZATION.tsv`
- `OPERATOR_ARM_DELTAS.tsv`
- `LSEG_OPERATOR_SENSITIVITY.tsv`

---

# 6. OA4 — 重点问题必须显式回答

最终分析至少回答以下问题，不能只给大表：

1. Prefill vs Decode 的 TLB 差异主要由哪些 operator 贡献？
2. Weight 的大翻译工作集主要来自 Attention projection、FFN，还是二者都显著？
3. Decode Weight 近似流式的现象主要集中在哪些 operator？
4. KV L2 高复用主要集中在哪些 Attention 相关 kernel，还是存在其他来源？
5. Segment 的 Lseg=5/10/20 强敏感性，是广泛影响所有 operator，还是集中在少数高频/高时间占比 operator？
6. 为什么大量减少 PTW/L2 TLB miss 后 full-ROI speedup 仍有限：是否因为受益 operator 的 ROI 时间占比有限，还是 downstream/cache/memory 行为抵消？
7. F8 相比 F7 的 Sub-entry 增量究竟在哪些 operator 出现；若几乎没有，需要明确报告。
8. 是否存在 layer-to-layer 重复模式；若存在，可按 layer 聚合，但不要把重复结构自动当成相同性能。

---

# 7. OA5 — C12 final 22/22 的异步接入

本窗口启动时 C12 仍是 20/22。

工作期间可以定期：

`git fetch origin hrl/vm-m4b-speculative-v0`

检查远端正式 C12 是否出现：

`C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`

在等待期间继续完成所有不依赖最后两个 arm 的 OA0–OA4 工作，**不得因为等待而提前停止 Goal**。

当 C12 final 出现后：

- 记录 final C12 source commit；
- 从该 commit 只读读取 final `ARM_STATUS.tsv` / `ARM_RESULTS.tsv` / final review pack；
- 验证 22/22 terminal PASS 及冻结 identity；
- 再补 Prefill F1、F8-L20 operator-aware 结果；
- 不需要把 live C12 branch 合并进 analysis branch 才能读取；可使用 `git show origin/hrl/vm-m4b-speculative-v0:<path>` 或其他只读方式；
- 若确需同步基础 docs，先提交本窗口自己的改动并避免覆盖 C12 review pack。

如果 OA0–OA4 已全部完成而 C12 仍未 final，可先提交 interim review pack，状态：

`C12_OPERATOR_AWARE_INTERIM_READY_WAITING_C12_FINAL`

这不是 hard blocker。继续等待/轮询合理时间并保持已有成果。

---

# 8. 统计与证据规则

1. **不同单位不能混算。** lane-level trace refs、coalesced cache transactions、TLB accesses、PTE requests 都必须保留各自单位。
2. 任何 additive metric 的 operator sum 应回到同一来源的 kernel/full-ROI total；若存在无法归属部分，必须有 `UNATTRIBUTED` 行保持守恒。
3. hit rate / miss rate 必须由总 hit/miss 重算，不平均 kernel rate。
4. heuristic operator labels 不进入 `MEASURED_OPERATOR_FACT`；可以单独做 sensitivity，但必须显式标注。
5. replacement 只说明相关性，不直接写成因果性能结论。
6. `UNKNOWN` 继续保持 UNKNOWN。
7. 不把 current modeled PA 称为真实 NVIDIA hardware PA。
8. C4/A 的数字只作为背景；C12 arm 性能只对同 ROI C5 F0。
9. 不根据当前结果修改 operator taxonomy 以制造更漂亮的机制收益。

---

# 9. 资源策略

该窗口默认只做离线解析/统计，C12 live simulator 优先级更高。

- 初始最多 4-way offline worker；
- 连续确认 memory/io PSI、swap、iowait 健康后可到 8-way；
- 一旦对 C12 tail 造成明显 I/O/内存压力，立即降并发；
- 不获取/抢占 C12 的 simulator ownership；
- 不操作其他窗口进程。

普通脚本、路径、解析、压缩文件、索引错误要主动排查解决，不要直接停下。只有无法证明地址命名空间/索引对应等真正 provenance/correctness 问题，才可形成 hard blocker。

---

# 10. Review pack 与 Codex 回报

本窗口所有正式输出写到：

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_OPERATOR_AWARE_CHARACTERIZATION/`

至少包含：

- `FINAL_REPORT.md` 或 interim `INTERIM_REPORT.md`
- `PROVENANCE.md`
- `OBSERVABILITY_AUDIT.md`
- `INDEX_ALIGNMENT_AUDIT.tsv`
- `KERNEL_OPERATOR_MAP.tsv`
- `OPERATOR_COVERAGE.tsv`
- `F0_OPERATOR_CHARACTERIZATION.tsv`
- `F0_OPERATOR_OBJECT_SUMMARY.tsv`
- `F0_OPERATOR_TRANSLATION_SUMMARY.tsv`
- `F0_OPERATOR_CACHE_SUMMARY.tsv`
- `ARM_OPERATOR_CHARACTERIZATION.tsv`
- `OPERATOR_ARM_DELTAS.tsv`
- `LSEG_OPERATOR_SENSITIVITY.tsv`
- `PAPER_FACING_FINDINGS.md`
- `CHANGED_FILES.md`

Codex handoff 回报写到：

`docs/vm_tlb/codex_handoff/operator_aware/LATEST_REPORT.md`

`PAPER_FACING_FINDINGS.md` 分层：

- `MEASURED_OPERATOR_FACT`
- `SUPPORTED_OPERATOR_SIGNAL`
- `HEURISTIC_ONLY`
- `UNRESOLVED`

每个结论都给出对应表格/原始证据路径。

---

# 11. Goal 最终状态

成功且已接入 C12 22/22 final：

`C12_OPERATOR_AWARE_COMPLETE_READY_FOR_REVIEW`

分析主体已闭合、仅等待 C12 final 两点：

`C12_OPERATOR_AWARE_INTERIM_READY_WAITING_C12_FINAL`

真正无法建立关键 provenance/索引/地址语义：

`C12_OPERATOR_AWARE_HARD_BLOCKER_WITH_EVIDENCE`

**资源等待、普通工程错误、单个 parser bug、某类 kernel 暂时无法分类，都不是 hard blocker。**