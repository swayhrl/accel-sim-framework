# B → D：冻结输入的 W/V 有界筛选 r1

本轮结论：**优先接收 FWT 的既定结果；DWT、CFD 是尚未证实的后续 W/V 诊断候选。Conv 是已确认的高复制压力、稀疏 V 命中锚点；vectorAdd 保留为高写回、无 GPU 写后读地址重合的负对照。当前没有证明任一候选存在“大量、短距离、淘汰后”的 V 复用。** 这是筛选和缺口清单，不是启动授权或机制收益排名。

只消费保存的 S 统计、E 当前接受的 Conv S/F terminal JSON、D 已保存的完整输入 manifest 与 opcode 汇总。CPU 提取读取 2,212,963B，约 0.04s；不读 trace 正文、SQLite 或 raw，不扫描共享存储。E011/E012 FWT 正在原定运行，其增长日志未读。新 GPU、模拟、构建、输入登记、预算调整、资格重置均为零。原 B Core4770adff、RO/参数/fixture 候选和旧失败证据保留。

## 给 D 的顺序及用途

此处“顺序”是下一份证据的接收/诊断优先级，不是预期加速排名。先保证实际资格，再看保存的传统 S 阻塞，再以无序读写重合作为 V 假说；不使用 cycles、加速比或新 F 性能选择 workload。不同年代计数不作统一数值排序。

| 优先级 | 冻结输入 | W 证据 | V 证据与用途 |
|---|---|---|---|
| 1 | FWT_7_21 | 历史 H0 S：178,569 WB/复制行、890,294 WBUF 重试、276,421 同址 WAD hazard 重试；WAD-full 为 0 | 保存模型全部 131,072 个读 line 也有 store，41,943,040 lane-line 读引用，19 个 kernel。最强的待核查读写复用假说；不是 L2 重用距离证明。优先消费 E 已运行的 S/F，不增加任务。 |
| 2 | dwt2d | 更旧 B0 上 WAD-full 74,044、scheduler 拒绝 281,249；新 S 的 WB/WBUF/复制量未知 | 122,880 个读 line 中 98,304 也有 store，5,066,286 读引用落在这些 line，10 kernel。读写重合加旧 WAD 压力支持候选；不能与 H0 五应用直接比数，更不能宣称实际 V hit。 |
| 3 | cfd_097k | 历史 S：31,123 WB/复制行，WBUF 重试仅 5；同址 hazard 9,841，bank wait 102,546 | 15,180 个读写 line、2,869,330 对应读引用，5 kernel。适合区别同址依赖与容量压力；重用顺序、是否在 V 寿命内未知。 |
| 校准，已有接受数据 | convolutionSeparable | 当前 main61 S：546,865 WB/复制行；WB-space 33,572 个首次阻塞请求；复制读、写各 546,865 次 | F 实际 V 读响应 **36**、1,152B，dirty forwarding **0**。保留为“安装多但直接读命中稀疏”的真实负向证据，不作为强 V 收益样本。 |
| 负对照，必须保留 | vectorAdd_4M | 历史 S：100,568 WB/复制行、440,161 WBUF 重试、bank wait 445,678 | 保存完整模型中 125,000 write-only line，250,000 read-only line，GPU read/store line 交集 0。支持“输出写回多、dirty victim 无读复用”的模型负对照。clean victim 的时序/sector 复用仍未知，不能由此宣布全部 V 命中必为零。 |
| 低 W 压力对照 | sad | 历史 S：3,975 WB/复制行、WBUF/WAD-full/hazard 均 0，bank wait 2,255 | 33,910 个读写 line、1,079,100 对应读引用，但没有淘汰时序证据。地址重合本身不足以提升优先级。 |
| 排除，不排名 | btree | 保留旧统计但不用于合法候选推断 | D/E 的 partial-mask/full32 地址语义 HOLD 未解除；旧 oracle 的大量读写重合不使用、不重扫、不用替代物填主图。 |

SGEMM 仍只是 D 待 E 决定的候选，未在七输入登记中，未自动加入；SpMV/Scan 已有输入缺陷，不能因旧压力高而加入。各原始 trace composite、登记 ID、模型引用、S 原始 SHA 和源码身份见 CANDIDATE_PROFILES.csv、SOURCE_MANIFEST.json。模型读引用按 lane-line 计，可能来自合并/线程空间重合，不能当成时间复用次数。全 epoch 的 read/store 交集也不说明先写后读。

## Conv：安装、服务、流量和等待分别报告

