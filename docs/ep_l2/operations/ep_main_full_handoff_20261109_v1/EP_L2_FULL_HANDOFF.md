# EP-L2 Main 完整交接文档

更新时间：2026-11-09，时区 Asia/Shanghai。用途：由一个全新窗口接管现有 EP-MAIN，继续 Performance-First 架构研究。**不是新科学启动授权，也不是重启旧Goal。**

## 1. 接手时先看这一页

- 主机：`ssh hrl-174-new`，先进入 `/root/workspace`。主要科研资产实际位于 `/root/data`，不是 `/root/workspace` 下任意同名旧仓库。
- 项目：`swayhrl/accel-sim-framework`；模拟器Core仓库：`swayhrl/gpgpu-sim`。
- 最新已发布研究基点：`ea480a05fb32eeb6b88dd1d8be1b0b9c89eb8526`，分支 `hrl/ep-l2-next-cost-aware-architecture-20261107-v1`。
- 该基点的上一科学收尾：UMT1 `eae40596cb9a550785a50a3d64617686a6daa160`；再前为V5 `1c63b67beace667ea8a8028d77fbf9e5f2a9afc7`。
- 当前工程目录：`/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1/`。
- 接手快照：无活动模型、无观察到的EP科学supervisor；已批准的近期完整应用均已关闭。部分更早请求的顶层 `RUNNING` 是历史元数据，不能据此认为还有模型在跑。
- 下一步是 **Victim新结构的5点有限申请**：GEMM extension0/1/2三点、Stencil extension0/2两点。全部使用同一新Core/ELF。当前批准、登记、消费均为0。
- 工程已完成，剩余是新范围用户明确批准及Main正式Host/Native/consumer/资源绑定。不要重复整轮CPU、Trace扫描、论文分析来拖延；也不要跳过剩余启动资格。
- 全局EP并发上限是 **10**，以实际CPU/RAM/cgroup/SSD/真164和其他owner承诺动态准入；不是必须凑齐十个才开始，也不是项目总实验次数上限。
- Main是唯一科学调度、预算、验收、Git集成和发布owner。有限临时子Agent可以辅助，但不能建立第二个长期科研Lane、dispatcher或竞争Git写入者。
- 大Trace、大数据和长期归档默认 **真164**；Source KEEP。禁止擅自删除资产、降低他人保证、重试失败、退款或借用旧剩余额度。

本包补充文件：

| 文件 | 作用 |
|---|---|
| `NEW_WINDOW_PROMPT.md` | 可交给新窗口的接管消息 |
| `EVIDENCE_INDEX.json` | 43份主要历史/当前Git证据的路径、blob、SHA256和URL，以及关键本地收据 |
| `SOURCE_LINEAGES.json` | 完整Source5、已接受谱系、样例Spec和实际源码/ELF/lib路径 |
| `NATIVE_REQUEST_SNAPSHOT.json` | 当前52个EP请求的状态、预算、授权/入口引用及进程观察 |
| `NATIVE_ENDPOINT_INDEX.json` | 295个结构化cohort/UUID context，含接受点、失败、Spec、归档和DONE引用 |
| `NEXT_FIVE_POINT_REQUEST_INDEX.json` | 最新5点申请的精确point、输入、Source5和配置引用 |
| `RESOURCE_AND_LIVENESS_SNAPSHOT.json` | 本次资源/boot/mount/进程快照；不是以后启动时可复用的准入 |
| `read_only_preflight.py` | 新窗口第一次只读核对脚本，不注册、不消费、不启动模型 |

## 2. 当前研究目标与组织方式

研究目标已从“解释零detach、整理论文Claim”调整为：**寻找能提高EP-L2真实应用绝对性能、具有明确硬件成本、能够跨输入推广的结构及系统参数。**

工作链是：Workload特征 → 资源限制/浪费 → W/V/M/T机会 → 有成本的结构候选 → 同Source、同硬件背景完整应用验证。

保留正、负和零收益；必要定向归因用于选择下一结构，不恢复大规模论文级逐条Claim收敛。不因默认参数收益小就提前否定机制，也不为了制造事件数不断缩Tag、延长DRAM或增加免费端口。

一个Main负责最终整合。最近A/B/C/D任务分别为：A成本感知Victim扩展，B压力RO收敛，C有时序的CLEAN计数/生命周期，D精确实验请求与执行资格。**这些有限任务已完成，不需要重建它们，更不是四个永久科研owner。**

## 3. 目录、仓库与入口

以下简写只用于本文：

```text
J = /root/data/ep_l2_full_workload_performance_20261027_v1
R = J/research
N = /root/data/ep_l2_dtc_l1_native_v2
L = R/next_cost_aware_architecture_20261107_v1
```

### 3.1 关键实际目录

