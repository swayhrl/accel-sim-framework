# 109大型科研资产冷存决策报告 — V4

证据基线：S109 V3 `8c028bb155c88bcf18151c22e179eb72a5666a24`；U174 跨项目审查 `8700af7cd3e0cd530f8efa8dfe5333ebdd9f1d1e`。本轮只对列名资产做元数据、进程与小型归档收据复核；未重读 Qwen3-30B、StageA 或 R26 九份大文件的全文 SHA，未做全盘盘点、归档复制、GPU 实验或任何删除。109 根盘仍为同一 ext4，采样可用 54.08 GiB、使用率 94%。真 164 挂载身份已复核，174仅是桥接路径。

**当前可执行删除白名单：空。** U174 尚无 AWMA、C16、AI-ARCH owner 的直接答复；未来7天（至11月11日）和30天（至12月4日）的精确任务均为未知，未知不等于无计划。109 现场没有这些精确路径的 cmdline/FD/mmap 命中，但 414 个 FD、105 个 maps 视图不可读或竞争，且模型加载后可能关闭文件。不能靠空命中提升资格。真164长期保存/109按需恢复是本轮待裁决的存储策略；用户已认可R27按需恢复原则，但这不能替代各科研使用方确认。

| 资产 | 109实际文件块 | 真164及恢复证据 | 本地驻留裁决 |
| --- | ---: | --- | --- |
| R26 九份 trajectory | 22.02 GiB | 九个精确目标均在真164；207项发布manifest SHA `8e0e30a90856f152cf1221c6a660ce6ceeeca84c402ed59cd8a6956f1e371159`，历史全文验证日志九项均 OK；109每份 dev/inode/size/mtime 从10月16日至V4未变，164目标大小/mtime与V1相同。恢复到各原路径后按manifest SHA复核；不以重新训练再生。 | **HOLD AWMA owner**。科研证据必须在真164长期保留；109是否可撤需确认具体续行/分析与7/30天时间。逐项见CSV。 |
| R27 三份 COMMON 副本 | 7.34 GiB | V3三源文件及真164 R26规范COMMON全文SHA一致；V4源身份与规范目标身份未变。可逐个从规范父本恢复到三条原路径并核SHA。 | **HOLD AWMA owner**。存储策略已获用户认可，科研owner尚未同意按需恢复；R26规范COMMON及其它R27资产保留。 |
| Qwen3-30B 26文件revision | 56.89 GiB | 历史 `EXACT_FILE_SET_SIZE_SHA256_PASS` 收据；V4源/目标元数据及收据未变。须恢复全26文件、原绝对路径、index/tokenizer与兼容runtime。当前空余 54.08 GiB小于完整revision 56.89 GiB，不能在未退役前于同盘另做整套测试副本。32MiB/s纯传输约30.3分钟，16MiB/s约60.7分钟，另计校验。 | **HOLD C16+AWMA owners**。118条AWMA runnable引用证明复现路径，未证明近期必跑或必须永远常驻；7/30天任务与可接受恢复等待未知。 |
| StageA BF16 两权重 | 5.75 GiB | V2双端全文SHA、V3/V4身份稳定；其它配置/收据不动。 | **HOLD C16+AI-ARCH A79 owners**。A79冻结精确本地路径、GPU_RESOURCE_DEFERRED，未发现已授权带日期重派；未来恢复后重新资格与等待须联合确认。 |
| StageA AWQ 一权重 | 2.50 GiB | V2双端全文SHA、V3/V4身份稳定；其它配置/收据不动。 | **HOLD C16 owner**。单独问AWQ资格续行与按需恢复；不能套用BF16的A79依赖。 |

R26 的 `COMMON_POST_BOOTSTRAP.pt` 规范父本、R27 的 B1_C1_K2、B0 原始张量、接受结果、控制记录均不在候选中；三处 pip HTTP 缓存、ImageLab、E1/A26/A61/NequIP也不在本Goal。本报告不把真164上有副本等同于科研owner同意109删除。

**有限条件组合（均非删除授权）：** R26九份单独 22.02 GiB；加R27三副本共 29.36 GiB，满足20–30GiB目标。若C16与AWMA另同意，Qwen3单独 56.89 GiB；与前组不重叠合计 86.24 GiB。StageA AWQ/BF16分别额外 2.50/5.75 GiB，不能先计作已批准。所有组合的**当前已闭合科研owner可释放量为0 GiB**。

下一次优先清理顺序是：先审 R26九份 trajectory、再审 R27三副本；若需超过50GiB，单独审 Qwen3。精确文件/组身份及门槛见 `NEXT_EXACT_LARGE_ASSET_COLDSTORE_WHITELIST.csv`。请将 `OWNER_FORWARD_REQUEST.md` 转给 AWMA Main、C16 Main、AI-ARCH A79；收到逐资产、带日期的答复后，才能把对应行升级为 `READY_FOR_USER_RETIREMENT_APPROVAL` 并另请用户批准实际删除。此分支只提交审阅文本/表格；完成后STOP。
