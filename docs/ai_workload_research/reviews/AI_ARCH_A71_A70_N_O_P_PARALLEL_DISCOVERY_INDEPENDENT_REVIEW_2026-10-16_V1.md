# Round A71｜A70 N/O/P三条主流模型并行Discovery独立科学审查

**日期：2026-10-16；审查者：ChatGPT／AI-ARCH Discovery；任务性质：GitHub远端来源核验＋纯计算复核，不是节点GPU执行。**

**综合裁决：对 N、O、P 三条分别接受 `NO_SURVIVOR_IN_SEARCH_SCOPE / STOP`，并加明确证据后缀 `SOURCE_SCOPE_ACCEPTED_NOT_NATIVE_NEGATIVE`。** 三线0个推荐/0个备选候选，不意味着混合模型、MoE、多模态已经没有GPU体系结构问题。本轮材料主要排除了现有实现已覆盖的**具体直观思路**；对真实强后端的残余时间成本依然缺观察。Lane M为用户明确“正在执行”，没有向其发指令、没有监控进程或触碰该分支，**不要把M列为STOP**。

## 0. Git/GATES与独立验证层级

固定共同Goal: `8f24af162ba37b4fa37f7a18d89b0fdb62697942`；科研基线 `10f3a51ee39884bcec3d3180e81cc405872cccb1`。

| Lane | 原执行branch | final commit | final tree | 起点→final | final→远端HEAD |
|---|---|---|---|---|---|
| N（174-new，混合状态） | `hrl/aiarch-a70n-hybrid-state-discovery-174new-v1` | `5076223db5db0256fd0ccacec50b5347a0cab8c5` | `592e12903c8fa029fb5108a967f8a00bb9cb9458` | ahead1/4文件 | identical |
| O（109，MoE） | `hrl/aiarch-a70o-moe-execution-discovery-109-v1` | `94ca01df352cf4cf707cd35e5f9f63d4eff014c6` | `b5b3d7f8f925c50aa845cebec2cb3057fe91b261` | ahead1/4文件 | identical |
| P（174-new，多模态） | `hrl/aiarch-a70p-vlm-pipeline-discovery-174new-v1` | `f2399777a30f4fdafa26858b3cd418e497538db2` | `811616c50e4594e1884d4ee4e4c622a72fb953d1` | ahead1/4文件 | identical |

从GitHub固定Git-data commit再次回读了三份final tree，均与用户报告一致；每条仅新增自身目录的`REPORT.md`、`EVIDENCE.tsv`、`CANDIDATES.json`、`RECEIPT.json`，三个CANDIDATES.json均为`[]`。独立解析EVIDENCE.tsv：N为21条、O为24条、P为17条，均11列、无字段数异常，ID各自唯一；报告按固定论文/源码/推导/未披露分列。

**核验限制：** 本轮没有像执行Lane一样逐文件字节重算三组共12个blob的全部SHA256；用户/各Lane已有单次远端fetch-back收据，我独立确认了远端文件blob身份与Git提交/分支、报告内容一致。资源均来自Lane提交的RECEIPT、不是本窗口实时节点测量。没有向109/174/164发任务或触及AWMA/C16/ISCAS。

## 1. N：主流混合模型状态

**接受限定0候选，**理由不是“混合KV/SSM没有任何成本”，而是三个直觉路线均有明确软件近邻：

- 固定Qwen3.5-4B text_config：32层中24 GDN＋8完整注意力。vLLM当前具混合分配/packed buckets等有条件能力；SGLang unified view/池、checkpoints/拷贝和前缀复用路径已经存在，不能将不同别名buffer相加或把旧WIP文档当当前实现。
- ReplaySSM `arXiv:2610.13778v1`针对Qwen3.5-4B已有输入ring＋checkpoint重放、周期性写回与标准decode分母。固定作者仓库 `Johnny-Liou/ReplaySSM@73a9592e9d8a2268620e8883a82f5cec7442ed36`的README已由本独立审查再次读取：GDN Triton实现与Mamba2上游支持范围有明确区别。**不得将所有fork/上游、allocator、Replay配置拼成一个实际可共同启用的最强路径。**
- 独立整数重算：conv每层`2*(2*16*128+32*128)*3=49152B`，FP32 recurrent每层`4*32*128*128=2097152B`，24层合计`51511296B=49.125MiB`/序列；8个full层BF16 KV`32768B/token`，内容容量交点1572 tokens。均为**DERIVED CONTENT**，不等于物理池峰值、HBM读写、stall时间或天然硬件headroom。
- 需保持`UNKNOWN`的：真实请求下checkpoints/copy/flush关键路径、缓存实际配置与缓存命中、8B之外不同混合模型状态、4080设备支持。0候选不能写成“所有copy/flush被软件隐藏”。