| 路径 | 内容与边界 |
|---|---|
| `L/main/` | 最终综合、Main独立验收、精确申请、归档和发布回执 |
| `L/agent_a/core/` | 当前Victim扩展候选Core；不是已接受生产Core的自动替换 |
| `L/agent_a/` | A构建、Source5、生产CPU、成本、负例及增量bundle引用 |
| `L/agent_b/` | RO跨输入收敛；本轮请求0个新RO点 |
| `L/agent_c/` | 独立CLEAN协议候选及生产CPU；不能与A混合为一个Source |
| `L/agent_d/FINAL_EXACT_EXPERIMENT_REQUEST.{json,md}` | 当前最权威5点配置、输入、预算和释放条件 |
| `R/unified_memory_taxonomy_20261106_v1/` | 统一访存分类、人口、证据和后续UMT1已接受实验 |
| `R/performance_first_v5_20261105_v1/` | cold过滤、pressure_epoch、3MM三点与最终8项接受 |
| `R/performance_first_v4_20261104_v1/` | Stencil/Transpose、Vector独立补齐、Host资格修复 |
| `R/performance_first_v3_20261104_v1/` | 中等Tag8项接受、最初Vector2项失败及事故修复证据 |
| `R/performance_first_v2_20261103_v1/` | 系统参数族和跨时钟修复族；16接受、2组合未释放 |
| `R/performance_first_20261103_v1/` | Performance-First初期、论文原件待转移状态及早期执行材料 |
| `R/implementation_performance_v2_20261029_v1/` | P1普通请求Tag释放修复、W-only与三臂工程/执行材料 |
| `R/observation_guided_20261029_v1/` | 观察驱动阶段资料 |
| `J/cases/`、`J/control/inputs/` | 原完整工作负载端点、输入binding及接受/失败证据 |
| `N/control/science_authority/` | 真实科学注册表、历史preimage及更新锁 |
| `N/control/qualification_ledger/` | 各cohort的INTENT/DONE，防重复消费的权威证据之一 |

Source78实际源码/ELF路径仍是：

```text
/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/core
/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/framework
/root/data/ep_l2_multiworkload_event_timeline_20261027_v1/build/accel-sim.out
```

Core862及Core812、7b4的实际路径见 `SOURCE_LINEAGES.json`，应以具体端点Spec的 `source_worktrees/binary_path/static_library_path` 为准。

### 3.2 科学入口和authority

```text
N/bin/native
N/activate.sh
N/control/science_authority/NATIVE_SCIENCE_REGISTRY.json
N/control/CURRENT_SCIENCE_EPOCH.json
```

只能通过已登记、精确有界的Native入口启动。历史各族有自己的versioned scoped入口，由真实registry绑定。**不能直接执行某个ELF绕过Native，也不能照抄旧run命令启动新cohort。**

注册表与epoch的SHA绑定必须一致。更新必须持有真实 `REGISTRY_UPDATE.lock`，保留其他request、旧history和科学状态；不要用整个旧JSON覆盖当前共享registry。只读快照不是写权限。

共享Main锁的已用路径：

```text
J/execution_performance_first_20261103_v1/control/ADMISSION.lock
J/execution_performance_first_20261103_v1/control/ARCHIVE_SHARED_WINDOW.lock
J/execution_performance_first_20261103_v1/control/MAIN_GIT_PUBLICATION.lock
```

不同族的私有锁不能替代跨族/共享锁。accept外层串行锁与子进程恢复锁必须不同，避免自己等自己。

### 3.3 本次交接工作树

```text
J/handoff/ep_l2_main_full_handoff_20261109_v1/review
branch: hrl/ep-l2-main-full-handoff-20261109-v1
base: ea480a05fb32eeb6b88dd1d8be1b0b9c89eb8526
```

这是本次独立文档工作树，可作为新窗口的干净阅读/文档起点。它不是新科学Lane或Source工作区。历史V3 review仍停在其最终分支，不要因为目录熟悉就把V3 HEAD当作最新主线。

仓库根 `AGENTS.md` 中2026-10-23的“当前唯一待办/入口只支持某旧cohort”是历史接管信息；按日期与最新用户指令、本交接及真实authority判断，不把旧文字当成当前授权或当前实现。

## 4. Source身份：最容易出错的地方

Source5 = Core commit、Framework commit、vendor pybind11 commit、ELF SHA256、静态 `libgpgpusim.a` SHA256。字段名 `archive_sha256` 在Source5里指静态库，不是某个结果tar的SHA。

