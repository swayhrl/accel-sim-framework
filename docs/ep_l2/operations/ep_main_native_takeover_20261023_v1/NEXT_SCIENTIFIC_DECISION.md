# EP-MAIN 唯一当前研究待办（2026-10-24）

本轮Vector r5 Goal已完成，当前没有获准的新完整应用，remaining0。原启动设计与精确来源保留在37fbc6c3ef38ccd7c288771daa3f5afdd1f82705的本文件，以及本轮FROZEN_SPEC/USER_AUTHORIZATION中；不恢复旧Goal、controller或未启动的旧额度。

资产依据：2026-10-24只读清点已完成，18个输入变体/14个benchmark程序；见[workload资产主表](../ep_main_workload_inventory_20261024_v1/WORKLOAD_ASSET_INVENTORY.md)。文件存在、历史接受、native准备和启动授权分别记录。

账户资产范围补充：双账户严格目录核查发现CUDA新增6程序、Rodinia3.1新增14程序家族、Parboil新增候选和PolyBench15程序trace覆盖；完整/裁剪/原生映射及未归属项分开记录，见[最新资产核查](../ep_main_account_workload_audit_20261024_v2/ACCOUNT_WORKLOAD_AUDIT.md)。下一项资产工作是按该表准备候选语义资格，不自动运行、搬运或继承DTC资格。

## 已完成的首要问题

Vector单端真实原生应用接受：250118个RO事务、749882个RO合并请求、1000000个RO请求/响应；687311次structural-eligible head-cycle，其中2385次与新Tag需求真正共现。covered新Tag需求915784次，目标set RESERVED最大3/16；实际生产FT/RO调用域TagFAIL、relieve、detach、detached退休均0。375000次TVD skip的raw维度保持NA。

完整56000000指令、15625 CTA、1kernel/64slice、75039cycles；真实exit0，hardware/ROC1/旧212/r5闭合通过。仅为诊断点，不与旧main61 S形成性能配对。真16444结果文件全SHA及两个native目标恢复完成，源KEEP。详见../ep_main_vector_r5_20261023_v1/FINAL_REPORT.md。

## 下一项唯一科学决策

是否有足够理由继续花一个Conv端点寻找Tag触发，还是先把论文T声明限定为已证功能/条件性机制，并优先补齐W/V的独立因果与端到端吞吐证据？

当前建议先收紧T应用收益措辞并整理证据，不自动启动Conv。现有r5 CFD、DWT、Vector三个有RO的精确覆盖点均未见生产TagFAIL/relieve/detach；SGEMM r4是正向证书但resident-hit/no-RO事务的独立条件。该事实不能推广为所有输入、所有路径或物理硬件均无压力，也不能断言T机制永远无价值。

## 全设计统一清单

| 优先级 | 问题 | 当前证据与下一交付 |
|---|---|---|
| P0 | 论文claim与证据边界 | 将本次零触发诊断加入候选证据表；T功能正确性、条件性机制与真实应用性能分开。EN-v22实物/表号尚未提供，未改母稿 |
| DONE | Vector r5完整诊断 | 本Goal已接受、归档、恢复；1完整应用+1help，0重试，旧57/44/T0与全部失败保持 |
| P1-W/V | 减少copy、victim读服务是否带来净收益 | 复用Conv/DWT W-only/copy-free与FWT完整接受配对及B早期未接受观察，分别保留正负/近持平。新因果验证需同binary同背景V-OFF等精确新设计，不随机扫描 |
| P2-T/M | 独立贡献及未覆盖域 | 旧Conv F/WV_M、F/WV_T同cycles保留；本次诊断新增实际联合负证据。正向输入若需额外控制，单列新cohort，不能借跨binary S/F或空证书对照 |
| CONDITIONAL | Conv r5最后覆盖缺口 | 历史未启动，本Goal未运行。仅在确认能改变科学判断且有精确新授权/预算/准入后提名，不自动继承旧r5余额 |
| P3 | 可移植性和现实吞吐 | MAIN6/7、Btree地址域HOLD、SGEMM独立探索保持。新输入需精确COPY_ONLY、source/capture/numeric边界；wall/IO与模拟cycles分开 |
| P4 | 面积/时序和稿件 | 依准确source/工具/网表出处推进，未测仍UNKNOWN，不把容量oracle当作有限硬件收益 |

只有EP-MAIN常驻。T-OPS按确切资产/存储/入口任务按需调用；大型已批准实验才设置有限临时子Lane，并合并回读关闭。本轮无子Lane、后台扫描或后续实验。

SM70统计补充：四套当前展开资产逐成员header均为70，53程序家族有trace（46常规、7仅裁剪），174-new可读27。逐程序全表、缺口及SDK版本边界见[SM70资产统计](../ep_main_sm70_trace_statistics_20261024_v3/SM70_TRACE_STATISTICS.md)。当前EP仍为Volta基础研究配置，AWMA4080限定基线不自动迁入。
