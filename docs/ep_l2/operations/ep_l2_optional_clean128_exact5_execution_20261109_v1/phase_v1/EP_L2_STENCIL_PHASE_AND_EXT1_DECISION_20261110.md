# EP-L2 Stencil 100-kernel 阶段分析与下一点判别

**供 EP-L2-8 审查。**分析对象是已正式接受的 `STENCIL_WV_EXT0` 与 `STENCIL_WV_EXT2`，每点各一次确定性模拟。本轮仅流式读取两份已接受压缩 raw；没有启动、登记、消费新点，也没有重扫 Trace 或修改 Source。

2026-11-10 15:55 UTC 对共享 Native registry 做只读检索，未见本草案所用 Stencil EXT1 cohort；当时 registry 文件 SHA256 为 `71d40678efd24108b112d5b0b4ab515de69760139af3ae84d334ca0309c511b1`。这是现场采样，不替代未来执行前的重新核账。

## 证据与守恒

两点 Source archive SHA256 同为 `7199f3dd5bdba2167186ca6858cd15603997f560660b54e8a1457761f115f48b`，ELF SHA256 同为 `9db48c06ca64e441b5824071f52e0aa0be50374045fbdcef6cdf5d4469182f86`，Stencil 输入 SHA256 同为 `bd0309dfeec5745ba97400978c2c5f1413fa9c604376b3dd97e1dd3d5c8cc146`。实际 283 项配置仅 `-gpgpu_ep_l2_victim_extension` 从 0 变为 2。每点均为相同的 100 个有序 kernel、6400 CTA、2,193,446,000 指令。Native registry 中两行均为 `CLOSED_ACCEPTED`；本分析核对 DONE ref、压缩 raw SHA 和 accepted bundle。

raw 的 `gpu_sim_cycle` 是逐 kernel 增量；B0/M0 `kernel_shared_delta` 每 kernel 各 64 slice；TVDV2/TVDX1 是每 slice 的累计快照，须按相邻 kernel 末尾差分。终端第 101 份快照与第 100 份相同，不重复累计。EXT0 的逐 kernel cycles 合计 4,768,787，EXT2 为 4,786,321；两者各加共同的 106-cycle 末尾，分别得到正式应用总数 **4,768,893**、**4,786,427**，净回退 **17,534 cycles（+0.3677%）**。B0 lower read 和两类 response 合计均与 accepted bundle 守恒。可复核的脚本、100 行 CSV、逐项 JSON 和汇总在同目录 `phase_v1/`。

## 阶段分布

| 人口或区间 | EXT2−EXT0 cycles | EXT2 扩展区 response | lower read 差 |
|---|---:|---:|---:|
| kernel 1 | −222 | 68 | −36 |
| kernel 2–100 | +17,756 | 56,644 | −66,393 |
| 有扩展区 response 的 50 个 kernel | +8,684 | 56,712 | −60,787 |
| 无扩展区 response 的 50 个 kernel | +8,850 | 0 | −5,642 |
| 全部 100 个 | **+17,534** | **56,712** | **−66,429** |

99 个 kernel 变慢，1 个变快；逐 kernel 差的中位数为 +173.5 cycles，最大 +326（kernel 44）。扩展区 response 发生于 kernel 1 及其余奇数 kernel，偶数 kernel 没有扩展区 response；两组均为同一命名 kernel 的不同有序实例，不能把奇偶分组当随机对照。最初两个 kernel 产生全部 6,729 个 Ext CLEAN install/spill，随后 98 个没有新 install，但 49 个奇数 kernel 仍得到 1,156 次/个的 Ext response。这个模式符合跨 kernel 保留的观察，不能仅凭这些计数证明哪一次服务缩短了关键路径。

以每 10 个 kernel 为箱的 cycles 净差依次是 `+1264, +2013, +1892, +1803, +1920, +1823, +1907, +1683, +1665, +1564`。回退贯穿整段，没有由少数末尾异常点支配；后 90 个合计 +16,270。扩展区 response 和 lower read 减少也贯穿这些箱，而非只在开头一次性发生。

## 结构与成本观察

| 64 slice 全程汇总 | EXT0 | EXT2 | EXT2−EXT0 |
|---|---:|---:|---:|
| Base retained responses | 4,930,426 | 4,933,062 | +2,636 |
| Ext retained responses | 0 | 56,712 | +56,712 |
| 实际 lower reads | 3,474,210 | 3,407,781 | −66,429 |
| 实际 lower read bytes | 111,174,720 | 109,048,992 | −2,125,728 |
| B0 lookup wait 观察 | 7,310,059 | 7,351,805 | +41,746 |
| B0 bank wait 观察 | 1,048,720 | 1,054,873 | +6,153 |
| B0 `block_payload` 事件 | 976,140 | 8,078,684 | +7,102,544 |

EXT2 另有 2,410,324 次 Ext query、2,388,405 次 selector read、77,538 次 Ext indexed read。`block_payload` 在生产代码中可由填充未获授权或前端 reservation fail 增加，是宽泛的失败分类；该差值**不是** 7,102,544 个独占 GPU 阻塞周期。更细的 `c7d_payload_capacity_allocation_denial` 与 `c7d_payload_service_port_denial` 两点均为零，不能把该差值解释成物理容量满或端口拒绝。bank/lookup 等也是 slice 局部、可能重叠的观察，不能相加解释 17,534 个应用 cycles。response 也不逐个等同避免的 DRAM 请求。

**可支持的结论：**同 Source/输入/配置下，EXT2 确实保留并再服务 CLEAN，lower read 减少，却持续发生小幅全应用净回退。无扩展区 response 的 50 个 kernel 仍累计回退，说明“有 response 就应加速”的简单解释不成立。**尚不能识别：**两段查询、Base 选择和 Ext lane 等硬件迁移包，与允许 CLEAN 保留的增量，各自对净回退的贡献。逐 kernel 相关性或 B0 事件差不能代替该反事实。额外 Ext metadata 的保守估算是 58,880 逻辑位/slice，另有比较器/端口/控制；物理 PPA、频率闭合、能耗与应用数值 oracle 仍未证实。

## 决策与下一动作

若要决定 CLEAN 策略本身应继续优化，最小可辨识对照是**同一 Stencil 输入的 EXT1 一点**：EXT0→EXT1 测迁移包净效应，EXT1→EXT2 测同扩展硬件下 CLEAN 保留增量，EXT0→EXT2 仍是已测的整体净效应。`EXT1` 申请草案见 [EP_L2_STENCIL_EXT1_EXACT_REQUEST_DRAFT_20261110.md](EP_L2_STENCIL_EXT1_EXACT_REQUEST_DRAFT_20261110.md)。它请求一个新的、明确授权的一次消费点；旧五点两份 request 已关闭且余额为零。本轮没有 EXT1 授权或运行。取得批准后先做当前 Native/owner/资源核对，再由唯一 Main 按新精确范围登记与执行；如不批准，保留当前负结果并停止该扩展方向的额外模拟。