| 谱系 | Core | ELF SHA256 | 科学地位 |
|---|---|---|---|
| Source78 | `78f4b59e865b136eede74df74c44c210f5b4ca04` | `78d4e96bb79c776e27146bcf168d7c70cf3897ef9cb84d837d8974fec4c91b8a` | 大量既有S/WV/F正式应用；保持原件 |
| 跨时钟修复862 | `862376f62ab19f9a677abe31c6a422028b44fcd0` | `083aa0d72173e8f27b298a76b88898bf117f44d119379b3e3ef9edd1b7ffa52b` | Vector850/1275/1700及后续W/WV正式接受 |
| 普通请求P1 | `1e07b263ca0879798387d2a712914a914f298775` | `54c3fbba9bb152d1a26539cccb617ac4a3368547a06509f427a202eeda6d8505` | Conv16×8三臂及特定OFF/ON对照已接受；不是全局替代Source |
| cold过滤 | `7b4c06678923153006b0aa7d6b8ca9db4770cda9` | `1f978f9b0f57ddf49041ac2cab86bd9c1576666870f700240e826166500bf7ec` | FWT新Source三点已接受，优化负结果 |
| pressure_epoch | `812fe1e029b4fb09afaf3d8d25d3f909464cc06c` | `a60600a418e6460e7aaf896b62469be0612046d0f4da34ac8c98da2eed3852e1` | Vector、Conv、Scan同Source正式对照已接受 |
| **当前Victim A候选** | `3d3887bb2e8d5073d13b0792ff9116834e89fe2f` | `9db48c06ca64e441b5824071f52e0aa0be50374045fbdcef6cdf5d4469182f86` | Main工程接受，完整应用0、新预算0 |
| 独立C候选 | `40a815dba41a690d2c16a377492fd246a92d5779` | `234bf2ffb98f6be6555091998c8e7bd5560e8c85f1113a470107e9f6e3a8af2a` | 有限生产CPU完成，完整应用0；与A分开 |

除独立C外，上表主要Framework为 `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`，vendor为 `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`。C的配套Framework是 **`d5bf17360d88e058ca3e048651a49fc947540d81`**，不能换回9dd仍称同Source。

另外存在Source92等独立接受context；完整身份见JSON，不自动混入当前基线。早期main61/r4/r5分别为：

- native/main61 Core `d010911e3174a3764791183cd108fe4664ba8731`。
- A2/r4 Core `9243f769620653f2a9d4df5599e9581e9dae6067`。
- E2/r5 Core `1093d2629e3d6a9130ba25b9dd119b6f3e16c092`。
- Tag lifetime参考Core `11c02df1034112013523429894f1f931323adbef`；容量/延迟各阶段实际Source要读各Spec，不能凭参考名字混接。

文档Git HEAD不等于运行Framework HEAD；重新编译也不继承旧ELF身份。Source78、862、812、A、C不能拼接二进制、统计人口、性能对照或资格。当前A的新Source基线必须新测，不用旧Source78的cycles充当mode0。

## 5. 研究历程及应继承的科学结论

### 5.1 历史接管与Tag detach根因

原MAIN、A2/E2及旧Conv T/M控制均已做只读接管。原57次/T0、失败、未完成、后续同raw补接受与独立恢复配对不能改写、相加当新预算或退款。

早期已接受r5：CFD covered RESERVED峰4/16、DWT3/16、Vector3/16；新Tag需求域最高3/16，实际TagFAIL/relieve/detach均0。因此这些精确条件的直接断点是没有真实TagFAIL，不能把独立reuse边际计数乘起来解释“被reuse_seen排除”。SGEMM某旧诊断虽有RO证书，但候选均resident hit、没有RO事务。

同Set新请求、满路RESERVED、可释放RO必须是同人口、同事件联合。Tag全VALID/MODIFIED仍可替换，不等于TagFAIL。detach只解绑Tag，不自动释放旧Payload/descriptor，也不减少其lower包。

后续小几何/真实负载确实出现过detach，不能永远套用“EP-L2全项目detach为0”。应读具体Source、输入和几何。**没有足够证据把detach次数当性能收益。**

普通nonRO请求在preview遭raw-full提前拒绝、到不了后端relieve是已证实现限制。P1补丁使用默认OFF开关和付费query/ticket，不放宽reuse、generation、sector、WAD等保护。Conv16×8同新ELF三臂：F−T362791、Legacy-F367152、Corrected-F364463 cycles；特定观察OFF/ON分别相同。修复较Legacy改善，但仍慢于F−T，不应称为T整体正收益或自动合入Source78。

### 5.2 访存路径与固定延迟

分层研究包含SM/scoreboard、L1/合并/MSHR、ICNT、L2队列/Tag/Payload/Bank、DRAM服务；全GPU平均数不能推断某slice/set满路概率。低L2流量也不必是坏瓶颈。TLB/PTW或缺失阶段不能凭印象归因，具体模型审查见历史报告。

**重要纠错：实际同几何延迟实验有效L0=100 CORE cycles，L1=200，不是30→60。** 30是某注册默认值，实际282项及覆盖配置是100；用户当时“若L0确为30则改60”的条件不成立，没有运行60。不要把旧建议写成实际结果。

`dram_latency`是调度器前固定延迟路径的一部分，另有MissQ、L2→DRAM FIFO、partition credit、FR-FCFS及Bank/返回等待；增加配置值不是扩大FIFO，也不等于请求真实队列驻留仅增加该数值。RO_LOWER_TIME是issued但未ready状态暴露，不是纯DRAM延迟。

该Vector/D几何的100/200下F−T与F分别均为77237/77767 cycles，TagFAIL/T触发均0；增大pending/预约重叠仍不足形成满8路新请求。停止该延迟扫描，不为制造非零继续加延迟。

