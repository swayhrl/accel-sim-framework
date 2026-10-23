> 最新科研进展（2026-10-24）：Vector r5 单端已完成科学接受、真164归档及两个native Target完整恢复。56000000指令/75039cycles，250118个RO事务；covered目标set RESERVED最大3/16，实际TagFAIL/relieve/detach均0。TVDskip375000次保持NA。本次新epoch2完整应用1次，另1次help资格加载；请求CLOSED、剩余额度0，旧57/44/T0与main61不变。精确新结果见[最终报告](../ep_main_vector_r5_20261023_v1/FINAL_REPORT.md)。以下保留接管时的历史状态；当前唯一待办以NEXT_SCIENTIFIC_DECISION.md为准。

# EP-MAIN 当前科学状态（2026-10-23）

接管状态：本轮有限只读科学交接完成。科研主 Lane 为用户指定的 EP-MAIN；原 A2/B/C/D/E2/F 的成果按精确提交接入证据索引，旧窗口、Goal、控制器均未恢复。这里的科研职责接管不修改 epoch2 运行注册表，也不自动采用历史 producer binary。

## 身份与入口

- 交接基线：`564808e166ca4bde2201dec6bc7a4d6e50c47c48`。
- 原生接管交付：`4a4931b2ac798c870df5b4661702dfec4900b331`。
- 独立 worktree：`/root/data/ep_l2_main_20261023_v1/worktree`，本地 ext4；分支 `hrl/ep-l2-main-native-174new-20261023-v1`。
- 唯一科学入口：先 source `/root/data/ep_l2_dtc_l1_native_v2/activate.sh`，实际启动只能经 `experiment run-native <新cohort> --project EP_L2`。本文不是可执行启动规格。
- 当前 epoch2 ACTIVE，holder `huangrulin-sshfs-174`；新科学预算 0，future requests 为空。管理 epoch1 与旧科学账本保留。
- 实时项目状态、挂载、lock 和本地模拟器进程核查见 `LIVE_READONLY_TAKEOVER_RECEIPT.json`。本轮观察到本地模拟器 0，qualification INTENT 均有 DONE；这是有时间戳的观察，不是未来资源准入。
- 生效 `tools/native_v2.py` SHA256 为 `6f1a0b5f1a4a3d08ba1fa0709eea02e7cc2ec75b5e76e7a168027c1caf1f90a1`。当前代码只选择已消费的迁移 cohort，且预算门先拒绝；并没有可直接提交任意新科研 spec 的通用入口。后续需要在同一入口完成有界工程接入、身份记录与准入，不能只改预算或直接运行 ELF。

## 旧 Lane 的精确接收

| Lane | Framework HEAD | 接收内容与解释 |
|---|---|---|
| A2 | f7869e5dfdc1b6659a1b82a732fcd6ca12f81ddf | E59/r4 producer Core9243/main d99a；16 类、48 次真实 fixture exit0，212 schema；producer PASS 不等于 native epoch2 应用资格 |
| B | 1af7a81629a90db4948f0842a4a9ca2659e6609d | W/V 历史正负观察与联合 fixture 边界；早期 FWT 未接受、SGEMM 未登记等陈述保留其时间，不当作后期 E2 状态 |
| C | ef6d9127eb4882229efc561d832a5985780cea60 | SGEMM whole-commandlist/128B/规范 VA 的证书及 E59 metadata carryforward；不是物理硬件、数值结果或 runtime 自动认证 |
| D | 0d8fec555d9ec8582404fe17b6eae06922dc8a95 | 归因报告、E59 funnel 合同、16 个带适用域的等式；旧 D 状态中的“尚无接受诊断”被后来 E2 接受记录增量补充，不改旧报告 |
| E2 | 7c2f830175f40e16651eab4a3cd3a7af73e9927b | 57 次历史费用、44 个有效执行状态/44 个接受结果索引、25 对；r5 CFD/DWT 已接受，Vector/Conv 未启动，controller STOPPED |
| F | ab8e04dce031aee26e9f92e1b9cebe88fd9f8c2f | 环境/条件部署与 blocked 历史保留；无新常驻 F executor、无委托构建 |

