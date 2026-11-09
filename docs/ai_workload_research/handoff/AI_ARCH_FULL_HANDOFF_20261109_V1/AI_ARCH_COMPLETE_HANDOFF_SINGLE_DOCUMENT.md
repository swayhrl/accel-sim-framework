# AI-ARCH 全项目完整交接｜2026-11-09 V1

## 1. 接班时最重要的事实

本窗口承担AI-ARCH真实AI负载发现、科学执行及证据整合，仓库swayhrl/accel-sim-framework，主要执行节点109。最新一个Q1实验Goal已完整完成、释放资源并发布，不存在必须续跑的半成品GPU进程。新窗口的首项工作是独立审查、纠正协调导航滞后和决定下一科研方向，不应再从Q1 V1/R1/R2的失败点重启。

最新Q1执行authority：5787826ca21f7af958e6e1c1f828d62fd58a1ec4 / tree a070243a93fee5594dd88d515f08e228677ebf75。状态NATIVE_Q1_LATE_PIPELINE_COMPLETE，NO_HARDWARE_CANDIDATE_PROMOTED。这是执行侧已发布且Git核验的证据；尚未由新独立窗口完成科学审查并选择性同步协调层，交接标签为REPORTED_PENDING_REVIEW。

协调分支hrl/ai-workload-research-coordination当前核实HEAD66b2dffc6141edf1c9f9f089091b3922556583f1，tree c9491cbc37d41c2155218763bf215615ef72b39b，CURRENT_STATE仍是11月6日Q1执行前状态。其“缺完整late state”“本轮NO_GPU_PROBE_READY”是历史快照，不能覆盖11月9日Q1已完成结果；也不能将新的Q1结果倒写为历史Goal通过。新窗口必须重新fetch实际HEAD并检查变化。

交接期间本窗口没有新GPU工作，没有查询其它项目的活动GPU raw。Git ref/worktree存在不表示对应任务正在运行。

## 2. AI-ARCH的科学目标与判据

目标是从真实AI训练/推理完整应用中找到强软件之后仍具体、可测、可证伪的GPU体系结构约束。范围包括LLM、MoE、Hybrid/KV、VLM、DiT、GNN、科学模型、3DGS，以及状态生命周期、计算、调度、数据就绪、cache/TLB、迁移/通信/容量。

工作顺序：
真实负载与合法输入身份 → 原生数值/质量和执行路径 → 完整成本分母与竞争解释 → 最强适用软件反证 → 独立输入验证 → 具体硬件资源变量 → 只有必要时才设计机制、仿真或RTL。

必须分开SOURCE_ONLY、作者实验、我方NATIVE、CPU独立重算、模拟器、理论估算和条件设计。逻辑重复、操作减少、物理服务抑制、局部时延、完整应用收益、PPA是不同层。软件正结果不能直接改名硬件创新；工程/资源STOP不是性能负例，数值FAIL不能筛掉或临时放宽。

OBSERVED、MODEL_CONSISTENT、PARTIALLY_ATTRIBUTED、CAUSALLY_SUPPORTED、INCONCLUSIVE分级；没有真实PPA不能称芯片能效提升。固定source/input/backend/precision/quality后再谈性能；host/device时间不能未经校准相减；时间并集与累计分开。

## 3. 当前研究组合与科研决策

| 路径 | 固定证据与状态 | 接班处理 |
|---|---|---|
| 3DGS Q1 | 最新完整native，20formal，完整状态和camera验证；无新GPU硬件候选 | 原PRIMARY本轮已收口；先独审，暂不自动追加GPU |
| Hybrid GDN/KV | A70N 5076223db5db0256fd0ccacec50b5347a0cab8c5；SOURCE_SCOPE_ACCEPTED_NOT_NATIVE_NEGATIVE / NO_SURVIVOR_IN_SEARCH_SCOPE | SECONDARY资格方向；缺完整合法模型、自然会话、状态/质量与兼容强runtime |
| MoE | A70O 94ca01df352cf4cf707cd35e5f9f63d4eff014c6，source范围0survivor；A30T 1a8b9317de4c16e3dd19018f7f42cae1ebf5750e为H200_SM90A_CONDITIONAL | CONDITIONAL；109 SM89不能冒充H200；自然route/FP8格式/完整分母需闭合 |
| Qwen BF16 Decode | V11 339559f6972f25ac1aec78fb3577b7bd2640410e，真实native/profile，NO_HARDWARE_CANDIDATE_PROMOTED | PARKED成熟负载分析基点，不自动V12 |
| Low-bit W4 | A81 492c7c79e130d60cb344d723c15751afe81a5a82，NO_REAL_TENSOR_AUTHORITY | PARKED；缺合法可读AWQ weight/activation pair，不能拿SHA或人工热点替代 |
| VLM | A70P f2399777a30f4fdafa26858b3cd418e497538db2，SOURCE_ONLY/STOP，cache/Graph/分离已有软件 | PARKED；自然媒体、质量和完整请求未闭合 |
| DiT | A30N 6f78a2e1e9a2fdb04bc9468f4b2d5594bc3229a6证据不足；A75D 6421e6768ff3df2ec20cddd87b3aa28b932c113a软件近邻无survivor | PARKED；不缩小官方设置塞16GB后声称同对象 |
| GNN | A67 c425819d1f41e0cbd3053315cd5590697e808a3c，IGB-small scoped eager FULL软件反证；储备4c1ba2c544a0f8ba309efa6f57eadfe248b98454 | PARKED_BY_USER；保留A61数值STOP、A65 compiled不对齐，medium未执行 |
| Serving/Agent自然输入 | A70M f2d6324da298be26f39cda427f3e7db1a7e7031d；A73W e7f2438aec9ee5c3ab677027c48a08dcd40c75b0，SOURCE_SCOPE STOP/输入缺口 | PARKED；usage/shape不能还原真实model-facing token |
| iso-PPA/资源交换 | A73H 06b17a72f683316a4088292a4b424c9d97c7437c；A74C d2530b3bb8a2743b716ec58e6a3113d18b66c71f | PARKED_FOR_PPA_OR_SIM_MODEL；没有合格SM100/PPA模型，不启动模拟器 |
| RL后训练 | A75R 8e53641295068cdef653362d0f8d7f441c636b11，SOURCE_SCOPE STOP | 作者rollout/trainer等待不是本机资源饱和 |
| NequIP静态batch | 1f69559df4f51290589de72876f36a756c5439f0的V1R1有144个native计时，数值合格、MIXED_RESPONSE | CPU邻居B2优于GPU B2，GPU B4/B8优于GPU B2；保留限定软件/规模响应，不自动复跑 |
| NequIP Green Context | 6953ac1690b7a905b6000833a879f9164c7c9e43，实际38/76SM quota与stream身份通过，G3 INTEROP_UNQUALIFIED_STOP | 仅API/microkernel可行性；整模型受控quota、数值与性能未成立，不自动R2/R3 |
| CAGRA/GloVe100 | 995f557c569e7d6ef3fbdbec87481e664993291f，真实full-index保存/重载与距离数值通过，但6个校准配置recall均低于0.95 | QUALITY_NO_GO，formal0；不是近似搜索或硬件普遍性能负例，不改质量门 |

