# C5 precondition decision

## 唯一决定

```
ARCHITECTURE_DECISION_REQUIRED
```

不得把这个 gate 降格为“资源恢复即可运行”或“带 caveat 运行”。本决定**不**启动 C5，
不改变冻结实现，也不否认 C4/C7 的 speculative 软件证据。

## 为什么不是普通模型修补

若只是一个已选 architecture 漏掉计数器或小的 timing 参数，可归为普通模型修补 gate。
这里尚未作出决定的却是会改变架构本身及其性能结论的选择：

1. Weight range hit 取得真实 PA 的方式：被 pin 的连续 `PA_base`，还是可计时的
   indirect mapping；identity-like `ppn=vpn` 不能二者兼任。
2. 谁能授权一个 VA range 为 accelerator-eligible：privileged driver/VM contract，还是
   当前 simulator object label；这同时决定 protection 和多 tenant isolation。
3. Segment table 是 per-SM replica、shared multi-bank 还是另一种结构；相应 port、queue、
   backpressure、10-cycle service 与 parallel-L1 completion policy 必须选择。
4. Sub-entry 的公平预算单位：equal-bit group 数、leaf-capacity-matched exact TLB，或两者；
   以及 64KiB-only candidate 与 2MiB/PWC alternative 的 comparison policy。
5. descriptor/group 的 update, invalidation, migration, UVM, context switch and ASID reuse
   protocol。

这些不是 replay 后可以从结果“推断”的参数；C5 的数值会依赖所选答案。故若先运行，将会
把无 PA mapping、无 port、无 lifecycle 的 shortcut 固化成 architecture performance claim。

## 解除 gate 的有序前提

| 顺序 | 必须有的已批准输入 | 可验证产物 | C5 前状态 |
| ---: | --- | --- | --- |
| 1 | Weight descriptor mapping form、context/permission fields、driver installation provenance | 数据结构/状态转换说明；证明 range 不能越权或返回 identity PA | 必需 |
| 2 | map/remap/free/UVM/context switch/shootdown 的 epoch 或 invalidate protocol | stale/racing update cases 的定向验证合同 | 必需 |
| 3 | N=1/4/16/64 topology、per-SM/shared placement、aggregate ports、queue/backpressure 和 L1 ordering | symbolic throughput table和明确 latency decomposition | 必需 |
| 4 | sub-entry equal-bit budget 和 exact/PWC/2MiB 公平 baseline policy | 以 `P,A,Q,Z,R` 实例化的 budget ledger；page-size policy | 必需 |
| 5 | 以上 architecture decisions 落为有 provenance 的模型且 standard mode 仍回归兼容 | 独立 code/test approval（不在 C8 实施） | 必需 |
| 6 | 原 C5 host/farm health gate | scratch、swap、Window A priority 检查 | 后续且仍必需 |

第 1--4 步是 architecture decision，不因资源健康而自动满足；第 5 步如获授权会是新的
受控开发阶段，不能在本 C8 analysis-only 窗口静默实现。只有这些前提与 C5 resource policy
都满足后，才可重新评估新的唯一 C5 gate。

## 仍可保留的结论

- C4 的 Segment+L1 软件 state machine 在受限输入上保持 exact-once 前端 telemetry；
- C7 的 Weight `HIGH` 与 sub-entry `MEDIUM` 是 analytical opportunity，不是硬件 performance
  prediction；
- `REFERENCE_APPROX_SUBENTRY_16`、`SPECULATIVE_CANDIDATE` 继续有效；
- 禁止自动进入 C5、KV segmentation、12K 或 M5。
