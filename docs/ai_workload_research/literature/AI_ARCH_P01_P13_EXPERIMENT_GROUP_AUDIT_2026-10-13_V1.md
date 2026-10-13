# AI-ARCH Discovery｜P01/P13 原始论文实验组审计：Round A1（2026-10-13 V1）

> **性质**：只读文献研究及可证伪问题设计；不是GPU/模拟器/Codex执行授权、复现实验结果或机制晋升。所属分支：`hrl/ai-workload-research-coordination`。研究主轴：P01（瓶颈随阶段/负载迁移）＋P13（资源配比与扩展规律）。
>
> **核验范围**：OSDI 2025 NanoFlow正式PDF、OSDI 2026 MPK正式PDF（包括图表页面）、ICML 2026 Exclusive Batching的arXiv 2606.00516v1 HTML（PMLR正式出版元数据另核）、Bullet arXiv 2504.19516 HTML、MegaScale-MoE arXiv 2505.11432 HTML、Sobek arXiv 2607.18074 HTML。前3篇作重点实验组审计；后3篇作跨服务、训练和非LLM的限定反证。不是逐页、逐字全文审计；没有运行作者代码或访问109/174/164 raw。每条仍为`PAPER_AUTHOR`，不是`NATIVE_MEASURED`。
>
> **恢复去重来源**：既有AWMA [Round09](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_09_BROAD_SIDE_RESEARCH.md)、[Round21](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/rounds/2026-10-02_ROUND_21_POST_R20_PROBLEM_DISCOVERY.md)及[跨项目证据索引V1](../AI_WORKLOAD_C16_AWMA_EVIDENCE_INDEX_V1.md)。本轮没有更改AWMA scientific authority。

## 0. 本轮科学摘要：五条不能混淆的边界

1. **“理论上计算主导”不等于“当前执行已经持续占用计算单元”**。NanoFlow在大批量、给定模型/设备下使用计算/存储/网络工作量估算服务的资源下限；其实际顺序执行可能只有有限计算利用率。这个差距是执行组织问题，不必然是计算单元不足。
2. **“低batch MPK明显改善”不等于“增加SM就能改善”**。MPK通过SM级任务化、持久kernel、事件依赖与算子间流水改变可供调度的任务和调度边界；主Figure 9是固定长度离线batch推理，不是真实到达队列/SLO曲线。
3. **“Prefill和Decode可以重叠”不等于“混合执行总更好”**。Exclusive Batching证实同GPU同软件体系下策略优劣随模型、输入配比变化；RTX PRO 6000与H200间也有明显差异，但硬件除带宽外多参数变化，不是带宽的严格单变量因果实验。
4. **训练扩卡要区分强扩展和弱扩展**。MegaScale-MoE固定全局batch扩卡时MFU下降、pipeline bubble暴露；工作量与卡数同比增加时是另一项试验。不能把投影的1T训练天数当成真实完成的训练。
5. **容量、算子吞吐、整模型端到端是不同结果**。Sobek删除边尺度中间物化后仍有随边数增长的图/特征存储；其图准备和编译排除在计时外，不能转成真实分子轨迹端到端加速。

## 1. 原始论文与版本注册

