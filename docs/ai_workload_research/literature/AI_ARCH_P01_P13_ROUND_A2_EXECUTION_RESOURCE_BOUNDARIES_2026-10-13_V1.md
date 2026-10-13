# AI-ARCH Discovery｜Round A2：GPU执行组织与资源瓶颈迁移的原始实验组审计（2026-10-13 V1）

> **性质**：AI-ARCH Discovery与总体科研协调的**文献/设计底稿**。只读论文及此前已接受的跨项目知识；不是论文复现、GPU实测、模拟器结果、机制创新认定或新Codex Goal。
>
> **主问题**：P01——AI负载在工作量和执行阶段变化时，GPU约束如何迁移？P13——增加SM、片上缓冲、计算/带宽或调度自由度时，收益为何饱和？
>
> **科学权限**：109 GPU、174模拟器、Stage A、AWMA新实验、holdout、新机制均未由本文件启动或获得新的执行权限；AWMA仍由独立窗口管理，C16只作历史证据。本文的新推论为HYPOTHESIS，外部作者结果为PAPER_AUTHOR；不得提升为NATIVE_MEASURED。资料先通过最新协调分支检查和AWMA Round09/21去重。

## 0. 新增来源及精读深度

| 来源编号 | 原始文件/版本 | 实际检查 | 证据类型 |
|---|---|---|---|
| B | [Bullet, arXiv 2504.19516 HTML](https://arxiv.org/html/2504.19516) | §2.2、§3.2–3.5、§4.1–4.6，Tables 1–5、Figures 14–20 | 原生GPU服务和局部硬件测量，另有拟合性能模型 |
| K | [Kitsune, arXiv 2502.18403 HTML](https://arxiv.org/html/2502.18403) | §3–6，Tables 1–2、Figures 5、9–14，资源灵敏度 | **A100原生queue microbenchmark + 修改过的A100类NVArchSim主体模拟** |
| V | [VTC, OSDI 2026正式PDF](https://www.usenix.org/system/files/osdi26-hu-muyan.pdf) | §7.1–7.6，Tables 1–4、Figures 9–12，方法 §5–6 | A100 PCIe/H100 NVL原生执行（**指定layer或block，不全是完整网络**） |
| T | [Tawa, arXiv 2510.14719v2 HTML](https://arxiv.org/html/2510.14719v2) | §III-B–D、§IV、§V-A–F，Figures 8–12 | H100原生kernel microbenchmark；代码生成与调参见原文 |
| W | [Twill, arXiv 2512.18134v1 HTML](https://arxiv.org/html/2512.18134v1)；[OSDI 2026正式发表](https://www.usenix.org/conference/osdi26/presentation/soi) | §3/5/6，Figures 7–11，尤其§6.1与§6.3 | H100/B200真实kernel + 离线约束求解；当前发表信息已核，实验数值依据指定v1 |

**阅读限制**：本轮是上述方法、实验、关键图表的有界审计，不是全部文本逐句核对；未运行作者GPU代码，未取得作者每次GPU执行原始日志。原始输入的完整revision、seed、全部自然到达timestamps与附带artifact若本次位置没有明确披露，逐项保留“未核实”；不从论文标题或模型名填补。

承接背景：[Round A1 22条具体实验组](AI_ARCH_P01_P13_EXPERIMENT_GROUP_AUDIT_2026-10-13_V1.md)、[Round A1机制层精读](AI_ARCH_P01_P13_RESOURCE_MODEL_CAUSAL_READING_2026-10-13_V1.md)、[跨C16/AWMA证据索引](../AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。

## 1. Bullet：请求级SM空间划分和时间调度（真实GPU）

### B-01｜§2.2 Figure 2/Table 1：理论wave-quantization与Prefill实际利用率

- **作者问题**：为何Prefill被概括为计算密集，Transformer一层的Tensor算力仍可能大量闲置？
- **实际对象/平台**：Llama-3.1-8B Prefill，NVIDIA A100；不同sequence length的QKV、Attention、O、MLP。
- **变化/控制**：在理论分析中改变长度/对应grid，估算在SM wave tail中的空转；同时有真实GPU计数器下的Prefill分类。
- **作者事实**：Table 1的“总层理论wave闲置比例”在seq 1024、2048、4096、16384分别为19.4%、10.4%、9.1%、0.5%，但单独O-proj的1024点为40.7%；Figure 2说明Attention等执行也有与矩阵计算不同的硬件利用率。
- **我们的解释**：SM波次填不满是任务几何问题，并非SM数越大越有帮助；但作者的“wave idle ratio”是理论近似，不能直接等同真实wall加速上限。Attention实际后端和shape也影响结果。

### B-02｜§3.2 Figures 8–10、Table 2：SM-scaling Roofline与竞争校准

- **作者问题**：分给Prefill/Decode不同数量SM时，计算服务、数据带宽和共存竞争怎样变化？
- **对象/变量**：A100、H20的SM partition；Llama3.1-8B / Qwen3-32B受控并发配置；执行状态包括两阶段sequence/context长度、batch和SM配额六维。
- **模型假设**：计算供给按可用SM数线性近似，带宽随SM数增加直到转折点饱和；先计算按FLOPs和bytes估计的Roofline延迟，再用实测延迟比例系数校准。对隔离SM仍共享的内存系统竞争，使用UG与memcpy共存的实测作校正。
- **作者真实样本**：7360个并发执行状态，每条件30次；95%的测得延迟对同状态均值偏离不超过±6.8%；Table 2报告若干稀疏采样范围的MAPE，例如Prefill 30样本覆盖到32k时5.3%，而18样本配置为9.1%。
- **结论边界**：这是**带真实校准的服务预测模型**，不是通过改变芯片上物理SM数量得到的新GPU架构；不同硬件的总内存带宽、L2、compute等同时变化，不能将跨卡预测当资源单变量实验。

### B-03｜§4.1/4.2 Table 3/4 Figure 14：有合法输入长度但合成到达的在线服务

- **输入/模型**：ShareGPT（聊天）、Azure-Code（生产代码补全来源）、arXiv-Summary（长文本）；请求到达按Poisson生成。Dense Llama3.1-8B/70B与FP8 MoE Qwen3-235B-A22B；CUDA12.4；8×A100-80GB、8×H100、8×H20三平台，TP用于多GPU。
- **基线**：vLLM v0.8.5 (1024 chunk)、SGLang v0.4.6 (1024/2048 chunk)、NanoFlow (1024 chunk)。Bullet基于SGLang v0.4.6/PyTorch 2.6.0，使用SM masking、两条异步执行线及CUDA Graph decode。
- **指标**：请求吞吐、平均TTFT/TPOT、指定数据集归一化TTFT/TPOT SLO与P90 SLO通过率；**不是只测某个GEMM的时长**。
- **作者报告**：相对SGLang-1024，在所报告单GPU比较中请求吞吐平均1.09×、最高1.20×；其他正文的TTFT倍数有不同请求率与分母，不能相加。
- **局限**：长度/任务来源真实，Poisson到达是人为生成；不同系统的chunk策略变化也是系统软件因素。摘要的总体1.26×与这里的1.09×对应不同综合范围，不能混用。

### B-04｜§4.3–4.5 Figures 17–20 Table 5：动态SM分配因果近邻与负面控制

- **对象**：Llama3.1-8B、Azure-Code请求率5req/s的SM份额时间线；ShareGPT 20req/s、0–27s硬件利用率观察窗；固定SM份额对照，A100相关。
- **变量**：固定Prefill SM数量/全部SM、动态SM份额；Naive共跑不调度、仅Partition、仅Scheduler、完整Bullet等消融。
- **作者报告**：固定配置无法同时最佳TTFT/TPOT；在指定ShareGPT窗口，Bullet平均active SM cycles为86.2%，作者报告相较SGLang高11.2%（原文百分号不擅自改成百分点）；TensorCore与带宽利用率改善另报。资源调整mean约4.1微秒，CPU metadata send/recv均值0.21ms。
- **科学局限**：SM active cycles不是Tensor Core利用率；固定SM mask改变的是**可供任务使用的资源配额**，不是实际增加芯片SM；部分并发消融包含调度/请求执行次序，因此不能声称只改变缓存参数。

**Bullet提供的已解决能力**：按模型和请求状态自适应分配SM、通过SM masking让Prefill与Decode并发、在满足SLO时调整优先级。不能再把“采用SM动态配给使两阶段并发”作为尚无人解决的宽泛新机制。

## 2. Kitsune：跨算子数据流和硬件资源缩放（原生micro + 主体模拟）

### K-01｜§4.1 Figure 5：原生A100 L2驻留原子队列

- **模型/输入**：不是完整自然模型；A100原生CUDA queue microbenchmark，54队列/108 CTA，测试payload尺寸和atomic同步开关。
- **作者实测**：128–256KB payload时合计约2TB/s；1KB时同步开销可造成约12倍吞吐下降；payload过大可能溢出L2、吞吐下降。
- **局限**：证明**该有限payload/队列组织的通信原语真实存在**，并不证明完整模型在真实A100上获得模拟中同样的应用加速。不能由合计字节吞吐推出零等待或任意数据交接无成本。

### K-02｜§6.1–6.3 Table 1/2，Figures 9–11：五应用的推理对照

- **对象**：DLRM推荐、MeshGraphNets、NeRF、GraphCast、Llama3-8B（Llama另分Ctx与Tok）。Table 2提供算子数量、纵向融合覆盖、Kitsune覆盖、逻辑估计的off-chip traffic差。
- **baseline**：unmodified PyTorch；另外用compiler/modeling flow构建来自TensorRT、AStitch、Welder等思路的纵向融合模型。注意这不是每个框架都在对应形状上运行同版本二进制的严格多实现Native A/B。
- **指标**：模拟器中局部subgraph/应用时间、应用跨部件估计traffic和operator覆盖。作者报告推理application geomean约1.5×；Llama-Ctx局部子图收益仅4%–8%，尽管子图时间覆盖84%。Table 2中Llama Tok traffic削减仅0.07%，Ctx 49.07%；不能因为两者都是Llama就混合推断。
- **来源层次**：**NVArchSim modified A100 model / SIM_MODELED**，不是五个完整应用的真实A100加速。
- **我们的解释**：同一模型Prefill/Decode对数据流结构的敏感性可很不同；强forward数值与实际loop/context驻留仍需独立验证。

### K-03｜§6.4/6.5 Figure 12/14：训练及非LLM应用

- **对象**：DLRM、MeshGraphNets、NeRF、GraphCast及Llama训练的fwd/bwd；同模拟A100、统一应用图及纵向融合模型。
- **作者报告**：training end-to-end改善约1.1–2.2×，低于部分推理场景；部分backward无法像forward一样完全流水化，若目标子图时间占比较低，Amdahl上限明显。
- **边界**：训练本身的数值/收敛并未由该模拟直接证明，本轮不称其为真实训练完整轨迹结果；作者明确承认用于纵向融合的训练支持是乐观建模。

### K-04｜§6.6及论文摘要的资源敏感性

- **受控变量**：在A100类已资格化模拟器中，**只增强特定资源**（如on-chip计算/L2带宽×2）并保持DRAM峰值带宽不变，检查BSP与Kitsune的响应。
- **作者报告**：摘要称廉价片上资源加倍时，Kitsune对推理/训练增益分别约47%/27%，而bulk-synchronous基线的变化约18–26%；另有资源低利用时间比例对照（low定义为峰值的33%以下）。
- **关键局限**：上述是模拟器模型relative反事实，而且“两个资源同时翻倍”的组合不能拆成各资源独立因果。它适用于论文的具体A100模型和五个应用，不可迁移为RTX4080真实性能预测。
- **已解决能力**：跨CTA队列、Tensor与SIMT任务共同驻留、必要grid-scheduler修改和ILP任务分配。新工作若要做类似操作，必须对照Kitsune而非只有传统串行kernel。

## 3. VTC：物理中间张量已被编译器广泛消除（真实GPU，强软件对照）

### V-01｜§7.1 Table 1：实际测试对象不是全套模型连续推理

- **模型组件**：Llama 3 8B **Decoder Layer**、Gemma 2 9B **Decoder Layer**；输入Query Length=1、Context Length=4096，BF16；EfficientViT-Base **Attention Block**、Resolution=4096；YOLOv11n **C3K2 Block**、Resolution=640；ShuffleNet **ShuffleUnit**、Resolution=224，非LLM部分为TF32。
- **GPU/基础环境**：A100 80GB PCIe（Xeon Platinum8358），H100 NVL（EPYC9454），Ubuntu22.04、driver535.183.06、CUDA12.1。batch 1与16。
- **关键口径**：正文叫“end-to-end inference”，但Table 1所列运行单元明确是**Layer/Block/Unit组件**；原文没有凭这些Table 1样本证明“整套8B Llama多层请求在同部署下快1.93×”。
- **控制**：相同组件与输入形状、切换compiler/runtime；不能把任意随机Tensor自动当自然文本输入。

### V-02｜§7.2 Figure 9/§7.3 Table 2：编译器性能与容量

- **强基线**：PyTorch 2.6.0 + torch.compile（Inductor）、ONNX Runtime 1.21.1、XLA、TensorRT 10；VTC加入TorchInductor改数据搬运表示。
- **变化/指标**：单GPU、各组件与batch 1/16；运行时延和PyTorch allocator peak memory。相对**四个baseline中每点最好者**报告至多1.93×、平均1.28×，不能只称“相对PyTorch”。
- **作者报告**：A100表2，在Llama组件BS=16，PyTorch 1787.3 MB→VTC 714.5 MB，减少60%；BS=1 528.8→461.8 MB。跨5个模块平均peak内存节约17.5%。
- **限定**：减少peak memory不是同幅speedup；训练不在这组评估。Table 1的网络成员名称不等于完整模型执行。

### V-03｜§7.5 Table 3/4：真正的强vLLM路径负例

- **样本**：vLLM V1，Llama 3 8B，4096输入token、BF16、单个Decoder Layer；A100与H100分别计时。
- **改变项**：VTC使QKV临时张量变为虚拟，直接发布Q和KV；两套结果同任务，是否启用此opt是主变量。Table 3另给子图时间与完整**decoder layer**时间。
- **作者实测**：A100 vLLM 9.152ms、VTC 9.055ms（约1.011×）；H100 vLLM与默认VTC均4.230ms，**没有性能提升**；强制使用虚拟张量优化时H100为4.600ms（约8%慢）。
- **作者归因**：H100上vLLM使用更高效cuBLAS QKV MatMul而VTC替换的Triton版本较慢；profile-aware选择器避免强制退化。不能将整个8%归因于“地址映射多做了指令”，有kernel差异。
- **我们的推断**：跨算子搬运是否消除，应在相同最好计算kernel选择之后判定残余，而不只是从图结构上发现了一次临时存储。

### V-04｜§7.6 Figure 11/12：非LLM组件真实案例

- **对象**：YOLOv11的C3K2（Split/Concat）和EfficientViT Attention Block的中间张量；使用第V-01组的输入分辨率与batch。
- **效果/原因**：虚拟张量将不同消费者需要的逻辑视图映射到已有物理存储，避免部分Split/Concat/reshape/transpose的单独搬运。YOLO的部分连续chunk仍足以访问合并；EfficientViT有5个实际计算kernel，省去中间的数据搬运节点。
- **边界**：虚拟映射可以改变产生与消费访存的方式，必须检查剩余计算内核的layout与访存代价；不能由“删除了一个operator”推得该operator全部time被免费收回。
- **已解决能力**：数据搬运算子的普通转换与跨消费者逻辑视图，VTC已给出软件实现。不能在P06直接声称“GPU必须物化每种layout”。

## 4. Tawa：H100内部warp级异步数据流（真实局部kernel）

### T-01｜§V-A/B Figure 8：GEMM，真实H100

- **输入/平台**：H100 SXM5 80GB，CUDA12.7；FP16/FP8，M=N=8192，K从256扫描到16384。数据为代表性shape microbenchmark，**不称完整LLM执行**。
- **强基线**：cuBLAS 12.7、CUTLASS 4.0.0、Triton相同commit（官方软件流水）、TileLang与ThunderKittens各自冻结commit；不同tile在64/128/256中调优。
- **报告**：FP16对cuBLAS平均约1.01×，FP8平均约1.06×；小K可能低于cuBLAS，大K TileLang/ThunderKittens个别更强；按不同分母给出其它收益，不能用与弱Triton的数替代强库。
- **公平局限**：Tawa的aref buffer大小D、MMA pipeline深度P**人工选优**，不是全流程自动全局最优；与强库相比的局部优势有限。

### T-02｜§V-C Figure 9：batched与grouped GEMM

- **输入**：batched GEMM，8个矩阵，方形M/N/K在1k–16k扫描；grouped GEMM改变组数量与形状，固定N/K、M为512的倍数。
- **对照**：Triton和TileLang，ThunderKittens无可运行对应kernel；报告对Triton至多约7%改善，部分batched组对TileLang至多50%。
- **语义限制**：这是**形状构造的GEMM代理**，不能把它称作自然MoE route完整dispatch→expert→combine。运行时专家负载及路由正确性未通过该实验被证明。

### T-03｜§V-D Figure 10：MHA与强FA3

- **输入/实现**：H100、batch4、head dim128、长度1024–16384、causal和noncausal、FP16/FP8。强对照包含CUTLASS C++实现的FlashAttention-3，以及Triton/TileLang/ThunderKittens。
- **作者报告**：FP16 Tawa最高达到FA3吞吐96%，对Triton约1.21×；FP8最高约FA3的89%，部分FP8 ThunderKittens输入失败。
- **局限**：达到“手工FA3的96%”是接近已有强能力，不表示比最强FA3快1.21倍；后者是相对Triton的分母。H100单算子实验不能转成完整serving。

### T-04｜§V-E/F Figures 11/12：流水加深反而会压低占用

- **受控条件**：K=16384的GEMM，扫描aref共享存储buffer深度D、MMA并行深度P，以及persistent与nonpersistent。(D≥P)的合法区间另需满足真实SMEM容量。
- **作者报告**：P从1→2通常改善，但达到3时register/accumulator/SMEM压力会降低吞吐；persistent通常比对应nonpersistent快约5–10%。该图的比较是局部microkernel，不是已证明所有AI kernel最佳P=2。
- **意义**：资源生命周期（producer数据预取、consumer持有碎片、共享缓冲可重用时间）与异步深度是共同约束，不是增加计算单元就能忽略。
- **已解决能力**：自动producer/consumer warp区分、aref的put/get/consumed规范、mbarrier的发布/借用/归还、有限环形缓冲、持久内核和基本流水搜索均已存在。

## 5. Twill：调度理论最优与真实GPU寄存器分配之间的边界

### W-01｜§6.1–6.2 Figures 7/8：H100和B200 Attention Forward

- **输入/平台**：FP16 noncausal FlashAttention forward，batch4、32heads、dim128，图内扫描序列长度；H100 SXM5 80GB与B200 180GB，CUDA13；Twill方案求解在单Xeon8570核上执行。
- **基线**：Triton tutorial、人工移植Triton IR的CUDA-default、Twill-SWP、Twill联立SWP/WS、官方FA3/FA4及部分cuDNN强实现。
- **作者结果**：Twill在Hopper可恢复与FA3相近的软件流水策略，相关强点接近FA3 1%内；Blackwell上得到与FA4相同的关键角色安排，长序列下实现性能与FA4相差约2%。
- **关键执行身份**：作者明确**没有让Triton直接生成最终高性能二进制**，而是把求出的schedule手工lower到CUDA C++。因此“自动推得策略”成立，但“全自动从Triton到最强可执行内核”没有由本轮论文验证。

### W-02｜§6.3.1 Figure 10：Hopper Backward的寄存器约束

- **输入/平台**：同FP16 noncausal attention规格，H100；与单pass FA3 backward及cuDNN对比，不把Triton tutorial的双pass较差算法当唯一强baseline。
- **作者结果**：在寄存器容量限制下，Twill 88秒求出不跨iteration进行ILP的策略，与FA3人工限制吻合；官方FA3在16384长度下约比作者手写版本快11%，作者认为部分来自更合适的80×128 tile。
- **意义**：有时候跨iteration流水**在给定寄存器预算内就是不可行**，不是调度算法不够聪明；若想提出新寄存器机制，必须证明软件tiling/register allocation之后仍有实质残余。

### W-03｜§6.3.2 Figure 11：Blackwell Backward的负面结果

- **对象**：B200、FP16 backward（包含global atomic reduction）。
- **作者结果**：最初找到理论上满足per-thread register budget的两warp group策略，但**ptxas实际分配导致大量寄存器spill并严重拖慢执行**；收紧预算后重新求解，改用三warp group策略，64秒求出与FA4类似的安排。整体结果差别不大，作者认为该single-pass算法主要受atomic reduction完成/带宽限制。
- **我们可以提的问题**：compiler抽象资源可行性与实际分配之间的差距何时影响真实时间？
- **不能做的推断**：这不是已证明“新寄存器硬件可稳定加速”或者“全AI训练都register-bound”；它反倒证明软件改变warp角色和注册预算可规避一部分问题。

### W-04｜§5.4：最优性资格

- **理论对象**：给定的singly nested、无额外control flow的tile级loop，已知依赖图、机器资源保留表和受限成本模型，联合最小化initiation interval；tile大小**不自动选**， variable-latency/TMA操作用规定近似及额外pipeline depth参数处理。
- **限制**：最优的是这个**抽象机器/循环类的schedule**，不是所有CUDA程序的全局最短真实时间；实际代码生成/同步/寄存器分配依然可能改变结果。优化求解几十秒至数分钟，预期离线编译或开发辅助，而非每请求在线调度。

## 6. 已有软件能力与真实剩余缺口矩阵

| 尺度/对象 | 代表研究 | 已经提供的可用能力 | 正确性/性能证据层 | 不能直接再称创新的宽泛主张 | 可能的剩余问题（只是假设） |
|---|---|---|---|---|---|
| **Request/阶段** | Bullet；NanoFlow；Exclusive Batching | SM按请求动态配给、服务SLO下的Prefill/Decode并行，nano-batching，以及策略切换 | 真实GPU服务；到达分布各有合成部分 | “动态分配SM/简单重叠” | 动态任务量下降时有效供给和资源饱和点会否稳定迁移？ |
| **跨operator/执行图** | Kitsune；VTC；MPK | 跨算子空间流水、tile队列、SM task事件、虚拟Tensor减少中间物化 | Kitsune主体模拟；VTC/MPK原生模块/执行 | “去掉layout中间数据”“把两个算子流水” | 同语义最佳各自布局/寄存器配置之间是否还存在未被软件吸收的依赖时间？ |
| **CTA/SM持久任务** | MPK；Tawa；Kitsune | SM级任务放置、persistent CTA、部分SMEM重用、控制流与执行资源约束 | MPK/Tawa真机；Kitsune模拟 | “GPU还不会持久任务/复用SMEM” | 当前最优任务组织是否受寄存器最大需求或精细任务调度成本约束？ |
| **Warp/异步单元** | Tawa；Twill；FA3/FA4 | producer/consumer warp分工、WGMMA/TMA overlap、软件流水、有限缓冲、约束求解 | H100/B200真实microkernel；部分编译lowering手工 | “自动流水/warp specialization是新想法” | 可变工作量/资源预算、实际compiler分配与理论排程的差距何时影响关键路径？ |
| **训练与非LLM状态** | Kitsune训练、Twill backward、VTC视觉、Sobek、MegaScale-MoE | 部分反向流水、向量/图表示优化、状态生命周期与通信重叠 | 模拟/原生kernel/原生训练，各自不同 | “AI都是Decode访存模式” | 统一资源约束能否解释导数阶和图更新/训练通信的不同饱和形状？ |

**结论**：以上工作实际上把“缺少软件融合、缺少warp specialization、缺少SM动态配额、必须物化所有中间tensor”等粗粒度动机大部分覆盖。AI-ARCH要找的是**强实现已覆盖这些能力以后，某个具体算子家族在确定工作量、依赖和资源预算下仍有实质不能被软件消除的性能/容量残余**。这不等于这些论文已经证明不存在未来硬件设计空间。

## 7. 对P01/P13的方法调整：研究资源曲线需先规定谁可调

从原文得到的统一判断（OUR_SYNTHESIS）：

1. **物理资源与软件分配是不同自变量**。Bullet变化SM mask配额，Kitsune在模拟器变化模拟硬件资源，Tawa/Twill变化流水buffer/warp角色，VTC变化逻辑中间值的存储组织；不同曲线不可直接叠加为“增加物理SM数量”的因果定律。
2. **解释一个拐点至少区分四种竞争假设**：(a)独立可调度任务不足；(b)所需服务带宽/算力达到上限；(c)数据/事件没准备好，即使资源闲置也不能发；(d)寄存器/SMEM/缓冲资源限制了可驻留任务。
3. **软件提供的优化不是免费的硬件oracle**。每种优化必须支付自己的缓冲、等待、索引、额外指令、改变后端或数值次序的成本。
4. **作者“增加一项资源更快”有时是模型内部反事实**。Kitsune的资源缩放是模拟结果；真实GPU不同SKU比较又同时改变多种资源；不应偷换为4090/4080 native测出的资源曲线。
5. **应用效果不可由两个局部speedup直接相乘**。训练还要计梯度写回/通信与数值合格，非LLM还要计图准备/导数阶与状态容量，服务还要计请求到达与SLO。

建议未来将资源响应定义为“同语义+冻结软件/输入+明确干预轴”的响应曲线，资源轴包括独立工作供给、SM配额/算力、warp/register/SMEM、L2/DRAM、数据就绪与网络等。只有当现有真实native/资格化模拟支持相应干预时才给定量速度数字。无效的“无限资源”oracle在缺乏架构校准时不升级为真实GPU结论。

## 8. Round A2结束只保留两张可证伪问题卡（不是机制或执行授权）

### Q-A2-01｜强软件后，任务供给饱和点与资源服务饱和点何时分离？

- **确切问题**：在语义、主要kernel实现和精度不变时，增加可同时ready的GPU任务数，是否存在一个时间/资源可辨的拐点：先受独立任务数不足制约，后受算力/DRAM/L2服务约束？“SM配额减少”与“物理SM增加”应分开讨论。
- **文献依据**：Bullet B-01/B-02的SM配额/短prefill wave现象；MPK已有的device端任务调度与低batch结果；Kitsune K-04有模拟硬件资源缩放但不是真实GPU。**反例**：VTC H100强软件路径无收益、MPK随某些batch收益收敛、Kitsune Llama-Ctx模拟加速仅4%–8%。
- **竞争解释**：后端切换/Graph路径不同；KV/权重带宽；launch overhead；请求到达排队；数据没ready；寄存器限制而非SM不足。
- **最便宜且当前可做**：CPU/纸面核对既有C16 Split-K不同M、MPK/NanoFlow固定输入与Bullet B-01中的实际任务几何；标出哪些点满足同实现/同负载与同指标。**不是授权恢复C16 Stage A**。
- **未来如果真有必要的发现性GPU探针（尚未批准）**：同一算子家族/精度/后端、固定权重和真实输入、只改独立task数量或batch中一个轴；记录未插桩wall、实际grid/SM task-ready、可识别的算力/带宽/launch指标。保留不参与筛选的调用位置/形状。
- **停止**：无法冻结同一实现或任务分母；成熟Graph/persistent/kernel后曲线无稳定剩余拐点；只看见利用率差而没有时间响应。
- **目前状态**：DISCOVERY_DESIGN_ONLY，无109、无174模拟、无新资产。

### Q-A2-02｜异构task的资源生命周期是否造成强软件仍不能避免的等待？

- **确切问题**：当producer/consumer各自采用成熟布局/tiling/warp specialization后，受SMEM释放、寄存器live-range、任务就绪发布及跨阶段容量的约束，是否仍有可区分、真实位于关键路径上的等待？该等待是否超出普通软件调度/虚拟tensor与强kernel能处理的范围？
- **文献依据**：Tawa T-04的D/P过深导致吞吐退化；Twill W-02/W-03的register模型与实际ptxas分配差；MPK per-thread register max与device任务图；VTC/FA3/FA4/Kitsune已经吸收大量物化和交接。
- **明确反例**：VTC强vLLM H100强制优化使Decoder Layer变慢；Twill降低register预算就解决一次实际分配失配；Tawa在小K跑不过cuBLAS。说明不少候选是软件调参/后端选择问题。
- **最便宜且当前可做**：进一步核MPK §7、Tawa Figure11、Twill §6.3、VTC Table3，把资源生命周期的“作者实测、源码机制、我们假设”分别列成界面；沿现有C16 FFN负例检查是否已证明上限不足（历史已判局部双流无效，不重复试）。
- **未来可能诊断（尚未批准）**：先找一个具同语义合法producer/consumer、必要数据发布和强kernel比较的operator family；以原生region wall和buffer/register/SMEM、ready/consumed事件为主要观测，必须包含非目标成本与严格数值输出。避免为了诊断自造劣质persistent kernel。
- **停止**：已有软件fusion/VTC/FA3/Tawa解决，或改变kernel实现无法匹配同语义，或观察的queue/traffic差无法兑现关键时间；直接转为软件优化/无硬件机会。
- **目前状态**：DISCOVERY_DESIGN_ONLY，无新GPU/硬件机制权限。

## 9. 下一阶段Round A3：明确工作、做法、交付及资源门槛

**拟议题目：P01/P13 最小证据闭环与候选准入检查（CPU/文献优先）。**

1. **执行内容**：以Q-A2-01和Q-A2-02为中心，查原始C16已审查的M1/M64、Split-K及FFN案例的现有小型review pack（不重跑，不全量扫描raw）；补齐作者源码/附录对寄存器及task调度的证据。核跨负载训练/非LLM是否存在一个可以独立检验的family，不按现有模型权重倒推。
2. **做法**：先制作两张“可辨识性账本”：工作量→强软件路径→一个受控变量→竞争解释→可测观测量→反例→时间/容量分母→STOP。若现有raw或源码缺失，不自动扩大到164大数据或新模型下载。
3. **交付**：一份最多两页的候选准入建议（每张问题是否能被现有证据区分、是否还缺必要自然输入和最强近邻）；最多**一项**未来109发现性探针草案，只有已明确人、模型、条件、预算和资源锁时才提出，不保证一定需要GPU。
4. **停止条件**：现有软件反证/无法取得同语义强基线/没有真实family覆盖/工具边界不支持因果；保留科学负面判断。
5. **资源与权限**：当前仅ChatGPT文献+GitHub只读交叉核对/协调笔记维护；**不启动109 GPU、174模拟器、Stage A、AWMA R27R3、不运行CPU-only Codex Goal、不动模型或GPU锁**。如果将来确需执行性CPU-only或GPU工作，应把具体合同清楚列出、单独评审，不由本笔记自动触发。

## 10. 与AWMA和历史C16的交接

- AWMA R27R3的最新独立接受状态仍为 R27R3_B0_REFERENCE_NOT_REPEATABLE / COMPLETE-STOP，未在本轮评价其根因、C1/S2、容量或重新运行。
- C16 Stage A TERMINAL_PARTIAL及最终Problem Discovery Reset全部保持冻结；旧FFN、Split-K案例只能按已接受范围复用，不能因新问题命名而改成新授权。
- 本轮引用Kitsune的训练/NeRF/GraphCast和VTC的视觉组件，仅将其作为外部证据和约束反例，不把它们变成本项目Native数据。
- 协调分支仅追加被核实的PAPER_AUTHOR与HYPOTHESIS；不改既有科学authority，不向AWMA同步未审查的推论为accepted。