直接来源：[N原报告](https://github.com/swayhrl/accel-sim-framework/blob/5076223db5db0256fd0ccacec50b5347a0cab8c5/docs/ai_workload_research/discovery/A70_N_HYBRID_STATE/REPORT.md)、[ReplaySSM固定源码](https://github.com/Johnny-Liou/ReplaySSM/blob/73a9592e9d8a2268620e8883a82f5cec7442ed36/README.md)。

## 2. O：MoE专家自然负载

**接受限定0候选，**因为新研究提出的通用分组GEMM、避免物化排序、融合专家路径、共享专家重叠都有直接成熟后端或论文。最关键独立反证是FlashInfer固定`18688d10022a183d36488858c9a3d7cd6ca03699`的MonoMoE代码，当前公开wrapper硬限制Hopper SM90a、block FP8、E256/H2048/I512、M≤8，接受router logits但不包含生成router logits的线性投影；不能把这一能力迁移成109 RTX4080的同条件已接受实测。

**O还有一项重要历史口径纠正，本审查独立证实：** C16 E3固定`NATURAL_ROUTING.json@378487015e513ed666c0929ca3f6c00392ff11c3`明确为Qwen3-30B Layer24 prefill、Qwen3MoeSparseMoeBlock **expert loop**，而非成熟fused decode。实录16384 assignments，93活跃expert、最大1602。旧11.577ms不是当前fused kernel wall，不能既拿来宣布当前强软件已经否定MoE，也不能拿loop大开销制造新机会。

本审查还从旧源直方图自行重算了按expert b行分组的条件几何：b16/b32/b64/b128时scheduled行=17248/18304/20544/25344，padding=864/1920/4160/8960，和O的CPU算术完全一致。但这**既非旧loop执行过的padding，也非现行强后端实测指令数/DRAM流量/wall**。实际有效路径还可能跳过分组对齐或使用weight-major persistent组织。

需保持`UNKNOWN`：同一自然路由及权重/量化合同下、经已支持/已调优后端的成对完整route-to-combine与请求wall；真实每步专家n_e分布；H200论文数值的对应边界。本轮不建议立即租H200——现有条件式未来方案不是已经成立的科学候选，更不能偷偷改Q30的旧STOP。

直接来源：[O原报告](https://github.com/swayhrl/accel-sim-framework/blob/94ca01df352cf4cf707cd35e5f9f63d4eff014c6/docs/ai_workload_research/discovery/A70_O_MOE_EXECUTION/REPORT.md)、[MonoMoE论文](https://arxiv.org/abs/2609.04244)、[FlashInfer固定源码](https://github.com/flashinfer-ai/flashinfer/blob/18688d10022a183d36488858c9a3d7cd6ca03699/flashinfer/fused_moe/monomoe.py)。

## 3. P：通用VLM视觉→语言交接

**接受限定0候选**，因为vLLM v0.20.1已经有视觉处理器输出缓存、encoder embedding缓存、encoder CUDA Graph预算/超额eager fallback、多模态分块Prefill及部分分离服务能力，不能只以“视觉编码器还没Graph”作为创新。

从GitHub固定`vllm-project/vllm@132765e3560659ff63ebd236203672e991b70e08`的`docs/design/cuda_graphs_multimodal.md`再次核验：作者性能分母是`vllm bench mm-processor`，单GB200、Qwen3-VL-30B-A3B、VisionArena-Chat 3000 prompt/300 warmup，FLASH_ATTN mean 5.13→4.52ms、P99 9.16→6.26ms；**不是Qwen3-VL-8B请求级TTFT/ITL，更不是多图或视频自然服务完整wall**。VisionArena-Chat数据卡单图，不可借视频支持的API声称已验证多视频端到端。

`UNKNOWN`仍有：Qwen3-VL-8B真实媒体token直方图、不同视觉batch/Graph budget导致的完整请求SLO变化、encoder与decoder资源竞争、当EVS使视频Graph禁用时自然性能/质量代价。但这些只是未测交叉变量，没有同语义强基线后的残余证据；**也不能因无公开数据而推定软件已经吸收所有多模态问题**。P推荐0候选合理，不自动下载VisionArena/视频或启动GPU。

直接来源：[P原报告](https://github.com/swayhrl/accel-sim-framework/blob/f2399777a30f4fdafa26858b3cd418e497538db2/docs/ai_workload_research/discovery/A70_P_VLM_PIPELINE/REPORT.md)、[固定vLLM v0.20.1视觉Graph设计](https://github.com/vllm-project/vllm/blob/132765e3560659ff63ebd236203672e991b70e08/docs/design/cuda_graphs_multimodal.md)。

## 4. 跨线综合：三个0候选意味着什么

| 筛查类别 | 我们现在可以接受 | 不能推导 |
|---|---|---|
| SOFTWARE_NEARBY_DIRECT | 有具体代码／论文提供混合state复用、MoE融合与VLM Graph的成熟软件能力，简单重复它们难成立新颖性 | 所有部署默认开启、软件达到理论最优或无硬件性能瓶颈 |
| ORIGINAL_EVIDENCE_LIMIT | 现有报告没有建立固定真实自然强软件后、同边界的可重复完整wall残余 | 真实残余不存在 |
| SOURCE_SCOPE_NO_SURVIVOR | 当前已读源范围内0个足以推荐新native的不同质问题 | 所有LLM/MoE/VLM问题完全排除 |
| RESOURCE_BOUNDARY | O未来H200/FP8是条件式另一资源提案，P/N也不能将别的平台作者数值写成109结果 | 获得GPU/权重/新数据授权 |

并行方法本身有效：每条在自己界内找到强反证或缩小了未来实验合同，3组共62条合格TSV证据，互不修改。**同时暴露方法风险：如果以后仅以“作者还没提供强路径性能数据”停止所有方向，就可能把所有值得先做低成本Discovery探针的问题都过早淘汰。** 本A70合同允许NATIVE_PROBE_PROPOSED而不需要事前完整机制上界。后续不是放宽质量与强软件门，而是要求在提出探针时明确一个具体尚未被覆盖的新变量、区分竞争解释的最小真实工作量和便宜且明确的否定条件。N/O/P目前均未凑齐这一组合，接受0候选。

**当前不新增第二波4个Codex窗口与CPU/GPU Goal。Lane M按用户消息仍在执行，等待它自己的完成回执后再综合最多2—3个主问题；不因三线0候选而要求M追求阳性、扩研究范围或新数据。** 如M也0，下一步应重新选负载阶段或部署变量、恢复研究广度，而不是在相同模型上反复追最新软件源码。

## 5. 后续权限与资源审计

三条执行receipt均说明CPU/source-only、未启动本项目GPU、未下载权重或自然数据集、未改其他项目。注意其资源测量强度不同：P的task-tree RSS与网络流量未连续测量；O/N的worker记录亦不等同系统总峰。不可用“交付干净”升级成所有资源峰已经精确测得。没有已知证据要求为此重复任务；保留原record和STOP。

协调分支只追加本审查与修正CURRENT_STATE，不合并N/O/P执行HEAD，不覆盖三个report、raw或Candidate空数组。A61/A65/A67 GNN终态、A69 ScanNet停止推进、C16 Stage A及AWMA独立权限一律不变。

**终态：A71 N/O/P三个SOURCE_ONLY负候选独立接受，M-A70继续执行中（仅据用户回报），当前无新增本窗口节点任务或GPU授权。**
