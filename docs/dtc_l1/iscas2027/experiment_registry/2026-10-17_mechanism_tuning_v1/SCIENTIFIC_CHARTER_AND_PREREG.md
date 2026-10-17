# DTC-L1 / ISCAS2027 — 机理补证与参数探索科学合同 V1

日期：2026-10-17。**状态：USER_APPROVED_BOUNDED_RESEARCH_PLAN；不是任何运行成功收据。**
用户同意先从既有合格日志做CPU-only机制补证，并允许规划、尝试有界调参，以争取更好的有证据支撑的设计点。此文将**探索集、指标、门槛和独立验证样本在看到任何新性能前固定**。不改变冻结的论文原结果，不以挑有利输入/参数的方式包装成原主实验。

## 0. 冻结权威与活动边界

- 工作环境为**原174账户/容器**，不是174-new。原Lane A的 `DTC_SERVICE_AND_MODERN_BASELINE_CLOSURE_174_V1` 已正常完成，原执行分支 `hrl/iscas2027-dtc-service-closure-174-v1` / HEAD `f5c37d6edcce832a72cb0830021bffa78df6cc13`。原44行41 strict PASS、0 RUNNING、3个Hotspot HOLD；原12负载中11个合法原三臂完整。独立Hotspot V2五臂、Btree-E六臂已完成，均不替代原输入。原GM12继续未定义。
- 既有源：Framework build `18a68dcccd795f1b6cda75504e9450d00c9cee02`，finite Core `6fba0136f8465b59fe5858a950fa39efb265f654`、binary SHA256 `fe2d2737ebaed01680ebfc2346f727306c8db58ee0ca20b1e1f038056e99833b`，传统Core `6582b9d171330d88b17e8d5294c97704229e3823`、binary SHA256 `4fcac62cd7bdccc5a49cc77950ffc45c60d5fce7c4ee44bba877e1fef2d07ef9`。新执行前均需原174现场SHA重新确认。
- 固定原trace、解析器、Core、binary、C16/C80/C+基线及全部strict收据/失败/科学HOLD。全部新研究独立执行分支、worktree、UUID、原始日志和strict收据；不修改原44行manifest，不恢复或重启原A/B/C/D Goal。现代128KiB DTC HOLD、SpMV/LayerNorm NOT_ADMITTED、2D新输入STOP、LUD不追加。
- 原A的coordinator已自然退出；其他disabled/strict监视进程和lock仍可能在。新运行须先检查实际PID/start_ticks、owner、resource、lock并采取**单一合法执行权**，不得借停掉原监视进程获取许可，不得创建与仍有效authority竞争的持久dispatcher。
- 本轮两个独立窗口：`M`只读CPU消费既有日志；`T`先CPU做参数/资源预检。M通过并提交报告后，T才可以启动本合同预注册的上限7个新模拟器attempt。两个窗口在不同worktree和分支，不共用写目录；没有第二套长期watcher。
- 本合同只对新pilot授予条件性执行权，不允许重调以前的baseline，也不允许另造第三输入解释、修改trace或假装是native/equal-area。

## 1. 三项科学问题

**H1（DTC内部）：** GEMM同实际PIB深度128时，OO128相对IO128是否仍获益？既有GEMM IO256与OO128的均值PIB占用181.05/79.19，并不是同深度控制。

**H2（查找覆盖）：** DTC仍有80KiB物理池和16KiB真实ordinary side array，但当前16KiB逻辑Tag只使128个地址同时可查询。增大映射数，是否在不改变物理池与服务点的情况下改善lookup命中/在途合并，从而降低新下行请求与cycles？这只是待验证假设，不能把每个新地址行直接记为新增可命中的数据字节。

**H3（设计取舍）：** 正例GEMM、回退例Gaussian及独立holdout上，扩大Tag覆盖是否具有一致收益，还是把开销从物理驻留转移到了额外元数据/更高比较成本？本pilot不测PPA，不能因此声称硬件性价比胜过C+。

## 2. 先行M：只读CPU日志补证