| ID | 原文（固定出版入口） | 本次读到的直接章节/图表 | 读深/不足 |
|---|---|---|---|
| NF | [NanoFlow, OSDI 2025 PDF](https://www.usenix.org/system/files/osdi25-zhu-kan.pdf) | §3.3–3.6，Figure 2/3，Table 1/2，§6.1–6.6，Figure 7/9/10 | 正式会议PDF；核关键方法/设置/图表；未重新执行 |
| MP | [MPK, OSDI 2026 PDF](https://www.usenix.org/system/files/osdi26-cheng.pdf) | §6.1–6.7，Figures 9–13，Tables 1/2，§7资源边界 | 正式会议PDF；核正文和主要图表；没有验证artifact |
| EB | [Exclusive Batching, arXiv 2606.00516v1](https://arxiv.org/html/2606.00516)；[ICML 2026正式元数据](https://proceedings.mlr.press/v306/zhang26eo.html) | §1，§3.1，§4.1–4.5，Table 2/4，附录A.2 | 实验组以arXiv v1为准；不能默认最终会议排版逐字一致 |
| BU | [Bullet, arXiv 2504.19516](https://arxiv.org/html/2504.19516) | §4.1–4.5，Figures 14/17–19、Tables 3/5 | 指定HTML公开版关键章节；未审全量实验/代码 |
| MM | [MegaScale-MoE, arXiv 2505.11432](https://arxiv.org/html/2505.11432) | §6.1–6.3，Tables 2–5，Figures 12/13 | 训练代表实例；需后续锁定具体PDF版本和训练数据集细节 |
| SB | [Sobek, arXiv 2607.18074](https://arxiv.org/html/2607.18074) | §5.1–5.4，Figures 2/3，Table 3，方法 | 非LLM代表实例；为算子级合成图与规模扫描，非完整自然轨迹 |

若具体输入seed、请求到达时间戳、checkpoint revision或单次重复数未在本次核验位置查到，只写**本次未核实/未见披露**；不替作者补齐。

## 2. 逐实验组审计

统一字段：**问**=确切问题；**对象/输入**；**平台/基线**；**变量→测量**；**作者报告**；**局限/我们的解释**。所有“我们的解释”均不视为作者原结论。

### 2.1 NanoFlow：整体资源下限和实际重叠分开

**NF-01｜§3.3，Figures 2/3；理论负载分类（MODEL_ESTIMATE）。**
- **问**：不同模型和输入输出长度下，理想重叠时整体计算、显存和网络需求哪个更紧？
- **对象**：LLaMA-3 8B（1×A100）、Mixtral/Mistral 8×7B、LLaMA-2/3 70B、Qwen2 72B（后四者8×A100）；Splitwise、LMSYS-Chat、ShareGPT的长度统计及512/512、1024/512、512/1024固定长度；其他GPU世代在Table 1另作规格敏感性估算。
- **变量→指标**：模型、长度分布、硬件峰值计算/存储/网络能力；以预估工作量／峰值速率的资源时间比分类，**不是真实整模型运行时哪一种单元阻塞了多少周期**。
- **作者报告**：多数被研究的“大批量服务工作量”在理想整体资源下限上计算占主导，但LLaMA-3 8B长Decode是边界/反例。**我们的解释**：不是所有LLM Decode均计算受限；分析结果依赖batch聚合、GQA/模型尺寸和假设的峰值速率。

**NF-02｜§3.4，Table 2；成本模型验证（MODEL+LOCAL_NATIVE）。**
- **对象**：LLaMA-2 70B，8×A100，dense batch=2048；计算每类操作FLOPs/数据搬运/网络流量，与硬件理论服务时间比较，再测实际算子时间。
- **作者报告**：多数操作的最大理论资源时间与实测方向吻合；**Prefill Attention因为kernel启动开销，实测显著超过模型推导**。
- **局限**：这是局部实测对分析模型的检验，不是整个服务具有2048个独立自然请求到达记录的证明；资源“下限”不能等于可达性能上界的经验事实。

**NF-03｜§6.1/6.2 Figure 7；离线吞吐（NATIVE_SERVING_OFFLINE）。**
- **对象**：FP16 LLaMA-2-70B，8×A100-80GB SXM、NVLink、TP8；固定输入/输出512/512、1024/512、512/1024；和Splitwise、LMSYS-Chat、ShareGPT中抽取的输入/输出长度。Splitwise全量约20k请求，另外两组各随机50k；均有真实长度来源，但**离线模式下不保留原始生产到达进程**。
- **强基线**：vLLM v0.5.3.post1（paged attention和chunked prefill）、DeepSpeed-FastGen v0.2.3、TensorRT-LLM v0.8.0（动态batch/paged KV）；分别调整已说明的batch上限。
- **变量/指标**：系统实现和长度来源；(input+output) tokens / GPU / 秒；作者报告对TensorRT-LLM，真实长度分布三组平均吞吐**1.91×**，理论理想算力吞吐为**1857 tokens/s/GPU**，最佳达到**68.5%**。
- **局限**：不能把1.91×变成低请求负载的收益；也不能把从计算速率推导的理论线当作真实单卡IPC上限。数据集中“真实长度”不等于执行过程中有真实到达时间。

**NF-04｜§6.3 Figure 8；请求到达/SLO（NATIVE_SERVING_WITH_SYNTHETIC_ARRIVALS）。**
- **对象**：同LLaMA-2-70B及三类真实长度分布；生成5分钟测试请求，**到达间隔服从指数分布**，逐级提高请求率。
- **变量/指标**：请求率；平均(每请求总延迟/输出token数)与200 ms/token的均值SLO。作者在LMSYS-Chat例中报告相比TensorRT-LLM可承载**1.64×请求率**而保持同规定SLO。
- **局限**：这是实机服务延迟，但**到达过程是生成的**，不是把Splitwise生产时间戳原样回放；200ms/token也不是每token严格P99或TTFT/TPOT双重SLO。

**NF-05｜§6.4 Figure 9；nano-batching与重叠消融（NATIVE_ABLATION）。**
- **对象**：LLaMA-2-70B，同平台；纯Prefill 512/0与Decode-heavy 512/1024及其它固定长度。
- **变量/指标**：无nano-batch不重叠、切分nano-batch但顺序执行、启用异质资源重叠、KV offload；测总tokens/s。
- **作者报告**：**单独切分反而使吞吐下降13.2%**；网络+计算重叠相对非重叠约1.07×，加上存储相关重叠约1.17×；KV offload因干扰使流水约慢3%。
- **我们的解释**：任务细化有自身成本；真正收益来自调度与资源互补，不来自“kernel越碎越好”。

### 2.2 MPK：任务粒度、强软件路径与资源开销

**MP-01｜§6.2–6.3 Figure 9；主系统对照（NATIVE_OFFLINE_BENCHMARK）。**
- **对象**：Qwen3-0.6B、Llama-3.2-1B-Instruct、Qwen3-1.7B、Qwen3-8B、Qwen3-30B-A3B；A100/H100/B200；batch上限1/2/4/8/16，**每请求固定64 prompt tokens+1024 output tokens**。
- **平台/对照**：BF16，paged attention与continuous batching；MPK与vLLM、SGLang和PyTorch（后者不能代替最强系统基线）。vLLM/SGLang利用FlashInfer/FlashAttention/cuBLAS/CUTLASS等库；不等于naive PyTorch。
- **变量/指标**：系统执行组织、GPU、batch；离线整推理吞吐/每token延迟表现。论文报告单batch相对最好系统基线约**1.0–1.7×**，小模型与更快GPU优势更明显。
- **局限**：该实验消除了真实到达不足导致的服务端停顿；不能拿它作为实际TTFT、队列延迟或动态到达SLO的直接证据。跨GPU比较非单资源变化。

**MP-02｜§6.4 Figure 10；MoE完整区域（NATIVE_OPERATOR）。**
- **对象**：Qwen3-30B-A3B、B200，batch 1–16；SGLang-MoE、MPK static MoE、MPK hybrid MoE。
- **变量/指标**：expert任务分配与融合gather-GEMM；完整MoE区域microseconds。作者报告hybrid相对SGLang约**1.07–1.18×**，纯静态并非始终最好；B1 SGLang中单独gather占该MoE区域至多11%。
- **局限**：改变了多个MoE路径软件因素；不能单独认定是路由不均或SM闲置的全部因果；不同route的自然形态是否参与该图仍需按作者runner进一步核。

**MP-03｜§6.5 Figure 11；Tensor Parallel多GPU（NATIVE_MULTI_GPU）。**
- **对象**：1–8张H100 DGX；模型和batch对应图11列示；MPK将AllReduce等分解为NVSHMEM异步传输和局部reduce任务。
- **强基线**：vLLM/SGLang；另报PyTorch+torch.compile+CUDA Graph（较弱的系统级比较对象）。
- **作者报告**：相对vLLM/SGLang在8×H100上约**1.1–1.4×**；相对PyTorch最高10×是**另一分母**。不能混为“对最强基线10×”。
- **限制**：提升同时包含CPU调度、细粒度依赖、kernel边界和通信重叠，图本身没有仅改变NVLink带宽的扩展曲线。

**MP-04｜§6.6 Figure 12；跨任务流水（NATIVE_TARGET_ABLATION）。**
- **对象**：Qwen3-8B最终Linear，B200，batch 1–16；cuBLAS、MPK-No-Pipe、MPK-Pipe；单位microseconds。
- **作者报告**：局部流水启用前后约**1.15–1.29×**，论文概述为1.2–1.3×。
- **局限**：这是单个目标算子的时间，不是整模型加速；相同任务组织A/B可定位软件流水价值，不能证明新GPU硬件单元必要。

**MP-05｜§6.6 Figure 13；计算-通信依赖粒度（NATIVE_ABLATION）。**
- **对象**：Qwen3-1.7B、4×H100，tensor parallel，batch 1–16。
- **变量**：同MPK运行时中，粗粒度AllReduce依赖事件 vs. 细粒度task事件；后者允许通信与计算重叠。
- **作者报告**：每迭代约**1.1×**改善。该对照比“MPK vs vLLM”更接近重叠机制因果，但仍非增加硬件资源的实验。

**MP-06｜§6.6–§7；消融与剩余硬件约束（SOURCE/INTERNAL_NATIVE）。**
- **作者报告**：Qwen3-8B传统实现每token约293次kernel调用；B200单次eager启动3.8μs，CUDA Graph路径约0.8μs；MPK整模型单mega-kernel消去这些边界，in-kernel scheduler时间很小。四个SM留作scheduler（A100/H100/B200 worker分别104/128/144）。
- **值得保留的硬件事实边界**：MPK可以按task释放/申请共享内存，但**per-thread register数是mega-kernel内部各task的最大需求**（§7）；因此它并非将跨算子融合的全部资源占用成本变成零。
- **我们的推断**：未来如要做P13硬件配比，可能应考察“task可发射性×寄存器约束×并行工作数”，但论文未做相同GPU上严格独立扩寄存器/SM的反事实，不可宣称已观察到寄存器容量成为新瓶颈。

### 2.3 Exclusive Batching：同GPU内受控模式与跨GPU外推分离

**EB-01｜§1 Figures 1/2；混合batch边际成本（NATIVE_MICROBENCH）。**
- **对象**：Qwen3-4B、固定ctx=16，RTX PRO 6000（论文标称1.792TB/s）、H200（4.8TB/s）；控制总token数与decode占比r，重复20次。
- **变量/指标**：mix composition与GPU；iteration时间随token数斜率、GEMM/Attention的时间组成；不是request/s服务指标。
- **作者报告**：mixed Attention相对pure decode出现边际成本交叉；对应decode占比RTX PRO 6000约**20%**，H200约**80%**，主变化落在Attention而不是GEMM。
- **我们的解释/警戒**：强烈说明“混合策略的干扰具有平台相关性”；但两个GPU不只在带宽不同，不能把跨GPU差异作为**仅带宽的严格A/B**。这里作者对带宽机理作解释，不等于我们已经量到了消耗在HBM上的全部关键等待。

**EB-02｜§4.2 Figure 3；阈值预测有效性（NATIVE+ANALYTIC）。**
- **对象**：H200、Qwen3-8B、合成几何输出长度分布；固定阈值扫描与在线EB()对比。
- **变量/指标**：切换阈值、batch容量自适应；吞吐、TPOT。
- **作者报告**：在线方案接近或优于固定扫描的最高吞吐（decode-heavy +8.0%、balanced +3.6%、prefill-heavy +0.6%，在指定比较下）。
- **重要公平边界**：在线方案**同时自适应阈值和batch容量**，固定扫描使用固定batch；不能把全部差值认作单独阈值理论预测精度。

**EB-03｜§4.3 Table 2；模型×平台×真实长度分布（NATIVE_SATURATED_SERVICE）。**
- **对象**：BF16 Qwen3-8B、Qwen3-30B-A3B；RTX PRO 6000/H200；ShareGPT、LongBench、WildChat、NuminaMath（文中输出长度可被截断）。v0/v1/EB()均在**同一vLLM build**、PagedAttention不变，按每策略/工作量网格寻找合适的token budget和max batch。
- **变量/指标**：调度模式、模型/硬件、长度分布；饱和请求完成率RPS；并另报TTFT/TPOT。
- **作者报告**：RTX PRO 6000上Qwen3-8B，ShareGPT v1=17.07、EB=19.68 RPS（+15.3%）；Qwen3-30B-A3B同一ShareGPT v1=15.98、EB=15.48（-3.1%）；H200 Qwen3-8B四组平均仅+1.5%，Qwen3-30B-A3B平均约-2.9%。
- **边界**：真实来源的是**请求长度/任务类别**；主实验是饱和并发而非逐条生产到达时间戳复现。30B是MoE，8B是Dense，跨模型变化不等于纯参数量变化。相同软件build能提高公平性，但优化batch设置随系统不同，仍是合法策略整体比较，而非固定kernel的纯调度A/B。

**EB-04｜§4.4 Table 3；非平稳到达/负载切换（NATIVE_SERVING）。**
- **对象**：RTX PRO 6000/H200，同系统；并发变化及长度分布切换；对照v1、EB()、EB+。
- **变量/指标**：请求强度/分布漂移，在线模式选择；吞吐、TTFT、TPOT、goodput。
- **作者报告**：EB+在非平稳场景保持接近两策略中更优者；**不是所有指标都同时全局最佳**。单一吞吐最优不代表用户请求尾延迟最优。
- **边界**：这些是作者定义的漂移脚本，不能自动当作运营环境的真实非平稳统计。

**EB-05｜§4.5 Table 4，Appendix A.2；反例检查。**
- **对象**：Qwen3-8B/WildChat在L40S与B300；H200/RTX的Gemma-3-1B-IT、Qwen3-8B、Qwen3-30B-A3B边际成本对照。
- **作者报告**：L40S EB=14.70、v1=10.36 RPS（+41.9%）；B300 EB=52.34、v1=50.47 RPS（接近）；**Gemma-3-1B-IT在两GPU上均未出现主文Qwen3的交叉点**。
- **我们的推断**：策略优势应当写成“具体模型/形状×平台×负载组成的条件性结果”，不能泛化成“带宽低一定EB优”。模型规模和软件形态也是重要条件。

### 2.4 训练及非LLM：第一轮必须真的出现的跨域反证

**BU-01｜Bullet §4.1–4.2 Figure 14/15（NATIVE_WITH_SYNTHETIC_ARRIVALS）。**
- **模型/输入**：Llama3.1-8B/70B及Qwen3-235B-A22B-FP8；ShareGPT、Azure-Code、arXiv-Summary长度/任务来源，**到达按Poisson生成**。平台包含8×A100/H100/H20，必要时tensor parallel；基线vLLM 0.8.5、SGLang 0.4.6（不同chunk）及NanoFlow 1024 chunk。
- **结果**：对TTFT/TPOT、请求吞吐、P90 SLO分别报告；作者在指定单GPU批次相对SGLang-1024平均吞吐1.09×、最高1.20×，其它摘要数字使用不同分母。
- **局限**：Bullet与NanoFlow虽同为并发但服务目标/SLO以及软件版本不同，不能直接把论文各自比基线的比率相除求性能排名；改变MPS/SM masking、任务并发与调度多个因素。

**BU-02｜Bullet §4.3–4.4 Figures 17–19；SM分配/资源反例（NATIVE_ABLATION）。**
- **对象**：Azure-Code的动态请求，以及ShareGPT中20req/s时的Llama3.1-8B局部区间。
- **变量/指标**：固定SM划分 vs 动态划分；等待、TTFT/TPOT、active SM cycles、Tensor Core和带宽利用率。
- **作者报告**：局部0–27s观察窗Bullet平均active SM cycles 86.2%，高于SGLang 11.2个百分点（原文写11.2%），但这不是Tensor Core占用86.2%；固定SM数量改变呈收益权衡，某一固定划分无法同时最优TTFT与TPOT。
- **局限**：它首先是运行时资源分配研究，而非物理增加SM数量；利用率增大不应未经时间对照等价为加速。

**MM-01｜MegaScale-MoE §6.1 Table 3/Figure 12（NATIVE_TRAINING_SCALE）。**
- **对象**：内部配置的352B MoE（60层、hidden4096、32 experts、top3；不是随手取公开352B完整checkpoint），seq8192、vocab65536、H800 240–1440卡；Megatron-LM commit `f1f03922`作为强基线，双方并行策略分别择优且均开启既有DP/PP通信重叠。
- **强扩展变量**：global batch固定720，增加GPU；测iteration seconds、tokens/s、MFU。作者报告MegaScale-MoE从240卡272.9k tokens/s到1440卡1407.7k tokens/s，MFU从32.48%降到27.89%，并解释为pipeline microbatch减少、bubble增大。
- **弱扩展变量**：GPU 480→1440与global batch 360→1080同比增加；另报效率趋势，不能与固定batch实验合表。
- **局限**：Table 3“训练1T tokens天数”按吞吐推算，**不是实际已训练1T的时间实测**；强基线和候选允许不同并行策略，属于系统方案比较而不是同kernel单参数A/B。训练语料确切数据包在本轮核验章节未获得可追溯身份。

**MM-02｜MegaScale-MoE §6.2 Table 5（NATIVE_TRAINING_ABLATION）。**
- **对象**：352B MoE、240×H800、batch720；依次加入SP+EP、跨算子通信重叠、算子内部重叠。
- **作者报告**：归一化吞吐1.00→1.13→1.22→1.28。**这是累积消融**；表中的+13%、+9%、+6%为作者给出的相对阶段标签，不能不问分母将三个增益当独立可叠加的硬件资源收益。
- **我们的解释**：训练扩展中的通信暴露可由合法软件/并行映射大幅改变；研究新硬件之前必须扣除成熟重叠能力。

**SB-01｜Sobek §5.1–5.3 Figures 2/3（NATIVE_OPERATOR_SCALING）。**
- **对象**：RTX5090、全FP32 eager/TF32 OFF，OpenEquivariance匹配基线；生成radius graph：
  - degree scaling：2048节点，改变cutoff使平均degree 4→1023；
  - graph-count scaling：重复128节点、平均degree32的图，graph count 2→511；
  - 两条轴覆盖约8.2k–2.1M条边。
- **变量/指标**：边数、每节点degree、图个数、特征和fwd/bwd/double-bwd；peak allocated CUDA memory与M edges/s。所有共享工作量同拓扑、权重、输入；新进程、warmup、10–30 CUDA event样本中位数；Sobek 128MiB receiver scratch。
- **作者报告**：OpenEquivariance部分profile在16k–260k边处OOM，Sobek到2.1M边仍运行且peak约0.4–1.5GiB；删除了边数×权重宽度的大中间物化，并**没有消灭图/特征的O(|E|)存储**。
- **局限**：这是构造radius图和重复图的算子实验，不是实际分子动力学轨迹；图生成、graph preparation和编译**不计入时间**。

**SB-02｜Sobek §5.4 Table 3；容量匹配的实现比较（NATIVE_OPERATOR, NUMERIC_CONTRACT）。**
- **对象**：固定128节点degree32图，16个fully-connected uvw及其它uvu profile，分别选OpenEquivariance各导数阶能执行的最大graph count，对两个实现施加完全同一输入与所需导数。
- **强基线理由（作者说明）**：OpenEquivariance提供对应的确定性forward/backward/double-backward合同；作者另知e3nn和cuEquivariance，并未宣称它们不存在。
- **数值**：每个实现自身两次完全一致，交叉实现采用明确的FP32容差；因归约顺序不同不宣称两者逐bit。
- **我们的解释**：这支持“容量边界可以由软件dataflow组织大幅移动”，不能直接成为新的GPU硬件能力不足。不同导数阶及准备成本不能以forward单项代替。

## 3. P01/P13研究矩阵：不要混合不同分母

| 观察层 | 本轮有效证据 | 对P01/P13能说什么 | 不能说什么 |
|---|---|---|---|
| 局部理论最小服务时间 | NF-01/NF-02 | 在定义的模型、规模、峰值速率下哪类需求主导“理想资源下限” | 真实阶段IPC、真实DRAM stall、另一个GPU上的精确拐点 |
| 离线固定推理 | MP-01、NF-03 | 同任务集/同平台内软件组织随batch的相对结果 | 真实用户等待、SLO以及跨论文速度比 |
| 饱和在线策略比较 | EB-03/04 | 同软件build中batch策略与模型/平台有关，存在真实正负例 | 仅改变带宽的因果归因、所有生产到达分布 |
| 运行时资源分配 | BU-01/02 | 动态SM配给可改变竞争和服务时间 | 增加物理SM数量时的scale曲线 |
| 多卡训练 | MM-01/02 | 强弱扩展与通信重叠明显影响吞吐/MFU | 单卡推理headroom、真正训完1T tokens |
| 非LLM容量 | SB-01/02 | 中间态数据流可以移动显存可行性边界 | 完整图准备/力计算/真实轨迹性能 |

本轮**没有**一条可将图中峰值利用率、命中率、理论下限或局部时间直接转换为“RTX4080增加X个SM能快Y%”的证据。P13目前只能提出待验证的资源响应实验，而不是已有跨负载资源扩展定律。

## 4. 形成的4条“有条件规律”（均为我们归纳，不是作者共同结论）

**H1｜供给—服务转折**：同一强执行路径随M/B/任务数上升，可能先受可调度独立工作不足约束，后转向计算/数据服务；转折点依赖GPU和具体kernel实现。NF-01提供高吞吐下限，MP-01显示低batch任务组织效应；**反例**为EB-05 1B无显著混合干扰，MPK大模型和高batch收益收敛。不能直接把不同论文点连成因果曲线。

**H2｜互补重叠与有害干扰共存**：在不改变功能要求下，异质任务并发在有互补空隙时可加速；若共享带宽/Cache/调度时序竞争，反而有害。NF-05“仅切分-13.2%、重叠为正”、MP-05“细粒度依赖为正”、EB-01/03“混合干扰/策略变号”是三个不同条件证据。旧C16 gate/up显式双流比合法串行FFN慢9.73%是项目内历史反例，不能冒充本文作者测量。

**H3｜资源扩展暴露下一个瓶颈**：强扩展的每设备有效工作缩小可带来pipeline bubble、communication或任务供给损失，弱扩展不等价。MM-01给训练多GPU限定支持；MP-03给低batch多GPU软件重叠近邻。**目前没有**统一跨AI训练/推理的定量物理资源扩展曲线。

**H4｜容量饱和不是吞吐饱和**：非LLM可能首先因物化中间值不能继续扩数据；通过合法流式软件修改生命周期，容量提高而整端到端收益未知。SB-01/02是正实例；AWMA R25/R26是局部容量与完整训练不同分母的历史警戒，数值R27R3仍保持独立资格失败终态。

## 5. 后续最多三项可证伪问题（**非实验授权**）

### D01｜同一个合法执行路径的任务供给饱和点在哪里？

- **竞争解释**：①低batch是CTAs/ready tasks不足；②已被Graph/成熟kernel解决；③时间实际上被权重流量/launch所主导；④shape变化切换了后端，不能当单变量。
- **最便宜下一步**：先用C16已接受的M1/M64/Split-K与MP-01的原始实现披露核形状和计时；如证据无法保持同实现/同语义则不外推。先形成按`same model × same backend × varied work`的设计表。
- **未来可能的最小native诊断（须新授权）**：单模型、同一任务语义、固定dtype/backend和输入池，只改变独立任务数量；检查实际launch/grid及未插桩wall、可提供工作量、资源计数；一处未用于筛选的形状作验证。
- **STOP**：软件已消除残差、没有显著任务供给变化、或需求与资源改善没有可靠时间关系。不以“SM utilization低”自动得出必须加SM。

### D02｜什么条件下Prefill/Decode重叠由收益变为竞争？

- **竞争解释**：①相同kernel同时争用带宽；②混合batch触发不同attention实现或KV布局；③调度/请求到达与排队，非GPU内部服务；④线上SLO与离线吞吐目标不同。
- **最便宜下一步**：优先从EB-01与EB-03/05记录同卡同软件强对照，结合NF-05/BU-02列举不兼容的分母；先不用109重造serving infrastructure。
- **未来native probe（须授权）**：固定真实请求内容和token预算、同模型/同GPU/同后端；纯decode、不同合法mix比例与分离执行，分别测GPU服务区间和端到端排队；保留独立输入。变化的kernel路径必须被识别。
- **STOP**：同runtime强对照没有稳定交叉，或策略变号完全由可避免的软件重选型/排队解释；不为“完美重叠”造免费oracle。

### D03｜同一个算子家族，任务规模加大时是吞吐先饱和还是容量先耗尽？

- **竞争解释**：①数据生命周期产生中间态爆炸；②已可通过软件stream/fusion解决；③图/索引准备反而占主要时间；④只有合成图触发极端局部性。
- **最便宜下一步**：Sobek §5完整原始样本与Round21已审源码/最近邻对照；首先查prepared graph缓存/ALCHEMI能力，不另开GNN工程。
- **未来本机最小probe（须授权）**：公开合法模型/几何及正确导数，覆盖图可复用与必要重建；原生强软件、容量和全区间时间单列；留未用几何样本。
- **STOP**：真实准备可复用、同语义现有软件已足够或没有完整应用时间价值。不要把OOM外推为持续吞吐下降。

## 6. 下一轮精读次序与必须补的证据

1. **NanoFlow**：§3.2–3.6和§6.4 Figure 9，进一步检查计算下限的可达性、batch/资源假设和真实干扰矩阵。
2. **MPK**：§4–5的SM级任务图和§6.6/§7，明确任务供给、寄存器最大化约束以及哪些依赖已经由软件解决。
3. **Exclusive Batching**：§1 Figure 1/2、§4.1、Table 2与附录A.2，彻底拆开GPU带宽、模型和策略选择的关联与因果。
4. **Bullet**：把固定SM份额、可变SM份额、真实到达合成方式与完整SLO仔细对齐；特别保留NanoFlow作为外部对照时的软件版本差。
5. **MegaScale-MoE**：训练强/弱扩展分别建模；核工作量原始权威和可复现软件版本。
6. **Sobek**：进一步检查原生模型/图准备阶段是否存在仍可辨识的剩余成本，不恢复AWMA原已关闭的R21支线。
7. **Kitsune/VTC/Tawa/Twill**：下一轮进入强软件近邻；查已解决的流水、virtual tensor、SM/task资源生命周期，防止给已存在能力换名。

**阶段门槛**：先把本笔记变成“来源明确、条件明确、反例明确”的理论与实验选型依据。CPU evidence核查如确有必要，单独形成新AI-ARCH CPU-only合同并请用户审；GPU/174模拟/Stage A/机制/holdout现在均不授权。

## 7. 科学authority/协作边界

- 本文件只登记外部作者论文实验证据与我们的待证解释，不增加`NATIVE_MEASURED`、`SIM_MODELED`状态，不更改C16旧终态。
- AWMA R27R3固定最终标签：`R27R3_B0_REFERENCE_NOT_REPEATABLE`，已独立审阅后STOP；本轮不推新R27R4/不推断C1/S2、容量或数学错误。
- 109共享GPU锁、174-new CPU/模拟、164大raw authority依旧；**没有SSH访问、没有修改运行中的Codex/模型/cache、没有新执行Goal**。
- 对未来推演：先用同一平台内强软件的合法对照区分机制，再允许跨平台/跨论文归纳；任何P13资源scaling实验需要已接受的硬件/模拟边界，不能用未经校准的“无限SM/无限端口”臆造结论。
