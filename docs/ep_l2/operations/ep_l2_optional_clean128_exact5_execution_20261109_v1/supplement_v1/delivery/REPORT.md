# EP-L2 Main：Native 剩余写入核账与五点续行补充

## 发布前复核

15:36:14 UTC 最后定向现场检查：registry/claims SHA 均未变，`/root/data` 实盘可用 19,417,575,424 B，仍低于 15:29 的诊断要求；未见独立 `accel-sim.out` 模型进程。磁盘继续变化，本报告的缺口只标注各自采样时间，不作为未来固定清理目标。

2026-11-09 15:29:56 UTC 再次有界只读采样，registry SHA 仍为 `c884c5afec814b6a8ab45bbc40c5d6eda4d275f9bca43a51ac8733c294efd3c8`，epoch 2 一致，claims 为空，五点消费仍为 0。Native 可用量在 GEMM/Stencil 两个相邻采样分别为 19,771,285,504 / 19,769,774,080 B；整族无 claim 诊断要求均为 26,436,707,378 B，对应即时缺口 6,665,421,874 / 6,666,933,298 B。诊断并非逐点准入；实际逐点 HOLD 的时间和数值见下表及原始回执。无启动验证回执为 `NO_START_VERIFICATION.json`，五点 prepare 均 PASS，两个真实准入均 HOLD，混合 claims 归属和未知 owner HOLD 检查通过。瞬时 RAM 与磁盘均须在下次真实逐点准入重新检查。

固定补充来源：`4c02b53b2f9737b2733e2108bdc188caffac09c7` 的 `MAIN_SUPPLEMENT.md`。109 来源：`74cba90276e5056b3c401e83bf3298883a19f688` 的 `MAIN_CONTEXT_ADDENDUM.md`。现场详账见 [NATIVE_WRITE_LEDGER_RECONCILIATION.json](NATIVE_WRITE_LEDGER_RECONCILIATION.json)，本报告中时间均为 UTC。

## 当前结论

2026-11-09 15:21:29 只读采样：Native epoch 2；registry/epoch 一致，registry SHA 为 `c884c5afec814b6a8ab45bbc40c5d6eda4d275f9bca43a51ac8733c294efd3c8`；真 164 已验证；五点请求仍各登记一次，GEMM 预算 3、Stencil 预算 2，**消费 0、模型 0、claims 空、验收 0**。未新建 Goal、预算或 dispatcher。五点原授权继续有效。

两个 family 的新 Host/资源适配和五份未消费 Spec 已按原 owner 事务版本化绑定；旧文件、旧 Spec 和 Native 路由均保留。新旧注册 Host 版本共存，原 Source5、输入、283 项配置和 Native 入口不变。五点新版 `prepare` 全部通过，未启动模型。`stage_dispatch_exact5_v2.py` 现在一次只处理一个精确 cohort；跨族 claims 按 request 归属，单族账本更新只计本族。完整结果归档与两个串行 Native 恢复共用一个 **128 MiB** 窗口，另计每族 2 MiB metadata；真 164 tar 不作为本地 tar 再扣。归档前以完整成员与 tar 需求检查 128 MiB，超界保留原件并 HOLD。

15:20:26 GEMM EXT0、15:20:28 Stencil EXT0 各做一次有界无启动的真实逐点准入，均 HOLD 并撤回新 claim。实际 `global_restore_dedup` 每次扣除 peer 的 134,217,728 B 恢复窗口，保留一个全局 128 MiB。两个窗口同时报告 Native 空间和瞬时 RAM 准入不足：

| 准入点 | 当时 Native 可用 B | 实际要求 B | Native 净缺 B | 当时所需/可用增量 RAM B |
|---|---:|---:|---:|---:|
| GEMM EXT0 | 20,167,233,536 | 26,168,271,922 | 6,001,038,386 | 11,158,526,362 / 5,933,774,274 |
| Stencil EXT0 | 20,167,229,440 | 26,235,380,786 | 6,068,151,346 | 6,863,559,066 / 5,638,531,317 |

这些数仅属于各自回执时刻，不是永久清理目标。上述 required 包含有效 5 GiB 底线、DTC 未关闭保证、另一族 carrier、本点输出/metadata 和去重后的唯一恢复窗口。cap10 是上限，未要求填满。无启动测试还覆盖了混合 claims 的本族计账、peer carrier 不变、未知 claim owner HOLD。详见 `NO_START_VERIFICATION.json` 和两个现场 `STAGED_ADMISSION_*` 回执。

## 逐 owner 的占额与真正增长

同一时点 DTC 请求的**准入占额合计 20,459,824,178 B**，不是已证实的未来写盘总量。六个新 DTC 请求的已发布 carrier 合计 **15,161,734,116 B**，预算均已消费且有 execution receipt，但 registry 内没有逐项 archive/restore 关闭引用，实际已写量及仍会增长的字节量均为 `UNKNOWN`；这些保证保持原样。另有 V100 1,143,128,181 B、MLP 1,202,171,865 B 的适配器剩余上界，Stage IIA first16 保留 2,684,354,560 B carrier（适配器派生剩余界 268,435,456 B），remaining48 的未来 metadata 为 268,435,456 B。first16 的 carrier 与派生界差 2,415,919,104 B，但没有 owner 的正式释放凭据，**未据此减账**。逐条 kind、bytes、来源和关账缺口见 JSON 与 [DTC_OWNER_CLOSEOUT_LIST.md](DTC_OWNER_CLOSEOUT_LIST.md)。

本 Main 的两行原 carrier 为 GEMM 258 MiB、Stencil 194 MiB，各只给本族 64 MiB 恢复窗。为兑现合同，两行在未消费状态下分别改为 **322 MiB** 与 **258 MiB**，各包含未消费点的 64 MiB 输出上界、128 MiB 恢复窗与 2 MiB metadata。去重前两行 580 MiB；跨族实际准入只扣 peer 重复的 128 MiB，合计仍为 **452 MiB**，没有削减原总体保证。单点成功 staging 后，原 owner carrier 才会降为本族已 claim 点的真实后续输出加 128 MiB 窗口和 metadata；所有 claims 关闭后本族 carrier 才清零。已落盘结果已经体现在 `df`，不再重复算作新增长；真实 164 tar 的大小直到终态生成才知，不能写 0。

## 边界与下一动作

本 Main 没有改 DTC registry、清空间、搬迁大资产或重启旧 Goal。109 最新接管已接受；exact36 新 dispatcher 历史终态 `FAILED_STOP`，冻结 2 提交、1 失败保留、33 待处理，33 项后续处置 `UNKNOWN`，不构成本五点前置门。

当前仍为资源 HOLD。请用户将 [DTC_OWNER_CLOSEOUT_LIST.md](DTC_OWNER_CLOSEOUT_LIST.md) 转交 DTC owner 核清并按其流程正式释放可证的剩余承诺；如仍有物理空间缺口，由用户处理 Native 实际盘。RAM 也需在下一次准入时重新采样。条件变化后本 Main按原授权对合法未消费点逐点 fresh admission，合格者直接接续一次消费、自然结束、验收、真 164 full SHA 与双恢复；不再请求同一五点批准，也不自动重试已消费点。无模型结果可等待。