32 份初始 GitHub 内容已按 Git blob SHA 与精确 commit tree 交叉核验；后补两份 r5 producer/Vector spec 亦同。完整引用、内容 SHA256 与本地副本见 `OLD_LANE_EVIDENCE_INDEX.json`。

## 历史账本核对

批准的只读投影位于 `control/source_historical_preimages/EP_REGISTRY_d8c402cce5d0d00c45c2a7512d2736d7fd0024d604d2603637f4615279eaaf07.json`，完整文件 SHA 与文件名及 epoch2 原始引用一致。未联系旧174执行 controller 或模拟器。

- T0：1792414193；57 个实际启动；执行行分布为 COMPLETE_VALID 44、FAILED 8、RESOURCE_LIMIT 3、INCOMPLETE 2。
- `accepted_results` 为 44 项，`accepted_pairs` 为 25 项。它们与执行行不是一一同义：E037/E038/E051 的原 FAILED 行保留，补充接受另外引用；E001/E004/E008 是有效控制执行但不在该接受结果索引。不能据此退款、覆盖原状态或把数字相加成新 cohort。
- E051 SGEMM 原解析失败保留；随后仅对同一 raw 离线修复解析、补充验收，无新启动。
- E011/E012 FWT 原 INCOMPLETE 保留；后来的 E049/E050 是单独接受的恢复配对。
- 原生产资格 HOLD、Btree 非零 mask 地址域 HOLD、未接受 B/C 额外联合 fixture 全量保留在投影。旧 top-level status 字段过时；本交接使用逐条记录及最新 E2 停止交接。
- 旧 r5 余下两端是历史未启动条件，不能转换成新 native 预算。旧 count/time 为 null 也不是无限授权。

派生记录见 `ACCEPTED_RESULT_AND_PAIR_INDEX.json`；本轮只投影身份与已有数字，未重跑终验或重新接受旧结果。

## 论文数字与科学分组

下表 S/F 表示已接受配对中的 cycles_left/cycles_right。保留正、负和近持平，不能统称为加速。

| 科学分组/输入 | S cycles | F cycles | S/F |
|---|---:|---:|---:|
| 原 MAIN convolutionSeparable | 292932 | 291469 | 1.005019402 |
| 原 MAIN cfd_097k | 79093 | 79157 | 0.999191480 |
| 原 MAIN dwt2d | 166519 | 167643 | 0.993295276 |
| 原 MAIN sad | 110773 | 109754 | 1.009284400 |
| 原 MAIN vectorAdd_4M | 73696 | 75039 | 0.982102640 |
| 原 MAIN FWT 恢复 | 493189 | 490402 | 1.005683093 |
| 独立 SGEMM 探索 | 343730 | 343442 | 1.000838570 |

原 MAIN 为 6/7；Btree 仍 HOLD，原七输入 GM 为 UNKNOWN。SGEMM 不替代 Btree。另有五对 Corefe7e/main93a9 容量/data-free 诊断及各类 main61 控制，全部 25 对的精确值、配对 ID、两端 receipt/path/SHA/source/input 均固定在 `PAPER_TABLE_SOURCE_INDEX.csv`，不与原 MAIN 混算。

当前母稿边界沿用用户确认的 EN-v22；EN-v24 是隔离候选。本轮未获得可读取的当前母稿实物，文件 SHA 与逐论文表号映射均为 UNKNOWN。CSV 固定了科学表值和来源，不能声称核对过未提供的稿件表号；未编辑或替换母稿。

## 三条 runtime 谱系

| 谱系 | Core commit | main SHA256 | 当前科学地位 |
|---|---|---|---|
| native/main61 | d010911e3174a3764791183cd108fe4664ba8731 | 61aad385723ac97a76cb1f32c124b286a10bc8609c9c58b1a3ef8a87413f2dd5 | 本地已资格化的冻结执行基线 |
| A2 E59/r4 | 9243f769620653f2a9d4df5599e9581e9dae6067 | d99ac88d60a596b123765009420a85eea1463c01e88807a8876ae946e380fd13 | 历史 producer 与 E051–E055 诊断；未自动迁入 native runtime |
| E2 r5/E057 | 1093d2629e3d6a9130ba25b9dd119b6f3e16c092 | e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33 | 历史 Tag-pressure 诊断接受；本地当前 main61 不含此观测接口 |

