# EP-L2 / ISCAS2027 review_r5｜六Lane并行与48GiB门槛解释（2026-10-16）

> **原6个Codex Lane尚未接收上一轮review_r4续行消息。** 本revision用于首次下发，**不是重新启动初始Goal**。先阅读同协调分支 `fast_track_2026_10_16_review_r4/PARALLEL_CONTINUE.md` 的各Lane任务，再应用本文件的增量澄清；有冲突时以r5为准，旧review_r3历史科学冻结不变。每窗口只执行与自己Lane相关的部分，先核查GitHub/STATUS/RECEIPT、实际进程/registry、旧174当前free，避免重复或打断正在运行的实验。普通工程问题自行解决，科学身份/资源预算/不可逆操作要升级审查。

## 0. 新证据与当前唯一的两项未解锁门槛

- **Storage-Ops已有独立扩展**：正式V6已发布在Framework `hrl/ops-174new-164-archive-goal-v1` 的 `docs/ep_l2/operations/174new_to_164_archive_v1/AMENDMENT_MULTI_PROJECT_ARCHIVE_V6.md`，发布SHA `837ca9e1a6cf520f14a381416ef65f9b05cc3f83`。**研究六Lane不承担源删除或目标拷贝**；V6仅由两个在运行的Ops窗口消费，加入了DTC-L1活跃项目保护和多项目归档候选体系。
- 目标侧174-new最新 `ffdcc4aef83ce3de631e3f81ebbeb0de466bc64f` 的 `PUBLICATION.json`已确认rev04远端回读，但仍是 `TARGET_READY_AWAIT_S01_READY`：S01/S02没归档没释放、旧174源侧还需独立确认nonce和READY标记消失。源侧已发布 `67b625bb43b69f4241fe4770fb58cd3a13c5020f`，真实旧174的`/workspace`可用空间此前约37.64GiB。两个已有Ops窗口继续完成V5 S01/S02并按V6有界挖掘，不新建Ops执行者。
- **48GiB不是GPU模拟器物理固有需求，也不是六Lane工作的全局启动门槛**。它是本轮**生产构建与正式应用模拟**的冻结保护策略：Lane1唯一R0.1 build要求live workspace free≥48GiB且另外有约2GiB增长余量；Lane5正式实验需live workspace free≥48GiB、available RAM≥64GiB、max2 long sims/8 CPU/32GiB reserve（scan exclusive）及其他项目保护。本review不降低现有准入政策。历史build对象大小或旧二进制大小不能充当本次未知峰值的安全证明。
- 当前公开Lane1候选Core `62dc1d179b5516e68b21b695c7a9c5d0667e9671`（该tree对应Lane1 Core branch发布 `c93d900e1f968a3b69990dc29b78d50fc18f35ac`）；已静态准备但**未编译**，独立资格未通过，旧R0/R1六次完成应用仍因physical-clock/host-warmup缺陷 `SUSPENDED`，Lane5现行正式pair数=0。此项不因V6而改变。

## 1. 六Lane可以**立即轻量并行**，不能将48GiB应用于全部工作

| Lane | 此刻有界可做工作（只读/小补丁/低I/O） | 仍然不能做的事 |
|---|---|---|
| **1：公共Core** | 核对唯一正式R0.1 source/build入口/两修复定向；在不调用全量编译器的前提下核对历史真实build占用和是否有可验证的其它磁盘挂载；可交付单独`BUILD_ADMISSION_ALTERNATIVES.md`，描述历史占用、未知峰值和可行替代方案。 | 不擅降48GiB+2GiB、不绕过`build_r0_1.py`，空间不足不重复尝试编译；不碰Storage-Ops/DTC-L1数据。 |
| **2：TVD** | 以Lane1现有未编译`62dc1d...`精准静态预适配、实际冲突/生命周期审计，交Lane1最小差分；对原`832d...`预适配不要重复制造虚假生产PASS。 | R0.1正式产物未冻结不得抢编译和应用资格。 |
| **3：RO** | 精确静态适配Lane1候选，审视detached fill/sector/Tag generation、host warmup和bank时钟；保留原完整epoch只读oracle和FWT负覆盖。 | 不重抓trace、不改oracle、不启动RO正式仿真或四模式合格宣称。 |
| **4：Ideal** | R1.1独立修复和Tag时间戳的静态审核、18格同binary runner占位与非绑定条件检视。 | 没有R1.1正式binary及Lane5当前资格，18格全部NOT_RUN。 |
| **5：独立资格** | 核对Lane1候选的两条新门槛与原相关回归计划、当前scientific acceptance veto、新key/跑批准入及旧174资源只读分析；不和源Ops重复空间清理。 | 不复制旧R0结果成新性能，不替Lane1编译，不放宽正式应用48GiB和内存/配额。 |
| **6：论文与PPA** | 在r3基础上改新稿、成本字段账、图表和对照论证；将可实现机制的copy/capacity/IPC因果分开，静态重划分/理想化比较写成**条件性计划**。 | 不引用已撤回perf为当前结论，不凭估算编写mm²/mW/STA或大规模新作图。 |

即使本次发表了可行资源替代设计，**也只形成用户待审备选**。正式改变48GiB floor、改变生产构建路径、切换机器、使用164作为编译盘，必须有明确测量证据与用户同意，且保留独立科学资格和run identity。

## 2. 两个项目共享旧174的具体协调边界

- 旧174同时跑EP-L2和DTC-L1；它们的源文件、trace、实验产物、运行状态和有效性属于各自独立研究线。不能把DTC-L1已完成历史研究的raw/trace因本论文赶期而当作“可删缓存”；DTC-L1实际热输出、run registry、正在写日志及之后的holdout一律保护。
- V6允许旧174 Ops**只读发现**包含DTC-L1在内所有有明确owner的冷/旧scratch，174-new同时准备164目标receiver、可恢复归档索引。归档≠源释放；其它项目原始数据默认`SOURCE_KEEP`，没有项目owner及用户对release范围批准不执行源清理。
- 如果DTC-L1活跃I/O或EP-L2/DTC-L1模拟器正在写，源侧元数据扫描需有界低优先级；不要为了空间恢复停止别的科学运行；中央EP-L2正式仿真仍由Lane5独占自身registry，迁移Ops不改它。
- 每次Space真的释放再由Lane5自己容器复测`df /workspace`；没有足够空间先按保守合同HOLD，不因其它五Lane轻量工作已完成便制造人工通过。

## 3. 近期首要里程碑

1. 两个现有Ops窗口完成V5桥接源侧独立absent ACK→S01 READY→164 DEST_VERIFIED→源清理资格→S02；同时各自按V6分工建立大资产候选/164 receiver，不多开传输流。36个Git pack源全部KEEP。
2. 六个Lane按r4+r5并行完毕低成本工作；Lane1/Lane5联合提交**有证据、未自动采纳**的构建空间准入替代评估。
3. 空间真正合格且科学输入身份稳定后由Lane1单独正式编译R0.1并冻结binary；Lane5独立新资格后滚动五负载B16/U_WB16，得到合格pair交Lane6；Lane2/3/4之后按各自独立身份扩展，不抢首批性能。
4. 只提交新的revision STATUS/RECEIPT、输入身份、测试真正执行范围与GitHub回读SHA，不重跑已经冻结的80行校准/旧oracle/历史影子WBUF，不覆盖旧论文或旧run终态。