### 5.3 工作负载扩展、观察与实现审查

已积累完整应用、MS/B0/M0a、LIFE/Tag、FT/TVD/WAD、RO与少量事件时间线资料。应先复用小型接受汇总、manifest和合同，避免重复大Trace扫描、内容Hash、GPU采集。

Lane O V1R2提交 `28c2c66c1a04388654ce65e55b15733568c5c296` 的计量合同持续重要：入口真实到达≠首次队头；事务期间merge≠严格fill前重访；RO人口≠普通MSHR独立地址并发；S的NI不能自动覆盖F/WV。FWT不默认替成RO-F。

Observation/Implementation Round2基点 `0fccabb561cd468251de865343e176791b0b2ee8`、更早 `f29b3e8` 是历史工程阶段，不是新任务已经运行的证据。host-write V3、MSHR64、Source92、P1等各自独立，不偷偷合到当前候选。

### 5.4 V2/V3几何与高频

V2收尾 `f6e39296ef3a4bb26c237119c9c4a67e4667350e`：16项接受、0失败；GEMM组合2点条件不满足，未消费。FR-FCFS256未产生值得继续扩大扫描的收益。

V3收尾 `9c4a1a958f726be1250608b0a3b82c79438d0926`：8项中等Tag接受、2项Vector Host失败。512 Tags/slice的G64×8在FWT/GEMM复现1024项G64×16的S/WV cycles。物理Payload仍1168，不是Data SRAM同步缩容或等面积证明。

| 输入 | REF S/WV | G32×16 S/WV | G64×8 S/WV | G64×16 S/WV |
|---|---|---|---|---|
| FWT |181827 / 178951|169934 / 170225|170266 / 170105|170266 / 170105|
| GEMM |558588 / 550642|548988 / 548988|548988 / 548988|548988 / 548988|

G64×8的WV绝对改善FWT4.9433%、GEMM0.3004%，但S也改善；同几何S/WV只有约1.00095与1.0。不能把容量改善全部归EP，也不能把“64Set下8way足够”推广成所有32×8或所有输入足够。

Core862高频新Source S/F：850MHz77184/77237、1275MHz53910/56038、1700MHz45974/55925。高频属于诊断服务敏感性，不是已校准物理V100。它暴露额外机制开销，而非高频自然释放EP优势。

### 5.5 V4独立补齐与跨输入

V3两次Vector失败因spec漏 `native_boot_id`，实际monitor触发KeyError；还丢失22项Native库/工具pins。Main资格检查漏掉完整启动/monitor合同，不是Core/GPU机制故障。旧失败一直保留，未退款或重跑旧cohort。

修复完成43字段/依赖闭包、124项合成检查和真实私有CPU stub的loader/strace/PID/maps/env/CPU/nice/AS/RSS/管道/退出/syscall闭环；这些不是GPU应用或应用NI。另用V4新预算/新cohort补齐Core862：W_ONLY45446、WV45425，与同Source已接受S45974/F55925构成分解。**“Vector还没补齐”是过期状态。**

Source78 G64×8跨输入：Stencil S4299729/WV4282418；Transpose S200330/WV200972，保留其负WV对照。3MM三点后来全部接受：G64×8 S1666917/WV1662803、WV_REF32×8=1671121。**“3MM WV_REF仍缺失”也是过期状态。**

### 5.6 V5与UMT1收敛

V5授权8点全部接受、0技术失败，新Core参考和OFF/ON配对均在同ELF内。FWT cold过滤：S181827、WV_OFF178951、WV_ON180074，ON较OFF慢约0.6275%；该方向停止，不继续扩散。

压力RO在Core812同ELF内的完整结果：

| 背景 | F_BASELINE | F_PRESSURE_EPOCH | cycles降低 | 激活slice |
|---|---:|---:|---:|---:|
| Vector4M /1700MHz |55925|45425|18.7751%|0/64|
| Conv /850MHz |335088|333789|0.3877%|61/64|
| Scan /850MHz |2224142|2212128|0.5402%|4/64|

Vector的收益体现无压力时回避开销，不证明压力下RO加速。Conv/Scan有真实激活但净收益小。查询减少不等于同百分比关键路径缩短。不同频率不合并平均；WV→F包含RO/M/T及交互，不是T独立成本。Conv的duplicate=1及事件级归因UNKNOWN保留，不隐藏也不凭它宣布已证协议Bug。

UMT1四点全部接受、8次Native完整恢复，最终收尾 `eae40596cb9a550785a50a3d64617686a6daa160`。原V3之后的近期18点均已接受，不能误报仍在等GEMM或旧Vector补齐。

## 6. 当前首选结构与下一5点精确申请

权威文件：

```text
L/main/EP_L2_NEXT_COST_AWARE_ARCHITECTURE_AND_EXACT_EXPERIMENT_REQUEST.{md,json}
L/agent_d/FINAL_EXACT_EXPERIMENT_REQUEST.{md,json}
L/main/MAIN_D_EXACT_REQUEST_AND_CONSUMER_ACCEPTANCE.json
```

