# N-A70｜主流混合模型 state 组织与执行 Discovery

日期：2026-10-16（Asia/Shanghai）。执行：174-new，CPU/source-only。固定起点：8f24af162ba37b4fa37f7a18d89b0fdb62697942。

## 裁决

**NO_SURVIVOR_IN_SEARCH_SCOPE；推荐 0、备选 0。** 本轮固定 Qwen3.5-4B 的真实 text_config，核了当前 vLLM/SGLang 状态分配、checkpoint、复制与融合入口。三类直观问题均有直接软件反证：混合页几何已有 packed/unified 分配；prefix state 已有合法 checkpoint、命中交集和私有状态复制；逐 token 大状态写回已有 ReplaySSM 原始工作及实现。它们仍有成本，源码也不证明最优，但本轮没有找到强路径之后、区别于已有工作且值得立即投入 native 的剩余变量。

这不是“混合模型无硬件问题”，也不是本机性能负结果。尤其没有把逻辑 padding、预留 slot、源代码 copy 或文档 TODO 换算成 DRAM 流量、stall 或可得速度。没有提出或启动后续 GPU Goal。

## 1. 冻结、证据层次与范围

已完整读 Goal 第0—4、N-A70第6、第9—10节；额外只读了其余 Lane 的题目边界。已读基线 10f3a51ee39884bcec3d3180e81cc405872cccb1 下 CURRENT_STATE、COORDINATION_PROTOCOL 第1—8节及证据索引相关条目，并回读 C16 已接受证据账本。A61/A65/A67、C16/AWMA 的原 STOP 与 scope 不变。

只研究纯文本请求经过混合 decoder 时，attention KV 与 GDN state 的大小、物理布局及生命周期。请求组成/Prefill-Decode 调度属 M，视觉编码属 P，MoE 分派属 O。本轮不等待或轮询其他 Lane。以下证据按 SOURCE_ONLY、AUTHOR_NATIVE、AUTHOR_TRACE_POLICY、DERIVED 分列；作者测量没有在 174 复现。

固定身份（源码 API 快照均在本轮读取，不追随 main）：

