# AE 匹配传统缓存 hash 对照：最终科学结果

在预先声明的固定完整 GEMM 与两组既定几何下，AE 保留了更大的组内改善：DTC 周期减少 **22.8967%**，传统缓存减少 **7.6831%**，两种组内加速比之比 **R=1.197314142>1**。这组传统 hash 对照没有消除 AE 的较大组内收益。该结论以表中资源、时序和零增量 hash 时延模型为条件；跨设计结构差异尚未消除，DTC 独有的因果机制与等面积硬件优势仍未建立。

| 设计 | 原索引完整周期 | 匹配 hash 完整周期 | 周期减少 | 组内加速比 |
|---|---:|---:|---:|---:|
| 传统 C+：C0/CM → C1/CH |1,511,333|1,395,216|7.6831%|1.083225106×|
| DTC：D0/DM → D1/DH（AE） |1,071,405|826,089|22.8967%|1.296960739×|

R=(D0/D1)/(C0/C1)=498280466160/416165188879=1.197314142257。R 是两个组内加速比的比值。所有周期为完整运行的 GPU 模型周期；主机墙钟速度不参与收益计算。完整精确分数与四格证明见 [COMPLETE_RESULT.json](COMPLETE_RESULT.json)。

## 匹配合同与保留差异

新缓存索引 B 直接调用未修改的 AE 辅助函数。设 line=addr>>7、S=2^s，开启 hash 的 set=4*(((line>>2) XOR (line>>s)) AND (S/4-1))+(line AND3)。C+ 使用 S=32，DTC 使用 S=64；这是相同 bank-preserving XOR 家族在各自几何上的实例，地址到 set 的函数并不完全相同。低两位 bank 色保持不变，传统数据 bank 函数和完整 block Tag 保持不变。组内全部270项有效选项仅有 hash 项不同：C+ 改 -gpgpu_cache:dl1 的 L→B，DTC 改 -gpgpu_dtc_l1_tag_hash_bankrow 的0→1。

| 合同项 | 传统 C+ | DTC |
|---|---|---|
| 活跃模式 | PAPER_BASE=1 | PAPER_OO=3，K0，AD0 |
| Tag/数据几何 | NORMAL32sets×24ways×128B | logical64sets×8ways；physical640×128B + ordinary sector32×4×128B |
| 建模数据容量 |96KiB|80KiB+16KiB=96KiB|
| 活跃 admission/owner 容量 | baseline PIB256、MSHR512 | OO PIB/slots128、物理/Ref 生命周期 |
| 时序路径 | 现有有界传统 cache，finite_service0 | DTC finiteV1，finite_service1 |
| unified L1/shared 选项 |96KiB|128KiB|
| 自适应 cache 配置 |0|0|

DTC 的通用 pib_entries=8、mshr_entries=32 选项不表示活跃 OO slot 容量；OO 构造和 admission 使用独立的 oo_pib_entries=128。常规 side-array、sector/NORMAL 行为、Tag 容量、PIB、寿命和服务语义均未跨设计完全匹配。统一 L1/shared 选项也不同。建模数据同为96KiB不能证明物理 SRAM、共享端口、总预算或面积相等；原128KiB物理 L1/shared HOLD 保留。hash 不增加模型周期是本轮与已有 AE 共用的假设，硬件组合延迟未实测。详见 [GEOMETRY_INTERPRETATION.json](GEOMETRY_INTERPRETATION.json) 和 [源代码/历史审计](SOURCE_HISTORY_CONTRACT_AUDIT.json)。

所有点使用同一个新 Core2e3bef4364e578cddd0e881c0baace2e51c55930、Frameworkcfd3ff56d7ba6642dab6c7710ec4f6065168174e、同一二进制与库，GCC11.4、CUDA12.4头文件。未声称与历史 GCC/CUDA 构建二进制相同。公共时钟为1410:1410:1410:850。新 Core 仅追加索引枚举/解析/生产 case 与独立资格测试；AE helper 未改。Framework 观察器源码与已接受 AG7 overlay 字节一致。

## 完整性、资源与存储

四次全新启动按 DM、DH、CM、CH 顺序通过 sole174-new epoch2入口执行，四个 UUID 互异，消耗4/4、剩余0。每点为原始完整 GEMM：739,246,080 active-thread instructions、1,024CTA、1kernel，原命令/trace member 顺序完整。每点自然退出0、无 stop_reason，实际 argv、native namespace、source/runtime/config SHA、完整 raw SHA、终态守恒、NATURAL进度、原资源策略均通过。每次严格验收、真164归档及独立174-new ext4恢复完成后才启动下一点，三个间隔均大于10秒。全部资源采样无 STOP，最大采样间隔小于10.18秒；原策略允许的告警被保留，不作为零效应或丢弃理由。

全部四格严格消费者已独立重放，四个不可变归档的全字节 SHA 与独立 native 恢复的**60个文件/目录/链接清单项**重新校验一致。归档目标为 admin-wcx@10.208.130.164:/home/shared 的真164挂载；恢复目标是174-new ext4，不表示在164执行模拟。全部原件 SOURCE_KEEP、source_release_bytes=0。逐点严格/原生/归档/恢复证明位于 evidence/CM、CH、DM、DH；原始 payload 保留在164不可变事务中，入口见 [RAW_RESULT_ARCHIVE_INDEX.json](RAW_RESULT_ARCHIVE_INDEX.json)。完整科学执行审计见 [FOUR_CELL_SCIENCE_REQUIREMENT_AUDIT.json](FOUR_CELL_SCIENCE_REQUIREMENT_AUDIT.json)。

