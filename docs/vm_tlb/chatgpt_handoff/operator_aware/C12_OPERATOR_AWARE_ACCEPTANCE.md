# C12 Operator-Aware Characterization Acceptance

本文件定义 `C12_OPERATOR_AWARE_CHARACTERIZATION` 的验收条件。该窗口是 C12 的并行只读分析窗口，不是新的 simulator experiment。

---

## A. Branch / worktree isolation

必须满足：

- Framework branch = `hrl/vm-m4b-operator-aware-v0`；
- 工作目录不是正在运行的 C12 worktree；
- Core 不修改；
- C12 live branch `hrl/vm-m4b-speculative-v0` 不 checkout 到本窗口 worktree；
- 不向任何 C12 simulator/scheduler/finalizer 发 signal；
- 不修改 C12 raw evidence。

PASS 条件：独立 worktree，`git status --short` 可解释，所有提交仅包含本窗口分析脚本/文档/review pack。

---

## B. Source identity

每个被分析的 C12 arm 必须：

- terminal status = `PASS`；
- Framework anchor = `d64408a97d76a320a6d49468653d416e33677af8`；
- Core = `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`；
- binary SHA = `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`；
- trace SHA 与 ROI 固定值一致；
- registration SHA 与 ROI 固定值一致；
- raw-log SHA 与 C12 `ARM_STATUS.tsv` / `ARM_RESULTS.tsv` 一致。

PENDING / FAILED_DIAGNOSING / INVALIDATED arm 禁止进入正式 aggregate。

---

## C. Kernel-list / semantic-name alignment

Prefill：

- compute-only entries = 692；
- SHA-256 = `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`。

Decode1：

- compute-only entries = 740；
- SHA-256 = `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`。

必须证明：

- compute-only list 第 i 项对应 simulator 第 i 个 processing-kernel marker；
- 每个 trace 文件恰有一个 embedded semantic kernel name；
- 原始 raw list 中被去除的 32 个 NCCL 不会造成 compute-only index 偏移。

必须输出 `INDEX_ALIGNMENT_AUDIT.tsv`，不能只在文字里声称“应该一致”。

---

## D. Address namespace / Weight layout alignment

必须证明：

- runtime sidecar Weight flat-buffer SimVA base 存在；
- `weight_layout` parameter name/offset/size 完整；
- trace global memory address与 sidecar SimVA 可直接比较，或已有明确的可逆转换；
- parameter ranges 无非法重叠；
- 识别到的 Weight trace refs 能回到已有 Weight object attribution / trace-locality 统计的兼容口径。

如无法证明，禁止使用 `DIRECT_PARAMETER_RANGE`；必须将该部分降级为 unresolved，而不是猜测。

---

## E. Operator classification correctness

每个 compute kernel 必须产生一行 `KERNEL_OPERATOR_MAP.tsv`。

每行至少包含：

- ROI；
- compute kernel index；
- trace filename；
- embedded semantic kernel name；
- operator class；
- operator group；
- evidence kind；
- evidence detail；
- direct parameter names；
- layer id（如可直接解析）；
- classification status。

合法 evidence kind 仅限：

- `DIRECT_PARAMETER_RANGE`
- `DIRECT_SEMANTIC_NAME`
- `MIXED_DIRECT`
- `HEURISTIC_SEQUENCE`
- `UNRESOLVED`

`HEURISTIC_SEQUENCE` 不得混入 formal measured operator aggregate。

---

## F. Coverage transparency

必须输出 `OPERATOR_COVERAGE.tsv`。

至少报告：

- kernel-count direct coverage；
- trace-memory-reference direct coverage；
- unresolved coverage；
- heuristic coverage；
- 若有 exact per-kernel cycles/instructions，再报告 cycle/instruction weighted coverage。

没有最低 coverage 的人为门槛；**高质量 unresolved 优于错误的100%分类。**

---

## G. Metric scope audit

每类指标必须在 `OBSERVABILITY_AUDIT.md` 中标记：

- `EXACT_PER_KERNEL`
- `TRACE_DERIVED`
- `FULL_ROI_ONLY`

禁止：