E 接受 pair `V2_MAIN_convolutionSeparable_S_F_MAIN61`；S=E010_1108e4d2，F=E009_76e25c1e。Core `d010911e3174a3764791183cd108fe4664ba8731`，Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`，main SHA256 `61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5`；trace composite `620f80f945d8ddbcef639e7e374fd2cb7122f8b07f239c82ccd32a2c4d90e79f`。配置 S=c580439c…、F=02fa921f…，完整身份及 E qualification/run-status SHA 在 REGISTRY_IDENTITY_SNAPSHOT.json。端点 hash 与接受记录相等；本轮没有重新 hash 大 binary 或 trace。

| 量 | S | F | 可主张范围 |
|---|---:|---:|---|
| dirty installs / WB created | 546,865 WB | 546,813 dirty installs | F 安装不是读命中；不能加上 clean 后称有效缓存容量收益 |
| clean installs | 功能 OFF | 499,725 | F 总安装 1,046,538，是累计事件，非唯一地址或同时留存容量 |
| V read responses / served bytes | 功能 OFF | **36 / 1,152B** | 全 64 slice 求和，已提交真实 response，不是 lookup 命中预测 |
| dirty-forward responses | 功能 OFF | **0** | 此真实应用未观察到在途 dirty forwarding；36 个不能全算 dirty hit，也不能区分原 clean 与已完成 WB 的 retained hit |
| promotions | 功能 OFF | 1,152 | 这是所有权/角色晋升事件，不等于读响应或避免的 lower read |
| lower read packets / bytes | 2,359,526 / 75,504,832 | 2,359,460 / 75,502,720 | 整体净差 66 / 2,112B；是 lower 发出边界，不重新命名为 DRAM 接受或外部显存物理带宽 |
| lower WB bytes | 69,787,264 | 69,826,496 | F **增加 39,232B**，保留负结果 |
| logical copy reads / writes | 各 546,865 | 各 0 | copy_free/l2_data_free 均 OFF；证明少了复制操作，不能直接推出同量 GPU stall 改善 |
| total physical bank grants | 9,217,033 | 8,118,075 | 少 1,098,958；接近但不等于少的 1,093,730 复制操作，其他路径也变了 |

实际 V 响应/累计安装=0.00344%，仅是两个事件计数的比值，**不是 hit rate**。F 留存积分 2,274,189,177 slot-cycle 也不是收益。查询数 1,181,110 包含重试；不能据此计算 demand hit rate。主路径 `ep-l2-tvd-directory.h:response_commit` 在真实 bank service 和成功 response enqueue 后递增 read_responses；`promote` 单独递增 promotions。`ep-l2-tvd-cache.inc` 中读返回与写/atomic 晋升分流。这支持“36 次确实服务了读请求”，不支持“独立 V 反事实恰好节省36个 lower read”。W/V/T/M 与 resident 占用、晋升共同改变执行；**66 个净差也不能全部归因 V**。需要同背景 V-OFF 控制才可隔离，现有矩阵与 E 预算决定是否采用。

等待计数保留正负方向：COPY_PIPELINE 请求等待和 546,865→0，WB_DATA_SPACE 848,913→0；SAME_ADDRESS_WB 638,854→538,426，但 distinct 首阻塞请求也从925→749变化。另一方面 F 新增 WAD_FULL 207 个首阻塞请求/5,987 请求周期、VICTIM_LOOKUP 1,181,110、READONLY_LOOKUP 1,251,627；MISS_QUEUE_FULL 等待和180,063→590,686；ANY_FIRST_BLOCK_TO_ADMISSION 2,725,714→4,095,486。它们跨 UID/原因/slice，不能相加为独占 GPU stall，也不能按 wait 和差给出 W/V 的真实 GPU 等待改善。全应用因果等待节省 **UNKNOWN**。逐原因完整表含零结果，不只保留有利项。

历史 bank 观测可辅助选背景：Conv bank0 logical share约31.3%，FWT26.4%，vector25.4%；这是请求落点分布，不是 bank 利用率或证明复制独占某 bank。历史 bank wait 和全部是源2309 的跨 slice 观察，不与 current main61 grant 强行拼因果链。DWT 的 WAD-full 也不是其脏淘汰数，不能靠该数构造 WB 流量。

## 已证实、可构造和精确缺口

已证实：Conv 真实稀疏 V 读服务与高 W 复制压力；历史 H0 FWT/vector 的 WBUF 重试和复制；DWT 更旧 WAD-full。已保存的有限 native cycling/streaming 正负对照证明“有复用可改变流量”和“无复用零 V hit”在受控 fixture 可达，见旧 r4 pack；不将其迁移为真实 workload 的命中或本轮新执行。

未证实：FWT/DWT/CFD 的 actual V hits/dirty forwarding、淘汰到重访的时间/同组栈距离、sector 命中覆盖、在有限池竞争下的存活、V 单独避免 lower read 及暴露到关键路径的等待。kernel 多/读写重合只产生假说；SM/文件顺序不能代替 L2 到达顺序。新画像不读地址索引全文，优先复用已保存聚合，因此不会虚构重用距离。

给 E 的最小诊断申请草案（**未提交运行、未实现新观测**）：

1. 首选零新启动：E 的原定 FWT 配对接受后，发布现有 64-slice terminal victim/first-wait/local-service 数据，复用本提取法；不轮询、不读中途计数、不新增 FWT 条件。
2. 若现有计数仍不足，E 在原合法范围内审核一个小诊断；本轮不占额度。申请上界沿原 screen 预算，至多一个输入、一个条件、120s 或2M指令先到即止；实际次数/预算/输入/资源由 E 决定，非全应用性能证据。若冻结 main61 没有必要事件接口则不能直接执行，也不为它在本轮重建。
3. 仅建议最小事件接口：每事件含 slice、物理周期、line、sector mask、类型(evict dirty/clean、WB accept/complete、V read commit/promotion/reclaim)、generation/UID；若 E/A 批准未来版本，可限一预登记 slice、最多4096事件、1MiB输出，显式报告截断。由这些事件关联同 line/generation 的淘汰→首次读及 reclaim，区分在途/完成 WB。已有 counter 足够的项目不加事件；不建全应用跟踪框架。抽样不能推出全应用率或收益。
4. 真正受控 V 效果仍需原矩阵同背景 V-OFF；若新对照超原授权，交 E/用户审核。安装、命中、净 lower 差、request wait、GPU timing 五栏分开，不以加速选样。

生产源码/配置/binary/input/E 资格完全保持。原 r5 dirty 失败及 A 修复历史保留；本轮以 E 最新 main61 接受记录为准，不沿用旧 HANDOFF_A 中 main773 的过时状态。E 接受 JSON 的 source_map 描述仍写旧 C994/producer75707624，已在身份快照标注，采用准确 machine identity 与正式 release，未修改 E 证据。