CPU资格保持有界：1,048,576地址观察、917,504 set移动、32个分离碰撞例、4个预期非法几何拒绝；传统线性路径与冻结旧库摘要逐字节一致。额外 entry、构造、元数据、归档门禁和消费者测试均为工程/合成或零kernel资格，不是免费模拟。新四格没有失败点被重试、退还或隐藏。

执行期间有两项公开修订：未启动传统模式的 DTC-only finite_service1 被 CPU 精确拒绝，改为支持的传统时序0，在 D0自然终态后更新仅 C0/C1 规格，D0旧授权原像保留；归档器采用当前注册外部预留加1GiB未知项目余量，保留原7GiB底线、自身1GiB预留、128MiB监控、RAM/挂载/锁/全SHA/恢复校验。科学源码、二进制、已启动绑定和启动预算未因此改变。共享 wrapper 后续增加 COPY_ONLY资产查询 case，experiment/result 的科学委派原样保留。对应原像、应用、资格与发布回读凭证位于 amendments/revision2 与 amendments/outbox_revision2。

## accepted / negative / HOLD 与论文边界

本轮新增 accepted 是四个完整 timing-model 点和条件性 R>1。传统 hash 本身也有正收益，AE 的组内收益更大。新工程负例包括不支持的 cache 几何与错误 PAPER_BASE/finite1 组合的预期拒绝，以及保留的早期构建/配置失败；它们未计为应用科学负效应，未消耗额外完整模拟。

原 AG/BA 及其它机制的 accepted、负例和 HOLD 已在 [原交接状态](../../DTC_MAIN_NATIVE_ONBOARDING_20261023_V1/CURRENT_SCIENTIFIC_STATE.md) 归并，本轮不改其分类。原 GESUMMV/BICG 回退、队列扩大中性/不利结果、有限 DRAM-service 反事实、未准入输入、K1/AC/AF范围等仍按原 tuple 独立保留。原44为41个 scoped strict PASS 加3个 Hotspot admission HOLD；AG8R1仍2次消耗、1个 accepted，Gaussian stdout-cap失败不修复，F=null、O provisional。75/77历史控制文件字节不变，仅当前epoch/登记表按版本更新；旧 source/qualification历史和既有其它请求行未变，49个交接包清单文件 SHA 均相符。

本次只有一个 discovery GEMM、每格一次确定性结果，未建立跨工作负载泛化或统计显著性。跨组差异未消除，R>1尚不能唯一归因于 DTC 结构；原生数值/ISA/一致性、PPA、等面积/等硬件时延均未建立。没有 pooledGM、历史 F 或 Hotspot HOLD 晋升。

英文 v0.23 仍为用户最后确认母版；实际包、路径、SHA及逐行文本/图核对仍缺失。未用 Git v0.18 替换、未修改母版、未晋升更新版本。Zhao Haoyu IO/OO 归属保留，DC/工艺/宏/面积/时序数值不补造。

可供后续母版核对的限定表述：On the fixed full-GEMM trace and stated configurations, bank-preserving XOR improved conventional C+ by 1.08323x and DTC by 1.29696x, with R=1.19731. The result is conditional on different tag geometries, active ownership resources and timing paths; physical equal-area performance, hardware hash delay and workload generality require independent evidence.

## 交付状态

科学矩阵、完整审计、最终审阅/控制/精确运行时恢复包已完成。四个原始结果不可变归档共60个 native 恢复条目通过校验；最终恢复包为23,664,640字节、313个恢复条目，归档 SHA为 `e6dd90a5f5f956dfd4688b3dc093b9b54a073fd0364fdab394ba76521402b1de`，源提交固定为1ee699ae42cbb9a2e04ee6a0e3b51946775bae03。该 COPY_ONLY操作新增0模型、未改科学登记表，全部原件 SOURCE_KEEP。

恢复包 true164 根为 `/home/shared/huangrulin/host174_storage_recovery/174new_archive/20261016_storageops_02/increments/20261023_dtc_aefair_epoch2_results/FINAL_REVIEW_EVIDENCE/a6b62fb21b24ad96da493d419cc330e8bed0344dc48e2d6963c355b8807e4231`。独立恢复位于 `/root/data/dtc_main_20261023_v1/ae_fair_v1/analysis/final_review_recovery/a6b62fb21b24ad96da493d419cc330e8bed0344dc48e2d6963c355b8807e4231`。完整凭证见 [FINAL_REVIEW_ARCHIVE_RECEIPT.json](FINAL_REVIEW_ARCHIVE_RECEIPT.json) 和 [最终交付审计](FINAL_DELIVERY_REQUIREMENT_AUDIT.json)。包内报告的待交付段落是源提交1ee699ae的时点快照；本次后续交付收据明确关闭该链，避免自包含/自引用归档。

科学启动4/4已用完、剩余0；所有模型及原有限控制器均结束。本次完整结果支持给定配置下更大的 DTC 组内 hash 改善，所有跨组物理/因果/论文范围限制保留。未启动额外模拟。
