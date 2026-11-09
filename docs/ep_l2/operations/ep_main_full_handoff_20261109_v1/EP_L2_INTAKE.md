# EP-L2 Victim 五点结果接收与审查

整理日期：2026-11-09。**状态更新：**最新完整交接 `08fc797a44d24906e8e8b08ef8a95cb25a288e64` 及本轮只读现场核对均显示五点批准/登记/消费为 0、未见活动模型；旧聊天“在执行”不能继续当作当前事实。接管结论见 [Main 回执](EP_L2_MAIN_TAKEOVER_20261109.md)。下表仍是**已发布精确申请中的预期身份**，不是实际启动、完成或接受回执；五点保持待授权。

## 固定范围与 Source 锚点

固定申请：[精确申请 JSON](https://github.com/swayhrl/accel-sim-framework/blob/ea480a05fb32eeb6b88dd1d8be1b0b9c89eb8526/docs/ep_l2/operations/ep_l2_next_cost_aware_architecture_20261107_v1/agent_d/FINAL_EXACT_EXPERIMENT_REQUEST.json)、[申请说明](https://github.com/swayhrl/accel-sim-framework/blob/ea480a05fb32eeb6b88dd1d8be1b0b9c89eb8526/docs/ep_l2/operations/ep_l2_next_cost_aware_architecture_20261107_v1/agent_d/FINAL_EXACT_EXPERIMENT_REQUEST.md)；工程主报告是同提交 `main/EP_L2_NEXT_COST_AWARE_ARCHITECTURE_AND_EXACT_EXPERIMENT_REQUEST.md`。本机早期状态来源为 `D:/Codex/Handover/projects/EP-L2.md` 和 `sources/imported/EP_L2_HANDOFF_2026-11-09_OPTIONAL_CLEAN128_ACTIVE_V1.md` §3、§5；其“在执行”叙述已由较晚完整交接及本轮现场核对修正。固定申请与当前台账均没有五点启动记录。

五点预期共用 **Source5**：Core `3d3887bb2e8d5073d13b0792ff9116834e89fe2f`；Framework 编译身份 `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`；vendor pybind11 `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`；ELF SHA256 `9db48c06ca64e441b5824071f52e0aa0be50374045fbdcef6cdf5d4469182f86`；静态库 archive SHA256 `7199f3dd5bdba2167186ca6858cd15603997f560660b54e8a1457761f115f48b`。它是独立 A 谱系，不能与 C 的 Core/Framework 拼接。旧 Source78 或旧 ELF 的 WV 结果不能替代本轮 EXT0。

共用条件：`WV_ZERO_RO`、G32×8、64 slices、128B line、DRAM 850MHz、L100、FR-FCFS128、Data1168/slice、四 Bank/P1、Base/WAD128、descriptor512、Line-MSHR128、每地址32。唯一新增选项是 `-gpgpu_ep_l2_victim_extension`；完整 283 项以固定申请和**实际** echo 对齐。每点一次，GEMM 三点与 Stencil 两点独立准入，不能由某点完成推断另一点状态。

| Family | 精确 point ID | EXT | 预期 full config canonical SHA256 | 用途 |
|---|---|---:|---|---|
| `A_GEMM_OPTIONAL128_CONTROL3_V1` | `NEXT_A_OPTIONAL128_GEMM_WV_EXT0_V1` | 0 | `cc63bb1dcff5a448cd44005f1dc69574f2c4fd3427c005867e944c1931bd03ee` | 新 Source 的 Base128 参考 |
| 同上 | `NEXT_A_OPTIONAL128_GEMM_WV_EXT1_V1` | 1 | `62511846afa946d0d0ff60cac3d63c706d648a1e9d5c1477b3ef208b96856861` | 扩展硬件/时序付费，保留关闭 |
| 同上 | `NEXT_A_OPTIONAL128_GEMM_WV_EXT2_V1` | 2 | `7ad25f970264bca94d26ffe0239b20124f19df8a26750f5199ec8274458ca2c1` | 同扩展硬件，optional CLEAN 保留开启 |
| `A_STENCIL_OPTIONAL128_NET2_V1` | `NEXT_A_OPTIONAL128_STENCIL_WV_EXT0_V1` | 0 | `8c333e8d75895b48b63ed7a47c78974f47527f4086001feea6b1d33cb30e315b` | 新 Source 的 Base128 参考 |
| 同上 | `NEXT_A_OPTIONAL128_STENCIL_WV_EXT2_V1` | 2 | `d56c8681ffac8022020baadf57f59b0990893c37c91f2c8ad42af55e906ff8c6` | 完整扩展结构的应用净效果 |

输入锚点也须逐点绑定：GEMM input identity SHA256 `140f6ed3a5cdb1d7183cd4d2acc37b086224a054893ef12d990fdb2d5ea3659b`，literal/canonical ordered commands SHA256 分别为 `fd9a9430fc95eb0af4c73b9710db271f8e32bff4ea2f5dd08a4e8e17c9b02057` / `7e2e13f4078ae885562cfc01190eaed71eb775ed07fa38c77c405a1d1f95babb`，3 次 initial HtoD＋1 kernel，739,246,080 instructions、1,024 CTA。Stencil input identity SHA256 `bd0309dfeec5745ba97400978c2c5f1413fa9c604376b3dd97e1dd3d5c8cc146`，literal/canonical ordered commands SHA256 分别为 `80dad07812b3b36228930b6f29e5a517b1c2e379608d17ee349b87d6eddc2ead` / `cf4aa2e310207d1de454a5e459c83b98655b0e06ca5d585e0ed7e5a622d3a9fc`，1 次 initial HtoD＋100 kernels，2,193,446,000 instructions、6,400 CTA。具体命令、各 kernel 身份及 SHA 仍以固定 JSON 与最终绑定核对；程序名本身不够。

## 结果怎样回答问题

只对**同输入、同 Source/ELF、同完整配置背景、同命令人口且两端均被接受**的点计算比较。设 GEMM 完整应用 cycles 为 `G0/G1/G2`，Stencil 为 `S0/S2`：

| 比较 | 计算 | 能回答的问题 | 不能推出 |
|---|---|---|---|
| GEMM EXT0→EXT1 | `G1-G0` | 两段查询、选择及扩展硬件的迁移周期代价 | 保留收益 |
| GEMM EXT1→EXT2 | `G1-G2` | 同扩展硬件下开启 CLEAN 保留节省的周期 | 无硬件成本的纯算法收益 |
| GEMM EXT0→EXT2 | `G0-G2`；降低比例 `(G0-G2)/G0`；加速比 `G0/G2` | 含新增 metadata/端口/时序的整体净效果 | 等硬件纯策略效果 |
| Stencil EXT0→EXT2 | `S0-S2`；降低比例 `(S0-S2)/S0` | 持续复用、跨 kernel 输入上的完整净效果 | 独立保留贡献或 EXT1 开销；本批没有 Stencil EXT1 |

需要同时看完整 cycles、Base/Ext 实际服务、资源与人口/drain。Ext query 不是 response，response 不是避免 DRAM 的次数；issued 字节不是完成带宽。计数改善而 cycles 未改善应作为负结果保存。额外 128 项是 optional CLEAN 身份 metadata，复用 Payload，不新增 Data；保守 row 逻辑位约 460 KiB/64 slices，物理 PPA/时序/面积比较未知。

## 未来结果的最小交付

授权并执行之后，由唯一 Main 提供小型已发布或正式关闭文件的路径/固定 commit 与校验值；活动 raw、Trace 或大包无需搬到本工作区。

1. **Main 本轮最终报告和执行 manifest/注册台账回执**：五个 point ID 到实际 cohort、UUID、execution 目录及 Source 的映射；各点注册、一次消费、启动、自然结束、consumer/验收状态与原因。若尚未关闭，按点注明缺失或 HOLD，不把 exit 0 当接受。
2. **每点冻结 Spec 与实际绑定/配置回显**：Core、Framework、vendor、ELF、库 SHA、input binding、literal/canonical ordered commands、完整 283 项 actual echo/指纹、模式、observer、时钟/几何，以及 Host/Native/consumer pin。若实际激活有正式修订，以其固定记录和差异说明为准，不猜 activation commit。
3. **每点关闭结果与接受回执**：完整应用 cycles、命令/kernel/CTA/instruction 人口、drain、正确性/数值或适用 consumer 判定、Base/Ext 服务与主要成本计数；失败、HOLD、负结果和原因也要原样交付。
4. **归档与恢复回执**：真 164 archive 路径、full SHA、Source KEEP，以及两次独立 Native 恢复的目标、SHA/比对和验收结论。提供回执即可，不复制 raw 或重做恢复。

接收时先填状态表，再做比较；缺一端或缺实际绑定就标“不可比较”。

| 点 | 实际激活/消费 | 结束与接受 | cycles | Source/配置/人口匹配 | 归档与双恢复 | 备注 |
|---|---|---|---|---|---|---|
| GEMM EXT0 | 未登记/未启动 | 无结果 | 无 | 待实际绑定 | 无 | 待授权 |
| GEMM EXT1 | 未登记/未启动 | 无结果 | 无 | 待实际绑定 | 无 | 待授权 |
| GEMM EXT2 | 未登记/未启动 | 无结果 | 无 | 待实际绑定 | 无 | 待授权 |
| Stencil EXT0 | 未登记/未启动 | 无结果 | 无 | 待实际绑定 | 无 | 待授权 |
| Stencil EXT2 | 未登记/未启动 | 无结果 | 无 | 待实际绑定 | 无 | 待授权 |

## 已知负例与未知边界

- 历史 W→WV 条件对照中 Stencil 约降 9.00%、GEMM 约降 1.49%，只说明旧 Source 的机会背景，不能直接移植成新 Victim 预测。旧 CLEAN/DIRTY-only observer 与完整 WV 参考背景不同，周期差不能当纯保留类别因果贡献。
- 旧 cold-policy FWT 负结果、低 V 机会 Transpose、以及大 Tag 后部分 WV 增量缩小均须保留；3MM 是后续长负载备选，本批没有启动。UMT1 的 4/4 已关闭，不能冒充新五点结果。CLEAN 独立工程 18/18 CPU 通过且 128 行选择/清理最低 384 L2 ticks，但 C 科学启动本批为 0，不能拼进 A 的 Source 或当性能证据。
- 最新完整交接与本轮只读现场均表明五点 0 批准、0 登记、0 消费、未见活动模型。因而没有本轮激活提交、UUID/PID、cycles、服务计数、完整人口或归档恢复结果；以后如有新正式执行记录，按实际回执更新。
- 物理 PPA、关键路径/最高频率、应用级 NI 与未合格组合仍未知；EXT1/2 仅在冻结的 Tag≤512、RO 关闭、initial prefill 后 kernel 等有限资格内解释。本批无 Stencil EXT1、S、3MM、RO/NI、CLEAN 配额或其他新增点。

接收五点后，把合格的正负结果和成本一起带回科学窗口讨论下一项；本文件不构成新实验或执行授权。
