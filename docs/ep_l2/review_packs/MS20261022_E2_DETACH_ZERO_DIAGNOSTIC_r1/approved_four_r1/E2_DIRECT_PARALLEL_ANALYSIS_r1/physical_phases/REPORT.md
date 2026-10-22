本表只投影已正式接收的 CFD E052、DWT E053、Vector E054 终验小元数据。没有读取或重扫 raw/trace，没有重新执行模拟、修改资格/台账或向 D 发消息；Conv 仍在运行，不纳入接收结论。22 个物理 phase（含各端 UNASSIGNED、OVERLAP_UNKNOWN）完整保留全部 212 项计数。

|已接收诊断端|有头观测|覆盖 raw probe|TVD 跳过（raw 未知）|实际 commit raw probe|RO 创建事务|raw FAIL / commit FAIL|relieve / detach|
|---|---:|---:|---:|---:|---:|---:|---:|
|CFD E052|1,742,633|1,524,394|218,239（12.524%）|1,163,176|51,678|0 / 0|0 / 0|
|DWT E053|2,199,038|1,863,454|335,584（15.260%）|1,793,713|9,965|0 / 0|0 / 0|
|Vector E054|3,775,296|3,400,296|375,000（9.933%）|831,673|250,118|0 / 0|0 / 0|

三端 detach=0 的本次可闭合路径是：有 RO 事务，但覆盖 frontend probe 未见 all-reserved Tag FAIL，实际 commit probe 也未见 Tag FAIL，因而未调用 relieve、未调用 detach。它们与 SGEMM 的“没有 RO 事务创建”原因不同。所有 pressure-conditioned 同 set 资格、way 扫描、preview relief 和 eligible 联合字段均为 0；分母亦为 0，属于未触发，不能解读为没有 live RO、reuse 阻塞或资格通过。

主要暴露的物理 phase：

- CFD：phase 6 / UID5 占 81.632% 的 covered head probes（1,244,388/1,524,394）、94.118% 的 RO candidate heads（388,608/412,896）、94.125% 的 RO 创建事件（48,642/51,678）。其余 RO 创建事件 3,036 发生于 phase 5 / UID4；UID1–3 无 RO 创建。
- DWT：phase 2 / UID1 包含全部 RO candidate heads（156,210）、RO 创建（9,965）与合并事件（29,871），但仅占 36.730% 的 covered head probes（684,454/1,863,454）。其余主要 probe 暴露为 UID8 16.432%、UID5 16.379%、UID2 15.938%，这些 phase 的 RO 创建事件均为 0。
- Vector：唯一 kernel UID1 / phase 2 包含全部覆盖 probe、RO 创建和合并事件；UNASSIGNED / OVERLAP_UNKNOWN 的计数均为源证实的 0。

这些是事件发生时的物理活跃 kernel 状态，不能当作 requester/victim 的因果归属，暴露占比也不是 walltime 或 critical-path 占比。RO 创建/合并属于事件计数域；旧 accepted RO 的逐 phase 归属并未发射，保持 UNKNOWN，不按比例分摊。样例不代替总体，head-cycle 与 commit 不强行配对。

三端仍分别出现 51,617 / 9,960 / 250,001 次 reuse_seen 首次转换，说明 reuse 观测本身存在；但没有 pressure-conditioned way scan，不能把这些转换解释成阻止 detach 的计数。DWT 有 7,250 次 raw HIT_RESERVED，状态与 all-reserved FAIL 不同，不能替换成 Tag 压力失败。

TVD 跳过是 raw 未观测，并非 raw PASS；不能据此推出 Tags 全局充足。capacity 的 not-consulted、unobserved、line-NA 也不意味着 pass/fail。phase 的 detach-success−retired 事件差可能跨 phase 为负，不是局部 live population；本投影明确保留 NA，而全局终态另有既有接收证据。

可并入的文件：PHASE_FOCUS.csv 为简明暴露表，PHASE_ALL212.csv 保留全部原计数，PHASE_MATRIX.json 含精确身份、既有接收指针、来源 SHA、真实分母契约与排序。10,739 项现有元数据一致性检查全部通过（212 字段跨 phase/64 slice 同字段汇总、精确已接收身份、uint64、NA 与稳定来源）。这不是新的应用资格测试或 S/F 配对。
