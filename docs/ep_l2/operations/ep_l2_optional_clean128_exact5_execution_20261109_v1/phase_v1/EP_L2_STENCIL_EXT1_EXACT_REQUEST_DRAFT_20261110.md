# Stencil EXT1 单点精确申请草案

**状态：待 EP-L2-8／用户明确科学授权；未登记、未启动、未消费。**这是一项新的 Stencil 消融，不属于已关闭的五点预算。申请一个精确点，候选 request ID `EP_L2_OPTIONAL_CLEAN128_STENCIL_EXT1_20261110_V1`，候选 cohort `EP_PERF_CLEAN128_STENCIL_WV_EXT1_20261110_V1`；最终 ID 须在当前 Native registry 中检查唯一性后冻结。

## 科学问题与停止条件

已接受 Stencil EXT0 `4,768,893` cycles、EXT2 `4,786,427` cycles；EXT2 有 56,712 次 Ext retained response 与 66,429 次较少的 lower read，但净慢 17,534 cycles。EXT1 与 EXT2 使用同一扩展硬件及时序，关闭 CLEAN Ext 保留。该唯一新点可区分：`C1−C0` 为扩展硬件迁移包净效应；`C2−C1` 为同硬件下 CLEAN 保留增量；`C2−C0=+17,534` 已确定。若 C2<C1，保留有增益但未抵消迁移包；若 C2>C1，保留本身净有害；相等则无测得净增量。各关系仅对本 Source/输入/配置的确定性模拟成立，不从一次结果推出统计稳健性或物理芯片收益。

## 唯一绑定与最小工程动作

- Source5 Core `3d3887bb2e8d5073d13b0792ff9116834e89fe2f`、Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`、archive SHA256 `7199f3dd5bdba2167186ca6858cd15603997f560660b54e8a1457761f115f48b`、ELF SHA256 `9db48c06ca64e441b5824071f52e0aa0be50374045fbdcef6cdf5d4469182f86`，保持 Source KEEP。不得跨 Source 拼接资格或性能。
- Stencil 输入 SHA256 `bd0309dfeec5745ba97400978c2c5f1413fa9c604376b3dd97e1dd3d5c8cc146`；沿已接受 EXT0/2 的同一 ordered command list：一次初始 HtoD、100 个顺序 kernel、6400 CTA、2,193,446,000 指令，不截断、不新扫巨大 Trace。详细 trace member、命令和 SHA 以已冻结 `BOUND_SPEC_CANDIDATE_STENCIL_WV_EXT2.json` 与正式 accepted bundle 绑定，后续 Spec 必须逐字段核对。
- `WV_ZERO_RO`、`REF32x8_L100`、850MHz、G32×8、L100、四 Bank/P1、Data1168、Base128/WAD128、descriptor512、Line-MSHR128、per-address32；实际 283 项选项取已接受 EXT2 map，仅 `-gpgpu_ep_l2_victim_extension` 从 `2` 改为 `1`。RO、T/M、NI、Trace 采集、Host 中途 copy 与 per-kernel flush 不加入。
- EXT1 复用 A 的三模式实际生产 CPU 资格、现有 Source5/Input/Host/consumer 资格和已接受 EXT0/2 人口与归档证据；只做新 ID、Spec、完整 283 项映射、43 字段 Host/Native pin、一次消费权限及目标资源的必要新绑定。已接受 GEMM EXT1 只支持同 Source 模式工程可执行性，不替代 Stencil 的科学结果。

精确对照锚点：已接受 EXT0 bundle SHA256 `00c90f7c592f8de6042a2b0a3f05cbb4ce89070a8ceda0bda293a7fabccfd396`，EXT2 bundle SHA256 `e160382e7c778fd78decac89b377cdcc89dbe3f6fa705c704561f7ef1aa4c779`。原五点正式回执为 `final_v1/FINAL_REPORT.md`；本草案的任何字段均不能覆盖其冻结结果。

## 成本、执行和验收边界

申请 **1 次 Stencil 完整应用启动、1 次预算消费上限、0 次自动重试/退款**。沿原申请保守估算：一模型一逻辑 CPU，RAM 预估 1 GiB、RSS 硬限 3 GiB、AS 硬限 10 GiB；候选硬墙 48 小时，在新 Spec 冻结。Native 结果估算 48 MiB、硬界 64 MiB；真164 archive 上界 128 MiB；两次独立 Native 恢复每次界 128 MiB，串行共用单个全局 128 MiB 窗口。旧 Stencil 自然墙钟约 3.714 小时仅作排期参考，新点实际时长未知。预算放开不放开实时 CPU/RAM/cgroup/Native 5 GiB 有效底线、其他 owner 承诺、真164和 cap10 准入。

仅唯一 EP-L2 Main 可在**明确批准此单点后**核对当前 registry/epoch、确认不存在同点登记/运行、冻结 Spec/Host/Native pin，按原流程登记一次并做实时准入。自然结束后验收实际 Source/ELF/输入/283 选项、完整人口、排空、lossless raw、逐 kernel/slice 守恒，再做真164全成员 SHA 归档及两个不同 Native 目标的独立完整恢复，发布同 Source 三点比较。若失败则保留原失败和一次消费记录，依原合同处理，不自动重试。不得新建第二 dispatcher，亦不动其他 owner 账本或 Source。
