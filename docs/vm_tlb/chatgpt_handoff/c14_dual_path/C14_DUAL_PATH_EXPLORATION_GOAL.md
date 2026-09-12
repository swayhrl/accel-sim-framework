# C14 dual-path exploration — Goal

状态：`AUTHORIZED_TO_START`

## 0. Goal

在不等待 C13 repaired full-ROI 全部结束的前提下，并行推进两条互相独立、都能在未来 4 小时内产生实质成果的预研路线：

- **Path P：Segment-positive continuation**
- **Path N：translation-criticality pivot**

C14 不是新的 paper-primary matrix，不允许把 microdiagnostic 结果升级成 full-ROI 结论。

最终目标不是“跑越多越好”，而是让用户回来时至少拿到：

1. 两条路线各自的 source-level root-cause map；
2. 两条路线各自最小 instrumentation / prototype；
3. 一组短时、可并行的 exploratory microdiagnostics；
4. 明确的 go/no-go 判据；
5. 若 C13 中途推进到 final/near-final checkpoint，自动把新证据纳入路线判断；
6. 下一阶段最多 3 个值得跑的 full-ROI 实验建议和预估成本。

## 1. Strict isolation

### Framework

C14 只写：

`hrl/vm-m4b-c14-dual-path-explore-v0`

### Core

Path P 只写：

`hrl/vm-m4b-c14-segment-positive-v0`

Path N 只写：

`hrl/vm-m4b-c14-criticality-v0`

### 禁止写入

- `hrl/vm-m4b-c13-diagnostics-v0`
- C13 D worktree
- `/workspace/vm-m4b-c13-diagnostics/results/`
- C12 formal branches / review packs / raw logs
- Operator-aware accepted branch

允许只读使用它们的 evidence。

## 2. C13 synchronization rule

C14 启动时读取 C13 当前 checkpoint；之后只在以下时点最多 fetch 一次：

- Path P source audit结束；
- Path N instrumentation设计结束；
- microdiagnostic结束；
- C14 final synthesis前。

不要高频轮询。

如果 C13 在 C14 执行期间出现：

- EQ1 PASS；
- EQ2 PASS；
- repaired H1/H2/H3 terminal；
- Path B correctness failure；

C14 必须记录到 `C13_DEPENDENCY_SNAPSHOT.md`，并根据证据调整“推荐优先级”，但**不得回写 C13**。

## 3. Phase 0 — common source audit

先独立梳理 C12 Core `57bb71...` 的翻译请求数据流：

`requester/L1-TLB → Segment candidate path → L2-TLB → MSHR/PTW/PTE → completion`

必须回答：

1. Weight Segment 与 L1/L2 exact lookup 的启动先后关系；
2. 哪些工作是 parallel、哪些可以 cancel/suppress、哪些已经无法撤销；
3. Segment hit 前后会不会已经消费 L2 port / lookup slot / MSHR；
4. requester latency计时起止；
5. translation completion 如何反馈到 memory pipeline；
6. 当前已有 telemetry 能观察什么，缺什么。

输出：

- `COMMON_TRANSLATION_PATH_MAP.md`
- `CURRENT_SEGMENT_RACE_TIMELINE.md`
- `OBSERVABILITY_GAP_MATRIX.tsv`

该阶段只读，不改 Core。

## 4. Parallel phase — P / N 同时推进

完成 Phase 0 后，允许在同一个 Codex Goal 内并行使用两个独立 Core worktree。

### Path P

严格执行 `C14_PATH_P_SEGMENT_POSITIVE.md`。

### Path N

严格执行 `C14_PATH_N_CRITICALITY_PIVOT.md`。

两个 Path 可以并行编译、跑 unit tests、跑 microdiagnostic，但不得共享 build tree / output directory。

## 5. Exploratory microdiagnostics

只允许 `C14_MICRODIAGNOSTIC_MATRIX.tsv` 中定义的探索点。

统一规则：

- 不修改 frozen trace bytes；
- 可以创建新的轻量 kernelslist / window list，但必须记录 SHA；
- micro ROI 与 full ROI 结果严格隔离；
- 任何结果都标 `EXPLORATORY_MICRODIAGNOSTIC`；
- 不计算相对 C12 full-ROI 的 paper speedup；
- 主要用于确认 instrumentation 是否工作、机制方向是否值得 full-ROI。

## 6. Resource policy for next ~4 hours

用户当前观察到：

- 512 logical CPUs；
- CPU average use约 9.5%；
- load average约 48；
- memory约 169/377 GiB；
- 主机明显 GREEN。

C14 可较积极使用剩余资源，但 C13 D 优先级更高。

### 初始

- C14 micro simulator：4-way；
- build/test可并行；
- 不限制轻量静态分析worker。

### 升到 8-way micro simulator

连续 3 个资源窗口满足：

- CPU idle >= 60%；
- MemAvailable >= 128 GiB；
- memory PSI full <= 1%；
- IO PSI full <= 2%；
- iowait <= 10%；
- swap-in/out <= 4 MiB/s；
- C13 simulator均正常推进。

### 最多 16-way

仅针对**短 microdiagnostics**，且：

- CPU idle >= 50%；
- MemAvailable >= 128 GiB；
- 已知单 micro arm RSS 后按 `1.5P+2GiB` 估算；
- 不影响 C13 D progress。

禁止 C14 自行启动新的 full-ROI matrix。任何 full-ROI建议只写入 handoff，等待用户回来审定。

## 7. Evidence language

统一分层：

- `SOURCE_VERIFIED_FACT`
- `EXPLORATORY_MICRODIAGNOSTIC`
- `SUPPORTED_CANDIDATE_SIGNAL`
- `DESIGN_HYPOTHESIS`
- `C13_DEPENDENT_PENDING`
- `UNRESOLVED`

严禁：

- micro结果写成 full-ROI；
- correlation写成causality；
- 用尚未EQ promotion的 C13 Decode结果当正式fact；
- 用旧 mode=1 C13结果指导机制优劣；
- 为了让某一Path看起来更好而选择性丢掉negative结果。

## 8. Final outputs

生成：

`docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C14_DUAL_PATH_EXPLORATION/`

至少包含：

- `FINAL_REPORT.md`
- `C13_DEPENDENCY_SNAPSHOT.md`
- `COMMON_TRANSLATION_PATH_MAP.md`
- `CURRENT_SEGMENT_RACE_TIMELINE.md`
- `OBSERVABILITY_GAP_MATRIX.tsv`
- `PATH_P_REPORT.md`
- `PATH_P_PROTOTYPE_AUDIT.md`
- `PATH_N_REPORT.md`
- `PATH_N_INSTRUMENTATION_AUDIT.md`
- `MICRODIAGNOSTIC_STATUS.tsv`
- `MICRODIAGNOSTIC_RESULTS.tsv`
- `GO_NO_GO_MATRIX.tsv`
- `NEXT_FULL_ROI_EXPERIMENTS.md`
- `CHANGED_FILES.md`

handoff：

`docs/vm_tlb/codex_handoff/c14_dual_path/LATEST_REPORT.md`

## 9. Stop conditions

正常：

`C14_DUAL_PATH_EXPLORATION_COMPLETE_READY_FOR_REVIEW`

如果一个 Path 技术上不可行：

不要终止总 Goal；把该 Path 标为 `NO_GO_WITH_EVIDENCE`，继续另一个。

只有两个 Path 都因同一个真实 correctness/provenance blocker无法推进，才允许：

`C14_DUAL_PATH_EXPLORATION_HARD_BLOCKER_WITH_EVIDENCE`

普通 build/test/path/resource问题主动解决，不等待用户。