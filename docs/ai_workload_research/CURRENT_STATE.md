# AI-ARCH｜当前科研协调状态

**快照日期：2026-10-14。执行者：ChatGPT／AI-ARCH Discovery。**

这是GitHub已发布科研结果的导航，不是节点进程监控，也不是GPU执行授权。AI-ARCH本窗口负责Discovery及总体协调；AWMA由原独立主窗口管理；C16为历史证据。方法遵循[协调协议](COORDINATION_PROTOCOL.md)、[问题图谱](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)及[证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。

## 最新SOURCE_ONLY：Round A28｜Rubble场景、CLM软件近邻与静态状态字节账

**执行者：ChatGPT／AI-ARCH Discovery，2026-10-14。** 已完成[独立A28论文和固定源码审查](literature/AI_ARCH_A28_RUBBLE_CLM_AND_GSSCALE_TRANSFER_SOURCE_AUDIT_2026-10-14_V1.md)。本ChatGPT只进行公开原文和GitHub源码研究，**未连接、重启或修改正在下载Rubble的109 Lane M、GPU锁及任何正在执行的A26GR1合同**。A26GR1“正在下载”仅来自**用户状态报告**，不是本窗口的实时节点确认，当前还不能报告该目标已经完成。

- **原始场景**：Mega-NeRF／CVPR2022的Mill19 Rubble为真实无人机废墟场景，正式论文Table1给出**1678张4608×3456原始照片**；GS-Scale固定源4×下采样的目标分辨率1152×864。官方tar为约9.10GiB压缩体，配套作者合并COLMAP。不能把照片包当训练模型/Trace或凭HTTP HEAD宣称输入bytes通过。
- **新增直接最近邻**：[ASPLOS2026 CLM论文](https://arxiv.org/html/2511.04951)与[作者固定CLM-GS@1119a10198b8398a81d4fcad0d5d407f8a330543](https://github.com/nyu-systems/CLM-GS/tree/1119a10198b8398a81d4fcad0d5d407f8a330543)，**同样使用Rubble真实场景**，已研究Gaussian的CPU offload、跨microbatch精确交集复用、双缓冲与CPU Adam重叠、相机重排。作者实验`Rubble4K/bsz4/100k`与当前GS-Scale`1K/batch1/200k`科学工作量不同，**不可直接拿作者时间比较109结果或变更运行中目标**；但它强烈限制后续“新Gaussian Cache/预取”硬件新颖性。
- **源码衍生标称字节，不是实测**：默认FP32/SH3/Adam下，GS-Scale每Gaussian包含GPU几何10、CPU外观49个float；参数与两个Adam moments合计**708 B/Gaussian**（未含grad等），全部59参数/梯度/moments完全物化理论944 B。完整外观H2D＋gradient D2H＋int32 index D2H条件性约**396 B/active Gaussian/step**；index dtype、真实copies、traffic、带宽和wall必须另测。
- **需排除的软件混杂**：`sh_degree_to_use`在前期逐级启用但代码仍传全SHN系数；CPUAdam的`calculate_update_ids`/`update_counter`有对全部N的全局扫描，并显式设64 OpenMP线程。未来必须区分软件冗余传输/CPU扫描与真实不可隐藏的硬件成本，不能以单步可见率或blocking源码行直接推Cache收益。
- **权限边界**：A28只是审查参考；不新增或修改运行中的A26GR1科学合同，不额外下载CLM、安装/启动CPU/GPU或授予新机制。待Lane M真实执行结果归档后独立评审。

**以下A27为原A26G合法STOP的历史审查结论，保持不变。**

## 最新已审：Round A27｜A26G G0存储资格STOP与单Goal修订提案

**执行者：ChatGPT／AI-ARCH Discovery，2026-10-14。** [A27 G0 STOP独立科学审查](reviews/AI_ARCH_A27_A26G_G0_STORAGE_GATE_INDEPENDENT_REVIEW_2026-10-14_V1.md)；[原A26G固定执行`e760f332ed41c609d3d19548f87d90b3f11357d8`](https://github.com/swayhrl/accel-sim-framework/commit/e760f332ed41c609d3d19548f87d90b3f11357d8)，tree `b2165a3fc75ca15c21876a46770e3b03027c8165`。**原A26G已push并STOP，不能用原用户授权直接重启。**

- **合法科学结果**：`G0=STORAGE_BOUND_UNKNOWN_STOP`；`G1-G3=NOT_RUN`；`G4=报告归档PASS`。本项目真实训练0步，GPU模型调用/显存0，真实完整step性能、应用质量、P13硬件资源剩余均**未评估**。旧NequIP/A16/A16R1/A21–A24、C16/AWMA不受影响。
- **A26G确实新增了资产来源证据**：执行侧官方Rubble HTTP HEAD为`9,773,995,561` bytes、支持Range；作者官方Google Drive COLMAP已从控制端解析到`cameras.bin=64`、`images.bin=427,380,490`、`points3D.bin=162,597,265` bytes，共`589,977,819`。但**node109 Google Drive直接连接超时**，三个文件未实际下载或格式/匹配核验，压缩包只获得前后小范围字节，完整scene SHA、tar成员全集、输入相机序列未资格化。不可写`REAL_SCENE_BYTE_PASS`。
- **STOP根因是设计侧存储准入次序而非真实空间不足**：A26G强制`完整gzip tar展开+缩图+新env`在**完整压缩包下载之前**由小metadata证明上界；官方未提供可用的小tar index。`ISIZE`仅是mod2^32大小，首64KiB压缩前缀无法枚举所有成员，猜压缩率不足以得硬上界。此门可由**压缩体已知安全落盘→不解压写盘的完整tar流式扫描→按实际成员尺寸安全提取**解决，但属于新修改授权，不得改写旧A26G STOP。
- **存储实际**：A26G初始同FS自由`144,192,610,304` bytes≈134.3GiB，用户原批准总新增60GiB且任时保留64GiB余量；未发生耗尽，只有新增保守<16MiB。原子任务HTTP body合计`2,143,328` bytes、CPU准备约974s、GPU共享锁只做7.2微秒预检、无CUDA/下载大场景/依赖安装。**独立从固定Git最终tree重算`SHA256SUMS`列20个源码/JSON/MD文件SHA256为20/20匹配**（第21个`SHA256SUMS`本身由commit tree Git blob认证）；164/raw与node直接HTTP状态没有ChatGPT另行测量。
- **唯一新的执行候选**：[**A26GR1完整有界下载/流式tar安全审查＋原G1–G4连续Goal草案**](goals/AI_ARCH_A26GR1_GSSCALE_RUBBLE_BOUNDED_TAR_NATIVE_109_PROPOSAL_V1.md)。仅在用户**重新明确授权**后启动；它保持同一个Rubble输入、固定GS-Scale强软件、原109 RTX4080、GPU非阻塞共享锁及所有原资源限制，跨A26G/R1**累计**计账（25GiB下载、60GiB磁盘且留64GiB、48GiB RAM、24线程、CPU准备4h、GPU锁2h/14GiB）；**另外显式请求**官方Google COLMAP必要时的受控controller中转及完整SHA验证。无需单独再分一个“tar查询Goal”。
- **目前实际许可边界**：`A26GR1_PROPOSAL_ONLY / USER_APPROVAL_REQUIRED / NO_NEW_BRANCH_OR_GPU`。科学STOP必须是实际payload无法合法验证、真实容量超额、作者软件ABI/质量或GPU锁不合格；不得仅因官方无小型tar index强制再陷入同一种工具STOP。即使通过也只能形成有限`EARLY_NATIVE`或`SCOPED_EXPOSED_SERVICE`，不可升级硬件Cache机制。

**下面A26G原“当前已批准但待启动”段改为历史授权快照；其一次性执行已收口，不是现行权限。**

## 历史已执行并STOP：A26G｜单场景Rubble连续门控原生发现（启动前已批准）

**执行者：既有Lane M／node109；科学监督：ChatGPT／AI-ARCH Discovery。** 用户在完整[A26预算与设计](plans/AI_ARCH_A26_3DGS_NATIVE_INVESTMENT_DECISION_AND_SINGLE_GOAL_V1.md)之后明确批准，并要求凡Codex执行**一次给出完整建议**，减少工具问题的往返。因此当前唯一批准的执行入口为[**A26G连续完整Goal**](goals/AI_ARCH_A26G_GSSCALE_RUBBLE_GATED_NATIVE_109_V1.md)与[**用户批准/预算边界记录**](goals/AI_ARCH_A26G_GSSCALE_RUBBLE_GATED_NATIVE_109_APPROVAL_2026-10-14.md)。**批准不等于已启动**，当前`AUTHORIZED_PREPARED_AWAITING_CODEX / NATIVE_NOT_YET_EXECUTED`。

- **唯一科学对象**：真实Mill-19 Rubble，作者GS-Scale固定源`SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`；目标只有强GS-Scale后的GPU/CPU状态交接、未隐藏完整step等待及是否值得进一步资源因果研究。旧A21–A25源审都已STOP；NequIP/V1R1/GreenCtx、C16和AWMA冻结。
- **一次Goal自助连续G0→G4**：官方源/真实COLMAP/预算/完整依赖CPU预检→**仅通过后**下载官方Rubble/合并COLMAP并构建新隔离作者旧软件栈和CPUAdam→线程限额验证→共享GPU锁下真实Rubble完整step功能/应用质量门→仅合格才有限early/条件性late等待诊断→所有PASS/STOP都形成raw小收据、Git提交/remote readback和STOP。普通数据Range、manifest/index、同版本wheel和ABI小问题在上限内`bounded solve-and-continue`，不机械拆多个Codex任务或设置硬编码必停。
- **正式批准预算**：官方累计下载≤**25GiB**；新磁盘总占用≤**60GiB**且保留≥**64GiB可用**；host RSS≤**48GiB**；CPU有效线程总数≤**24**（CPUAdam源码`omp_set_num_threads(64)`需**实际封顶验证**）；CPU准备≤**4小时**；109独占`/data/c16/locks/c16_gpu_campaign.lock`非阻塞、GPU阶段**累计持锁≤2小时**、显存≤**14GiB**。仅一RTX4080、一真实scene与最多3个合法真实训练窗口，**禁止200k完整训练、跨卡/跨场景、新机制和模拟器/NCU/NSYS/NVBit**。
- **科学身份与负结果**：Rubble原tar之前只HEAD约9.77GB；合并COLMAP/相机顺序/展开存储/训练状态尚未实际冻结；用户允许合法下载后产生首次SHA但不能冒称论文原bytes。作者旧Torch/IPEX可能发生`PLATFORM_PACKAGING_BLOCKED`，正常STOP；真实后期必须从头完整训练到达，只有短早期点不得叫late/代表性大Gaussian。GPU-only若OOM只报告容量，不构造时间speedup；GS-Scale的deferred Adam非bitwise同等算法、训练质量须明确约束。
- **执行分支**：`hrl/aiarch-a26g-gsscale-rubble-gated-native-109-v1`独立起点为本轮正式批准后固定协调提交；新worktree和新archive目录。**该分支创建不表示任何节点已经下载/运行**。Codex完成/STOP后推送独立branch，ChatGPT独立科学审查才可能修改协调状态。
- **过门/停止**：缺真正科学payload/授权、空间或资源不安全、软件跨版本必须改数值/算法、线程上限不可控、共享锁忙、数值质量未合格都在本次单Goal内记录+STOP，**不自动生成A26R2或恢复其它任务**。即便发现候选未隐藏等待，也不是P13已资格硬件机制。

下面已完成的A26与A25及所有早轮次均保留为历史研究/预算提案；新执行权限只由此A26G批准记录和完整Goal共同定义。

## 历史已完成：Round A26｜Rubble真实原生实验投入评估与单Goal合同

**执行者：ChatGPT／AI-ARCH Discovery，2026-10-14；全程GitHub/论文/源码只读，无新GPU、安装、场景下载或Codex Goal。** [A26完整投入评估与单一条件执行科学合同](plans/AI_ARCH_A26_3DGS_NATIVE_INVESTMENT_DECISION_AND_SINGLE_GOAL_V1.md)。

- **当前裁决`CONDITIONAL_GO_FOR_BOUNDED_REAL_SCENE_DISCOVERY / NO_GO_FOR_FULL_200K_REPRO / NO_NATIVE_RESOURCE_APPROVAL`**。在A21–A25接受的真实Mill-19 Rubble、强GS-Scale状态依赖、109 Intel host平台和GSArch摘要近邻基础上，推荐**只考虑一条**完整G0→G4门控任务（input/隔离env/功能与质量/真实有限等待时间/STOP），不再拆独立下载、wheel、ABI、小数值和性能Goal，也不立即开发Cache。
- **成本事实**：Rubble原始archive执行侧只读HEAD为**9,773,995,561 bytes**（9.10GiB），作者合并COLMAP SHA、展开后大小未知；109 RAM available快照60–61GiB、可用磁盘134–135GiB，并不证明安装+全scene可fit。Rubble preset**200,000训练步**、densification stop`refine_stop_iter=15000`；两小时做完200k意味着所有工作平均≤36ms/step，109没有该资格。作者当前`{step,splats.state_dict()}` ckpt没有明确完整Adam moments/counter/RNG，不能直接用于真实后期训练step恢复。
- **已有软件包发行入口≠可运行**：PyTorch历史CUDA12.1/2.2.0及IPEX2.2.0 CPython3.10/3.11官方wheel可查，但目标109旧torch2.10+cu126、NumPy2.x与作者入口不一致；Intel官方已经公布IPEX EOL计划。GS-Scale优化版源码显式依赖IPEX优化器，CPUAdam又有硬编码`omp_set_num_threads(64)`，而109为16核24逻辑线程。任何线程调整须算新软件配置身份和质量对照，不可从host变慢推硬件带宽。
- **建议新的封顶预算，尚未批准**：单个真实Rubble场景，外部下载累计≤25GiB、新磁盘≤60GiB并保留≥64GiB余量、主机RAM≤48GiB、CPU有效线程≤24且需实际验证、CPU准备≤4小时、109独占GPU锁累计≤2小时、单任务显存≤14GiB；阶段分开标source/asset/functional/early/late，**不授权完整200k训练**。数据/安装/GPU新使用需要用户明确批准**上述具体预算**后才能创建新执行分支、发Codex指令。
- **科研门**：保留强GS-Scale完整host及可fit的gsplat GPU-only，naive host只是消融；不同软件epsilon、densification/相机/高斯规模不能当bitwise同语义。只有在**真实自然训练阶段**测得强软件后无法隐藏的显著host-state或GPU等待，才考虑下一步资源单变量；短初期运行不能外推后期大Gaussian或达到PSNR时间。
- **所有旧工作冻结**：A21/A22/A23/A24及更早Lane M/T/N均STOP；AWMA/C16/NequIP/GreenCtx权限不随A26研究改变。此提案**没有创建新执行branch或进行远端节点任务**。研究结论不代表P13硬件机制晋升。

下列A25及更早章节为历史已接受科学证据，新的下载/安装/GPU执行尚待单独资源批准。

## 历史已审：Round A25｜A21–A24独立联合审查（四项均已STOP）

**执行者：ChatGPT／AI-ARCH Discovery，2026-10-14。** [A25四份3DGS源/输入/平台与新颖性独立联合审查](reviews/AI_ARCH_A25_A21_A24_JOINT_3DGS_INDEPENDENT_REVIEW_2026-10-14_V1.md)已完成，审计GitHub固定提交、四份报告SHA256、GS-Scale/GS-Cache原始HTML及关键作者源码行。**四项执行结果均独立push并STOP**，当前无运行中的AI-ARCH实验、没有新109 GPU、174模拟器或数据下载授权。

| 任务/节点 | 固定执行commit、实际交付 | 科学身份 |
|---|---|---|
| **A21／Lane T／174-new** | [`9575a674e5aa5af60e5803c07399fb64ae2c8488`](https://github.com/swayhrl/accel-sim-framework/commit/9575a674e5aa5af60e5803c07399fb64ae2c8488)，仅一份Mill-19 Rubble真实场景source/input报告 | `SOURCE_INPUT_CONTRACT_FEASIBLE_PENDING_ASSETS`：原`rubble-pixsfm.tgz`只读HEAD报告9,773,995,561 bytes，真实archive/COLMAP SHA、训练camera列表、合并素材与展开规模未知；不能报告实际scene runtime |
| **A22／Lane T／174-new** | [`3b46ae8f94b5a72d1af4e06d352058bd2140abe6`](https://github.com/swayhrl/accel-sim-framework/commit/3b46ae8f94b5a72d1af4e06d352058bd2140abe6)，一份逐step状态source地图 | `SOURCE_LIFETIME_MAP_COMPLETE_WITH_INPUT_GAPS`：实际GPU常驻means/scales/quats，CPU常驻opacity/SH与相应Adam；GPU cull→blocking ID D2H→host selected H2D→GPU backward→CPU Adam与异步/同步交接。**没有真实等待时间或跨步ID复用率** |
| **A23／Lane N／174-new** | [`c096521d06483517bf6772689e5cc2c513186173`](https://github.com/swayhrl/accel-sim-framework/commit/c096521d06483517bf6772689e5cc2c513186173)，一份GSArch/GS-Scale/GS-Cache硬件近邻反证 | `NO_HARDWARE_HEADROOM_QUALIFIED`：GSArch原出版者仅摘要可及，具体真实/模拟实验组`ABSTRACT_ONLY`；GS-Cache证据为推理渲染，不是训练Adam。当前**未能量化强软件后单物理资源剩余**，不等于已证无空间 |
| **A24／Lane M／109** | [`fc73b042726ef2312cb62bb9204941ec0ac195d5`](https://github.com/swayhrl/accel-sim-framework/commit/fc73b042726ef2312cb62bb9204941ec0ac195d5)，一份只读脱敏109平台报告 | Intel i7-13700、AVX2/FMA、无AVX512，CPU厂商门PASS；旧torch2.10+cu126/NumPy2.x环境不等于作者torch2.2+cu121/IPEX2.2/NumPy<2发行身份，`PLATFORM_VERSION_GAP / ISOLATED_STACK_RUNTIME_NOT_EVALUATED` |

**独立Git核验**：四branch当前HEAD皆等于各提交、相对固定原branch基点`ahead=1/behind=0`且每条仅新增一份Markdown，commit tree与报告Git blob一致；本ChatGPT再次计算四份**UTF-8 SHA256**，A23与执行者提供的SHA完全相同，报告无U+FFFD。执行侧174/109本机资源与工作区清洁据各Lane报告，**本窗口没有SSH二次查询**。

**必须前置的性能混杂**：固定作者`cpu_adam/src/cpu_adam.cpp`确有`omp_set_num_threads(64)`，而109为16核心/24逻辑线程；强软件的线程调度与绑定可能影响CPU Adam等待，不能直接认为CPU硬件带宽饱和。3DGS Gaussian array row index在densification/pruning时不稳定；作者8.28%当步可见比例不是时间Cache命中率。optimized GS-Scale与GPU-only在部分Adam epsilon/动态生灭语义上不严格bitwise等价，比较需完整质量目标而非自造零成本oracle。

**本阶段最终科研裁决**：`A21_A24_ACCEPT_SCOPED / NATURAL_ASSET_BYTE_IDENTITY_MISSING / NATIVE_NOT_EVALUATED / HARDWARE_NO_GO_CURRENT`。保留唯一真实3DGS问题`Q-A20-GS`为**真实输入/强软件后的残余诊断候选**，不为了已做源审就直接下载9.77GB archive、安装作者软件并占用109 GPU。下一次真正值当的独立实验需同时批准一个**完整且单Goal连续执行**的场景identity→隔离环境/ABI→数值与质量→限定原生诊断合同，必须明确下载、磁盘、时间、GPU锁和失败STOP；当前未授权。

**工作方法更新**：用户不要求按固定20小时规划；[协调协议](COORDINATION_PROTOCOL.md)第12节明确优先按**科学依赖**合并工作，一份输入及同预算下source/环境/数值/必要限额测量可在获准后一个Goal连续完成。原20小时队列提前全部交付，原计划的到点重复复审提醒已关闭，不再按20小时人为排期。174 Lane T/N、109 Lane M旧任务历史STOP、C16 Stage A与AWMA独立authority不变。

**下文20小时队列是原启动前历史计划，已经完成，不代表仍待向窗口发送。**

## 历史执行计划：20小时三Lane CPU研究队列（已完成）

**用户指示：接下来20小时无人值守，要求提前准备并行任务与有界自动收口。** ChatGPT已完成[**20小时无人值守总计划**](ops/AI_ARCH_UNATTENDED_20H_2026-10-14_V1.md)与三个独立Lane Goal（旧STOP继续冻结）。此Git记录是**可执行安排而非Codex已启动回执**。

| Lane/节点 | 无人值守唯一已安排工作 | Git与硬预算 |
|---|---|---|
| **Lane T／174-new** | [A21→A22连续CPU/source-only Goal](goals/AI_ARCH_20H_LANE_T_A21_A22_174NEW_V1.md)：先基于既有[A21现实Mill-19场景身份/强GS-Scale基线合同](goals/AI_ARCH_A21_GSSCALE_REAL_SCENE_SOURCE_ADMISSION_174NEW_V1.md)完成单份report、push并STOP A21；随后**仅**在新独立branch执行[A22训练step动态状态寿命source表](goals/AI_ARCH_A22_GSSCALE_STEP_LIFETIME_SOURCE_ONLY_174NEW_V1.md)。正常A21输入Blocked不妨碍A22代码能力审查，但不得伪造真实输入。 | A21 branch `hrl/aiarch-a21-gsscale-real-scene-source-174-v1`，旧起点`d3d5e235db0822a2404e05dcdb705ffc942e70ec`；A22 `hrl/aiarch-a22-gsscale-step-state-lifetime-174-v1`。CPU≤4/RAM≤8GiB，两阶段≤7h，新文件总≤200MiB。 |
| **Lane N／174-new** | [A23真实3DGS硬件强近邻独立原文审查](goals/AI_ARCH_20H_LANE_N_GSARCH_HARDWARE_NEAREST_174NEW_V1.md)：GSArch/GS-Scale/GS-Cache逐真实实验组，区分仿真和native、冷热Gaussian/cache/atomics已解决问题；独立完成一张负面反证与候选。不得和T共享worktree。 | 新branch `hrl/aiarch-a23-gsarch-hardware-nearest-174-v1`，CPU≤2/RAM≤4GiB，6h内STOP，论文总下载≤40MiB且文献来源先只读。174内存或根盘紧张则RESOURCE_DEFERRED。 |
| **Lane M／109** | [A24只读GS-Scale CPU平台资格](goals/AI_ARCH_20H_LANE_M_GSSCALE_109_CPU_PLATFORM_V1.md)：核CPU vendor/ISA、内存/存储余量及已装Python/Torch/IPEX**发行元数据**，判断Intel-only/旧PyTorch ABI差距，禁止Torch import和CUDA。 | 新branch `hrl/aiarch-a24-gsscale-109-cpu-platform-gate-v1`，CPU≤1/RAM≤1GiB，1h内STOP，新目录≤30MiB；GPU锁0、设备kernel0、安装/下载0。 |

**统一STOP与独立性：** 三Lane都只能读取作者公开固定paper/Git源码和合法本机非敏感CPU信息；不开GPU、174模拟器、AWMA/C16、模型/大数据下载或新机制。工程路径、Git ref、manifest、小包装问题在同Goal里`bounded solve-and-continue`，不来回请求用户；科学身份/预算/真实数据缺失保留UNKNOWN或STOP。原Lane T A4/A10、N A4、M A16R1及NequIP V1R1所有正式STOP与raw/164 authority保持不变。

**自动回收**：计划20小时后只对GitHub固定分支/新报告做状态汇总和有范围的审查，**不会替用户SSH运行Codex或启动GPU**。若分支无新结果就明确`NOT_LAUNCHED/NO_DELIVERY`，不可把预建分支称为已运行。完成后用户只需提交Lane回执，ChatGPT复核并决定是否值得真正申请一个3DGS原生实验。

**以下A20和更早章节保留为有范围历史审查结果，不构成本无人值守计划中的GPU执行许可。**

## 历史已审：Round A20｜重新筛选三类AI负载，优先3DGS自然场景

**科研执行者：ChatGPT／AI-ARCH Discovery，2026-10-14。** [**Round A20完整原文、实验组和公开源码审查**](literature/AI_ARCH_A20_REAL_AI_WORKLOAD_REDISCOVERY_THREE_FAMILY_AUDIT_2026-10-14_V1.md)。**本轮没有执行GPU、模拟器、训练、下载模型/场景或启动Codex**。回到现有`P08/P10/P13/P14`问题图谱，避免重复Green Context工具工程。

| Family | A20新增原始来源事实 | 当前科学决定 |
|---|---|---|
| **3DGS真实场景训练** | [ASPLOS2026 GS-Scale论文](https://arxiv.org/html/2509.15645)有RTX4080 Super16GB与真实Mill-19/GauU场景、完整epoch/容量/PSNR/LPIPS对照；单step平均使用8.28% Gaussian（作者限定大场景），Building参数/梯度/优化器状态约占显存90%；GS-Scale原已实现host state offload、GPU frustum、CPU optimizer forwarding/deferred update。公开[代码固定`SNU-ARC/GS-Scale@6471e958…`](https://github.com/SNU-ARC/GS-Scale/tree/6471e958f7e318f4870234d8107e0aa91c2d6932)有GPU-only、naive host、full GS-Scale三条路径。**HPCA2025 GSArch已有Gaussian冷热驻留及原子等硬件近邻**。 | **`Q-A20-GS`优先CPU-only真实场景输入/软件/host平台准入**；尚无109本机训练/硬件headroom，更不是新Cache机制 |
| **MLIP/MD** | 现有Lane M OAM-S/Si静态32帧已真正运行；[NVIDIA ALCHEMI Batched MD](https://docs.nvidia.com/nim/alchemi/alchemi-bmd/latest/performance.html)与[NEMP 2026](https://doi.org/10.1039/d5sc07248d)已有批量MD、CPU邻居表与GPU力计算异步近邻；实验模型/输出/平台与静态OAM-S不同 | `P10_STATIC_NATIVE_QUALIFIED / REAL_MD_TRAJECTORY_MISSING / PARKED`；不因既有batch收益直接重做邻居流水 |
| **HSTU推荐训练/推理** | [NVIDIA/recsys-examples固定源`6b983fc…`](https://github.com/NVIDIA/recsys-examples/tree/6b983fc950ac49bd131e0411d6e72968e9f343bf)提供**16×H100**训练六个累加软件组、Zipf**合成序列和ID**：CUTLASS后302.6 TFLOPS/GPU，加入DynamicEmb cache变296.8，prefetch最后仅310.6，说明缓存/预取未必端到端增益。单L20 inference亦合成输入 | `STRONG_SOFTWARE_EXISTS / REAL_USER_INPUT_NOT_QUALIFIED / NOT_LOCAL_4080_ADMITTED` |

- **科学可辨识性**：3DGS的**给定16GB可训练Gaussian规模和质量上限**、**同工作量完整step/epoch wall**、**达到固定画质的时间**是三个不同分母。作者虽报告RTX4080 Super 9M→40M容量扩展，但那不是本机RTX4080数据或纯硬件效益；其deferred Adam的ε近似也不代表bitwise数值完全相等。不能在缺真实场景与同语义baseline时下载大数据开跑。
- **下一步已备好一个具体、单次CPU源码准入Goal**：[**A21 GS-Scale真实场景/环境资格`](goals/AI_ARCH_A21_GSSCALE_REAL_SCENE_SOURCE_ADMISSION_174NEW_V1.md)，执行候选为原174-new **Lane T**复用窗口，独立新分支`hrl/aiarch-a21-gsscale-real-scene-source-174-v1`，起点`d3d5e235db0822a2404e05dcdb705ffc942e70ec`。**本ChatGPT已准备Git分支但尚未启动Codex**。限定最多8个真实作者source、一个Mill19自然scene的数据identity与最强software/time/quality合同，禁止GPU/源码编译/新环境/scene下载和109/164访问；若数据/平台不合格，source-only STOP。
- **论文价值与硬件STOP**：作者已有强软件GS-Scale、同类GSArch缓存/atomic加速和系统级敏感性。只有将来验证完整训练中强软件之后仍有可归因、可观的GPU/host资源服务延迟且能与active set/数据语义对齐，才可能提出新的体系结构问题。当前`P14_RESEARCH_PRIORITY / NO_NEW_NATIVE_OR_MECHANISM_ADMISSION`。
- Lane M（109）A16R1有限API G1/G2 PASS、G3 SOURCE_ONLY STOP及NequIP V1R1原生结果保持各自冻结；Lane T历史A4/A10、Lane N、C16 Stage A及AWMA独立权威均未改变。GPU锁、164 raw authority继续独立，当前没有新增109 GPU实验许可。

以下A19/A18及更早内容为历史已审事实或历史审批，不因A20研究自动重新启动任何旧任务。

## 历史已审：Round A19｜Lane M A16R1 Green Context有限PASS与G3 STOP

**独立审查执行者：ChatGPT／AI-ARCH Discovery，2026-10-14。** [完整A19固定审查](reviews/AI_ARCH_ROUND_A19_LANE_M_A16R1_GREEN_G3_INDEPENDENT_REVIEW_2026-10-14_V1.md)；[Lane M正式执行提交`6953ac1690b7a905b6000833a879f9164c7c9e43`](https://github.com/swayhrl/accel-sim-framework/commit/6953ac1690b7a905b6000833a879f9164c7c9e43)，tree `5d993895142148886b24e7cc32d3035acf308361`，分支`hrl/aiarch-a16r1-nequip-greencontext-109-v1`已验证HEAD一致。

- **G1 PASS：实际SM89/RTX4080 76物理SM**；一次唯一合法SM分区请求38，实际partition38，Green stream关联`CUgreenCtx`句柄严格相同且资源查询38SM。CUDA12.6 Driver API真实路径通过，属于`DEVICE_GREEN_QUOTA_AVAILABLE`，不是新增物理SM。
- **G2 PASS：实际自有Green stream一个tiny kernel**，256个`output[i]=3*i+11`全部正确，34项Driver API调用均报告CUDA_SUCCESS，当前context恢复、stream/自有资源同步与清理成功。本窗口**独立重算256/256输出**，并重算7份GitHub关键报告文本SHA256全部匹配。
- **G3 `SOURCE_AND_CAPABILITY_ONLY / INTEROP_UNQUALIFIED_STOP`，但不是实机互操作性失败**：固定环境`torch2.10+cu126`报告`SUPPORTED=True`、`_CUDAGreenContext`存在；源码有create/set/pop和外部stream接口。实际G3 runner在不同子进程只做静态与无CUDA初始化的capability读取，**没有调用Torch GreenContext.create/set/pop，也没有运行NequIP AOT/OEQ/ALCHEMI任何GPU操作**；其代码预置`INTEROP_UNQUALIFIED_STOP`。这不能被当作已证兼容或不兼容。
- **G4未运行**，Green配额下NequIP数值/边集合及所有性能结果均未建立（模型计算0、正式计时0）。历史NequIP V1R1科学`ACCEPT_SCOPED_NATIVE_MIXED_RESPONSE`不因这次Driver PASS自动扩展。
- **资源/归档**：执行者报告共享GPU锁1.159878s；子进程maxRSS约735MiB，新增磁盘约2.23MiB，无下载/安装；GPU采样显存0MiB但短命context真实峰值未完整采样、仅明确自有设备分配1024 bytes。164原始28项＋closeout25项读回PASS是**执行侧报告**，本窗口未SSH再次校验大包；执行branch已STOP、旧A16及V1R1文件不变。
- **科学决定**：`ACCEPT_SCOPED_G1_G2 / G3_NOT_RUNTIME_TESTED / G4_NOT_RUN / P13_RESOURCE_HEADROOM_NOT_EVALUATED / GREENCTX_LINE_CLOSED`。遵守本轮一次修订界限，不自动开启A16R2/R3、GPU性能扫参或新机制；若未来独立科学对象确有价值，必须先设计**同一个活的进程**内真正可执行且可撤销的框架互操作canary，再按新科学合同审批。
- **方法学纠偏**：后续凡属于已批准范围内的普通接口、路径、manifest、依赖包装等工程问题，设计Goal时应允许同一轮`bounded solve-and-continue`，预先核目标版本/ABI/驱动，并设置可实际执行的资格门；不能将“需要获取证据”写成**必然STOP的代码分支**再反复开轮。超过科学语义/预算/实际授权边界的情况仍fail-closed。详见[协调协议](COORDINATION_PROTOCOL.md)第11节。

**以下A18/A17及之前段落均为历史批准和科学审查快照；最新Lane M为A16R1已完成STOP。Lane T/N、C16与AWMA旧边界不变，当前没有授权的新GPU、模拟器或Codex任务。**

## 历史已执行并STOP：Round A18｜Lane M A16R1一次定点修复（当时尚待启动）

**执行者：Codex Lane M／109；独立科学审查：ChatGPT／AI-ARCH Discovery。** 用户在A17审查及有界修订提案后明确回复“同意”，现已批准[**A16R1唯一技术合同**](goals/AI_ARCH_A16R1_NEQUIP_GREEN_CONTEXT_109_CORRECT_G1_PROPOSAL.md)及[**2026-10-14批准记录**](goals/AI_ARCH_A16R1_NEQUIP_GREEN_CONTEXT_109_APPROVAL_2026-10-14.md)。状态：`EXPLICITLY_APPROVED / AWAITING_LANE_M_CODEX_LAUNCH / NO_NEW_GPU_RESULT`。

- **唯一技术改动**：不用A16的错误命名`cuStreamGetDevResource`；改用CUDA12.6明文的`cuStreamGetCtx_v2`核实新stream关联的`CUgreenCtx`身份，再由`cuGreenCtxGetDevResource`核实该context真实SM quota，配合`cuCtxFromGreenCtx`及context/stream所有权和清理。先静态核原始CUDA12.6头文件/导出符号。原`A16 G1 STOP`是合同设计缺口，**不等于RTX4080 Green不支持**。
- 原`hrl/aiarch-a16-nequip-greencontext-109-v1`分支仍STOP于`3dfc5826960ada62548183365d5ad7489f89ae12`；新独立分支`hrl/aiarch-a16r1-nequip-greencontext-109-v1`从此固定STOP提交创建，旧V1R1 NequIP科研结果`1f69559…`、164归档与原环境全不动。
- 顺序门仍为`G1 device quota及stream身份`→`G2短小kernel与自有context`→`G3 torch/OEQ/ALCHEMI/AOT全路径流归属`→`G4原Si0/109 NequIP数值canary`。各门失败则STOP、已取得有限合法证据保留。所有阶段都是**资格检查，不产生正式性能数据**。
- **原保守硬预算**：仅node109一张RTX4080，原非阻塞独占GPU锁≤600秒、显存≤4GiB、CPU workers≤4/RAM≤12GiB、本地新增≤512MiB、下载安装=0，一档合法SM quota、一个小kernel、最多两帧五次平均；**不授权**性能SM配额扫参、NCU/NSYS、训练、模型下载、驱动或PyTorch升级。
- 当前GitHub只记录批准和准备，**并未启动Codex、初始化CUDA或检查实时109状态**。若新G1链也不支持，或G3旧强软件无法合法接管，则按有界STOP结束GreenCtx路线，不连续追加R2/R3。

下列A17/A16旧段为已接受历史STOP和原批准快照；最新执行权限仅以本段及本次固定批准文件为准。

## 最新已审：Round A17｜Lane M A16版本不匹配接口STOP

**执行者：ChatGPT／AI-ARCH Discovery（原始Git审阅、7文件哈希独立抽核、CUDA12.6官方文档核对）。** [A17固定独立审查](reviews/AI_ARCH_ROUND_A17_LANE_M_A16_GREEN_INTERFACE_STOP_REVIEW_2026-10-14_V1.md)，[Lane M A16固定执行提交`3dfc5826960ada62548183365d5ad7489f89ae12`](https://github.com/swayhrl/accel-sim-framework/commit/3dfc5826960ada62548183365d5ad7489f89ae12)。

- **A16在G1合法STOP并已完成发布**：0.301507s共享GPU持锁、GPU任务显存抽样0MiB、下载/安装0；76为**设备物理SM数**，实际Green quota=**未建立/null**；没有创建Green context/stream/kernel、数值或任何正式性能点，G2/G3/G4全未运行。164的17 raw＋23 closeout回读PASS是**执行侧报告**，本窗口未SSH重新散列164 binary。
- **设计侧接口错误被确认**：原A16 Goal强制调用`cuStreamGetDevResource`，而NVIDIA官方**CUDA12.6** API并不列出它；Lane M调用`cuGetProcAddress`返回API调用本身`CUDA_SUCCESS`，但`queryResult=CU_GET_PROC_ADDRESS_SYMBOL_NOT_FOUND`且地址NULL，因此依法STOP。**不能将其写为设备不支持Green Context或RTX4080数值失败**。
- [CUDA12.6 GreenContext](https://docs.nvidia.com/cuda/archive/12.6.0/cuda-driver-api/group__CUDA__GREEN__CONTEXTS.html)与[Stream](https://docs.nvidia.com/cuda/archive/12.6.0/cuda-driver-api/group__CUDA__STREAM.html)文档已给出替代`cuStreamGetCtx_v2`查询stream实际`CUgreenCtx`句柄＋`cuGreenCtxGetDevResource`查询对应SM配额的受控来源链，且**两接口均在此次109执行侧有限导出清单中出现**；但新链**尚未运行或批准**。
- [**唯一A16R1修订候选合同**](goals/AI_ARCH_A16R1_NEQUIP_GREEN_CONTEXT_109_CORRECT_G1_PROPOSAL.md)：只替换G1版本错误接口，保留原OAM-S/Si0/109五次均值、旧模型/AOT SHA、原shared GPU锁≤600s/4GiB显存/12GiB RAM/512MiB新增磁盘与0下载、G2–G4严格门与0性能样本；**`PROPOSAL_ONLY / USER_APPROVAL_REQUIRED / NOT_LAUNCHED`**。此候选还明确`cuCtxFromGreenCtx`与current-context保存/恢复和自有stream生命周期。**不创建新的A16R1执行分支，不向旧STOP的Lane M发自动重试**。
- **P13仍`NOT_EVALUATED`**；A16未触发新的SM资源敏感性或硬件机制结论。NequIP先前V1R1 `ACCEPT_SCOPED_NATIVE_MIXED_RESPONSE`、Lane T/N原STOP、C16 Stage A与AWMA独立权威均不改变。

**以下“当前获准A16”的描述是其启动前历史授权快照，已经由本段正式G1 STOP取代；批准只对那次A16有效，不能延续到新A16R1。**

## 历史已执行并STOP：Round A16｜Lane M最小NequIP Green Context API与数值资格canary

**执行者：Codex Lane M／109（仍需用户向Codex窗口发送Goal）；设计审查者：ChatGPT／AI-ARCH Discovery。** 用户已回复“同意”上一轮提出的低成本API与数值canary方案；**只允许本次一档SM配额的受控API/数值资格，没有正式性能采样或新机制。**

- [**唯一Goal V1**](goals/AI_ARCH_A16_NEQUIP_GREEN_CONTEXT_109_CANARY_V1.md)、[固定用户同意与自限预算记录](goals/AI_ARCH_A16_NEQUIP_GREEN_CONTEXT_109_CANARY_V1_APPROVAL_2026-10-13.md)。对象仅原已审NequIP OAM-S/Si canary帧0与109、同AOT SHA、原FP32 model_dtype与FP64辅助常量、5次均值`atol=rtol=5e-5`，不重新下载/编译模型。
- GPU硬上限**10分钟非阻塞共享锁、4GiB显存、12GiB RAM/4 CPU worker、512MiB本地增量、0模型/依赖下载**；锁忙立即DEFER。只用109 RTX4080，限制**一档约半数合法SM资源**、一个绿流小kernel及条件性两帧数值canary。任何不合平台/兼容/身份、无法证明stream所有权或改变软件行为必须STOP。
- 逐门：`G1 CUDA12.6 Green API + actualSM`→`G2 自有绿流kernel及结果`→`G3 torch2.10/OEQ/ALCHEMI/AOT stream集成`→`G4 原模型数值`。**有条件地执行G4；若G3不可证明则直接STOP，不能把Driver API通过写成真实全模型SM quota通过。**
- 建立单独`hrl/aiarch-a16-nequip-greencontext-109-v1`分支和新worktree，不修改旧Lane M V1R1结果`1f69559d…`、其AOT/env/cache，以及C16/AWMA与174 Lane T/N。
- **状态：`USER_APPROVED_NARROW_API_NUMERIC_SCOPE / PREPARED_AWAITING_CODEX_LAUNCH / NO_NATIVE_RESULT`**。ChatGPT只做GitHub准备，没有连接109启动实际CUDA/Goal。
- 最新已接收A15源结论仍是`CUDA12.6_DRIVER_API_EXISTS / Torch210_CUDA126_INTEGRATION_NOT_QUALIFIED`，A16真正新增的证据应来自固定执行receipt；用户没有授权SM quota性能曲线、NCU/NSYS、Qwen模型或新P13机制。

**以下A15及更早轮次为历史已接受结论；不因本次批准被修改。**

## 最新已审：Round A15｜CUDA12.6底层Green Context与PyTorch2.10源码接口闭环

**执行者：ChatGPT／AI-ARCH Discovery；连续source-only（与A14同轮窗口完成，无设备执行）。** [Round A15固定源码接口核查](literature/AI_ARCH_ROUND_A15_GREEN_CONTEXT_CU126_SOURCE_INTERFACE_CLOSURE_2026-10-13_V1.md)。

- NVIDIA **CUDA12.6.0 Driver API**文档已经包含Green Context资源split/create及相关stream API，对8.x明确最小分区量级；不能从现代PyTorch的CUDA>=12.8便利封装推出“底层12.6完全没有”。
- 原109已接受PyTorch**2.10.0+cu126**的固定[`torch/cuda/green_contexts.py@v2.10.0`](https://github.com/pytorch/pytorch/blob/v2.10.0/torch/cuda/green_contexts.py)源码**确实已有条件性Python shim**：仅当`torch._C._CUDAGreenContext`存在才`SUPPORTED=True`；这是早期`GreenContext.create/set_context`接口，**不是**当前PyTorch文档中的`GreenContext(...).Stream()`包装。当前109 wheel是否编译启用、具体driver能否申请SM分区，均**没有实际查询**。
- `torch.cuda.ExternalStream`在v2.10.0也存在，但其合法接管NequIP AOTInductor、OEQ、ALCHEMI和跨流事件/allocator语义仍不合格；不能只因Python API可调用就把旧V1R1观测升级为SM敏感性实验。
- **最终`SOURCE_FEASIBILITY_COMPLETE / NO_NATIVE_ADMISSION`**。A14的C14-01（已有原生Si模型）与C14-02（Qwen0.5B自然模型候选）均PARKED；后续如需真正新结果，必须先独立批准对象/授权GPU小型API与数值canary或新的模型/输入资格，不再重复无限源码版本搜索。
- Lane M、T、N继续原STOP；旧V1、C16/AWMA和GPU共享锁边界不变，0新GPU/模拟器/训练/权重下载。

**下面A14及更早结论为已接受历史来源，不自动启动任何新任务。**

## 历史已审：Round A14｜SM89资源旋钮与负载可行性筛选

**执行者：ChatGPT／AI-ARCH Discovery；全部GitHub与作者/NVIDIA官方文档只读。** [**Round A14完整报告**](literature/AI_ARCH_ROUND_A14_SM89_RESOURCE_AXIS_AND_WORKLOAD_FEASIBILITY_2026-10-13_V1.md)。**没有GPU、模拟器、模型下载或新Codex执行。**

- **找到可研究的资源API，但不是已证明本机工作**：官方CUDA Green Contexts支持给执行流分配SM集合/配额，可在功能保持时测试减少可用SM后的响应。它不会增加物理SM，也会捆绑变化SM附带register/SMEM/算力，L2和DRAM仍共享；不能假装是“只加寄存器”或从少SM线性预测新GPU。PyTorch GreenContext封装要求CUDA≥12.8，与已审109原A9环境的torch2.10+cu126不匹配，兼容与stream执行资格仍未确认。
- **Ada正式能力**：SM89每SM64K×32位寄存器、100KiB共享存储最大容量、128KiB统一L1/shared data cache；`cudaFuncAttributePreferredSharedMemoryCarveout`为L1/SMEM容量互换的**提示**，并非单独增加物理Cache或SMEM，必须核真实配置才是有效对照；SM90限定的TMA/WGMMA/`setmaxnreg`不适用于SM89，但8.x仍有基本异步copy能力。
- **C14-01**：原生已接受的OAM-S 32帧/完整energy-force-stress作为低成本真实输入锚点，旧109结果仍限定`ACCEPT_SCOPED_NATIVE_MIXED_RESPONSE`。其GreenCtx quota接管AOT/OEQ/ALCHEMI整路径未合格、SM受限残余未见，`PARKED_LOW_HEADROOM`。
- **C14-02**：[Qwen2.5-0.5B-Instruct模型页](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)（24层/14Q2KV/BF16/head64）+官方支持Ada的FlashAttention2/SDPA，可作为实际边缘LLM规模候选。但**完整权重SHA、自然token bank、目标执行后端和109整请求正确性均未资格化**；`PARKED_IDENTITY_AND_PLATFORM`，不是下载/执行授权。
- **C16 Grouped W4 Split-K**旧P01规模反转属额外算术/CTA/reduction的软件组织响应，不经本轮升级为P13新机制。所有固定Lane M、T、N旧STOP以及C16/AWMA原权威不变。
- **科学结论：`API_LEVEL_SM_QUOTA_PATH_FOUND / TWO_CANDIDATES_SCREENED / P13_HARDWARE_RESIDUAL_NOT_ESTABLISHED / ZERO_NATIVE_ADMISSION`。**
- **后续Round A15建议（执行者：ChatGPT／AI-ARCH Discovery）**：只读核低层Green Context driver合约与现有PyTorch/cu126集成断层、强后端实际stream要求，先选一个科学对象；任何109实机API查询/性能、版本升级、权重下载、NCU/模拟器或holdout均须重新明示预算与授权，不能自行启动。

**下面Round A13及更早轮次为历史已接受结果/旧提议，不构成新执行许可。**

## 历史已审：Round A13｜片上状态寿命与寄存器资源最近邻审查

**执行者：ChatGPT／AI-ARCH Discovery，连续source/literature-only（未启动Codex/GPU/模拟器）。** [**Round A13原始论文/官方PTX定点审查**](literature/AI_ARCH_ROUND_A13_ONCHIP_STATE_LIFETIME_STRONG_SOFTWARE_CAUSAL_AUDIT_2026-10-13_V1.md)。与A12使用相同窗口连续完成，以减少纯ChatGPT阶段的重复审批。

- **Tawa** H100真实GEMM（K=16384）§V-E：aref的SMEM buffer深度D与WGMMA pipeline深度P（D≥P）形成tradeoff；P1→2通常改善、P3因register/SMEM/liveness引起occupancy/吞吐退化。作者已经使用cooperative warpgroup、persistent和强cuBLAS/FA3对照，不是新的空白。
- **Twill** H100/B200真实FMHA backward：Hopper给定tile+register限制下不支持跨iteration的更深ILP，solver重获FA3类似策略；B200理论可行的两warpgroup方案在ptxas下spill，减register budget后得到三warpgroup、接近FA4方案，但作者同时指出atomic reduction/bandwidth会成为后续瓶颈。属于作者有范围软件/硬件约束，不是寄存器扩容实测加速。
- **MPK** OSDI26真实LLM离线推理与源描述：SM级任务/事件调度、**paged SMEM已按task生灭重用**；per-thread寄存器仍按mega-kernel中最大task需求静态占用。**没有直接报告“只去掉reg最大值”能提升完整wall多少**。
- **硬件重要反证**：[NVIDIA官方PTX `setmaxnreg`](https://docs.nvidia.com/cuda/parallel-thread-execution/#miscellaneous-instructions-setmaxnreg)可在**SM90a及部分更新架构**的每CTA register池中动态调节warpgroup配额；**SM89/RTX4080不支持**。不能把“任何GPU缺少动态寄存器再分配”作为新机制，也不能把CTA内重新分配当作物理扩容/提高CTA级occupancy。
- **唯一`Q-A13-01`**：MPK持久异构task的最大寄存器需求是否在已有paged SMEM/动态CTA内reg重分配/强软件重选后，仍造成真实可量化的轻任务占用及完整wall损失？`PARKED_NEEDS_NATIVE_RESIDUAL_AND_PLATFORM`，当前只有结构限制+外部局部kernel资源权衡，没有该对象真实剩余墙或合格SM90对照，**不准入硬件机制、新GPU或模拟器任务**。
- **后续Round A14建议（执行者：ChatGPT／AI-ARCH Discovery）**：只读筛选SM89本地真正可运行、强软件之后仍有物理单变量资源可辨识的候选；若无则停止当前平台P13实证路线并重新评估独立Hopper/仿真资源资格，而不是再扩大NequIP batch或重启C16/AWMA。
- Lane M（109）、T（174-new）、N（174-new）继续STOP；原V1/Stage A/R27R3权威不改；0新109 GPU、174模拟器、164大raw、Codex/模型下载、holdout。

**以下Round A12及之前记录是有范围历史接受事实，而非新项目执行授权。**

## 历史已审：Round A12｜跨负载任务粒度与硬件资源可辨识性

**执行者：ChatGPT／AI-ARCH Discovery（GitHub source/literature-only，无Codex/GPU）。** [**Round A12固定研究报告**](literature/AI_ARCH_ROUND_A12_CROSS_WORKLOAD_GRAIN_RESOURCE_IDENTIFIABILITY_2026-10-13_V1.md)。

- **P01有限成立**：Lane M `1f69559d…`的RTX4080/OAM-S真实32帧，CPU B2=20.758ms、GPU B2/4/8=26.044/13.548/7.602ms；软件组织与批次数选择对完整energy/force/stress wall具有强响应，三进程/144样本已在A11独立复算并核数值。四臂不构成纯物理资源扫描。
- **新增`OUR_DERIVATION`，仅数学参照非硬件oracle**：保持G2每调用整组平均成本不变时，G4/G8按8/4次调用推得13.022/6.511ms，实际13.548/7.602ms（比分组比例参照分别多4.04%/16.76%）。说明改善接近批次数比例，而非出现需假设SM/Cache机制的额外收益；也不能证明全部来自CPU launch，因单次形状、图构建、模型kernel选择同时变化。
- **跨负载反例**：C16已审`a3a36e64…`的GROUPED W4 Split-K在M1/16/32使用Split8更快，M64 Split1反超4.93%；它增加CTA并产生额外reduction，与M缩减批次调用具有不同干预身份，不能拼成同一“资源扩展曲线”。
- **强近邻已审核对**：NanoFlow纳米批次异构重叠、MPK SM级持久任务、Bullet SM配额、Kitsune资源模型与Tawa/Twill SMEM/register流水均已有作者限定范围证据；**原生真实时间、局部kernel、模拟器模型和当前source检查不可混成统一实测**。
- **唯一候选`Q-A12-01`**：强软件任务组织选优后是否仍存在单一物理资源敏感的剩余wall？**`PARKED_RESOURCE_AXIS_NOT_IDENTIFIABLE`**，原因：M缺CPU B4/B8的成熟对照，M/C16均缺物理资源R的受控单因子干预、跨负载统一时间与独立样本。明确`NO_NEW_NATIVE_OR_MECHANISM_ADMISSION`，不是当前可执行Goal。
- **建议下一轮Round A13｜强软件后的片上状态寿命与资源因果缺口定点精读（执行者：ChatGPT／AI-ARCH Discovery）**：仅选Tawa§V-E、Twill§6.3、MPK§5.3/7逐实验组核register/SMEM生命周期与实际时间上限，最多一张可证伪问题卡；若最近邻覆盖充分或缺资源单变量则PARKED；0新109 GPU、174模拟器、Codex或新holdout。
- **Lane**：M／109 Round A9与T／174 Round A10均STOP、M原V1独立STOP不变；N／174旧源审STOP。C16 Stage A、AWMA科学authority及所有既有资源锁边界保持不动。本次只更新GitHub科研笔记与协调导航。

**下面Round A11及更早轮次保持为历史已审证据，而非当前待执行阶段。**

## 历史已审：Round A11｜Lane M原生结果与Lane T训练源审联合科学审查

**执行者：ChatGPT／AI-ARCH Discovery。** [固定联合独立审查](reviews/AI_ARCH_ROUND_A11_LANE_M_T_JOINT_INDEPENDENT_REVIEW_2026-10-13_V1.md)；当前两Lane均**已完成并STOP**，且没有获准执行的新109 GPU/174模拟器任务。

| Lane | 固定执行提交 | 独立科学裁决 |
|---|---|---|
| **Lane M／109，Round A9 V1R1** | [`1f69559df4f51290589de72876f36a756c5439f0`](https://github.com/swayhrl/accel-sim-framework/commit/1f69559df4f51290589de72876f36a756c5439f0) | **`ACCEPT_SCOPED_NATIVE_MIXED_RESPONSE`**。固定OAM-S模型+32 Si真实静态帧，3 fresh processes×12完整blocks=144原生wall样本，四臂均通过num/edge/compiled资格。整组中位C2/G2/G4/G8：**20.758/26.044/13.548/7.602ms**；36对block下C2→G2变慢约25.48%，GPU G2→G4/G8时间下降约48.07%/70.86%。本窗口独立复算全部144行时序/108个配对比与7个Git小文件SHA；属**软件组织响应**，不证明物理SM/Cache/带宽瓶颈。 |
| **Lane T／174-new，Round A10** | [`859eb16a51c7bf085d6e39a9000de198c0f4e710`](https://github.com/swayhrl/accel-sim-framework/commit/859eb16a51c7bf085d6e39a9000de198c0f4e710) | **`ACCEPT_SCOPED_SOURCE_ONLY_NO_VALID_SMALL_TRAINING_PAIR`**。直接源审TorchTitan GraphTrainer已有SAC、offload和MoE paged stash；当前配置C4未固定真正token bank、没有RTX4080单卡合法完整训练步的证明。不存在新training GPU Goal资格；不否定其它公开小训练模型。 |

- **Lane M现为`NATIVE_QUALIFIED / MIXED_RESPONSE / NORMAL_COMPLETION_STOP`**；原Round A8 V1 `ENVIRONMENT_BLOCKED/NOT_EVALUATED`独立终态不变。164 raw **444项**和closeout **30项**由执行者报告readback PASS；ChatGPT未SSH独立复核164实际raw，仅GitHub固定小包与原始时序复算。
- **Lane T**当前A10完成/STOP，历史A4仍STOP；原Lane P仅是尚未启动时拟议名称，新任务实际上在174复用**Lane T**执行。Lane N（174-new）旧报告完整性问题及历史STOP不变。
- **优先科研解释**：NequIP响应主要是提交粒度、构图与完整评估的**P01工作量组织**；没有可从四点直接晋升的**P13单变量物理资源扩展**。训练线有强软件近邻，不应再开发朴素offloader。
- **建议下一步Round A12｜跨负载资源约束可辨识性与候选收敛（执行者：ChatGPT／AI-ARCH Discovery）**：优先source/literature-only，利用新原生M数据与旧限定证据，给最多一项真正能区分批次摊销与硬件资源约束的候选；不自动做profiling、更多GPU、新机制或模型下载。新执行需独立合同和明确权限。

下面A10以及A9“正在执行/已批准/等待”均保留**当时快照**，最新完成状态以本段为准。

## 历史并行安排：Round A10｜训练资源生命周期源码与论文对照

**执行者：ChatGPT／AI-ARCH Discovery（原文与因果审计，已完成）；拟执行：Codex Lane P／174-new（独立CPU/source-only，尚未由用户启动）。** 109 **Lane M**的已批准V1R1由用户报告正在执行，**不干预、重启、改GPU锁或改变数据合同**。当前ChatGPT不能核验Lane M实时进程。

- [**ChatGPT本轮实际研究报告**](literature/AI_ARCH_ROUND_A10_TRAINING_RESOURCE_LIFECYCLE_NEAREST_WORK_2026-10-13_V1.md)：2026-06-23 PyTorch Graph-based CPU Offloading官方报告的8×H100真实训练实验组、2026-10-09 SlackSwap作者arXiv**摘要级**A100 trace-driven仿真、固定TorchTitan 2026-10-13 GraphTrainer source强能力与MoE paged-stash；不把文献模拟/源码升级为RTX4080性能。
- **重要近邻**：TorchTitan固定源码已有`sac_and_offload`和`sac_and_paged_stash`，后者移植Megatron-Core 0.19.0且用于静态capacity padded MoE。普通activation offload/prefetch和capacity-padded共享页本身并非待发明硬件空白。
- **P13因果要求**：同策略固定时的真实资源响应，与每一硬件点重新优化强软件之后的响应必须分开。单卡改budget/seq属于P01负载/软件变化，不是单变量扩SM/host-link实验。没有新GPU授权或硬件机制晋升。
- [**Lane P／174-new单一独立Goal**](goals/AI_ARCH_A10_TRAINING_LIFECYCLE_SOURCE_AUDIT_174NEW_V1.md)：冻结公开`pytorch/torchtitan@8a75afd90773fe410340e0709b0b1af427c4af58`，审≤10处source的训练输入、GraphTrainer lifecycle及小规模真实训练pair可行性。独立分支`hrl/aiarch-a10-training-lifecycle-source-174-v1`；**本ChatGPT未启动Codex窗口**。不得访问109 GPU或164、运行模型/模拟器、安装环境。
- 预计下一步：Lane P固定报告回来后，ChatGPT独立核其强软件/自然输入/容量准入；Lane M的V1R1结果独立审查，两线互不构成授权。若新训练pair不成立，明确STOP；不得为了多窗口并行制造实验。

**下面的A9“执行尚待窗口启动”为写入当时的审批时点，不可据此否定用户随后报告Lane M已运行。**

## 已批准的Round A9历史执行许可（批准时尚待窗口启动）

**用户2026-10-13明确批准两个阶段：A＝官方原版本ANTLR源码包的一次受控本地wheel构建；B＝仅在A以及其它已冻结依赖门合格之后，按V1原科学参数与剩余累计预算恢复109 GPU观察。** [固定审批记录](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1_APPROVAL_2026-10-13.md)、[完整V1R1方案](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1_WHEEL_EXCEPTION_DRAFT.md)及[原V1合同](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1.md)为本次执行依据。

- 运行执行者：**Lane M／node109独立新worktree**；准备独立分支`hrl/aiarch-nequip-static-batch-109-v1r1`，起点为原V1正式STOP提交`06674a961632c107681ac146d735d932dde112d6`。原V1 STOP、原164归档及前轮资源消耗不能覆盖或清零。
- `EXPLICIT_APPROVAL_V1R1_A_AND_B / AWAITING_LANE_M_LAUNCH / V1_STOP_PRESERVED`。本ChatGPT仅记录批准与准备GitHub，**没有登录109启动Codex、安装任何wheel或初始化CUDA**。是否真的运行须依用户/执行报告。
- 唯一打包例外是官方`antlr4-python3-runtime==4.9.3`固定同一sdist SHA的一次CPU构建；不得换版本、使用第三方wheel或擅自处理第二个源码包。
- 原四条件N-C2/N-G2/N-G4/N-G8、数值/输入/强软件基线、GPU锁和STOP仍冻结；原累计依赖下载8GiB上限减前轮保守消耗3,333,112,827 bytes，**余5,256,821,765 bytes**，其它资源原V1预算不重新计起。
- Lane T、Lane N（174-new）、AWMA、C16全部继续原独立任务状态。只有具本次确切许可的Lane M能进入本轮。

下面的Round A8停止审查和更早“拟议/已启动”描述保留作为历史，不应覆盖此新批准状态。

## 最新已审：Round A8｜Lane M依赖wheel门STOP（执行者：ChatGPT独立审查）

**当前接受的科学状态：`V1_ENVIRONMENT_BLOCKED / NOT_EVALUATED / COMPLETE_STOP`。** [Round A8独立审查](reviews/AI_ARCH_ROUND_A8_LANE_M_ENV_STOP_INDEPENDENT_REVIEW_2026-10-13_V1.md)已在固定[执行提交`06674a961632c107681ac146d735d932dde112d6`](https://github.com/swayhrl/accel-sim-framework/commit/06674a961632c107681ac146d735d932dde112d6)和公开PyPI官方发行上核对停止依据。执行分支`hrl/aiarch-nequip-static-batch-109-v1`保持STOP，**不自动恢复、重启、merge或修改旧receipt**。

- 受控解析锁定82个发行包，`antlr4-python3-runtime==4.9.3`的**PyPI官方wheel缺失**触发V1预冻结wheel-only STOP；官方sdist存在且hash相符。轮子缺失不是模型加载失败，也不是Python包被证实不能安装。
- **四条件N-C2/G2/G4/G8全部0计时样本**，0正式进程、0数值/边集合/compiled资格；不能给性能排序或新硬件现象。
- 执行者报告模型/Si字节身份PASS，109 GPU锁占用/正式观察/峰值显存为0；依赖下载保守计约3.11GiB、wheel阶段RAM峰值约92.6MiB，但全部resolver阶段RAM峰值未测。164归档通过是执行侧报告；本窗口GitHub抽检5份关键文件SHA通过，不宣称现场重算164全部raw。
- [**Round A9候选V1R1合同**](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1_WHEEL_EXCEPTION_DRAFT.md)只提出从**原官方同版本sdist**有界构建一次本地wheel并继续原参数/预算下的资格；**尚未获得新的GPU/依赖打包例外批准，未创建V1R1执行分支**。不允许换4.13、随意降低数值门或从第三方wheel补包。
- Lane M（109）现已STOP；Lane N（174-new）非LLM旧审查与Lane T（174-new）训练旧审查仍STOP。C16 Stage A、AWMA R27R3旧科学结论及独立管理边界不受本轮影响。

**下面A7/A8批准与启动段落保留为历史时点记录，其“当时待启动/已启动/待审批”状态都已经由本段A8正式STOP取代。**

## 历史授权：Round A8｜109静态结构有限观察（当时已批准、用户报告已启动）

**用户于2026-10-13在本AI-ARCH窗口明确同意A7提出的整份A8合同及资源硬预算。** [固定批准记录](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1_APPROVAL_2026-10-13.md)与[科学合同V1](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1.md)共同界定本轮唯一执行范围。状态：`EXPLICITLY_APPROVED / USER_REPORTED_LAUNCHED / NOT_NATIVE_VALIDATED`。用户已报告在109启动Codex并将窗口命名为**Lane M**；本窗口未直接核验node109实时任务、GPU锁或任何执行门结果。

- 执行者：**Lane M（node109，Round A8）**；原**Lane N（174-new，非LLM源审）**和**Lane T（174-new，训练源审）**继续保留原名与STOP。三个Lane名称在节点间不复用；仅命名更正，不变更科学合同或资源预算。
- 四条件N-C2/G2/G4/G8、相同32帧、单batch编译产物与完整energy/force/stress，GPU单RTX4080及既有非阻塞共享锁，依V1预冻结数值/边集合/时间统计与STOP。
- 用户批准GPU锁占用硬上限90分钟、观察阶段15分钟，模型和Si下载<=12MiB、依赖下载<=8GiB、新环境<=25GiB、CPU<=8 workers/RAM<=32GiB/GPU显存<=12GiB、raw日志<=256MiB；任何科学/资源边界变化均不得静默执行。
- **用户随后明确报告Lane M已在109启动。** 这是`USER_REPORTED_LAUNCHED`，不是本窗口已经核验运行、CUDA资格PASS、采集完成或结果有效。不得从Git HEAD推断实时GPU状态；执行合同、锁与STOP条件全部保持。

## 历史设计完成：Round A7｜非LLM发现性观察完整合同与执行前审查

**执行者：ChatGPT／AI-ARCH Discovery。连续设计阶段已一次完成；没有启动Codex或109 GPU。**

[完整合同：AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1](goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1.md)，初始发布提交 `8d4ed06e3696b0721b83f706b03cbc6b058f9f46`。

| 项目 | 本轮完成内容 | 当前边界 |
|---|---|---|
| 模型固定 | OAM-S:0.1；Zenodo 18775904的指定5.6MB文件与官方MD5已核，禁止注册名自动升级 | 本轮未下载包；实际SHA256/dtype/包内源码在获批后的资格门核验 |
| 输入与选样 | 固定Si文件；32个零基帧号、canary 0/109明确；所有臂相同2048原子工作量 | 静态结构评估，不声称连续MD、跨帧复用率或统计独立holdout |
| 软件/数值 | 候选PyTorch 2.10.0 cu126、固定NequIP/OEQ/ALCHEMI；FP32/TF32-off；沿官方5次均值与5e-5 allclose；边集合精确比较 | 静态接口核查通过不等于本机组合已可运行；不调容差或替换模型 |
| 四条件 | CPU构图B2；GPU构图B2/B4/B8；共用一个batch AOT产物 | 是构图放置及提交粒度研究，非物理SM/带宽扩容实验 |
| 测量/统计 | CPU常驻输入至CPU结果完整wall；3 fresh process×12完整四条件block=144样本；诊断另列 | 编译/准备一次性成本另报；不从局部event之和推全程关键路径 |
| 连续执行合同 | 从隔离环境、资格、canary、计时、自检到发布一次Goal；失败按事前规则STOP | `DESIGN_COMPLETE / GPU_APPROVAL_PENDING / NOT_NATIVE_VALIDATED`；执行分支尚未创建 |

## 历史规划：Round A8｜109静态结构有限观察（当时待明确GPU审批）

**原设计时的拟执行者标签为Codex Lane N／109；现更名为Lane M／109（用户报告已启动）；科学审查：ChatGPT／AI-ARCH Discovery。**

不是再开一轮ChatGPT方案整理。若用户批准完整合同的设备/获取/编译边界，就按该合同一次Goal完成必要资格与观察，再交本窗口独立审查。未批准之前不发送启动指令、不改变现有Lane本地工作区。

拟申请范围：固定模型＋几何合计下载<=12MiB；隔离依赖下载<=8GiB、环境/缓存/产物增量<=25GiB；CPU<=8 workers、RAM<=32GiB；单109 GPU，任务显存<=12GiB，现有共享锁独占硬上限90分钟，纯观察阶段<=15分钟。以上是预算上限，不是已用资源或完成时长预测。禁止NSYS/NCU/NVBit、训练、MD、驱动升级和新机制。

有意义结果包括软件组织收益、CPU构图更快、批量响应、零/不稳定响应；不强求5%端到端收益，不因正数自动晋升硬件。当前仍无新GPU执行授权。

## Lane与独立项目状态

| 工作线 | 固定已审来源 | 当前状态 |
|---|---|---|
| Lane T | [A4训练源审@a1a70180736499687435b1e2d99984d4ebba4c53](https://github.com/swayhrl/accel-sim-framework/blob/a1a70180736499687435b1e2d99984d4ebba4c53/docs/ai_workload_research/reviews/AI_ARCH_A4_TRAINING_SOURCE_REVIEW_174NEW_V1.md) | 原任务完成/STOP；A5接受有限未准入判断。不追加352B调查 |
| Lane N原174源审 | [V1@e355f096eeac44328d7463ef3256cc649ec9cb03](https://github.com/swayhrl/accel-sim-framework/blob/e355f096eeac44328d7463ef3256cc649ec9cb03/docs/ai_workload_research/reviews/AI_ARCH_A4_NONLLM_SOURCE_REVIEW_174NEW_V1.md) | A5确认文本丢失，整体文档仍PARTIAL；A6最后读回仍此HEAD。本轮未重读分支，不声明V2已修复或本地进程状态；修复不阻塞本窗口直接核实的源码设计 |
| C16 | [Reset@635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f](https://github.com/swayhrl/accel-sim-framework/commit/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f)；[Stage A@ccd6928bfb420d1e4c554ec0e377bb8fbe377501](https://github.com/swayhrl/accel-sim-framework/commit/ccd6928bfb420d1e4c554ec0e377bb8fbe377501) | 历史Stage A TERMINAL_PARTIAL、Reset关闭；不恢复Observer、Tier1或旧holdout |
| AWMA R27R3 | [独立review@d6e9bbfb562814bcd5dc5adb444d3c572e7f446b](https://github.com/swayhrl/accel-sim-framework/blob/d6e9bbfb562814bcd5dc5adb444d3c572e7f446b/docs/vm_tlb/literature_notes/awma/empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md)；[协调同步](R27R3_INDEPENDENT_REVIEW_SYNC_2026-10-13.md) | 保持B0_REFERENCE_NOT_REPEATABLE、COMPLETE/STOP；AWMA后续以原窗口最新已审权威为准 |
| 训练新方向 | [Round A6](literature/AI_ARCH_ROUND_A6_NEQUIP_PATH_AND_PUBLIC_TRAINING_2026-10-13_V1.md)的TorchTitan/C4、SimpleFSDP与卸载近邻 | 公开输入与软件方法研究保留，不用单卡代理冒充多GPU实验；本轮不新开训练任务 |
| AWMA其它证据 | [C16/AWMA证据索引](AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md) | Pre-L1模拟、R23G局部软件、R26容量与R27R2资格失败分别保留；本窗口不改实验结论 |

## 历史轮次与证据导航

A6完整旧导航保存在[CURRENT_STATE@5fd748c3f2da64924ed84978c07bca90e7e6ea92](https://github.com/swayhrl/accel-sim-framework/blob/5fd748c3f2da64924ed84978c07bca90e7e6ea92/docs/ai_workload_research/CURRENT_STATE.md)，A1–A5旧导航保存在[CURRENT_STATE@3d0a959d3d6b77de67fdf9cc3f891d4adcc5416b](https://github.com/swayhrl/accel-sim-framework/blob/3d0a959d3d6b77de67fdf9cc3f891d4adcc5416b/docs/ai_workload_research/CURRENT_STATE.md)。导航更新不重写历史报告。

- [A1论文实验组](literature/AI_ARCH_P01_P13_EXPERIMENT_GROUP_AUDIT_2026-10-13_V1.md)；[A1资源/调度因果](literature/AI_ARCH_P01_P13_RESOURCE_MODEL_CAUSAL_READING_2026-10-13_V1.md)。
- [A2执行资源近邻](literature/AI_ARCH_P01_P13_ROUND_A2_EXECUTION_RESOURCE_BOUNDARIES_2026-10-13_V1.md)。
- [A3历史证据与准入](literature/AI_ARCH_ROUND_A3_HISTORICAL_EVIDENCE_CLOSURE_AND_CANDIDATE_ADMISSION_2026-10-13_V1.md)。
- [A4三family与并行安排](literature/AI_ARCH_ROUND_A4_NATURAL_WORKLOAD_PARALLEL_DISCOVERY_2026-10-13_V1.md)。
- [A5联合独立审查](reviews/AI_ARCH_ROUND_A5_LANE_T_N_INDEPENDENT_REVIEW_2026-10-13_V1.md)。
- [A6非LLM路径与公开训练](literature/AI_ARCH_ROUND_A6_NEQUIP_PATH_AND_PUBLIC_TRAINING_2026-10-13_V1.md)。

后续同一ChatGPT可连续完成且不依赖新外部结果的核查、设计与自审合并处理，不因轮次编号反复索要同意；实际GPU/资源授权边界仍独立。工具Skill只用方法，不安装或合并候选分支；尚未直接读取的节点raw不声称本窗口已重新验证。