- 模型 Qwen/Qwen3.5-4B，revision 851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a；官方配置与元数据，发布许可 Apache-2.0，未下载权重、未接受额外许可。[配置](https://huggingface.co/Qwen/Qwen3.5-4B/blob/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a/config.json)
- vLLM fa75d3456d60a5ffe923818c4b495295675b38e1（2026-10-16 06:17:51 UTC）。[源码树](https://github.com/vllm-project/vllm/tree/fa75d3456d60a5ffe923818c4b495295675b38e1)
- SGLang a448fdf3161a10c059921ee1fba3c6b23b1792af（2026-10-16 07:51:55 UTC）。[源码树](https://github.com/sgl-project/sglang/tree/a448fdf3161a10c059921ee1fba3c6b23b1792af)
- Transformers 9fb4b5a9458a83a0bb9d8ddb6d4443a7bd146a62；仅静态读取 modeling_qwen3_5.py，未 import。[源码](https://github.com/huggingface/transformers/blob/9fb4b5a9458a83a0bb9d8ddb6d4443a7bd146a62/src/transformers/models/qwen3_5/modeling_qwen3_5.py)
- ReplaySSM 作者 artifact 73a9592e9d8a2268620e8883a82f5cec7442ed36；其 README 明说基于上游 ee1d99636702b8ed9ad88c2c2b833d331dce01c1，并区分已上游 Mamba2 路径与仍在 fork 的 GDN Triton 路径。[README](https://github.com/Johnny-Liou/ReplaySSM/blob/73a9592e9d8a2268620e8883a82f5cec7442ed36/README.md)

## 2. 真实状态与数学语义

Qwen3.5-4B 是官方通用多模态模型，具有合法纯文本推理路径；本轮不展开视觉部分。其32层是24个 linear_attention/Gated DeltaNet 与8个 full_attention，周期3:1；4B版本是 dense FFN，不能把家族模型卡泛称的 MoE 自动套入它。完整 attention 有16个Q头、4个KV头、head_dim256；GDN有16个key头、32个value头、key/value dim均128、conv kernel4；BF16模型，配置指定 mamba_ssm_dtype=float32。MTP存在但本模型计算只计目标 decoder，关闭 speculative/MTP，不计视觉、权重或激活（E01）。

GDN 和 Mamba2 不是同一更新。按 value×key 约定，GDN 为 S_t=alpha_t*S_(t-1)*(I-beta_t*k_t*k_t^T)+beta_t*v_t*k_t^T；额外 delta 擦除项需要旧 state 的投影，不能替成 Mamba2 的纯衰减加外积。K/V头分组、归一化和gate均属于模型语义。prefill可用chunk并行算法，decode为递归更新。原始 Gated DeltaNet 论文的1.3B/100B FineWeb-Edu训练组和单H100训练吞吐不是Qwen4B服务state测量（E02）。

### 状态形状与生命周期（TP=1、非speculative）

| 对象 | 实际runtime逻辑形状与dtype | 更新、复用及归属 |
|---|---|---|
| 每个full层KV | K/V分别 [tokens,4,256]，本推导固定BF16；backend物理stride可不同 | 随token增长；合法prefix可共享只读页，后缀单独分配；命中必须与GDN的同token端点相容 |
| 每个GDN recurrent state | vLLM/SGLang约定 [32,128(value),128(key)]，FP32为本推导合同 | 每序列/分支可变；不能用末端state逆推出任意较短prefix；需对应端点checkpoint或重算 |
| 每个GDN conv history | 8192 channels × (4-1) history，BF16；vLLM默认SD为[3,8192]，SGLang为[8192,3] | 当前token与前三个历史值共同卷积；和recurrent state必须同端点复原；不是KV token页 |
| prefix checkpoint | 一套conv+recurrent状态；可能有多个端点和请求私有副本 | 命中时KV可共享，递归状态后续会变，需私有更新；树中checkpoint、active、ping-pong、scratch是不同角色 |
| ReplaySSM | checkpoint + 有界输入ring + cursor/flush metadata | 活跃ring未flush不能当完整checkpoint直接复制；仅复制temporal而丢ring会漏掉更新 |

形状来自 E03/E08/E21。Transformers参考路径使用 key×value state 约定，不能仅因本模型128×128维度相等就宣称跨runtime raw bytes可互换（E15）。dtype也须读最终runtime配置，不能拿权重BF16推定所有state都BF16。

## 3. 当前强runtime的反证

**vLLM 分配与前缀（E04—E07）。** 固定源码 MambaSpec 明确区分 state_content_size_bytes 与 page_size_bytes；align模式的每请求驻留预算是 2+num_speculative_blocks+num_prefill_checkpoint_blocks，而block table行长度可随上下文增长，二者不能混为每token物化state。当前 kv_cache_planning.py 已有 block-outermost mixed-page packing，按state bucket装入已有block；其他布局仍可能统一页尺寸和padding。因此移动设计文档 Case4 的“替代padding策略WIP”不能证明当前实现普遍缺失该能力，更不能证明本模型会走那个旧几何。

当前 HybridKVCacheCoordinator 有命中对齐/交集处理，kv_cache_utils 有带条件的 fine-grained partial hash hits；不能依据旧issue称“混合prefix一律0命中”。QwenGatedDeltaNetAttention 的 FlashInfer prefill 可导出中间checkpoint以避免为对齐拆分prefill；还存在 fused gating/recurrent decode和融合precopy入口。backend、layout与build限制都要保留，静态存在不等于4080默认启用或性能最优。

**SGLang 分配与状态归属（E08—E11）。** unified_memory_pool.py已有一个物理字节池上的不同sub-pool视图、虚实slot映射与弹性共享；视图不能分别累加为独立allocation。源码明确 unified 模式下 ratio 只控制总预算而非固定runtime split。unified radix有checkpoint/命中、组件独立回收和HiCache接口；MambaComponent在可用路径捐赠ping-pong slot，完成请求还可转交所有权，不能假定每次缓存都复制完整state。MambaPool.copy_from支持融合conv slot copy并约束Replay源必须fully flushed。

能力不组成无条件的“超级基线”：本次固定 UnifiedMambaPool 明确禁用 linear ReplaySSM；普通MambaPool有Replay ring但默认构造参数不证明全局默认启用。必须分别核合法配置，不能把unified、Replay、量化checkpoint、speculative路径全拼在一起。当前代码也没有证明所有CoW、migration、compaction延迟被隐藏，相关实际成本为 UNKNOWN；但单凭尚未测量不能提出新的硬件优化结论。

## 4. 最近直接工作与具体实验组

| 原始工作 | 核验组与真实分母 | 对本轮的反证及边界 |
|---|---|---|
| Gated DeltaNet，arXiv2412.06464v3 / ICLR25 | §3更新、§4：1.3B，100B FineWeb-Edu，4K训练；Fig3单H100训练吞吐 | 既有chunk算法；不移植其训练吞吐为Qwen推理收益（E02） |
| Marconi，2411.19379v3 / MLSys25 | §5.1/B：7B混合4/24/28层的LMSys/ShareGPT/SWE-Agent trace策略组；另有Jamba-1.5-Mini FP16、4×A100-40GB的TTFT组 | 已有计算价值感知admission/eviction；trace hit-rate/策略计算与native TTFT分开，不能把旧“runtime不支持hybrid”当现状（E12） |
| SegLen作者组，2026在线文章 | Setup/表：Qwen3.5-9B、1×H100，SWE trace及低复用ShareGPT，比较LRU/Marconi/SegLen的mean TTFT | 成熟的更强软件反证；精度、runtime固定commit等未充分披露，不将其百分比外推4080（E13） |
| ReplaySSM，2610.13778v1，2026-10-09 | AppE Tables5—7：Qwen3.5-4B BF16、FP32 state、1×H10080GB、TP1、L16、CUDA graphs、调优vLLM；完整decode-step speedup在B1/B8/B256分别0.99/1.03/1.27 | 逐tokenstate写回已经直接研究且有软件方案；kernel与整步、standard decode与含prefill的spec请求分母不同。没有本机复现，也不是natural arrival trace证据（E14） |

ReplaySSM论文AppD已讨论continuous batching下每行不同flush位置和graph内cursor，不把“异步flush”单独包装为本轮新问题。其作者artifact对GDN的可运行实现，与本次上游vLLM中搜到的Mamba2 Replay支持不是同一资格；README对此有明确区分（E16）。剩余读取、ring、flush以及低精度误差并未免费消失，本文不声称软件消除了所有state代价。

## 5. 唯一容量/准备代价模型（DERIVED，未测GPU）

只用E01/E03/E08/E21的尺寸做整数计算；不调用模型库。令R为并发active序列数，C为独立cached端点state套数（不包括active），A为额外checkpoint/ping-pong套数，n_i为每条序列未共享KV token数，共享prefix KV只计一次。

- 每层conv：2*(2*16*128+32*128)*3=49,152 B。
- 每层recurrent：4*32*128*128=2,097,152 B。
- 全24层一套state S=24*(49,152+2,097,152)=51,511,296 B=49.125 MiB。
- 全8个full层KV每token k=8*2*4*256*2=32,768 B；S/k=1,572 tokens仅是容量交点，不是性能交点。
- 有效state容量：M_eff=(R+C+A)*S+k*(sum(n_i)+unique_shared_prefix_tokens)。未共享分支各有可变state；KV共享不表示递归state可以任意原地共享。
- 物理峰值：M_pool_union + M_scratch + M_activations + M_weights + allocator/graph/metadata；M_pool_union包含有效内容、页/层padding与空闲reserve。共用buffer的view按字节区间并集算一次。无runtime输出时padding、reserve和scratch均 UNKNOWN，不能把M_eff叫峰值显存。
- 例：align且spec=0、额外prefill checkpoint block=1时，三套slot的内容预算为147.375 MiB/序列，未含页padding；不能套入所有backend。
- 传统逐步更新的逻辑读+写内容量为2*S=98.25 MiB/序列/token；一次完整state复制同样有读+写。缓存命中、融合、ring重放、slot捐赠与DMA/片上驻留会改变实际流量/时序；本数不是HBM测量，也不能除以标称带宽得到合法wall收益。

此模型明确只计非spec GDN与full KV。Replay ring、FP32 read checkpoint与其他别名可占额外容量，不在上述基准内容项中伪装为零。

## 6. 筛选、自审与未来边界

| 被筛问题 | 最强反证 | 科学分类与关闭原因 |
|---|---|---|
| 大GDN页导致padding，需要新硬件state分配 | 当前vLLM mixed-page packing；SGLang unified allocator | SOFTWARE_OPPORTUNITY/已有软件覆盖；未发现固定强路径上的实测容量缺口，padding不等于stall |
| 混合prefix无法复用，或每个checkpoint都要全量拷贝 | prefix命中交集、checkpoint exporter、slot捐赠、CoW及flush边界 | 该绝对前提被源码否定；尚无强路径后暴露copy wall，不推荐靠关闭reuse造弱基线 |
| 逐token写回大state是新机会 | ReplaySSM正好覆盖真实Qwen3.5-4B，并有调优整步对照 | 软件/原始工作已覆盖直接假说；换成Ada或重复batch曲线不构成新科学变量 |

与旧证据的区别已审：C16账本E1是量化FFN权重局部驻留，FFN双流负结果与Split-K分组针对另一对象；不能用它们否定GDN state。反过来，本轮也没有理由恢复这些旧任务。AWMA fast-weight/TTT与GDN不能仅因都叫state而等同；本报告只保留索引边界，没有把AWMA当GDN原生反证。CANDIDATES.json因此为空，未用内部标签代替上述否定理由。

**当前下一步是协调侧回收此0候选结论，不建议马上申请GPU或更大GPU。** 只有以后得到一个区别于上述软件的明确观察，才重新冻结最小native合同。重开时最小辨别条件应为：同固定模型/精度/请求，强runtime合法路径开启；基准测完整arrival→first token/完成和完整decode step；诊断记录真实state内容/页/slot/共享区间、checkpoint复制或flush的暴露wall；关闭prefix或synthetic单shape只能作成本分解；独立验证用不同自然会话集合或真实另一个混合模型，不能探索集同时作holdout。

若仅剩allocator碎片，归普通软件；若copy/flush不在关键路径、端到端差在噪声内、质量门不通过或现成软件已经解决，即negative STOP。未来任何GPU/权重/数据/ABI与数值门都要另立获批Goal；本轮没有可执行native合同，也不推荐为复现实验先下载资产。4080容量/ABI未检查，不把H100结论自动迁移；若真正需要大batch或9B/更大模型，需更大显存的理由与资源另审。

资源、访问缺口、固定source SHA及交付流程见RECEIPT.json；每项证据的作者声明、推导与未披露字段分列于EVIDENCE.tsv。所有报告数字仅来自固定配置/整数重算或明确署名的作者实验，GPU测量为0。