只读消费原174已经接受的`stdout`、spec、config、terminal/strict与已有机制表，先固定两项：
- **GEMM正例**：C+ UUID `ba4b73f1-33bc-49ab-9945-f7df3d1a3955`，IO256 `b106a859-3c31-4a7b-949a-bf83cdf17e51`，OO128 `c76bcd36-f912-4854-8d1c-481fbf8f488a`。既有cycles 1,511,333 / 1,457,468 / 1,377,919。
- **BICG回退例**：C+ `f91d33da-730a-4047-998c-566c4fc416c0`，IO128 `87c9040b-1ce7-4166-b68e-38da9bceb1d6`，OO128 `8a5da6ac-ef65-4ca0-b1de-15a69d6ba613`，另核C16/C80/WAIT128既有行。cycles C+25,353,488 / IO12893,312,525 / OO12847,533,116。
- **预留非调参独立样本DWT2D**，仅在形成解释后只读检查；已知C+247,588 / OO237,887。DWT2D的任何新candidate性能在pilot决策结束前**不得运行、不得阅读**。
- 对Tag/pending命中、拒绝原因、MSHR/PIB/physical、下行请求、L2/DRAM量、ready/collect/WB、map-loss/duplicate等字段先建立原始定义表。凡两侧单位、路径、是否含retry、per-kernel reset或计数位置不可对齐，标UNCOMPARABLE或UNAVAILABLE，不制造公分母。credit acquired不是DRAM字节；PIB-full count不是stall cycles；现有零下行cap-full不等于全部下层瓶颈消失。
- 输出METRIC_DEFINITIONS.md、EXISTING_RUN_MECHANISM.tsv、CLAIM_SUPPORT.md、MISSING_FIELDS.md、SOURCE_SHA256.tsv、LATEST_REPORT.md。允许有来源的包装确定性恢复；禁止重跑或改原raw。M中任何原raw身份无法闭合则STOP，而不是用包装文件假装有科学数据。

## 3. 预声明的新实验点（T）

**T0：GEMM IO128 one-arm。** 已有原GEMM OO128与IO256继续原样保留；新IO128只改`-gpgpu_dtc_l1_io_pib_entries`从256到128。保持原full GEMM trace、Core/binary、16KiB Tag、640 physical lines、finite V1、clock/ICNT/L2/DRAM、global cap32768及其他有效选项。需完整strict自然终止；不修改已验OO128数据。用于同深度组织比较，不声称解释OO/C+差额。

**T1：只用OO128的Tag结构探索，共6个attempt，候选全在性能前冻结：**

| Candidate | logical_sets | logical_ways | 逻辑条目 | 覆盖 | 其余 |
| --- | ---: | ---: | ---: | ---: | --- |
| accepted original (read-only reference) | 32 | 4 | 128 | 16KiB | 不重跑 |
| T1-A | 32 | 8 | 256 | 32KiB | 640物理行、OO128 |
| T1-B | 64 | 4 | 256 | 32KiB | 同上 |
| T1-C | 64 | 8 | 512 | 64KiB | 同上 |

每个候选仅在**GEMM、Gaussian**两个固定发现负载各运行完整原输入，总计3×2=6。保留4 Tag banks、1/bank/cycle、现行LD/ST multiplier1、有限服务所有配额、ordinary16KiB、physical640×128B、shared96KiB及所有公共参数。不同ways会增加比较与元数据成本，当前1cycle Tag时间只是探索模型条件，**不能在没有相应RTL综合前推广为可实现的同频性能**。不同sets也会改变Tag冲突映射，需分别归因。不得试logical80或依性能追加其它组合。

原GEMM：OO128 1,377,919 / C+1,511,333 cycles；原Gaussian：OO128 3,798,174 / C+3,379,152。新候选的每个分母只使用已验**相同原trace和未更改对照配置**；若旧对照完整身份不匹配，STOP而不是取近似值。所有负收益、deadlock、资源失败都保留原始收据。

**T0与T1合计最多7个新full simulator attempts。** T不能把早期停止的部分数据叫性能，也不能在GPU运行前修改候选定义。所有6个T1均为探索，不进入原12主图。

## 4. 审核门槛、资源与选择规则