- 把 full-ROI counter 按比例分摊到 kernel；
- 用 trace reference 数近似 runtime cache transaction；
- 用 kernel 数比例近似 cycle contribution；
- 把 lane refs 当 coalesced requests；
- 把 MSHR-full event 当唯一 blocked request。

---

## H. Conservation / aggregation

对所有 additive、可归属指标：

`sum(operator direct + heuristic + unresolved/unattributed) == same-source kernel/full-ROI total`

若无法精确闭合，必须给出差额和原因。

Rate 必须由聚合后的 numerator/denominator 重算；禁止平均 per-kernel miss/hit rate。

不同 source/unit 的统计不能互相做 conservation。

---

## I. F0 baseline characterization

两个 ROI 的 F0 必须至少形成：

- `F0_OPERATOR_CHARACTERIZATION.tsv`
- `F0_OPERATOR_OBJECT_SUMMARY.tsv`
- `F0_OPERATOR_TRANSLATION_SUMMARY.tsv`
- `F0_OPERATOR_CACHE_SUMMARY.tsv`

至少回答：

- Attention / FFN / Other 的 Weight/KV/UNKNOWN 构成；
- unique 64KiB translation pages；
- 若可 per-kernel，TLB/PTW/PTE/Cache 的 operator attribution；
- 若不可 per-kernel，明确 `FULL_ROI_ONLY`，不伪造。

---

## J. C12 mechanism operator attribution

对 terminal PASS arms 必须覆盖以下公平比较：

- F1 vs F2；
- F5 vs F0；
- F7 L5/10/20；
- F8 L5/10/20；
- F8 vs F7 at same Lseg；
- F8-L10 vs F9；
- Prefill vs Decode。

若 per-kernel cycles exact：允许 operator-level speedup/delta。

若不 exact：只能做 operator-level mechanism activity attribution + full-ROI performance，禁止声称“某算子加速X%”。

---

## K. C12 final dependency

启动时 C12 = 20/22。

本窗口不得等待最后两个 arm 才开始，而应先完成可独立工作。

只有在正式 C12 branch 出现 22/22 terminal PASS + final review pack 后，才可把 Prefill F1 与 F8-Lseg20 纳入 final operator matrix。

若主体分析完成而 C12 仍在运行，合法 interim 状态：

`C12_OPERATOR_AWARE_INTERIM_READY_WAITING_C12_FINAL`

不是 hard blocker。

---

## L. Findings evidence tiers

`PAPER_FACING_FINDINGS.md` 只允许四层：

### `MEASURED_OPERATOR_FACT`

完全由 direct operator classification + exact/trace-derived measurement 支持。

### `SUPPORTED_OPERATOR_SIGNAL`

多项证据一致，但仍不能证明因果。

### `HEURISTIC_ONLY`

依赖 sequence/模型结构推断，不能写成正式结论。

### `UNRESOLVED`

当前数据无法回答。

不得把 replacement correlation、TLB miss减少或 Segment hit 增加直接写成端到端因果。

---

## M. Final review pack

目录：

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_OPERATOR_AWARE_CHARACTERIZATION/`

至少包含：

- `FINAL_REPORT.md` 或 `INTERIM_REPORT.md`
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

Codex回报：

`docs/vm_tlb/codex_handoff/operator_aware/LATEST_REPORT.md`

---

## N. Git discipline

- 禁止 `git add .` / `git add -A`；
- 只 stage 明确路径；
- runtime大文件/raw trace/raw log 不提交；
- 提交分析脚本、轻量表格、review文本；
- push `hrl/vm-m4b-operator-aware-v0`；
- 最终报告列出 commit、changed files、未提交状态。

---

## O. Final states

### PASS

`C12_OPERATOR_AWARE_COMPLETE_READY_FOR_REVIEW`

要求：C12 final 22/22已接入，所有核心审计与输出闭合。

### INTERIM

`C12_OPERATOR_AWARE_INTERIM_READY_WAITING_C12_FINAL`

要求：只缺C12最后依赖，其他工作已尽可能完成。

### HARD BLOCKER

`C12_OPERATOR_AWARE_HARD_BLOCKER_WITH_EVIDENCE`

仅限真正无法证明关键 provenance/index/address semantics，且已穷尽合理排查。

普通工程错误、路径问题、parser bug、部分 kernel unresolved、资源降级均不构成 hard blocker。