三者 runtime Framework 同为 9dd1ee57a83d83b56b7874bc7c716185ab52c8f7，vendor f90c430c3a1ce8f08c09942a5a1c3a797bb2295b；本科研文档分支 HEAD 与模拟器 runtime Framework HEAD 分开记录。Corefe7e/main93a9 容量诊断是额外独立谱系，不借用其 oracle 结果证明有限硬件收益。

main61 的 W/V/T/M 配置与已有控制可以作为新 epoch2 设计的源参照；仍需新 input/config/spec/profile 资格与预算，不能重用 E013 的 Q2 cohort。新增 detach/Tag-pressure counters、候选修复或其它 Core 改动须采用精确新 runtime 与 native 资格；复制旧字节和重新编译也分别记录，重编译不得继承旧 binary SHA。

## 已接受的 Tag-detach 结论

- C 的 SGEMM 正向模型证书：64480/98272 条读行、75423744/76505088 次读 lane-line 引用。它描述认证域，不代表 miss、RO 准入或性能。
- E051 的正向证书被识别，但可见候选全为 resident hit；RO 事务、relieve、detach 为 0。该点是补充接受的 r4 F 诊断，不与旧 S 构成跨 binary 性能对。
- r5 E056 CFD：51678 个 RO 事务，covered 目标 set RESERVED 最大 4/16；新 Tag 需求子集最大 3/16。实际生产 TagFAIL/relieve/detach 均 0。
- r5 E057 DWT：9965 个 RO 事务，covered 最大 3/16；新 Tag 需求子集最大 3/16。实际生产 TagFAIL/relieve/detach 均 0。
- 这些覆盖域未到达 all16 RESERVED 的必要触发条件。满 VALID/MODIFIED occupancy 仍可替换。TVD skip 等未观察域保持 NA；物理阶段不等于 requester/victim 的 kernel 因果归属。
- Vector/Conv 的 r5 联合条件仍未测，不能用 r4 零值回填。尚无接受的真实 workload Tag-detach 正收益证明。

W 的 copy 消除、V 的真实读服务、T 的 detach、M 的 line-MSHR bypass 分别建立证据；S/F 全机制变化不能拆成 T/M 独立贡献。旧 FWT 未接受快照中的 V/dirty-forward 事件保留为历史观察；完整配对接受也不会自动补出 V-OFF 因果控制或 byte-level 数值验证。

## native 迁移与数据边界

EP 新迁移：Q1 STOP_UNACCEPTED、Q2 ACCEPTED，各计费 1；Q2 为 73696 cycles、56000000 instructions、15625 CTA、1 kernel、64 slices、drained。DTC GEMM 与 legacy NN 是另外两次已消费启动，合计四次迁移启动，不计入旧 EP57。

当前 EP 自动 ensure 只有 `EP_VECTORADD_S` 两个冻结成员，映射到真164；其它输入未声明可用。`INPUT_ASSET_REQUIREMENTS.json` 保存 8 个历史选择的有界候选清单，均为未批准、未注册、未搬运的草案。SGEMM、FWT、CFD/DWT/Conv、Btree 等需要 T-OPS 精确 COPY_ONLY 清单；Btree 科学 HOLD 不因搬运解除。

新实验热写只能为174-new本地 ext4。结果按科学接受 → typed COPY_READY → 单 receiver 真164 COPY_ONLY → 关闭重开全 SHA → 独立 native Target 恢复签收。历史和新源原件 SOURCE_KEEP，释放 0B。输入与结果使用各自 manifest，不能用归档 PASS 代替科学资格。

下一项唯一优先决策及全设计待办见 `NEXT_SCIENTIFIC_DECISION.md`。本轮模拟、构建、旧 Goal 重跑、trace 正文读取、源删除与官方 ledger 改写均为 0。
