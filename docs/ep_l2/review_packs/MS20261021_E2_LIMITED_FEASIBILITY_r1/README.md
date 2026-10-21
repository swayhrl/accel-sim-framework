# 下一阶段有限实验决策审查：本轮零启动

实际E最新基点是 `b8a1ddc5995456332ef4ac8e36d028ec8f77e097`，晚于用户引用的ac5b执行终态。A2源审查基于`04f255e4316d69eb773ca178b3349699958a1dde`及正式main61发布；D已完成[E031/E032四端逐kernel分析](https://github.com/swayhrl/accel-sim-framework/blob/2789e3034493bb57a66948c77a67fdcb26bf6ef0/docs/ep_l2/review_packs/MS20261021_D_DWT_FOUR_KERNEL_r1/README.md)。当前32/40、剩8；4对MAIN及10项控制接受结果不变，contingency8/8，原控制器STOPPED。

| 优先级 / 候选 | 新启动及硬结果预留 | 原矩阵 / 最小资格缺口 | 预计walltime |
|---|---:|---|---|
| P0 DWT F_MINUS_R | 1 / 384MiB | 不在当前矩阵；拟用未启动FWT F_MINUS_W格。复用现有R0原生证据、E17 WAD增量和完整DWT输入；补独立DWT精确profile资格及登记。W1V1T0M0、物理P1，不能借用S/F资格直接运行。 | 12–25分 |
| P0 Conv S_WB64 | 已接受S可被独立证明适用时1 / 384MiB；否则新observer0 S与WB64共2 / 768MiB | 原STATIC_CAPACITY格。真实1168=1024resident+80landing+64WB，每bank256/20/16；新增48WB由landing128→80支付。旧observer1草案被main61拒绝；observer0需要有限解析器/profile资格，保留64slice闭合、缺失observer指标UNKNOWN。现有observer1 S比较指纹不同；须独立证明observer等价并批准比较归一化，不能修改旧回执或暗借基线。否则额外S基线须另有槽位。暂不纳入首批。 | 每端45–80分；匹配两端90–160分 |
| P1 Conv S_L2_DATA_FREE | 1 / 384MiB | 原LOCAL_DIAGNOSTIC格；S local/ROP7真实PASS与源等价可复用，补准确输入/profile资格及finite residual service说明。诊断标签保留，不作为硬件加速结果。 | 45–80分 |
| P1 Conv F_L2_DATA_FREE | 1 / 384MiB | 原LOCAL_DIAGNOSTIC格；复用F_data_free实际exit0、D512/Line128/ICNT64/dirtyWB有限证据及当前WAD增量，必须单列`full_data_free_finite_residual_service`门。原F资格没有该专属门，不能替代。保持完整oracle范围及诊断标签。 | 45–80分 |
| P1 Vector F恢复 | 1 / 384MiB | 原F已计费RESOURCE_LIMIT；新重试格未批准。拟用未启动Btree F格；复用当前main61资格、完整56000000指令输入及有效S，不重跑S。旧F为真实空间保护exit−15/wait15，绝非PASS或退款。 | 12–25分 |
| P2 FWT S/F恢复 | 2 / 768MiB | 原两端已计费INCOMPLETE；复用当前main61资格、19kernel/791609344指令输入（1785749774B）。次选拟用两格Conv L2诊断；LOCAL_DIAGNOSTIC仅预算角色，S/F运行标签仍为物理端点。原143发送者/初始原因UNKNOWN；durable exit的8项有界验证已覆盖已知监护缺陷，不能反推旧exit0。 | S80–110分，F85–120分；双路90–125分 |
| P2 L2/DRAM敏感性 | 本轮推荐0 | 现有统计无法选择有依据的一档容量、延迟或带宽变化；不生成网格。若以后有依据，一档新参数S/F也需2次、独立共同配置/资格及槽位成本审查。 | 不推荐，未虚构估时 |

资格复用以精确源blob、真实原生退出回执、当前E17 WAD增量及完整输入范围为边界；本轮没有重建或重跑native。配置草案已生成并算出准确hash，但没有资格登记、READY_QUEUE、租约或应用启动。WB64的障碍是具体终验/比较合同缺口，不是I/O压力；不阻塞其他候选。

**首选，最多4次：DWT F_MINUS_R → Vector F → Conv S/F_L2_DATA_FREE。** 精确替换`V2_FWT_7_21_F_MINUS_W→V2_dwt2d_F_MINUS_R`、`V2_btree_F→V2_vectorAdd_4M_F_RESOURCE_RETRY`；两项Conv诊断使用原格。预算32→36/40、剩4，预期390–510MB、硬预留1.5GiB。实际双路门禁通过时约70–115分（含终验发布）；单路114–210分。先完成两个便宜条件，再做两侧诊断；逐点接受即交D。

**第二选择，同样最多4次：DWT F_MINUS_R＋Vector F＋FWT S/F。** 保留首选两项替换，再将原Conv S/F_L2_DATA_FREE两格分别替为FWT S/F恢复格。预期436–550MB、硬预留1.5GiB，双路约115–160分，单路189–280分；代价是放弃两种原计划Conv诊断。新FWT两端仍分别计费，旧INCOMPLETE不退款。两方案互斥，不能执行并集。两方案都保留Btree S HOLD和原七输入MAIN登记；直接删除两格Btree会破坏现有七输入矩阵，未建议该做法。32行仍是预算登记，不是32种独立配置或七输入全有效的宣称。

D的精确闭合：W_ONLY→F **+851 = K5 +998＋K8 +157＋其他−304**，残差0。K5/K8没有新增RO查询，仍不能排除前序状态影响或把851唯一归因为V/RO；这支持优先DWT R0控制。DWT平均DRAM利用率S/W_ONLY/F约26.10/26.05/25.38%，高L2 miss本身不足以指定敏感性参数。D还复核了既有Conv局部队列压力、CFD服务量/周期非单调及SAD零lower-read前缀收益：均不能据此选择具体容量/延迟/带宽变化；26%数值仅适用于DWT，不能外推其他输入或证明没有内存瓶颈。

只读双路资源预测通过：workspace约29.66GiB、Share约41.17GiB、MemAvailable约218.74GiB；不是正式准入。累计新结果4766183693B、总19075760077B；四端各384MiB后，新6GiB上限只余65654515B（62.6MiB），总20GiB余788463667B。必须包含后续回执/metadata并逐次复核；若不足，停止未启动条件，不扩额。预算、旧生成量及源迁移账不归零。

批准后仍须发布逐条件资格、精确修订及输入/config/spec，再由唯一中央控制器执行，最多双路；单路可进则不等双路。每次启动复核source/main/archive/build/native、完整输入、lease、CPU/RAM/Share、5GiB底线＋2GiB监控余量及结果生成量；I/O压力本身不作为停止理由。原2026-10-21北京时间18:00新启动、22:00 intake截止和每端10800秒timeout不变。真实exit0、全指令、64slice及全部科学终验后才能接受。

全部逐候选证据见`DECISION_REPORT.json`、`A2_STATIC_REVIEW.json`及`RECOVERY_COST_REVIEW.json`；两份`*_PROPOSED_MATRIX_32_NOT_ADOPTED.json`仅为可审查提案，中央矩阵/registry/CLIENT均未改。
