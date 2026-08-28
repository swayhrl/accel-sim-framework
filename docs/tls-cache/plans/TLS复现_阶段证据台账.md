# TLS-Cache 复现：阶段证据台账

更新：2026-08-23（Asia/Shanghai）。本台账区分“有当前可检查证据的已完成阶段”
与“尚不能据此宣称完成的 P9 公开规模结果”。它不是论文结果表。

当前实现来源：framework `hrl/tls-cache-repro-v0@4d6c8a6`，core
`hrl/tls-cache-gpgpusim-v0@e50e733edd9d`。framework worktree 除用户拥有的
未跟踪 `.agents/` 外无本轮未提交改动；本台账与 raw run data 位于主
Accel-Sim worktree，版本身份仍以该双仓记录为准。

| 阶段 | 当前结论 | 直接证据 |
|---|---|---|
| P0 | 已验证 | `p0_verification.md`：双仓 baseline、release/debug 构建、CFD 完整 drain 的重复 golden hash。 |
| P1 | 已验证 | `p1_verification.md`：default-off 与 P0 关键整数统计完全一致，非法 TLS 配置显式拒绝。 |
| P2 | 已验证 | `p2_verification.md`：拓扑、0/1/2 hop、first-touch/frozen map 和完整 physical mapping 单元测试。 |
| P3 | 已验证 | `p3b_verification.md`：有限双向 ring、方向资源和 CFD 完整 drain；P3A 的有界 smoke 仅作集成证据。 |
| P4 | 已验证 | `p4_verification.md` 和 `verify_p4_observer_off.sh`：observer 开关下既有 timing/cache/ICNT/fabric 整数一致，ICL 可从原子计数重算。 |
| P5 | 已验证 | `p5_verification.md` 与 `verify_p5_shared.sh`：endpoint/MHSR/xbar/fabric 守恒及 CFD 自然收尾。 |
| P6 | 已验证 | `p6_verification.md` 与 `verify_p6_l15.sh`：RDC local-home 禁止、容量边界、等待者和 fabric 排空。 |
| P7 | 已验证 | 本次复跑 `verify_p7_tls.sh hw_run/tls-cache-p7/tls-cfd-drain-v4.out` 返回 PASS；验证 CL1/RL1 outcome、remote-only RL1、xbar/fabric/stage 排空。 |
| P8 | 已验证 | 本次复跑 `verify_p8_suite.sh`（P3/P5/P6/P7 CFD drain + CFD/2MM/frozen CUTLASS 窄带宽压力）返回 PASS。注意非 frozen CUTLASS 输入没有远端 fabric traffic，不能代替 frozen 压力输入。 |
| P9A | MINI 已完成，结果仅作机制矩阵 | `hw_run/tls-cache-p9/matrix-v4/P9_completion.md`、32 条 4×8 MINI raw logs、summary/paired CI/provenance。2026-08-23 再次执行 schema-v4 verifier 后，summary 完整性检查为 32/32 rows、schema-v4、all completed。不得与论文 4×64 数值直接比较。 |
| P9B | **进行中，尚未完成** | public-v1 的 CFD 097K、SRAD trimmed 与 PolyBench GEMM 均已完成 4 mode × dynamic/frozen 的 8 条自然结束样本，并分别通过严格子矩阵门。FDTD2D 的 dynamic 4 mode 已于 2026-08-25 启动、尚未结束；其 frozen-hash 对照尚未启动。因此不能把已有三个应用的通过扩大为完整 P9B。旧 `paper-v4` 的 4×64 TLS dynamic/frozen 仅使用 1-cycle、32 B/cycle ring，保留为资源形状/回归证据；不满足公开描述重建的 32-cycle/768 B-cycle 主配置。 |

## 正在推进的 P9 闭环

1. ICL 候选筛选已完成并生成排名：SHOC GEMM 0.726679、Mars SS 0.724581、
   SORT 0.499642、SPMV 0.059273、ST2D 0.016320、FFT/REDC 0。SS 使用经
   manifest 约束的 kernel-only-v4 list；ST2D 的 wrapper 历史失败后以
   `posthoc-verified` provenance 封存，明确标记原始二进制 hash 未记录。
2. TLS-PAPER public-description reconstruction v1 已完成 TLS-CFD 有界 smoke：
   `mgpu-*-paper-public-v1.config` 使用 4×64、1 GHz、32 cycles/hop、768
   B/cycle/有向链路；未公开的 xbar、DRAM、地址映射和带宽口径在
   `assumptions.yml` 中明确标注。公开配置 smoke、单样本 runner 和 fail-fast
   矩阵验证/汇总接口已具备；后者不会启动或等待模拟。首次 128-set LLC
   smoke 因 IPOLY 不支持 128 sets 而在 kernel 前断言，失败证据保留；修正为
   64 sets × 32 ways（仍为 256 KiB/slice）后，10k-cycle TLS smoke PASS
   （8.91 s，peak RSS 1.18 GiB）。CFD 的 dynamic/frozen 各四个 matched
   mode 已全部自然结束，`verify_p9_paper_public_matrix.sh ... cfd_097k` 返回
   PASS；TLS frozen 的 read service、latency histogram 和三个 timestamp
   counter 均守恒。该小矩阵是合格的单应用结果，不替代完整 P9B 汇总。
   2026-08-23 静态审计已修正 public-v1 的 LLC 容量：Baseline/Shared/TLS 为
   16 × 256 KiB = 4 MiB/chip；L1.5 为 2 MiB LLC + 2 MiB RDC。smoke/matrix
   verifier 会拒绝不符合此容量契约的输出。
   同日还固定并校验论文公开的 Local-Xbar 选项（40-B flit、512-entry
   in/out buffers、iSLIP）。当前承载层为 aggregate 256×64 Local-Xbar，而非
   四个独立 64×16 arbiter；此重建限制已在 `assumptions.yml` 标注，不能在
   结果解释中隐去。
3. SRAD trimmed 的 8 条 matched mode/placement 样本也已自然结束；在 `4d6c8a6`
   将 verifier 改为单次索引最终统计后，`verify_p9_paper_public_matrix.sh ...
   srad_trim` 在 30 秒内返回 PASS。GEMM 的 eight-row matrix 已全部自然结束并由
   `verify_p9_paper_public_matrix.sh ... polybench_gemm` 返回 PASS；其 partial summary、
   strict gate transcript、raw logs 与资源记录已保存在 public-v1 matrix 目录。冻结
   页放置的四 mode 均约 9.24--9.43M cycles、IPC 78--80，明显区别于 dynamic，须以
   page-map/remote-path 统计解释，不可直接当作 TLS 优劣结论。
4. P9 matrix verifier 的字段读取已在 `e5272f3` 修正：它现在会去掉等号前的空格，
   可正确读取 `TLS_FABRIC_* = value` 的最终守恒统计；`4d6c8a6` 进一步将校验改为
   先建立最终统计索引再执行不变量检查，不改变“最终重复计数取最后值”的语义。
5. 因此不能把 P9A 的 MINI completion artifact、已通过的 CFD/SRAD/GEMM 子矩阵或旧 P9B 的
   1-cycle 控制当作 P0–P9 全部完成的证据。

## 结论口径

机制阶段 P0–P8 有可回查的测试和日志证据；最终目标仍依赖 ICL 筛选完成及
P9B public-v1 的 smoke、自然收尾的 matched workload 结果和结果管线。只有这些
产物齐备并通过相应 verifier 后，才可宣称 P0–P9 闭环完成。