Git对应 `docs/ep_l2/operations/ep_l2_next_cost_aware_architecture_20261107_v1/`。本包索引为 `NEXT_FIVE_POINT_REQUEST_INDEX.json`，保留完整输入SHA及配置SHA。

### 6.1 A：付费CLEAN扩展，不扩Data

- 原Base128、mandatory/WAD128不变，另加128项只容纳optional CLEAN的metadata。
- Base淘汰CLEAN时迁移原Payload handle到Ext，不复制Data，不迁移dirty/WB责任。
- 固定G32×8、64Slice、Data1168/slice、四Bank/P1、descriptor512、Line-MSHR128/per-address32；RO关闭。
- 复用一个128项地址比较结构：Base查1周期，真实miss后Ext再查1周期；增加有限indexed Ext读视图及一个更新lane，有row/UID/fanout边界，竞争等待。
- Base选择及同Bank回收费2周期，计入tap、Bank比较、127个64-bit age比较及winner mux。Ext只检查固定RR目标并付费重核，没有免费LRU扫描。
- 增量逻辑row字段128×460=58880 bits/slice，64Slice共460KiB，另计端口/比较器/控制；C++ entry 80B不是物理面积，PPA/关键路径/最高频率UNKNOWN。
- 工程覆盖256个Base/Ext唯一owner及symbolic sector、跨阶段重查、Bank压力前进性、原子/写/缺失sector、ICNT拒绝、reader lease、epoch耗尽和内部WB排空。负例及修复历史保留。
- extension1/2限Tag≤512、CLEAN扩展、冻结assertion-enabled构建；RO、runtime flush、目录已填充后的Host prefill未资格。
- 新增X1 SEGMENT/CONTROL记录；Source-specific consumer必须核对Base/Ext服务与全局Payload role守恒。旧282/Source78 consumer不能直接声称已验收该Source。

| 模式 | 结构/目的 |
|---|---|
| extension0 | 原Base128资源及时序的新Source基线 |
| extension1 | 真实扩展硬件/控制，但关闭Ext保留 |
| extension2 | 与1相同付费硬件，允许CLEAN保留 |

0→1测迁移开销，1→2测同扩展硬件下保留增量，0→2测包含硬件资源变化的净效果。0→2不能称所有硬件相同的纯策略比较。

### 6.2 待授权矩阵

| 独立范围 | point_id | 模式 | 新完整应用 |
|---|---|---|---:|
| GEMM | `NEXT_A_OPTIONAL128_GEMM_WV_EXT0_V1` | WV/extension0 |1|
| GEMM | `NEXT_A_OPTIONAL128_GEMM_WV_EXT1_V1` | WV/extension1 |1|
| GEMM | `NEXT_A_OPTIONAL128_GEMM_WV_EXT2_V1` | WV/extension2 |1|
| Stencil | `NEXT_A_OPTIONAL128_STENCIL_WV_EXT0_V1` | WV/extension0 |1|
| Stencil | `NEXT_A_OPTIONAL128_STENCIL_WV_EXT2_V1` | WV/extension2 |1|

全部同一A新Source、850MHz/L100/FR-FCFS128/G32×8、283项完整配置。GEMM输入SHA `140f6ed3a5cdb1d7183cd4d2acc37b086224a054893ef12d990fdb2d5ea3659b`；Stencil为 `bd0309dfeec5745ba97400978c2c5f1413fa9c604376b3dd97e1dd3d5c8cc146`。

**当前5点提出、0批准、0登记、0消费。** point_id是提案身份，不能把它当已登记可运行cohort。未请求S、RO、CLEAN C、NI、3MM重复、Transpose、频率或Tag扫描。

各点独立释放，可三短两长同时准入；**没有跨族归档/完成门**。V3“先FWT四点全接受再GEMM”是旧范围规则，不得套到本5点。历史GEMM WV约1.257h/点、Stencil约3.714h/点只是排期背景；新结构真实wall/CPU busy未知，正式hard wall需激活前冻结。

### 6.3 批准后的剩余绑定，不要误解为重新做研究

1. 读取用户明确批准内容，分别登记GEMM3、Stencil2的fresh scoped预算，不借任何旧余额。
2. 基于最终A Source、5份283图和真实输入binding生成不可变正式Spec；校验完整命令序列和ordered kernel身份。
3. Main完成最小Source-specific X1 consumer接线、Base/Ext/global Payload守恒、43字段Host合同、22 Native与Host/Trace-child依赖pin、当前boot/mount及全运行图封印。
4. 安装真正精确Scoped Native、绑定runtime/postprocessor和安全路由；不因CPU工程PASS就直接替换共享生产入口。
5. 动态准入CPU/RAM/cgroup/SSD/真164/所有owner剩余承诺；cap10与controller/Native/资源合同一致。
6. 先确认旧owner自然退出，再由Main唯一dispatcher连续执行；无逐点重复审批、无自动扩范围、无失败重试/退款。
7. 每个接受点完整kernel/CTA/instructions、协议/所有权及drain、真164全SHA和两次独立完整Native恢复；正负零全部发布，最后回读远端HEAD。

