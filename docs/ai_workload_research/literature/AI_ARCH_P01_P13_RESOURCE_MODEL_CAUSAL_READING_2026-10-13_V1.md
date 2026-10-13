# AI-ARCH Discovery｜P01/P13 机制层精读：资源约束、调度粒度及因果缺口（2026-10-13 V1）

> **定位**：承接 [Round A1的22条实验组证据](AI_ARCH_P01_P13_EXPERIMENT_GROUP_AUDIT_2026-10-13_V1.md)。本文件只整理原论文可核的机制/建模假设与我们提出的可证伪问题，不是原论文复现、AI-ARCH native结果，也不授权任何109 GPU、174模拟器、新机制或旧Stage A工作。AI-ARCH协调分支只是共同知识层；AWMA/C16 authority均不变。

## 0. 本轮直接核对的原始资料

- NanoFlow，OSDI 2025正式论文，[PDF](https://www.usenix.org/system/files/osdi25-zhu-kan.pdf)，§3.1–3.7、§4.1.1–4.1.3、§6.1–6.5、Table 2/3、Figures 3/4/5/9。
- MPK，OSDI 2026正式论文，[PDF](https://www.usenix.org/system/files/osdi26-cheng.pdf)，§4–5、§6.1–6.6、§7、Figures 7/8/9/11–13，另检查附录Artifact说明。其正式artifact在论文末尾标注`mirage-project/mirage@8b981a4`的`tgx-osdi26-ae`冻结分支，**未在本轮运行或校验代码**。
- Threshold-Based Exclusive Batching for LLM Inference，ICML 2026，[指定arXiv HTML版本](https://arxiv.org/html/2606.00516)，§1、§3.1–3.5、§4及附录A.2/B/C/F；论文的HTML有部分公式渲染信息缺失，因此本轮只有可以文字直接核对的公式意义，不反向填造符号、具体常数或理论精度。
- 训练和非LLM的跨域防护参考仍是前述Round A1的MegaScale-MoE及Sobek，其详细实验组、输入、指标及限制仍以相应22条记录为准。
- 去重入口：AWMA Round09/21、跨项目证据索引V1。没有重新取得或执行109/174/164的数据。

统一证据类型：`PAPER_AUTHOR`（作者论文的原始方法/实验）、`OUR_DERIVATION`（我们从数字/约束做的数学归纳）、`HYPOTHESIS`（今后需证伪，不能说成实测现象）。以下各段分别标注。

## 1. NanoFlow：整体“计算主导”究竟是什么意思？

### NF-M1｜§3.1–3.3：作者的资源工作模型

- **PAPER_AUTHOR**：研究目标是服务**总处理token数/时间/每GPU**，同时包括Prefill和Decode token。计算吞吐的限制涉及模型权重重复使用/大批量聚合；存储成本以最大能放入权重及全部KV的dense batch作为容量约束。其理论内存服务时间`T_mem=MemSize/MemBW`建立在“每次迭代把设备内存中相关内容完整读过一次”等最大batch假设上；计算侧以`T_compute≈2B_dense·P_model/Compute`近似，网络侧按TP collective总传输/网带宽估算。
- **PAPER_AUTHOR**：在其设定的计算主导区域，使用profiling得到的CUTLASS有效计算峰值，而不是无条件采用GPU营销标称峰值；理论最优按约`Compute/(2 P_model)`推算。LLaMA-2-70B、8×A100的例子给出1857 tokens/s/GPU理论参考。实际吞吐的含义必须同时绑定模型、数据类型、GPU和最大batch假设。
- **OUR_DERIVATION**：模型回答的是“在既定理想重叠与峰值速率假设下，累计哪类资源需求先构成硬性下界”，而不是“当前时间线上每个kernel都处于Tensor Core stall”或“增加SM就能增加吞吐”。
- **重要外推边界**：显存容量不足/低负载到达/长Decode KV急剧变化时，最大batch假设可能不成立，故不要从这条计算下界推出单卡B1 Decode的性能原因。

### NF-M2｜§3.4 Table 2：具体计算，不能把三个时间相加当测得wall

作者在LLaMA-2-70B、8×A100、dense batch2048的原始成本模型与局部计时中列出：

| 资源轴 | 作者按服务量与峰值推得的时间 |
|---|---:|
| 所有operator的`T_compute`合计 | 114.17 ms |
| 所有operator的`T_mem`合计 | 45.09 ms |
| 所有operator的`T_net`合计 | 31.33 ms |

- **OUR_DERIVATION**：在忽略操作相关性、实际争用、启动开销并假设能够完美重叠的情况下，资源供给必要条件给出`T >= max(114.17,45.09,31.33)=114.17 ms`，其中理想compute需求约为memory的2.53倍、net的3.64倍。这是**该表资源账本上的必要下界**，不是新测量、不是完整系统上限，也不构成现实调度可达性的证明。
- 原表实测各算子的wall分别列16.08/16.01/69.92/34.96/35.60/4.56/47.92 ms；其描述性合计为225.05 ms，**不能冒充某一次整请求或完整迭代的wall**。其中PfAttn估计`max(0.37,0.13)=0.37 ms`，实际4.56ms，作者明确归因于启动成本。
- **科研价值**：这个“累计需求下界—实际程序的完成时间”差距，是未来P01/P13值得解释的量；不同时间分母、并发union、等待及执行阶段必须先统一。

### NF-M3｜§4.1：作者并未假设重叠免费

- Stage I：依据模型原始依赖和算子局部无干扰计时，用MILP决定nano-operation数量、batch形状与先后；约束同种瓶颈资源的算子避免同时叠加。
- Stage II：保持结构并纳入**实机成对并行的GEMM/GEMV、GEMM/网络干扰profile**，重新选计算单元占用份额`R`与实际归一化性能`P`；不是把`R`等同每种内存/网络任务的执行进度。
- **PAPER_AUTHOR明确简化**：作者假设成对干扰测得的`R→P`映射可用于三类kernel同时重叠；排程搜索约10分钟可找到**可行好的方案**，并非保证全局最优。因此，文中“optimal throughput”是某个服务量下界，而自动搜索不是已证明的真正最优排程。
- **原文消融**：§6.4 Figure 9，单纯拆nano-batch顺序执行平均吞吐下降13.2%；适合并行后才追回这一成本，额外KV offload可能再慢约3.0%。不能把“更细粒度”本身当优化。
- **HYPOTHESIS NF-H**：GPU硬件如果能减少因依赖/交接产生的额外空隙，其潜在价值应该在经过这种真实干扰校正后仍然存在；否则只是软件尚未调度好的空隙。该假设未经过我们自己的native或模拟验证。

## 2. MPK：把“可执行任务”作为第一类资源

### MP-M1｜§4–§5，Figure 7/8：工作量不只由FLOPs与bytes组成

- MPK把模型转换为具有显式producer→consumer事件、SM级任务的`tGraph`，常驻mega-kernel执行；不是把原有kernel名字简单合并并宣布无同步。
- **JIT dispatch**：必须等依赖事件达到规定完成条件，scheduler才向worker发任务；优势是在attention这类数据决定执行时间的环节动态均衡负载；代价是额外worker↔scheduler往返。
- **AOT dispatch**：事先将任务放入固定worker的队列，事件未激活时worker局部等待；依赖释放后免去一次scheduler往返，适合均衡/确定的段落；缺点是可能产生固定任务绑定和等待。
- **Hybrid**：按operator是否有数据相关的不均衡并结合全局barrier选择JIT/AOT；不是两者无条件重叠。论文把已有运行时可表达的依赖事件和可发射任务作为软件能力。
- **OUR_DERIVATION**：同样的数学GEMM/Attention工作量，任务“什么时候ready”“被哪台SM消费”“是否必须经kernel边界才能发布”和“是否被等待掩盖”，是计算/带宽账本之外的约束维度。

### MP-M2｜§5.3、§7：软件已解决与仍保留的资源约束

- **PAPER_AUTHOR**：shared memory被按32KB page动态分配/回收；后续任务可趁前一任务计算时预先搬入自己的数据，但须满足：前者自己已发完数据搬运且释放足够pages，且必要的SM内同步仍付出。
- **PAPER_AUTHOR**：worker/scheduler资源在启动时固定划分（A100/H100/B200的worker分别104/128/144个SM，scheduler占4个SM/16个scheduler warps）；整个megakernel的**per-thread寄存器需求固定为各task类型的最大需求**。文中没有因此直接测出“寄存器是主瓶颈”的响应。
- **不能重报的新意**：一般的SM级task执行、跨operator流水、细粒度数据就绪、paged SMEM分配与host调度搬到device，MPK已做出实机软件原型；未来若做硬件，必须和这个能力而非naive kernel串行比较。
- **OUR_DERIVATION**：其遗留的P13问题之一可定义为“固定register footprint使可并发worker/warp数受限”，但只有真实任务族同时证明寄存器上限造成合法时间残余才能立为硬件机会。**当前只是源码约束，不是测得的瓶颈**。

### MP-M3｜§6真实消融说明不能将整模型speedup完全归因于单因子

- §6.2将64 input +1024 output、batch1–16设为离线推理，排除了服务到达不足，这是**固定需求下runtime/执行组织**的对照；不能当真实用户请求SLO。
- §6.3的MPK vs vLLM/SGLang包含CPU调度/内核切换、跨算子流水、实现选择等多个变化，约1.0–1.7×不能归因于寄存器或内存瓶颈。
- §6.6 Figure 12：相同MPK中的`No-Pipe→Pipe`在Qwen3-8B最终Linear的局部指标有约1.15–1.29×加速，属于更强的局部流水因果证据，**不等于完整请求时间也提高同一比例**。
- §6.6 Figure 13：把AllReduce依赖改粗粒度后约1.1×，证明细粒度依赖有本身贡献，但同时包含这组特定4×H100 TP部署；不是单机Cache机制。
- §7的artifact可按论文冻结分支支持以后独立复现；本轮**未运行artifact、未声明109兼容**。

## 3. Exclusive Batching：原论文实际能支撑多强的带宽因果？

### EB-M1｜§1/§3/§4.1：在相同GPU内改变mixed batch组成

- **PAPER_AUTHOR**：把iteration时间表示为固定成本加每token边际成本，边际成本又是GPU、batch的decode比例`r`和软件路径的函数。为分析策略，先用**Qwen3-4B、ctx=16，控制总token数**改变decode比例，图上测到mixed-batch Attention成本与pure decode的交叉。
- **可归因的因素**：在**每一张固定GPU内**控制模型和总token数，通过改变r观察实际执行成本变化；这是比较强的组成敏感性证据。
- **不能归因的因素**：RTX PRO 6000和H200不仅内存BW（1.792 vs 4.8TB/s）不同，FP16算力、缓存容量、调度能力及算子实现也可能不同；跨卡约20% vs80%的交叉点与BW关联很强，但**不是“只加带宽”的单变量实验**。
- **边界**：上下文ctx=16的microbenchmark不能直接代表长KV自然请求。Figure 1/2的边际成本和完整服务RPS、TTFT/TPOT也不是同一分母。

### EB-M2｜§3：为何切换点同时受负载和容量限制

- `EB()`设计涉及Prefill/Decode独占切换阈值和**峰值KV容量允许的batch**。阈值的推导用输出长度的hazard/完成概率分布，先从CFR常风险率/几何长度得到基准，再处理IFR（随着生成时间增加，完成概率上升）的近似校正；且batch上限又随KV记忆与完成情况变化。
- **PAPER_AUTHOR**：面向非平稳到达的`EB+`进一步实时在MB和EB之间选择，也使用EMA平滑的occupancy、负载decode比例和一次性硬件profile标定；不是单纯静态“BW阈值分叉”。
- **软件强基线**：相同vLLM build、PagedAttention、BF16下的v0/v1/EB；但各策略允许针对给定workload寻找合理token budget/max batch，属于公平系统级优化比较，**不是只改变一个CUDA kernel的严格A/B**。

### EB-M3｜§4 Table 2/3/4及附录：支持与反例

- RTX PRO 6000、ShareGPT：Qwen3-8B v1=17.07，EB=19.68 RPS（+15.3%），但Qwen3-30B-A3B v1=15.98，EB=15.48 RPS（约-3.1%）。在H200，Qwen3-30B-A3B四类负载平均EB相对v1约-2.9%。**同卡不同模型也出现策略反转**。
- **重要细节**：30B-A3B是MoE，8B是Dense；在同GPU上比较是“模型/执行特性综合变化”，不是只改参数规模或带宽。
- EB+改变的是整个在线策略；Table 3所显示的轻载下恢复MB的TTFT与重载下EB吞吐，不证明所有分位TTFT/TPOT/throughput可同时最优。论文的非平稳负载根据合成到达/长度分布切换构造。
- **我们的审查结论**：现有原文足以说明`P01`存在实际条件相关的策略交叉和反例，尚不足以识别`P13`中的单独“增加L2/SM/HBM带宽”的量化因果。
- **需继续核实**：Figure 1的模型内行为随着真实backend与Attention kernel方案变化是否保持同一实现、以及复杂长度分布下r与KV大小是否一同变化。不可将“推理混合比例”与“硬件带宽”互称干净单变量。

## 4. 三篇论文研究的是三个不同调度尺度，不能直接把speedup叠加

| 层次 | 论文主要控制什么 | 软件已有能力 | 仍不能从论文直接得到的硬件结论 |
|---|---|---|---|
| 请求/iteration级策略 | Exclusive Batching | 在MB、EB及阈值/容量/服务负载之间动态选择 | 同GPU带宽翻倍后的确切交叉比例 |
| Nano-operation/nano-batch级 | NanoFlow | 依照完整算子依赖及实测干扰，将计算、数据、通信操作流水并行 | 真实4090/4080同负载的“纯硬件算力/带宽扩展”响应 |
| SM/task/event级 | MPK | 持久kernel、JIT/AOT事件、paged共享内存及任务间流水 | 最大register footprint在真实工作中的性能损失和可硬件消除部分 |

这三个层次可同时存在于一次服务，**但不能拿三篇论文的速度提升直接相乘或相加**。改变上层批处理可能改变下层任务供给；下层更细的执行也可能反过来改变最优上层调度策略。所谓“软件剩余硬件约束”必须先有一个能承载三者某种组合的合法执行基线，而不是将某篇作为永远已解决一切的软件oracle。

### 建议统一的概念性资源表达（OUR_DERIVATION）

在固定工作量/实现和固定资源供给`R`下，对每个操作`i`记实际必要计算`F_i`、设备存储服务字节`B_i`、网络字节`N_i`；令`P_comp/P_mem/P_net`分别为经校核的可用服务率。理想资源服务账本为：

`L_comp=ΣF_i/P_comp`，`L_mem=ΣB_i/P_mem`，`L_net=ΣN_i/P_net`。

只有在明确的服务定义、无未计入工作、且具有相应峰值约束时，`T≥max(L_comp,L_mem,L_net)`才是资源容量型**必要下界**；若存在数据依赖，真实`T`还必须满足依赖路径、启动与并发竞争限制。**不能认为这个max一定可达，也不能把它与一个未证实的“无限并行时间”当严格双端界**。

若动态任务图`G=(V,E)`合法，则将每个task的可发射时间、资源占用、依赖满足时刻以及buffer/寄存器生命周期作为额外输入。P13不应从未经校准的SM容量伸缩直接计算真实RTX4080速度；在相同软件和合法任务时序下，资源干预还必须确保功能/数值与必要I/O未改变。

## 5. 三个有限科学问题和当前最低成本工作

### D01｜可供执行的工作量不足，还是工作本身消耗过大？
- **最便宜且现在可做**：只读梳理MPK §6.3/6.6、原C16 Split-K不同M与Graph正确性审查，区分`task供给/launch开销/内存流量/算法kernel切换`；制作必要证据表（无GPU）。
- **下一步的设计（未授权运行）**：同一语义、固定backend/精度、改变独立任务量；记录worker任务就绪、SM任务填充、wall、工作集与实际上下文。与已成熟Graph/融合/Persistent强基线比较。
- **停止条件**：已由强软件完全解释；同函数/资源预算不具有单变量身份；同样的供给变化没有可辨识wall响应。

### D02｜何时Prefill和Decode争用使混合执行劣于分离？
- **最便宜且现在可做**：进一步核EB Figure1/2/表2，区分同GPU`r`扫描、跨平台能力及模型混杂；把NanoFlow Figure9与Bullet的SM partition反例纳入同一对照分母表。
- **下一步的设计（未授权运行）**：同模型同GPU，同一真实请求长度序列，只改合法混合/独占策略，记录GPU执行段、TTFT、TPOT、RPS、内核实现及资源利用。用一组输入选阈值，另一组冻结不调参。
- **停止条件**：强软件已通过动态切换吸收大部分差距；剩余差主要是队列与实现重选；带宽因果缺乏可控干预。

### D03｜细粒度流水能否进一步受制于寄存器/共享资源的生命周期？
- **最便宜且现在可做**：只读深入MPK §5.3/§7，与Kitsune/Tawa/Twill/VTC实际现有能力对比，形成“已有能力—尚未量化约束”表。**需要先核强近邻，不能直接把MPK的register max一项宣称发现硬件不足。**
- **下一步的设计（未授权运行）**：若存在合法目标task pair且可比较，先做同语义、同完整任务边界的未插桩native计时与SMEM/register实测；避免为了演示“寄存器不足”自造弱persistent后端。
- **停止条件**：强编译/软件分段能够避免注册资源浪费；显存服务或任务数主导；跨任务优势只因改变kernel和数学算法。

## 6. 下一阶段建议（研究层默认执行，计算节点另审）

**建议Round A2：“跨调度尺度的瓶颈转折与最近邻对照”**。在本协调分支中读[Bullet](https://arxiv.org/abs/2504.19516)、[Kitsune](https://arxiv.org/abs/2502.18403)、[VTC](https://www.usenix.org/conference/osdi26/presentation/hu-muyan)、[Tawa](https://arxiv.org/abs/2510.14719)、[Twill](https://arxiv.org/abs/2512.18134)的**具体实验组**，输出：
1. 每篇真实input/model/platform/正确性/强基线/改变变量与指标的证据表；
2. 对NanoFlow/MPK/EB分别判断软件现有能力、功能语义和保留的硬件约束；
3. 最多两张新的可证伪问题卡，附一个反例和不用GPU的最便宜证据检查；
4. 训练/非LLM继续对照MegaScale-MoE、Sobek，不让第一轮总计划退化为纯LLM推理。

**Round A2现在只开展原始文献/协调分支研究，不下发任何Goal**；是否需要以后174 CPU-only源审或109 GPU发现性探针，须先明确模型、输入、受控变量、可观测指标、成本/STOP，然后另外形成提案。旧C16 Stage A与AWMA R27R3继续关闭；AWMA只同步已审查fixed evidence。
