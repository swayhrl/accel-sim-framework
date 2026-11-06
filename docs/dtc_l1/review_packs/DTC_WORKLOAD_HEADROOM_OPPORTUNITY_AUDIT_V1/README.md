# DTC-L1 Workload Performance Headroom & Opportunity Audit V1

本包是逐应用已有性能证据审定、Oracle源码/CPU资格和未来执行准备。**本轮新模拟、真实GPU运行、科学request登记、生产Core修改均为0。** 英文LaTeX v0.23保持冻结。

## 已经能回答的问题

- 固定核心32的CH/DH-P0/F128/F256共192格完整接受；32个独立Opportunity Record保留完整输入SHA、实际kernel、原始周期与计数器证据位置。另3项和7项身份未决分别列出。
- 14/32程序在至少一种已测合法干预中出现DH周期减少；18项尚无测得改善。这是逐应用观察，既不是统一方案GM，也不能判定后18项没有架构空间。
- MVT在physical扩容后自身加速1.1332×，仍落后于固定CH-P0。convolutionSeparable和scan的DH-F256自身加速约1.4223×和1.2836×，但此类下游扩容也惠及CH。GEMM在PIB相关扩容后约1.0146×；BICG和2DCONV的结构回退均保留。
- 相同32程序GM CH/DH在P0/F128/F256为1.100072/1.096584/1.098448；两种F配置的相对改善I略低于1。不能把局部正例推广为套件相对优势扩大。
- 当前stock Oracle三路线均不具备直接执行资格：`l2_ideal`在固定源码中无消费路径；Perfect Memory与DTC整行四sector返回协议存在CPU反例；匹配L1理想化机制未实现。所有程序的真实Oracle周期、S/H和严格理论上界仍为UNKNOWN。

## 七项交付

1. [CORE32_HEADROOM_EVIDENCE_MATRIX](CORE32_HEADROOM_EVIDENCE_MATRIX.md)：32程序周期表、完整身份、512条来源角色记录及原始缺失/负例。512是引用角色数，不能当作512次独立实验。
2. [ORACLE_SEMANTIC_QUALIFICATION](ORACLE_SEMANTIC_QUALIFICATION.md)：源码路径、实际改变/保留的资源、CPU反例和资格限制。
3. [WORKLOAD_OPPORTUNITY_CLASSIFICATION](WORKLOAD_OPPORTUNITY_CLASSIFICATION.md)：逐应用已测敏感性、机制假设和未知项。
4. [L1_VS_DOWNSTREAM_HEADROOM_METHOD](L1_VS_DOWNSTREAM_HEADROOM_METHOD.md)：C1/C2/C3、比较集合、指标及禁止推断。
5. [INDEPENDENT_SCIENTIFIC_REVIEW](INDEPENDENT_SCIENTIFIC_REVIEW.md)：独立来源、算术、Oracle语义及合同复核。
6. [NEXT_ORACLE_EXECUTION_GOAL_PENDING_APPROVAL](NEXT_ORACLE_EXECUTION_GOAL_PENDING_APPROVAL.md)：独立新版本工程及严格门控的未来DH合同；当前不注册、不执行。预声明固定8，条件扩展核心32，最多128个明确计划槽位，CH默认预算0。
7. [NEXT_DTC_ARCHITECTURE_PRIORITIES](NEXT_DTC_ARCHITECTURE_PRIORITIES.md)：现有证据支持的架构研究优先级与证伪对照。

## 固定来源与复现边界

StageI `361fa6fa0700825bb9cda43e25b9fd1f60e0b262`；StageII用户指定 `b665d5ea77b5ae022a86cd03c6c464f5b11cb15e`，完整终审补充 `60ccf830553425105d6d5a905e392cc403475f65`。两提交的核心32科学结果压缩包已证明同字节。V2准备 `320b1365902a72502fa61ba114cb4a4a28b934bb`；R1最终结果 `e218746921111d475c6ad8bda8023ad7fe33a33d`。

Core `9eedb3131937748f0492fa83aad37d3691118d70`，Framework `02775fd795cde5aae1480d81cee6eb481d0a08f4`；SM70/V100-derived、64SM、10MiB L2、DRAM850MHz。实际既有binary SHA为 `02a289360b42a573832698c978f21ad2125182a453067a35be60410f1eb8888d`。

CH常规L1为96KiB/768Tags；DH另有16KiB兼容路径及active OO 512Tags/640 physical lines/PIB128。不能把这些结构当成等面积、等时序或单一可相加容量。HtoD更新、初始状态、capture ELF/源码对应及完整应用数值认证保留原限制；完整声明trace不自动等于完整原生应用认证。

AgentA原概述“R1两组合8项均相同”有一句过度概括，本包保留原文件并提供[不可变更正](evidence/A_correction/README.md)：7项相同；scan为6680780与6651571。原始数值JSON/CSV本来正确，没有改动历史结果。

所有机器数据、32个记录、7298个kernel位置及43788条六格kernel证据均是已有结果的派生分析。原始日志、trace、模拟器binary不进入Git。SHA清单绑定公开报告字节，所有缺失不补零，不使用逐程序最优拼接GM。未取得真实Oracle前不报告数值“理论空间”，Oracle反事实差额也不能相加或等同可实现DTC收益。

数据与工作树位于true164独立分析目录：`/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_workload_headroom_opportunity_audit_20261106_v1`。本阶段在新的真实科学执行授权边界停止；不启动Oracle、Tag恢复、capture、109任务或额外结构组合。