已完成的A/C生产CPU与Main复放不重跑。除非Source/依赖/范围变化或出现新具体风险，不重新扫描大Trace、不为NI缺口默认申请整矩阵，不强制PPA综合作为本轮共同前置门。

## 7. 独立CLEAN C与其它后备方向

当前C不是旧bf4直接可用版本：Core40a815、Frameworkd5bf为独立工程Source。K1优先，K2仅有限读lane比较；六个depth1注册head共用一个计数提交路径，入口+READ+COMMIT各1周期；净0 CLEAN替换也收费，取消不退READ。任意双非零delta免费合并不成立。

**18/18真实生产CPU已完成**，Main独立复放cache/partition关键用例，并以新Python V2核对16个真实事件快照；不要把已完成测试写成尚未测，也不要把旧Python模型称为生产实现。

支持initial HtoD后一个或多个kernel、跨kernel保留、after-commandlist真实tick清理。after-kernel memcpy、per-kernel flush、RO/NI及任意组合未资格。128行清理含EMPTY行最低384 L2 ticks，完整选择也至少384 ticks加修改；这是保守成本/正确性负参考，不是已证性能优化。**C当前申请0点**，先解决选择成本与完整Host/consumer，再考虑独立cap128/64/0。

Stencil/GEMM是真实Victim服务正例；3MM是后续长输入备选，Transpose保留低机会/负WV对照。不要只用FWT或Vector设计结构，不重复已停止的cold方向，不靠削弱S获得比值。

## 8. 统计、协议与比较合同

- 区分request/transaction/line/sector/byte、entry-arrival/first-head/重复head-cycle、Base/Ext query/response、RO admit/merge/strict-fill-before-revisit。比率必须给同人口分母。
- 联合事件必须实际观测，不能乘独立边际；同窗共现只是相关，不是某个Tag分配失败的因果证明。
- `RO_LOWER_TIME`是issued且未ready累计暴露；S没有RO时为NOT_APPLICABLE，不能补0后与F求均值。
- 等待原因常重叠，不求和当独占GPU关键路径。issued字节不称DRAM完成带宽；Victim响应不等于避免DRAM包数。
- 完整在飞drain不等于末端脏行全flush。`flushL2=0`时必须保留末端边界；无DtoH数值oracle时numeric validation=UNKNOWN。
- S/F是全机制组合；F−T/F才隔离T；W→WV是V包，WV→F包含RO/M/T及交互。增加硬件后要同背景S/EP，绝对cycles与比值分开。
- 同一Mode名、同样cycles、同样源码若不同ELF都不能自动互相接受。S的NI不继承F/WV；CPU NI不继承应用NI。
- fixed111不是“偏差自动抵消”的数学证明。新profile/Source应用NI未测，B0/M0a未证明，保持明确边界；具体新控制干扰风险才局部HOLD并申请最小NI，不自动占用当前预算。
- 新Source283项不是旧282项缺一，必须按实际注册/回显逐项检查。少数历史profile文字标签复用，不能凭label/cohort名推断真实Tag几何；实际Spec/完整echo才是依据。
- 所有结论分PROVEN/LIKELY/UNKNOWN/HYPOTHESIS。工程/构建/producer PASS不是完整应用接受、通用正确性证明、物理GPU校准或PPA证明。

## 9. 人口、工作负载与既有资产

原始统一清单103行 = 96内容组 + 7未决槽位；35代表输入、42目标程序/槽位、53早期SM70家族、118/125输入资产、DTC去重候选是不同口径，不互相替代。

截至本次快照，Native中52个EP前缀请求，结构化端点按cohort+UUID去重为295 context = 290接受 + 5不接受。**这不是295个workload，也不是EP全历史所有启动次数。** 更早integer consumed、兼容singleton、原57/T0等没有被本索引重建；别把原台账混加。统一分类涉及28个接受输入SHA，实际分类适用域与Source要保留。

端点索引保存精确Spec、Source5、input SHA、mode、cycles、DONE和archive refs。全量事务/raw/trace不塞进交接包；需要时按cohort恢复单个必要资产。输入按Suite/版本/程序/内容/完整有序commandlist及kernel身份去重，不仅看程序名，不合并不同尺寸/算法实现。

SM70与Ada/RTX4080、地址语义/RO证书、裁剪输入、未知capture completeness各自保留。不可把DTC可读Trace、旧118输入或EP53程序家族自动提升为Native科学资格；不得重新采集109/4080来完成交接。

## 10. 存储、资源与恢复

用户明确偏好：**大资产放164；如果影响速度需报告实测影响、缓存规模和收益；空间真缺由用户清理。**

```text
输入常用根：/root/share/mnt164/huangrulin/traces/bundles/
长期结果：/root/share/mnt164/huangrulin/host174_storage_recovery/
当前A源码增量/build：/root/share/mnt164/huangrulin/ep_l2_next_cost_aware_20261107_v1/agent_a/
```