- T先在CPU上核真实`logical_sets`/`logical_ways`受冻结Core配置读取（已核来源 `gpu-sim.cc` opt parser、`shader.cc`构造、`dtc-l1-common.h` tags size=`sets*ways`）。核bank索引、Tag替换、physical generations和RefCnt约束；对全部新候选做静态容量/metadata/合法范围估算和已有directed test覆盖评估。配置或正确性存在缺口则停止相关arm，不为了性能改掉保护规则。
- 必须先生成完整immutable manifest：exact source/input/member/list/ordered-kernel/active-instruction/CPU proof/config effective-options/Core/binary SHA、新UUID、工作负载及pilot/holdout归属；**push+fetch-back在任何新性能出现之前**。新attempt用独立输出，不复用原44行或Hotspot/Btree-derived UUID。若无法在原174以不竞争的authority独立安全派发，STOP交审。
- 安全调度最多2个新simulator并行，且须先确认实际RSS/swap/IO余量、其它项目和锁；必要时降到1个。严禁因为空闲就自行扩大矩阵。失败不自动改参数重试；普通runner/index/manifest包装可确定性修复，身份/科学输入/finite机制变更必须STOP。
- 只有自然exit0且相同full trace / 100% ordered kernels/active instruction / credit/reference/physical/PIB/lower/ordinary排空、实际Tag配置echo、source/core/binary/mode/cap/64SM、输出SHA与11 finite metrics严格PASS的点可进入探索选择。invalid、deadlock、timeout均保留，不能优化性挑掉。
- **探索排序规则固定在看新结果前**：对GEMM、Gaussian分别定义 `R=accepted_original_OO_cycles/new_OO_cycles`，仅取两点均strict PASS的候选。令 `R_min=min(R_GEMM,R_Gaussian)`，`R_g=sqrt(R_GEMM*R_Gaussian)`。只在`R_min >=0.98`且`R_g >=1.02`时认定具备进入独立验证的候选；如多点符合，取最大的`R_g`，近似相同（差<0.5%）选更少Tag数，再选较低ways。不允许按负载各挑一个最佳来宣传通用配置。
- 如没有满足门槛的点，结论是`NO_QUALIFIED_TAG_PROMOTION_IN_T1`。全部结果仍汇报，可以提出有边界的负面机制认识；**不因“曲线不好看”继续扩大扫点**。新IO128无论快慢都如实保留。
- T1结束后先停，向ChatGPT提交完整审查包和是否满足门槛的建议。仅经新审查允许的单个胜出配置才可进入下面holdout；不在本Goal自动启动holdout。

## 5. 后续只规划、未在T1自动授权的分支

- **HOLDOUT**：固定DWT2D（正例）和BICG（强回退例），只对选出的**同一个**T1配置运行OO128全输入，先无条件保留其accepted original与C+；DWT2D轻量可先跑，BICG预计耗时较大，必须基于受理资源预算审。ATAX/GESUMMV不因为结果有利而加入选择后均值。Holdout中意外退化也保留，不调第二套。
- **Service sensitivity T2**：M若找到特定阶段可比的服务压力，可设计一个新增、显式opt-in的单因素点，例如collection或者refill，不应笼统提升所有服务。当前冻结Core的finite服务配额可能不是可配置参数；必须先读代码，必要的新实现另建Core分支、默认关闭、测试+固定baseline同模型公平预算、PPA前提与预注册。**本T1 Goal不授权源修改或T2运行**。
- **Hardware Pareto**：Tag从128增到256/512的元数据、way comparator/bank、SRAM端口、时序必须真实计价；可考虑后续缩小physical pool以测性能—面积前沿，但不能把物理容量变更与Tag变化混在同一因果对照，不能声称“同数据=同面积”。
- **观察者**：若M证明必要字段真的未输出，再单独申请默认OFF observer。不得悄悄修改原解析器/finite/Core或用带observer的新周期替换冻结主结果。

## 6. 论文和交付

探索结果应以`exploratory design-space sensitivity`呈现。只有经过独立holdout和硬件成本审查的一个全局配置，才能考虑更新论文设计点；即便如此也不能回填旧IO/OO原44行、原GM12或跨输入比值。始终报告T1整张候选表、胜出规则和负面测试。源论文机制仍来自原学位论文第4章，不能把已发表材料冒充本次新机制。

固定证据入口：Lane A final `final_closure_v1` / `checkpoint_20261016T2133Z`；原v0.10补证计划 `DTC_ISCAS2027_V0_10_EVIDENCE_PLAN_ZH.md`；冻结Core `src/gpgpu-sim/gpu-sim.cc` 配置行428–436、`src/gpgpu-sim/shader.cc`约4341–4343、`src/gpgpu-sim/dtc-l1-common.h` IO/OO构造。原authorised baseline每一文件与当下执行身份以现场SHA为准。
