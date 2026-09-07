# C10-A Acceptance Matrix

Goal：`C10A_ARCHITECTURE_MODEL_IMPLEMENTATION_LOW_RESOURCE`

本矩阵是 C10-A 的硬完成标准。任何一项没有满足时，不得把本轮标为完整 PASS。

| ID | 要求 | PASS 标准 | 失败/未完成时处理 |
|---|---|---|---|
| A0 | 起点锁定 | Framework 从 `04be2899...`；Core functional delta 从 `c21137bc...` | provenance 不符则停止 functional 修改并修正起点 |
| A1 | Window A 隔离 | A worktree/scratch/process/priority 全部 untouched | 立即停止 C10-A workload，先恢复隔离 |
| A2 | 低资源边界 | 无 full build/full replay/C5；focused compile 仅单进程且通过资源 gate | 重验证 defer C10-B |
| M1 | Real-PA mapping | Segment 能返回 non-identity PA；registered conventional path 对相同页返回一致 PPN | 不得保留 `ppn=vpn` shortcut |
| M2 | Trusted registration | eligibility 来自 versioned privileged registration，不来自 `OBJECT_WEIGHT` | object map 必须降为 telemetry-only |
| M3 | Atomic registration | invalid/overflow/overlap/pin failure 不产生 partial live descriptor | 修复 install transaction |
| M4 | N=8 local table | 每 translation cluster local N=8；单 provisioned ASID；manifest 可见 | 不得用 unconstrained vector 冒充 |
| M5 | Port contract | 1 accept/cycle/table；冲突/denial/backpressure 有显式行为/telemetry | 不得静默吞请求或覆盖 |
| M6 | Lifecycle | ASID+epoch；install/revoke；stale descriptor 不可命中 | stale hit 是 correctness failure |
| O1 | HIT_FIRST | L1 hit 可先完成，不因慢 Segment 无条件等待 | wait-both 回归必须被测试捕获 |
| O2 | Segment-first | Segment hit 可先完成并阻止 conventional lower translation | Segment hit 后 lower launch 是失败 |
| O3 | MISS_JOIN | lower L2 只在 L1 与 Segment 均 miss 后启动 | duplicate/early lower launch 是失败 |
| O4 | Exactly-once | late result/retry 不产生重复 completion/Segment probe/side effect | 必须 root-cause 修复 |
| O5 | Mapping consistency | L1/PTE 与 Segment 都提供 mapping 时一致；不一致 assert/error | 不得以 winner policy 隐藏 mismatch |
| L1 | Latency points | Segment 5/10/20 可配置且进入 manifest；10 只作为 nominal | 不得 hard-code 唯一 10cy 架构事实 |
| T1 | Segment telemetry | accept/deny/hit/miss/fallback/Lseg/install/revoke 可审 | schema gap 必须补齐 |
| T2 | Ordering telemetry | L1-first/Segment-first/both-miss/join-wait/late discard/mismatch 可审 | schema gap 必须补齐 |
| T3 | Conventional waits | MSHR/PWQ/walker/PWC/PTE wait/DRAM 等已有关键 telemetry 保持 | 不得为了候选简化而删弱 |
| T4 | Cross-layer continuity | 新 profiles 与现有 L1D/L2/DRAM/queue structured telemetry 兼容 | 若只能 C10B 验证，需静态 schema 证明 + deferred 标记 |
| S1 | Standalone fair sub-entry | official G=96；16-way；6 sets；64KiB-only | 768-group 不得作为 official equal-cost |
| S2 | Combined fair sub-entry | official Segment+sub-entry G=32；16-way；2 sets | 其它 G 必须明确非官方诊断 |
| S3 | Index correctness | set count 基于 G/16，G%16 验证 | 不能继续固定 48 sets |
| S4 | Fill/invalidate | sibling fill/group replace/leaf invalidate/empty free/generation race 语义闭合 | focused test 失败必须修复 |
| F1 | Fair arm metadata | F0-F9 budget/capacity/associativity/page/replica/latency/port 信息进入 config/manifest | 缺一项则不能称 execution-ready |
| F2 | Historical unfair arm guard | old 768-group profile 标 historical/unfair，官方 selector 不可选 | 必须有 validator/test |
| F3 | PWC fairness honesty | F5 未实现时必须明确 blocker，旧 128-entry software PWC 不得冒充 equal-budget | 可 partial，但必须命名 blocker |
| V1 | Mapping tests | non-identity/overflow/overlap/ASID/epoch/boundary/access/conventional-consistency 覆盖 | 未覆盖不得 PASS |
| V2 | Ordering tests | L1-first/Segment-first/miss-join/both-miss/late/retry/mismatch 覆盖 | 未覆盖不得 PASS |
| V3 | Table tests | N=8/9th fallback/port/lifecycle/context 覆盖 | 未覆盖不得 PASS |
| V4 | Sub-entry tests | G96/G32/sibling/replacement/invalidate/stale/2MiB reject 覆盖 | 未覆盖不得 PASS |
| V5 | Static/focused validation | Python/static PASS；可用时 focused unit compile/test `-j1` PASS | full link 可 defer C10B |
| P1 | Checkpoints | coherent implementation 分段有 checkpoint commit；明确 staging | 不得 `git add .` / `-A` |
| P2 | Review pack | 规定 C10-A review pack 文件齐全、SHAs 可追溯 | 补齐后再 closeout |
| P3 | STOP | C10-A 完成后没有启动 C10-B/C5/full replay | 启动即越界 |

## 允许的最终状态

### `C10A_IMPLEMENTED_FOCUSED_VALIDATION_PASS_FULL_BUILD_DEFERRED`

仅当：
- M/O/L/T/S/F 核心实施项完成；
- focused/static tests 通过；
- full build/regression 明确留给 C10-B；
- 没有未命名的 correctness blocker。

### `C10A_IMPLEMENTATION_PARTIAL_WITH_NAMED_BLOCKERS`

用于：
- 某个明确独立子项（例如 F5 physically-accounted PWC model）尚未完成；
- 已完成部分有清楚验证；
- blocker、影响、下一步均被命名；
- 不允许把 partial 描述成 full PASS。

### `C10A_ARCHITECTURE_CONTRADICTION_REQUIRES_DECISION`

仅用于：
- C9 已冻结的两个或多个 architecture invariants 无法同时满足；
- 不是普通 coding/test/tool 问题；
- 必须给出最小复现和选项。