真164需验证挂载source为 `admin-wcx@10.208.130.164:/home/shared`，常见fstype `fuse.sshfs`；不能只凭目录名含164就宣称是真164。174只保留必要Core/build、热结果、有限恢复工作集。不要先复制完整Trace到本地，也不重复大内容Hash。

本次快照174可用约19.9GiB，真164约38.6TiB；cgroup memory.max256GiB、memory.current约19.9GiB、cpuset512CPU/CPU quota约384核当量。只是时间戳快照，**不是启动资格或已占有的资源保证**。Swap几乎耗尽也不能单凭它说RAM不足，应看实际RAM/cgroup余量、压力和增长。

SSD按真实增量写入、已承诺未发生写入及适度应急量计算；不重复扣已占用bytes，不把旧35GiB池、9.4GB生命周期上限或每个点整套共享空间当新增。一般小余量原则不能覆盖其他owner已有明确5GiB等保证；当前Native实际floor5GiB应尊重，不擅自降低。

RAM按实际RSS与剩余增长，不把AS上限当物理占用，不重复计同任务budget与现占RSS。识别动态loader下实际模型和strace父wrapper，按PID start_ticks/输入/config/UUID精确关联，wrapper不重复算模型。进程先出现、PID元数据稍后发布时可短暂安全HOLD；不要忽略未知owner，也不要因它杀正在运行的任务。

接受链：自然完成 → 完整身份/配置/命令序列/协议/drain验收 → 真164全SHA关闭重开 → 两个独立完整Native Target恢复 → CLOSED_ACCEPTED → 汇总/发布/远端回读。失败同样保留消费、raw/DONE和negative archive，不用恢复成功把失败升级成接受。

小型工程/文档包的“两次tar恢复”不等于完整应用Native恢复。最新ea480工程包只做了小成员关闭重开检查，明确没有完整lib body恢复；不能为交接美化成做过所有大库恢复。本交接包自身恢复也只证明交接小文件完整性。

## 11. 需要带走的故障经验

1. **Host/schema漏项**：只测静态mode/构建会漏post-fork monitor字段。必填43字段、当前boot/mount、限额、输入、完整Native库/工具和当前Host闭包需在consume前验证；保留真实小CPU进程闭环，不靠全模拟烧预算试错。
2. **不能整体替换pinned_files**：合并新Host依赖时丢失旧库/tool pins会使映射检查失败；也不能盲拷旧91项中的历史Host/pyc/旧路由。按实际Source闭包重建。RO关闭时路径字符串非NULL并不一定读取，查真实T||M gating。
3. **Host trace-child依赖**：实际可能执行 `/bin/sh → /usr/bin/cat` 和系统解释器；应记录当前SHA、resolved path及别名，历史未记录则UNKNOWN，不臆断造成过失败。
4. **共享Native误阻断**：其他owner合法insert-only曾反复阻断EP收尾。不能取消身份验证，也不能任意insert全放行；保留原EP路由、限定授权cohort/handler/模板、原字节与owned图。采用reviewed scoped-entry sealed执行避免校验后共享路径替换。未知/删改/替换/遮蔽仍fail-closed；必要时Main只读复核后做有界Host-only登记，不重跑模型。
5. **资源绑定错名不等于接线**：旧SCOPES未含新请求会unknown-scope。必须真实snapshot验证新Root/CPU/self-claim豁免及foreign去重；不能仅改request字符串称PASS。
6. **CPU/GPU归因**：Host模拟器变慢不是GPU cycles变差；CPU fixture cycles也不是应用加速比。必要hard wall依据真实成本/不确定度冻结，而不是从kernel数或AS限额猜。
7. **旧坏输出保留**：parser读help注释、漏最终`-trace`、cap0 fixture错误前提、stale generated-version TU、活锁ticket及提前busy=false等均有历史负例。修正fixture不能删除生产assert或擦掉原失败。

## 12. 历史资料阅读顺序与查找

优先只读以下顺序，不从所有旧raw开始：