上述排序继承已接受组合包f88e40123f4060328aa50a16d22fa328cee51cfe。Q1完成改变了资格事实，尚未自动产生“某新硬件方向PRIMARY”的决策。原文综述、三个问题合同、组合状态与62文件证据索引在：
[组合包](https://github.com/swayhrl/accel-sim-framework/tree/f88e40123f4060328aa50a16d22fa328cee51cfe/docs/ai_workload_research/discovery/AI_ARCH_NEXT_STAGE_PORTFOLIO_REVIEW_V1)。
本交接核实42个固定Git tree，不是全远端分支内容审计；发现更晚已接受authority时先核差异并记录。

## 4. 最新Q1 3DGS：已做完什么

[固定完整报告](https://github.com/swayhrl/accel-sim-framework/blob/5787826ca21f7af958e6e1c1f828d62fd58a1ec4/docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1/FINAL_REPORT.md)。
输出根目录：
docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1/

原GS-Scale/Rubble、downscale4、CPUAdam、SH、densification与deferred语义保持。nominal max_steps=200000、refine_stop=15000未改；本Goal要求的是自然推进到晚期测量状态，实际生产next15240，最终保存next15301，不声称完整200000步收敛。原初始N=1,694,315，正式窗口N=6,720,398。

完整C_D(next15140)、C_V(next15240)、C_FINAL(next15301)均保留；包含参数/grad、optimizer moments/counters、pending梯度、RNG、loader/camera cursor、live buffers、stable ID及alias。每态44Tensor/35完整浮点字段独立CPU全SHA与有限性复核通过，且有实际GPU恢复，CPU测试不替代GPU资格。

固定发现窗口15150–15199+closure15200；验证15250–15299+closure15300。完整50目标camera credit闭合加1个自然closure循环，保留后续pending而不是额外改算法清零。C_FINAL：GPU processed15300、CPU applied through15299、pending15300、prepared15301；真实重载数学semantic精确。

8warmup、20formal、3ON诊断、1末态恢复成功；正式OFF与ON分池，每格5formal。全部正式样本保留，无筛选。所有formal初始semantic状态精确，camera顺序在phase内一致，两phase51个camera ID集合不相交。没有第二scene或跨scene结论。

| phase | T8 median/MAD秒 | T16 median/MAD秒 | T16相对T8降低 |
|---|---:|---:|---:|
| discovery | 8.683307 / 0.050807 | 7.629178 / 0.026169 | 12.1397% |
| validation | 8.739618 / 0.037407 | 7.679067 / 0.055039 | 12.1350% |

T16是原接受基线，不能将其相对T8优势说成超过原基线的新优化。线程是OMP cap，Torch intra请求仍64；实际CPU集合14logical/10core ID，不能当8/16个物理核。

关键反证：发现T16 ON窗口CPU Adam约3.416s，参数转发/所需Adam约2.541s，合计75.59%；验证约74.70%。全局ID选择/扫描约2.52%，显式join/synchronize并集仅0.165%（验证0.104%）。CPU状态生产路径是主要已测主线程成本；低U/N（约13.6–13.7%）并不证明全局扫描是主要瓶颈。

GPU事件median约27.10ms/25.61ms，含launch gap，非纯kernel active。H2D约8.45GB、D2H约9.34GB/51步是调用操作数，不是DMA/PCIe/DRAM计数。主线程区间并集、累积和、GPU跨度分开，不跨时钟相减。归因PARTIALLY_ATTRIBUTED；CPU算术/主存、真实PCIe服务及GPU SM/DRAM未独立操纵，不升级CAUSALLY_SUPPORTED或PPA收益。

数值：最终状态指纹/样本存在敏感性，保留早期A/A和历史比较；没有新容差，没有训练轨迹/质量等价PASS。可作相同恢复起点与camera工作下的描述性native对照。新窗口审查不能把性能可比直接提升为逐bit训练等价。

最重要的文件：FINAL_REPORT.md、FORMAL_SAMPLES.tsv、FORMAL_ANALYSIS.json、NUMERICAL_OBSERVATIONS.json、NATIVE_INPUT_WINDOW_IDENTITY.json、COST_LEDGER.json/tsv、DIAGNOSTIC_ANALYSIS.json、STATE_AND_NUMERIC_CONTRACT.json、STATE_INDEPENDENT_INSPECTION.json、RESOURCE_ANALYSIS.json、RESOURCE_OBSERVATION_SCOPE.json、RESOURCE_AND_INTEGRITY_NOTES.md、SOURCE_AND_INPUT_IDENTITY.json、BINARY_IDENTITY.json、PRIVATE_RAW_INDEX.json、PUBLICATION_VERIFICATION.json、RECEIPT.json。逐文件固定URL见Q1_FIXED_FILE_INDEX.json。

## 5. Q1历史失败与工程修复，不得混淆

| 版本 | authority | 实际终态/新增事实 |
|---|---|---|
| 原Goal | 34a598f4e5f40fffde337ae6b167bd4ffb3fccac | 完整可执行科学合同；不是执行结果 |
| V1 | ba477c42561cb265714b030d1c4346ede035c292 | early自然到next8，C_E/C_R_E保存；VmSwap可选字段读取StopIteration，INPUT_OR_RUNTIME_NO_GO；GPU恢复未执行 |
| R1 | 39e129a6db5236f7acc595b5abaef14331df8ac9 | 两旧态实际semantic恢复通过；save中semantic漏赋值，A1/A2保存失败后退出监控RESOURCE_STOP；orphan chunks不冒充完成态 |
| CPU加固 | 24a1d00b9c4d8130324e2984a14de369f9ba9c3b | 另修端点semantic漏赋值、避免先删C_D、补完整CPU链和退出记账；235适用测试通过+2 scoped skip，未GPU验收 |
| R2 | 491b8e5177c954ac7df609724fd8a6fad483af61 | 六个真实GPU保存/续行/重载资格点均exit0；production开始后线程亲和ProcessLookupError，strict STOP；具体失败TID未保留，不能追认合格censor |
| 最新完成 | 5787826ca21f7af958e6e1c1f828d62fd58a1ec4 | 用户新授权并解除旧预算，完成线程生命周期修复与握手、完整late生产及矩阵；W1旧STOP保留，W2完成 |

最新执行的线程规则：仅kernel枚举的自身线程，在ESRCH、两次自身task路径不存在、同身份健康parent/root/worker且无独立gap时记录affinity=None/censored。不是填0或假称全亲和观察完整。活线程不可读、PID冲突、未知GPU仍STOP。100个真实Linux线程退出回归及实际GPU日志都有证据。

完成收口协议：worker结束计算且CUDA同步后发布READY及身份/hash，监督器完整live检查后ACK，取得真实OS退出码并确认context清理，再采后续资源/放锁。受控ACK到reap区间treeRSS未连续采样，kernel charged peak保留。不要删掉或泛化所有psutil异常。

工具最终目录util/ai_workload_research/q1_3dgs_completion/。worker、q1_supervisor、state_store、loader_state、terminal_protocol、process_observation、shared_gate/shared_lease、source_transform、transfer_observer及测试均已归档。它们包含固定OUT/CFG、环境变量、dispatch副作用：**不要为了“看看”直接import/运行旧worker/supervisor/CPU计划器**。分析脚本也可能写结果；只读审查用git show/json解析，必要执行时新路径复制隔离。

当前source并不保证通用平台所有GPU边界已验证。后续移植仍需固定实际binding、完整snapshot、真实结束/错误路径测试，不能以235 CPU PASS代替实际GPU模型验收。科学研究不要再拆成一系列低信息量准备Goal；已授权范围内普通工程同Goal解决。

## 6. Qwen完整脉络与可复用认识

模型固定Qwen/Qwen2.5-3B-Instruct@aa8e72537993ba99e69dfaafa59ed015b17504d1，BF16 TP1无量化，冻结A00/A01各512token。strong vLLM0.30.0 VLLM_COMPILE/inductor/FULL_AND_PIECEWISE、FlashAttentionImpl、UnquantizedLinear。P1–P6为B1/B2、输出1/32，历史scientific-field SHA8571824801bf46ae9f1c84c55470274e580fa7d8b9ff5491ded36e87172a5397。

V1 NVML API工程缺陷；V2/V3/V4资源准入STOP，不能算性能负例；V4普通ComfyUI compute驻留不符合当时合同。V5新gated-resident协议后发现logprob问题；V6 RSS生命周期错误；V7两组真实诊断完成，A00/A01首token B1/B2分数差稳定约0.10269761/0.05504596、token一致、top20非统一变化。

V8明确将旧atol0.05/rtol0.01 FAIL保留为数值敏感性观察，不再自动阻止合法固定长度性能采集；不能回写旧FAIL。V8有150formal/5配置，logprobs=None减少约4.2–4.5ms的32-minus-1差值，R仍约1.033。选中raw logit相同27.25、CPU FP64 logsumexp解释该端点分数归一化贡献，不定位native首次前向分歧。

V9有18点90formal，B1约10.125、B2约10.448ms/额外token，R约1.0318448；时间线显示Dense主导。V10对应QKV节点实际DRAM读约10.492/10.510MB；B1 GEMV与B2 WMMA不同，不将B2当两个B1。V11扩展主导Dense与局部数据状态反事实，保留B1复用失败、写驱逐混杂及共享观测边界，最终NO_HARDWARE_CANDIDATE_PROMOTED。

不能将条件191.31GB权重模型当实测DRAM；不把单节点乘36层当全应用读量；batch摊销不是新硬件创新。altered eager首差层不等于native compiled首差层。Qwen当前PARKED，不自动V12。V1–V11所有固定SHA/tree在AUTHORITY_INDEX.json，可按需定位，不要重跑原曲线/五配置/旧QKV计数。

## 7. 已有文献与强软件资料，避免重做

首次导航：协调分支README.md、CURRENT_STATE.md、COORDINATION_PROTOCOL.md、AI_ARCH_RESEARCH_AUTHORITY_INDEX_V2.md、AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md、AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md。

组合包f88e40123f4060328aa50a16d22fa328cee51cfe目录discovery/AI_ARCH_NEXT_STAGE_PORTFOLIO_REVIEW_V1/包含：
AI_ARCH_RESEARCH_PORTFOLIO_STATUS.md；
RECENT_LITERATURE_AND_SOFTWARE_EXCLUSION.md；
NEXT_THREE_SCIENTIFIC_QUESTIONS.md；
AI_ARCH_NEXT_STAGE_DECISION.md；
CURRENT_STATE_UPDATE_PROPOSAL.md；
EVIDENCE_INDEX.json。
Q1合同及状态/矩阵/资源草案在goals/AI_ARCH_Q1_3DGS_LATE_PIPELINE_SINGLE_GOAL_109_V1.md和planning/Q1_3DGS_LATE_PIPELINE_SINGLE_GOAL_109_V1/，固定34a598f4。

已做的定向原文组：GS-Scale、CLM、TideGS、GSArch；Strata、HybridKV；MonoMoE、Patterns Behind Chaos、Not All Models Suit Expert Offloading。用原包核具体实验组、模型、硬件、软件与未披露项，不重复宽泛罗列；需更新新论文时再明确有何新增竞争变量。

CLM已有camera/visibility reuse、选择性appearance传输、optimizer overlap与调度。TideGS涉及eviction后optimizer cold restart与camera顺序，不能作为无损同语义替代。Strata/HybridKV不能与Hybrid GDN exact-state不加区别混用；MonoMoE weight-major融合和route-aware placement是强软件碰撞，不能另取硬件名字。

跨项目C16/AWMA是证据参考，不是本窗口的执行管辖权。C16 StageA ccd6928bfb420d1e4c554ec0e377bb8fbe377501为TERMINAL_PARTIAL；W4转换局部oracle0.8262x及预展开改变表示必须保留；逻辑重复不能直接换算收益。AWMA R27R3 7bd31fa… / accepted review d6e9bbf…为B0参考梯度重复性STOP，不能改成容量/性能负例。完整来源走E-C/E-A索引，不查它们的活动raw。

## 8. 运行、权限和工作方式摘要

详细路径/命令见OPERATIONS_AND_ASSETS.md。只用109已授权资源，不访问164；174模拟器不是本包授权。EP-L2、DTC-L1、AWMA、C16、VM/TLB及Image-Lab均有独立所有权，不重启、部署或清cache。

原Image-Lab共同锁/data/c16/locks/c16_gpu_campaign.lock，fcntl.flock(LOCK_EX|LOCK_NB)，不是lockf；覆盖CUDA初始化、全部模型/子进程、最终同步/退出、context清理。必须预约+实时loaded gate和身份核验，不以空队列/0%/404MiB或静态JSON当资格。历史独立cache/gpu-validation.lock不能代替共同锁。

历史Q1用户曾解除该Goal旧时间/容量预算，不等于本交接授权新窗口永久无限GPU/租卡/下载/系统权限。后续新科学执行需要明确目标、当前resource-owner窗口及实际物理资源资格。只读CPU整理/独审/提案不取锁、不初始化CUDA/JIT。

用户偏好：同一已批准Goal中连续完成资格、工程修复、真实对照、独立验证和发布；不要逐小阶段索确认。科学身份、数值/质量、资源共享边界的实质变化必须显式记录。只在确实缺必要授权/输入时询问，说明具体来源。负结果正常，不临时换模型或放宽门限找正结果。不要自动恢复STOP或开下一Goal。

## 9. 建议新窗口立即完成的工作

P0：仅CPU只读fetch本交接、最新协调和最新Q1，记录实际commit/tree；核读本包与Git文件身份。检查本地AGENTS适用范围，建立自己的独立工作区，勿改已有执行worktree。

P1：独立审查Q1。先复算20个formal的median/MAD、交错顺序、每格5次与无筛选；核camera同序/跨phase不相交、strict初始状态和完整pending/frontier；核OFF/ON分池、Host并集与GPU事件不相减；检查logical payload不当DMA、所有数值不等价/监控范围与W1 STOP保留。先用Git公开证据；没有必要不重hash19.5GB状态或重新训练。需要重载状态时才做完整合法读取资格。

P2：独立审查握手及censored规则，确认没有掩盖活进程不可读、未知GPU或放宽数值门。接受/不接受逐项标注，不以执行报告自我声明当独立验收。已知控制元数据覆盖如实保留。

P3：形成科学review和CURRENT_STATE更新提案。保持Qwen/旧STOP不变，登记Q1完整native与NoHardwareCandidate，将“缺late state/尚未执行Q1”旧语句更新为历史入口。新任务未明确授权前，不直接推协调分支、不merge历史执行HEAD。

P4：给下一研究方向决策，首选Hybrid/KV真实资格调查；MoE仅H200条件路线。先找合法可读真实模型/自然会话/强runtime/质量与容量资格，不凭config或下载缓存晋升；无合格输入允许NO_GPU_PROBE_READY。3DGS若继续，必须是具体软件残余反事实，不重复全套生产/线程矩阵。

交付建议：独立科学review、选择性协调更新提案、研究组合决策与一个可证伪最小合同。先向用户报告Q1审查是否接受和下一步选择；新GPU、模型下载、Profiler、模拟器/RTL不由交接文档自动授权。完成Git发布及精确远端回读后STOP。

## 10. 资料完整性与不能推断的范围

本包是固定证据的完整导航与接班说明，不是把整个仓库和数百份raw复制一遍。AUTHORITY_INDEX包含42个对象的实际tree；Q1_FIXED_FILE_INDEX列90公开文件。历史执行branch存在不代表仍运行；其它项目当前活动未查询。公开路径、私有state存在性与Git身份已核验，未无意义重审全部历史科学数据。

若新窗口无法SSH、某私有state已被合法移动或权限变化，先记确切缺口，使用固定Git报告继续独审；不下载替代数据、不伪造完整state、不修改旧receipt。科学执行若必须依赖缺失数据则停止该子任务。

本交接任务仅生成独立资料包和消息，不做协调层合并、不恢复任何旧Goal。最终交接包commit/tree及远端逐blob核验见发布回执。


---

# Appendix A: Operations and assets

# 接班操作、节点资产与安全边界

## 1. 环境与Git

本地用户环境：Windows，D:\repo，PowerShell。科研主节点109：
```text
ssh huangrulin@10.156.120.109
cd /home/huangrulin/workspace
```

仓库共享对象库：/home/huangrulin/workspace/accel-sim-framework。
该主worktree在交接检查时位于其它C16协调分支，**不要在这里checkout/reset/stash/清理**。新任务使用独立worktree/branch。

推荐只读启动（以下在SSH后的Linux shell中运行）：
```bash
repo=/home/huangrulin/workspace/accel-sim-framework
git -C "$repo" fetch origin hrl/aiarch-new-window-handoff-109-20261109-v1
handoff_sha=$(git -C "$repo" rev-parse FETCH_HEAD)
git -C "$repo" rev-parse "$handoff_sha^{tree}"
git -C "$repo" show "$handoff_sha:docs/ai_workload_research/handoff/AI_ARCH_FULL_HANDOFF_20261109_V1/README.md"

git -C "$repo" fetch origin hrl/ai-workload-research-coordination
coord_sha=$(git -C "$repo" rev-parse FETCH_HEAD)
git -C "$repo" rev-parse "$coord_sha^{tree}"
git -C "$repo" show "$coord_sha:docs/ai_workload_research/CURRENT_STATE.md"

git -C "$repo" fetch origin hrl/aiarch-q1-scientific-completion-109-v1
git -C "$repo" rev-parse FETCH_HEAD
git -C "$repo" rev-parse FETCH_HEAD^{tree}
```
Q1应核5787826ca21f7af958e6e1c1f828d62fd58a1ec4 / a070243a93fee5594dd88d515f08e228677ebf75。handoff与协调若有新提交，先保存实际identity和diff；不要把本包记录的HEAD当永远最新。

新审查worktree示例（先确保名字未用）：
```bash
git -C "$repo" worktree add -b hrl/aiarch-handoff-independent-review-109-v1  /home/huangrulin/workspace/worktrees/accel-sim-aiarch-handoff-independent-review-109-v1  "$handoff_sha"
```
不要merge历史执行HEAD。显式git add限定本任务路径；不用git add . / -A，不force push，不修改第三方runtime。网络认证必要时沿用已有gh auth git-credential helper；不要输出token/credentials或私有环境变量。

本地AGENTS.md标题为VM/TLB，明确适用于hrl/vm-core-v0及其VM/TLB后代；不能将其分阶段仿真任务误作为AI-ARCH当前Goal。新worktree仍应读所有实际适用的AGENTS和任务协议；若scope发生实质冲突，按具体授权处理，不能直接忽略。AI-ARCH主要协调规则为docs/ai_workload_research/COORDINATION_PROTOCOL.md。

## 2. 最新Q1完整工作区与数据

```text
执行worktree：
/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-completion-109

分支：
hrl/aiarch-q1-scientific-completion-109-v1

OUT：
/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-completion-109/docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1

TOOL：
/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-completion-109/util/ai_workload_research/q1_3dgs_completion

W2：
OUT/windows/W2
```

三份真实完整状态：
- OUT/.private/STATES/C_D，next15140；
- OUT/.private/STATES/C_V，next15240；
- OUT/windows/W2/.private/STATES/C_FINAL，next15301。

均由本次仅做存在性+MANIFEST路径核查确认仍在；完整SHA与科学资格以固定PUBLIC/PRIVATE索引、STATE_INDEPENDENT_INSPECTION.json及实际GPU恢复收据为准。交接没有再次完整hash19.5GB。原.raw/STATE_*_MANIFEST.json是保存时公共收据；sidecar和owner在状态目录同级。不要修改、补造、移动、删除这些既有状态。

主要私有raw：
OUT/.private/JOBS/PRODUCE_LATE；
OUT/windows/W2/.private/JOBS/<job>/；
每个job有REQUEST、WORKER_IDENTITY、RESTORE_INITIAL、RESULT、REGIONS、TRANSFERS、GPU_EVENT_SPANS、TERMINAL_READY/ACK等（具体依实际模式）。
Resource journal原字节在各.private/RESOURCE_SAMPLES.original.jsonl，Git中有lossless .gz与identity。大chunk不在Git。PRIVATE_RAW_INDEX.json固定全路径、长度、SHA，共约19.5GB retained private payload。

根RESOURCE_RECEIPT.json是W1原始RESOURCE_STOP；W2原收据为windows/W2/RESOURCE_RECEIPT.json，NATIVE_Q1_MATRIX_COMPLETE。整体终态是根RECEIPT.json的NATIVE_Q1_LATE_PIPELINE_COMPLETE。不要看到W1文件就误判最新Goal未完成。

历史Q1 worktree均在同一worktrees父目录：
accel-sim-aiarch-q1-3dgs-continuation-contract-109-v1；
accel-sim-aiarch-q1-3dgs-late-pipeline-native-109-v1；
accel-sim-aiarch-q1-3dgs-late-pipeline-r1-109；
accel-sim-aiarch-q1-cpu-hardening-109；
accel-sim-aiarch-q1-r2-109。
旧C_E/C_R_E在V1 OUT/.private/STATES，分别next5/8，不能与最新C_D/C_V混称late。

## 3. 合法原资产与环境

GS-Scale原资产：
/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014
- software_sources/gsscale/examples/simple_trainer_hybrid_optimized.py
- software_sources/gsscale/cpu_adam/cpu_adam.cpython-310-x86_64-linux-gnu.so
- scene及scene/images_4_png（1678张接受的预处理图像）
- venv/bin/python（Python3.10.12、Torch2.2.0+cu121、IPEX2.2.0、NumPy1.26.4、psutil6.0.0）

运行旧GS Python通常需：
LD_LIBRARY_PATH=/data/c16/env/cpython-3.10.12/lib。
未加时加载libpython失败不是环境已损坏，不因此重装。

监督器Python：
/data/c16/envs/c16-vllm-v0.30.0-sm89-v1/bin/python。
它在Q1只提供psutil/NVML绑定；这不表示GS使用vLLM模型runtime。

原trainer SHA：
17e70b6466f7e33a24d1610aa7deb69316cd177dc2c212cd8b717b9884f4808a
CPUAdam C++ SHA：
f3f32bc04f61749baf57d1bd877b24379597e50cf4a94d04fdde80a11c19ce9f
CPUAdam binary SHA：
c451fda99327e5969da9f0476ef3f4915815dc9ff314c22cce002e5551379a55
renderer实际私有so记录在BINARY_IDENTITY.json。接受的AlexNet evaluator已在private Torch cache，不重新下载权重或重建旧环境。

只有读取Git/json和轻量CPU审查时，不运行Torch模型、JIT、CUDA或NVML初始化。CPU分析可用原已安装NumPy；不能随意执行旧worker/supervisor：它们会读固定OUT/CFG并启动GPU或写原目录。

CPU复算正式统计可仅使用标准库csv/statistics读取固定FORMAL_SAMPLES.tsv；按phase/policy分组5个closed_window_wall_seconds算median及MAD，检查valid=True、actual_steps=51，保留全部20行。

## 4. GPU共享协议：历史身份不等于今天白名单

唯一共同锁：
/data/c16/locks/c16_gpu_campaign.lock
实现fcntl.flock(LOCK_EX|LOCK_NB)，非lockf。单owner覆盖CUDA初始化、模型、子进程、同步/terminal握手、context清理至放锁/预约释放。不等待冲突锁，不kill/暂停/调优其它项目。

实际Image-Lab状态入口历史为http://127.0.0.1:8188/gpu-sharing/status。
当前工具shared_gate.py/shared_lease.py包含challenge/no-store/age校验、loaded modules/functions hash、实例身份、nonce、kernel holder、reservation、quiescence与异常状态验证。任何新执行都重新验这些实际条件，不能凭静态JSON、空队列、0%利用率或小显存批准。

历史验收信息仅用于回查：
- GPU RTX4080，UUID GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59；
- Image-Lab source761ab4f22690f6305b7f903e15a99cc685382a1b；
- 审计4bcee3fe8d0f82a891d67818cd02d8c580dbe6fb；
- 当时ComfyUI PID3518111、UID1004、start_ticks442348560；
- restricted profile，禁用若干H3/Ollama路径；
- 历史Windows收据路径D:/repo/image-lab-gpu-sharing-v2.1/，存在性/时效不能假设；
- 旧cache/gpu-validation.lock不等于共同锁，不能拿它替代；
- 历史普通compute PID3246996不是可放行的固定白名单。

允许VERIFIED_GATED_RESIDENT_CONTEXT仅当实际代码已加载、全部GPU入口被锁门控、当前无GPU执行且child/drain闭合。桌面共存及逐进程activity遥测缺口必须记录；不等于绝对无干扰。不要重部署Image-Lab或重复canary；身份变化若缺生产验收，先停止GPU准入，向资源所有者核实。

admin配置路径与SHA已在历史EXECUTION_BINDING.json中，凭据只在既有API请求内使用，不复制到交接、日志、Git或聊天。

## 5. 资源：历史授权与物理保护分开

原Q1 V1/R1/R2资源上限8h Goal、3h持锁、14GiB显存、40GiB sampled RSS、48GiB charged、64GiB新增盘、free32GiB、训练≤16logical/监督≤2logical。旧单窗口规则亦保留在各版STOP中。

后来用户明确允许109接续并解除该执行原预算。最新Goal实际配置24h/23h运维看门狗、训练8–21/监督22–23、Host MemAvailable≥10GiB、free≥32GiB、charged guard参考节点MemTotal约62.4GiB、NVML15GiB、Torch allocator仍13GiB，checkpoint上限由当时内存/盘余量约45.3GiB决定。RSS大哨兵值仅解除逻辑sumRSS预算，不能解释成节点有1TB内存。具体以RESOURCE_CONTRACT和各cfg为准，不拿历史snapshot当新空闲承诺。

实际两窗口GPU累计4537.190s（75m37s），峰值NVML3778MiB、sampled RSS23.367GiB；session charged峰值27.255/16.915GiB。容量未触及旧数字，但顺序窗口与监控协议在新授权下修正；不能因此说旧单窗口合同其实通过。

新窗口接班文档本身不扩大权限。对未来新科学Goal，明确资源所有者当前窗口和实际CPU/内存/cgroup/盘/GPU可用性；保持物理安全，不用“解除限制”绕过未知竞争、身份、数据许可或数值规则。没有授权不启动GPU、下载、安装、全局时钟/功率/权限调整。

## 6. 跨项目与工具使用

不访问164，不恢复174 simulator。C16、AWMA、EP-L2、DTC-L1、VM/TLB是独立项目，仅读固定公开证据，不看它们活动GPU raw、不清旧cache/模型。主repo有大量其它worktree，不等于允许接管。

Linux远端可能无rg；文件搜索优先rg，若确无则用git ls-tree/固定路径/少量Python查询，不做全盘扫描。Windows调用远端Python可用PowerShell here-string经ssh stdin；中文可能受本机编码影响，生成UTF-8内容时用明确编码/Unicode escape，最后检查U+FFFD。csv输出用LF，避免CRLF使git diff --check报尾空白。JSON.stringify不是shell escaping。

同Goal普通路径/API/日志/receipt错误有界修复；实质模型、precision、quality、强后端或共享资源合同变化单独明确。任何时刻只一个GPU dispatcher；CPU子任务也共享真实资源，别让多窗口同时写CURRENT_STATE/manifest。

## 7. 结束验收

每次实质交付：精确commit/tree、显式路径staging、相关测试及diff --check、push/fetch-back、remote ref/commit/tree与文件blob/字节核验、worktree clean。大raw留private加完整SHA，不通过把raw改名为PASS使任务结束。观察时段不完整、无法校准时钟、退出码未记录必须如实保留。

本包只核身份、文件入口与状态存在性；不启动任何锁、模型、GPU或后台Goal。后续审查应新建自己的工作区，禁止原样运行本包里任何历史执行命令。


---

# Appendix B: Fixed Git authorities

|Object|commit|tree|
|---|---|---|
|coordination|66b2dffc6141edf1c9f9f089091b3922556583f1|c9491cbc37d41c2155218763bf215615ef72b39b|
|portfolio|f88e40123f4060328aa50a16d22fa328cee51cfe|03274c2ddb7c45aff4bd7ad1f7d48fca94e4a48f|
|Q1_contract|34a598f4e5f40fffde337ae6b167bd4ffb3fccac|6f705347ec2ca9aca1405ea7515db23f78019b6e|
|Q1_V1|ba477c42561cb265714b030d1c4346ede035c292|63b05bc76c953bdd9dd2201e236c73084205b982|
|Q1_R1|39e129a6db5236f7acc595b5abaef14331df8ac9|45d92fd777037400b5cc1bbe9a85ec2a0ea9e2d0|
|Q1_CPU_hardening|24a1d00b9c4d8130324e2984a14de369f9ba9c3b|f0ca2858909d19a41634430699d860eb1530f5f1|
|Q1_R2|491b8e5177c954ac7df609724fd8a6fad483af61|84dd0460153da3ccec3e1115e60820accb9ac045|
|Q1_complete|5787826ca21f7af958e6e1c1f828d62fd58a1ec4|a070243a93fee5594dd88d515f08e228677ebf75|
|GS_A26GR1|cf80f6ec07a31eccdaff264c3bce64e0511179f8|c66008a9da553d06a00195c8c133c3e7ec16692d|
|Qwen_A79|1ad28dbe2fe7280aea46a24f6ba9a97c021b08b7|9ed5906e445923e6ac8ee600093c23acbf0b987b|
|Qwen_V1|efeb32f7e8f08b58a1518a3bef6227ad5d3f15ee|9886d63c04e00e7e5edcdaf0f8bfb279b6ee5abc|
|Qwen_V2|190352cb9fdb8b1db844f0388aa95876337c1436|06e9fb7638dc571b230407a49432d53fd01f7b9d|
|Qwen_V3|24250f101719044407eceed9c2523696dc30d9b2|4ceb8c04c9c27fd191bfd0a0c1d53c8a82142c8f|
|Qwen_V4|67fe889266d6e0b28bf752ca3d878cba464d00cc|7e708a28f3492c2d6fc1f971832486de01558a54|
|Qwen_V5|065b3e91eb8b29db215b3e82b06624e3f2df94b0|133854121895b8bb9a418082fdf74800a914fb40|
|Qwen_V6|29a86372d47f622afe1e1a53b675b8f1cd499a16|c2f954519910af464548e5f4fc631437a318c12f|
|Qwen_V7|a43a44a49da80496547dc29c68a3030730fd9adb|c707f1f18abe8f17fca03007d37b1074f91d8f01|
|Qwen_V8|b3e0adf450a563997717126fd1c1985e884855a3|304788b4233d429a154b528e5bb42e421062c9b8|
|Qwen_V9|b8456ce48d8ac4939a8586bc1450239cf4d344fc|c8ea0c16805a0b3631bfa101ed5f79ccf9ffbd3b|
|Qwen_V10|94cbc8197cc3a5ec22669a55e7ccfb1a3df16962|56c90b40360d9f7c555534f44411d2b1d5a28752|
|Qwen_V11|339559f6972f25ac1aec78fb3577b7bd2640410e|c8c8391a6a0c83294ae4b6441e8c8d130180ffd2|
|Hybrid_A70N|5076223db5db0256fd0ccacec50b5347a0cab8c5|592e12903c8fa029fb5108a967f8a00bb9cb9458|
|MoE_A70O|94ca01df352cf4cf707cd35e5f9f63d4eff014c6|b5b3d7f8f925c50aa845cebec2cb3057fe91b261|
|MoE_A30T|1a8b9317de4c16e3dd19018f7f42cae1ebf5750e|11ce04902cc3b5abcda7c5c07722a898e2ec221f|
|Lowbit_A81|492c7c79e130d60cb344d723c15751afe81a5a82|350b5f2b9076729243ab1afe74f276659962aeea|
|VLM_A70P|f2399777a30f4fdafa26858b3cd418e497538db2|811616c50e4594e1884d4ee4e4c622a72fb953d1|
|DiT_A30N|6f78a2e1e9a2fdb04bc9468f4b2d5594bc3229a6|d95d82afe8ec3d2760d80ce32e008f23d24b8481|
|DiT_A75D|6421e6768ff3df2ec20cddd87b3aa28b932c113a|f10bb08891193d01b5ad98534f4514610df48eb3|
|GNN_A67|c425819d1f41e0cbd3053315cd5590697e808a3c|5ae9be2bf51ba959b9588a8111ae28bf6f03af84|
|GNN_reserve|4c1ba2c544a0f8ba309efa6f57eadfe248b98454|106097371df433f4a891a6fcf420910e5561669e|
|Serving_A70M|f2d6324da298be26f39cda427f3e7db1a7e7031d|5cbb8f8eaa4fb00efcd51bc963bf68c6b3263d52|
|Serving_A73W|e7f2438aec9ee5c3ab677027c48a08dcd40c75b0|ba20263794bd7b9b94f0050b4e985347578ae7ad|
|PPA_A73H|06b17a72f683316a4088292a4b424c9d97c7437c|0e53a3747c069f82322eea003f045c1b54ac1804|
|PPA_A74C|d2530b3bb8a2743b716ec58e6a3113d18b66c71f|7effe7d22591998bfbef4a6f627d02be8bf09d1b|
|RL_A75R|8e53641295068cdef653362d0f8d7f441c636b11|8861ec3174330260b8faaa205e80efca80183f69|
|review_A71|94f2b2f7d7def1adac47c76ee279eb78977c654a|a89cb2cd64c48d7fb783f4afc84981e67e22e19a|
|review_A72|df7e11bc1206a53e4dd28c021309baf26142a333|0f131d1ebd10eb460e7bd18c771ef0fe4c7d3ef5|
|review_A32|53a333f2b38236632f1c371bb72119dbf52f2b14|aaddac0bad9bf5753252966797c5484695e9f2ec|
|C16_StageA|ccd6928bfb420d1e4c554ec0e377bb8fbe377501|e65d19edcbaa8bffb306e1e138837d6ab13d89f0|
|NequIP_static_R1|1f69559df4f51290589de72876f36a756c5439f0|88b04f379cb6db582164d9a6ccc601f9c460f75d|
|NequIP_green_R1|6953ac1690b7a905b6000833a879f9164c7c9e43|5d993895142148886b24e7cc32d3035acf308361|
|CAGRA_A50G_recovery|995f557c569e7d6ef3fbdbec87481e664993291f|38d83cace03c4f7d214754fe2fcc90afbf976ce3|

---

# Appendix C: New-window message

请接续AI-ARCH项目，使用109节点，但本次先做CPU-only接班、独立审查和研究决策，不启动GPU或恢复旧Goal。

仓库swayhrl/accel-sim-framework。先SSH huangrulin@10.156.120.109，进入/home/huangrulin/workspace。只读fetch交接分支hrl/aiarch-new-window-handoff-109-20261109-v1，固定实际commit/tree，然后阅读：
docs/ai_workload_research/handoff/AI_ARCH_FULL_HANDOFF_20261109_V1/README.md
docs/ai_workload_research/handoff/AI_ARCH_FULL_HANDOFF_20261109_V1/AI_ARCH_FULL_HANDOFF.md
及同目录OPERATIONS_AND_ASSETS.md、AUTHORITY_INDEX.json。

最新Q1已经完整完成并STOP：
5787826ca21f7af958e6e1c1f828d62fd58a1ec4，
tree a070243a93fee5594dd88d515f08e228677ebf75。
实际完整状态、20formal、T8/T16、OFF/ON、独立camera和末态恢复都完成；当前没有GPU半成品要续跑。旧V1/R1/R2的STOP保持只读，不重新训练或重跑整个Q1。

协调分支hrl/ai-workload-research-coordination当前交接核实66b2dffc6141edf1c9f9f089091b3922556583f1，仍是Q1前快照；重新fetch核实际最新，不强行reset。先用固定结果独立复算/审查Q1的时延、输入/状态、数值边界、Host并集与GPU时钟及资源协议，再给协调更新提案和下一阶段组合决策。Q1执行侧结果待独立review，不能自动称科学审查已接受。

现有组合：Qwen成熟基点PARKED；Hybrid/KV为下一资格调查优先方向；MoE仅自然route/强软件/H200条件候选；Low-bit缺真实tensor；其它STOP不自动重开。完整资料和固定trees见交接包。

新建独立branch/worktree，不改协调分支或旧实验，不merge历史执行HEAD。普通工程问题有界连续解决，负结果保留，不放宽数值/质量门。本次允许CPU只读整理与独审提案；GPU新科学任务、下载、Profiler、模拟器、RTL及跨节点操作另需明确任务/当前资源授权。历史“资源解除”不当永久无限授权。109 GPU若未来获批仍必须原Image-Lab共同flock、预约、loaded gate和实时身份验收；不干预其它项目、不访问164。

交付独立review、协调更新提案、下一研究方向及最小可证伪合同，完成Git发布/远端commit-tree-blob核验后STOP。先报告接班核验结果和计划，不用等待我逐阶段批准已经授权的CPU整理；不要自动启动下一GPU Goal。


# Appendix D: Coordination update proposal

# 协调状态更新提案：待新窗口独立审查

当前核实coord66b2dffc6141edf1c9f9f089091b3922556583f1仍是11月6日Q1前状态。此文件仅提案，没有修改协调分支或CURRENT_STATE。

建议独审后：
1. 增加Q1执行5787826ca21f7af958e6e1c1f828d62fd58a1ec4 / treea070243a93fee5594dd88d515f08e228677ebf75及独立review authority。
2. 将“无完整late state、尚未执行Q1”保留为11月6日历史入口；新增C_D15140/C_V15240/C_FINAL15301完整保存与实际恢复、20formal、独立自然camera验证的有限事实。
3. 登记T16相对T8约12.14%描述性窗口差异、CPU Adam+参数转发约75% ON Host成本、显式join/sync<0.2%；不升级为GPU memory-bound、物理因果或PPA。
4. 数值敏感性、共享resident/desktop遥测、非独占CPU、censored线程/terminal RSS范围、W1原STOP均保留。
5. NO_HARDWARE_CANDIDATE_PROMOTED不变；软件反事实尚未穷尽。Q1收口后是否继续PRIMARY研究需新组合决策，不自动追加GPU或硬件。
6. Qwen PARKED、Hybrid/KV SECONDARY、MoE H200 CONDITIONAL及其它各线SOURCE_ONLY/STOP/park边界不变；不将旧NO_GPU_PROBE_READY误写为当前Q1未测，也不凭新Q1结果认定Q2/Q3已GPU_READY。
7. 更新README、authority导航与CURRENT_STATE时只追加事实和来源，不merge执行分支、不覆盖A80快照、不修改原raw或其它项目。
8. 在独立审查之前，新结果只标REPORTED_PENDING_REVIEW。执行侧发布/Git核验不等于科学独审通过。

新窗口首次交付建议：Q1_INDEPENDENT_REVIEW.md、SELECTIVE_COORDINATION_UPDATE_PROPOSAL.md、NEXT_PORTFOLIO_DECISION.md及清楚的是否GPU_READY结论。新科学输入不足可直接NO_GPU_PROBE_READY，不制造正候选。
