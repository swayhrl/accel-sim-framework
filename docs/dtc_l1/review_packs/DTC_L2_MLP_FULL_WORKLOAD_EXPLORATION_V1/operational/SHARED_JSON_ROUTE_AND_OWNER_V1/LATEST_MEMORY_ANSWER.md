# 最新内存与安全提速核对（只读）

2026-10-28 **01:02:55 CST**：47个本轮模型RSS **105.952 GiB**，4个其它模型10.023 GiB，总115.976 GiB。Host MemAvailable109.485 GiB；256 GiB cgroup尚有严格余量94.225 GiB，加15.204 GiB可回收clean-file信用后为109.429 GiB。后者不是全都可立即使用的物理空闲。

当前未来增长预留由55.237 GiB减到54.475 GiB，已核验padding优惠仅0.762 GiB，不能继续引用旧快照9 GiB节省。按原8 GiB floor、88%预算，剩余准入余量34.782 GiB。**现在直接阻碍新任务的是JSON工程HOLD，不是内存已经耗尽。** 本轮没有启停模型或修改资源设置。

**01:05:37读取最新完整aging记录**：目标已固定Lava DH-P0，全额预测81.178 GiB，仍未consumed。保护额度21.235 GiB，实际slack36.850 GiB，普通小任务可回填约15.615 GiB；Lava本身仍缺44.327 GiB。46个fresh PSS witness显示own-drain后180.542 GiB可用，故等待自然完成积累75%保护是可行路径，不能把全部空隙继续填满小任务。这里使用实际journal，不仅凭线程存在推断调度健康。

可立即安全推进：主修复并资格确认JSON读写链后，解除对应工程准入HOLD，让已有owner恢复符合完整预测和aging保护的任务；保留CPU外层及已有资源门。88%提到90%在本快照只多约2.03 GiB，先恢复已有约15.6 GiB回填空间更有价值。未知/失败下界、claims、foreign和新candidate继续全额估计，不用当前RSS冒充最终峰值，不降hard cap。

“只剩10 GiB就暂停”适合先用于**停止新增准入**。暂停模型不能释放已占RSS，暂停短任务尤其不能换出所需大空间；暂停大任务只能暂时阻止其继续增长。现有原生worker又不支持长暂停（此前已确认超过约30秒会触发supervisor终止），因此不能直接SIGSTOP健康模型。当前swap约2 GiB几乎用尽（仅116 KiB余），没有可假定的交换缓冲；监控周期之间的大分配/外部突增也未证明有界。要采用可恢复模型暂停，需要独立资格确认supervisor协议和身份安全，不能当成现有安全机制。

证据目录：`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1/agents/E/latest_memory_status_v1/` 的 `LATEST_MEMORY_SNAPSHOT.json`、`LATEST_AGING_DECISION.json`；原始资源模块及配置SHA、BATCH_STATE路径/时间均在snapshot。快照与journal分别取样，数值没有混称同一原子时刻。

CPU外层保留的frame guard安装API已经实际B.install_on_frame+E38 CPU PASS4：`cpu_outer_coupling.install_in_owner(main, aging, res, owner_assert)`，三引用splice为CPU→guard→旧E→B。`res.choose_dispatch`继续原CPU wrapper；不改code或冻结源码。恢复可CPU→guard→E，或先撤guard再CPU→E；源码SHA `deea89ce9036630ebd5d39dd842a76b7993ff4a132a40afba89e39ecb89915d8`，资格SHA `d209baa712fc5188372a52ed217825bae29229ebc4731ee927b86c0028691f87`。本任务未生产安装。
