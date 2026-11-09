请作为新的 `174-new EP-L2-MAIN | Performance-First Continuation` 窗口，接管现有EP-L2唯一Main职责，不重启历史Goal，不另建科研Lane或第二个dispatcher。

首先 `ssh hrl-174-new`，进入 `/root/workspace`，完整读取本交接包同目录的 `EP_L2_FULL_HANDOFF.md`，以及 `EVIDENCE_INDEX.json`、`SOURCE_LINEAGES.json`、`NATIVE_REQUEST_SNAPSHOT.json`、`NEXT_FIVE_POINT_REQUEST_INDEX.json`。

远端可直接读取：

```text
/root/data/ep_l2_full_workload_performance_20261027_v1/handoff/ep_l2_main_full_handoff_20261109_v1/review/docs/ep_l2/operations/ep_main_full_handoff_20261109_v1/EP_L2_FULL_HANDOFF.md
```

最新研究基点是 `ea480a05fb32eeb6b88dd1d8be1b0b9c89eb8526`，分支 `hrl/ep-l2-next-cost-aware-architecture-20261107-v1`；不要停在V3 `9c4a1a95`。目前最新工程目录为：

```text
/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1/
```

V3之后的Vector独立补齐、Stencil/Transpose/3MM、V5、UMT1已关闭，具体结果、负例、Source5及归档在交接文档中。旧两项Vector技术失败保留，不能退款或重试；3MM WV_REF后来已接受，不能再称缺失。

下一步是Victim新结构：Core `3d3887bb2e8d5073d13b0792ff9116834e89fe2f`、ELF `9db48c06ca64e441b5824071f52e0aa0be50374045fbdcef6cdf5d4469182f86`。精确申请在当前工程目录 `agent_d/FINAL_EXACT_EXPERIMENT_REQUEST.{json,md}`：GEMM extension0/1/2三点，Stencil extension0/2两点，全部同新Source、850MHz/L100/G32×8/WV、283项配置，Data1168不变。**目前5点批准/登记/消费均为0；这条交接消息不是新的科学启动授权。** 先只读核对是否有之后新增的明确用户批准；没有则不得启动或借用旧余额。

接手后先核对实时Native/epoch/registry、活动模型/owner、远端HEAD及资源，简短报告接管回执，再继续已收敛工作。若用户另行批准5点，只完成必要Main Host/Native/consumer/依赖与资源绑定后连续执行；各点独立释放，不套旧FWT→GEMM阶段门，不重复旧CPU、巨大Trace扫描或论文分析。

保持Main唯一调度、预算、验收、归档及Git集成owner；如需并行，沿用既有最多4个有限工程子任务的组织方式，不创建永久Lane或竞争自动写入者。全局EP上限cap10动态准入，不要求填满，也不是全项目次数上限。

大Trace/大数据/长期归档放真164；174只保留必要热工作集；Source KEEP。尊重其他owner承诺，不能清理旧资产或重复静态SSD池。每个正式接受结果完整身份、命令序列、kernel/CTA/instructions/drain、真164SHA和两次独立完整Native恢复；正/负/零/失败全保留，不自动重试退款。不跨Source/ELF拼性能、资格或NI。

当前CLEAN C是独立工程候选、完整应用0；RO本轮申请0，论文编辑不恢复，不采集109/4080，不干预DTC与原资产工作。请以实际性能、合理硬件成本和多真实输入验证为主，不用长篇论文级分析替代可执行实验准备。
