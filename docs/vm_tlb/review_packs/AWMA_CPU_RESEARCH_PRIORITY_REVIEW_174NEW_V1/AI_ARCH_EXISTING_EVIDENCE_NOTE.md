# 给 AI-ARCH Discovery 的一页旧证据
只读导航版本 `4e5953c189792dd5a4ac5c13c33ba922b8c2a1e9`。P01/P13 的新广泛论文与资源扩展研究由 Discovery 管理。

| 旧证据 | 可复用事实 | 外推限制/固定入口 |
|---|---|---|
| Q05 translation | 原 10k/50k 固定窗口 ideal identity translation 进度约 +56.55/+76.55%；125 requester = 19 allocation+106 merge | 固定窗口进度不是整 kernel speedup，更非真实 RTX4080 TLB latency；协调 E-A01 / `bb92e5a1559dd7e2b2520e9a7a4937262664512c` 的 characterization |
| Ada cross-calibration | Native/sim 并发形状曾方向或幅度不一致；accepted 10/80 仅 translation overlay 资格 | `8d1f14a32f5538660d74da86ccb03a2c504c5735` / AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/KNOWN_LIMITATIONS.md；不能跨所有资源定量预测 silicon |
| Pre-L1 independent Reduce | 服务130→10，cycles仍7716 | 服务量与时延必须分开；协调 E-A04 指向 frozen review pack，不重跑 |
| L1/M1 scale pair | 原同 function、每 CTA 67,464 指令/514 动态 memory inst，2048 vs256 CTA 为8× aggregate；有限资源反事实的响应不同 | `d116e64b6c2d7faab1babc56c966ff4c1d628904` / AWMA_AI_GPU_RESOURCE_BOTTLENECK_CHARACTERIZATION_V1/CROSS_SCALE_ANALYSIS.md、PROTOTYPE_DECISION.md；只对该 config/trace，旧终态 NO_ACTIONABLE_PROBLEM 不是全领域 negative |
| C16/Native强实现边界 | compiled observer 不完整；FFN双流合法负例；Split-K/GROUP_M 软件吸收局部性损失 | 协调 E-C08/C09/C14、E-A02；profile/stall/逻辑访问不能混成同一时间分母 |

本轮没有 NanoFlow/MPK/资源 scaling 新综述，没有更新协调分支。上表中 E-A01/A04 为沿已审索引继承，L1/M1 的 compact source/report 直接读到；均没有 Native 重算或 simulator 重播。