1. 当前综合：`ep_l2_next_cost_aware_architecture_20261107_v1/main/EP_L2_NEXT_COST_AWARE_ARCHITECTURE_AND_EXACT_EXPERIMENT_REQUEST.md`、Main验收、最终5点JSON。
2. UMT1分类：`ep_l2_unified_memory_taxonomy_20261106_v1/README.md`、方法论、选点、统一JSON；再看该目录 `execution_authorized4_20261106_v1/control/UMT1_FINAL_SCIENTIFIC_RESULTS_AND_CLOSEOUT.md`，避免把早期“申请0启动”的README当最终运行状态。
3. V5最终：`ep_performance_first_v5_20261105_v1/execution_authorized8_20261105_v1/control/V5_SCIENTIFIC_RESULTS_AND_COST_AWARE_CONCLUSIONS.md`。
4. V4审批/收尾：`ep_performance_first_v4_20261104_v1/`，具体以Main/activation最新闭合回执为准，README早期HOLD不替代后期接受。
5. V3/V2最终：各 `FINAL_PERFORMANCE_REPORT.md` / `FINAL_SCIENTIFIC_REPORT.md`；原失败、未释放组合、跨时钟修复边界。
6. Lane O：`ep_lane_o_workload_memory_characterization_20261028_v1/{MAIN_HANDOFF,MEASUREMENT_CONTRACT,NI_MATRIX,OBSERVATIONS}.md` 与 `PILOT_GAPS.json`。
7. 全负载：`ep_full_workload_performance_20261027_v1/closeout/` 下最终报告、FIXED8、FOREGROUND、HOST_WRITE、LONGTAIL CURRENT。222接受/110对是旧快照，不替代后来实时数。
8. P1/模式：`ep_main_implementation_performance_v2_20261029_v1/` 与 `ep_main_observation_guided_optimization_20261029_v1/`。
9. Tag/MLP：`ep_tag_detach_rootcause_20261026_v1/`、`ep_tag_reservation_lifetime_20261026_v1/`、`ep_tag_capacity_scaling_20261027_v1/`、`ep_matched_baseline_t_dram_latency_20261027_v1/`、`ep_multiworkload_event_timeline_20261027_v1/`。
10. 最早权威接管：`ep_main_native_takeover_20261023_v1/`、`ep_main_vector_r5_20261023_v1/` 和资产/SM70索引。它们保留历史时间，不取代2026-11最新状态。

以上均相对Git目录 `docs/ep_l2/operations/`。`EVIDENCE_INDEX.json`提供固定Git blob与SHA。若本地旧材料是未物化路径或失效链接，用固定commit的 `git show COMMIT:path` 读原Git对象，**不要修旧链接、覆盖Source或再造原始证据**。

关键代码可从具体Core的 `src/gpgpu-sim/` 追：`gpu-cache.cc`、`l2cache.cc`、`ep-l2-ft-cache.inc`、`ep-l2-tvd-cache.inc`、`ep-l2-tvd-directory.h`、`ep-l2-ro-runtime.inc`、`ep-l2-ro-transactions.h`。行号随Source变化，不能沿用另一个commit的行号作证明。

## 13. 论文与不属于当前主线的事项

论文编辑、Related Work、重绘图和为论文新仿真已暂停。EN-v22是最后用户确认的历史英文母稿；v23/v24是独立审查候选，未晋升母稿。Lane6 EN-v8不能代替v22；历史稿件不含11月新结果。

用户曾从个人ChatGPT Library找回原件名：v22 ZIP `EP_L2_EN_v22_FULL_SYSTEM_SOURCE.zip` 67530200 bytes、PDF `EP_L2_EN_v22_FULL_SYSTEM.pdf` 133529 bytes、revision notes；v24 ZIP `EP_L2_EN_v24_D_SCIENCE_SOURCE_AND_AUDIT.zip` 484419 bytes、PDF `EP_L2_EN_v24_D_SCIENCE_REVIEW.pdf` 133055 bytes，主TeX为 `EP_L2_EN_v22_FULL_SYSTEM.tex`。

本次仅检查约定真164论文目录 `/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_paper_archive_20261103_v1/`，该目录仍不存在。因此本交接**没有闭合原件完整取得、CRC、SHA、TeX/PDF重建关系或论文归档完成**；只保留用户提供的文件身份线索，不把文件名当恢复证明。不重新扫描整盘/个人库，不主动编辑稿件。若用户以后交付原件，另做只读归档，完整ZIP优先164而非普通Git历史。

不干预DTC-L1扫描/模型/dispatcher、SM70资产迁移、109 GPU采集、4080 Trace、其他owner资源和账户工作。误投GPU训练记录不属于EP-L2任务，不继承其执行指令。

## 14. 新窗口第一次接手动作

1. 读本文、最新ea480综合及5点JSON、本包快照/Source索引，核对日期优先级。
2. SSH只读检查当前Native/epoch/registry一致性、模型与controller PID generation、Git远端HEAD、当前资源；本包脚本可辅助，但不能把快照当长期事实。
3. 简短回报：接管的最新基点、当前任务边界、是否有活动模型、5点是否已获新的明确授权、下一件具体工作。
4. 当前未授权则不运行5点、不注册预算；可继续必要的Main绑定准备与用户审批包，不重启已关闭V2/V3/V4/V5/UMT1。
5. 收到精确授权后才完成剩余正式绑定、准入和启动；若发现真缺口，仅HOLD受影响族，继续独立合格族。不要请求用户重新批准已经批准过且仍适用的普通只读/工程工作。
6. 模型、验收与发布保持一个Main。原窗口在交接后不再另行开展科学启动或作为第二个调度owner。

**接管的是尚未结束的整个EP-L2研究主线，不是把所有历史Goal逐个再跑一遍。下一科学决策已收敛到有真实成本、同新Source对照的Victim保留5点。**
