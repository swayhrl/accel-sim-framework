# Round24｜R23G之后的问题发现与CPU语义检查

日期：2026-10-02。作者：ChatGPT。性质：文献/固定源码核查、研究设计、ChatGPT容器CPU合成单测。**不是execution Goal，不授权109 GPU、174/Accel-Sim、profile、trace或硬件任务。**

## 0. 结论

只保留一个优先准备的问题：**共享输入embedding与输出classifier权重，在两路梯度到达时间不同的情况下，能否通过合法延迟生成、分块合并与一次提交，减少完整dense梯度的物化及存活成本？**

目前证据是：最近邻明确覆盖边界、一个可证伪的软件调度假设、CPU计算语义检查。**不是GPU数值资格、性能positive、训练收敛、新颖性穷尽证明或硬件残差。**

曾进入初筛的MoE×多LoRA联合分组，已有作者工作明确讨论compound sparsity，当前源码还有更强融合和小批量路径，不凑成第二个候选。普通embedding反向/update融合、稀疏卷积提前建图也不作为新动机。[S05,S07–S12]

## 1. 当前authority与读取范围

本轮文献分支起点`ad06a071464f698760459c895d8587d020214eee`，compare结果identical。读取了R23G当前收口、Round22的34行边界账本、当前/历史README，以及Round18正文部分；Round18长响应有截断，不宣称重读全部历史正文。

R23G accepted result：`99d05f0ad221a1d44dd11bac0ed83965bb2c0942`，tree `b3bcf21e81e1bc34a3281d41b570d6021d8a1edd`，有范围的软件positive。Lane G完成STOP；F/R22F1、E/R22E保持STOP；R20 CLOSED。没有重开R81、OEQ、R101或旧C16采集。

本轮核心登记13项外部原始材料，包含论文、官方文档、作者技术文章、配置和固定源码，**不称13篇全文论文**。本记录列出阅读范围。未运行作者GPU程序、未读取164张量/大raw，未重测R23G。

## 2. 被筛掉的直观动机

| 对象 | 本轮核到的已有能力 | 处置 |
|---|---|---|
| embedding反向后更新 | FBGEMM TBE明确融合backward与optimizer，并支持不更新、输出sparse gradient。[S05] | 单纯“融合embedding更新”不是新能力；不据此宣布共享dense head场景也已全解。 |
| expert×adapter联合碎片化 | AWS/vLLM作者已明确compound sparsity和联合调参；9月23日固定源码有one-shot shrink/expand、register中间量、naive/grouped与NPID策略。[S07,S08] | 不重做朴素两kernel融合，也不拿额外adapter维本身作新意；无已资格化的新残差。 |
| 异构LoRA rank/布局 | S-LoRA、tLoRA、InfiniLoRA分别有异构rank/布局、训练组织、kernel与服务优化。[S09–S11] | 训练/推理和Hopper/4080分开，不把作者平台数字搬来。 |
| 稀疏卷积映射准备 | Spira已有one-shot mapping及双数据流等方案。[S12] | 泛泛提前建图不立项，不恢复OEQ准备线。 |

这些是当前投入选择，不是相应领域无机会的证明。

### CPU结构反例，不作为新颖性

脚本构造两个不同合成工作负载：4个expert、4个adapter、每adapter 8个token、top-k=2，总64次assignment。expert边际与adapter边际相同；联合非空格分别8和16个。固定BLOCK_M=16时逻辑padding槽分别128和256。

这说明两个边际直方图不足以决定联合分组；但它们不是语义等价优化对照，不是自然路由，也不是2倍时间差。作者已指出compound sparsity，因此只留作方法反例。

## 3. 唯一优先准备假设

### 3.1 最近邻明确留下什么

FORGE §2.2及Appendix A Remark 1将tied embedding等多backward路径权重留在standard optimizer。它把逐坐标梯度tile与更新融合，但要求更新前完成旧权重读取。这个fallback是作者实现边界，**不是共享权重不能软件优化的证明**。[S01]

FlashOptim gradient release已有post-backward hook更新；其该模式限制global clipping、microbatch accumulation、GradScaler。PyTorch也已有optimizer-in-backward教程，不能把“梯度出来马上更新”说成新能力。[S02,S04]

固定CCE `cce.py`保存末层hidden e、classifier c、LSE等，backward返回de、dc、dbias。这里e不是输入embedding权重。该接口有助于识别dH/dW，但不等于新训练runtime已经资格化。[S03]

### 3.2 两路梯度必须先合并，再更新一次

设同一个参数W[V,d]用于输入lookup和输出classifier：

```text
W -> input lookup -> backbone -> H -> classifier/CE -> loss
|__________________________________________^

G_W = G_head + G_lookup
一次 AdamW(W, G_W, m, v, step)
```

lookup贡献仅涉及实际输入token行，head softmax贡献一般是dense；**总梯度不是稀疏梯度**。由于AdamW二阶矩含总梯度的平方，分别对两路做两次更新不等于对总和更新一次。dH和所有checkpoint重算等旧W读取也必须在overwrite前完成。[S01；本轮代数推导]

旧CCE `ec1ccad7bbcead8853cd97840a2007d96f325aa3`针对全量zero-fill，已建立11.85%完整loss/backward软件收益，但没有完整训练/optimizer结论。新问题是两路贡献之间的完整梯度物化、合并与存活；必须使用旧first-contributor优化兼容后的强基线，不把zero-fill重新加回来制造收益。[A04]

旧CCE `1e-2`容差不能转成新optimizer容差，R23G greedy资格也不能转成训练资格。R101/Muon数值流程不属于本假设。

## 4. 有限软件反事实

只准备一种调度：

1. 正常forward保存末层H、原LSE、target等必要统计，W仍为旧版本。
2. 先计算dH，完成backbone反向和所有旧W读取；暂不形成完整head权重梯度。
3. 按输入token ID正确归约lookup梯度，存为紧凑U×d数据，U不超过输入token数。
4. 逐词表行tile重新生成head梯度，加上本tile的lookup贡献；做一次相同AdamW后释放临时梯度。
5. 下一个tile仍读它自己的旧W，继续用原H/LSE；禁止跨已更新的词表重算softmax分母。

这是我们的调度假设，不是作者已测方案，也不声称首次提出延迟提交。

**代价必须全部计入**：拆开dH/dW可能多一遍logits/概率计算、损失融合复用；H/LSE存活更长；lookup索引/去重/归约及同步；tile owner可能损失token轴并行性、增大register/shared压力；原W与moments读写仍存在。不能把减少的逻辑bytes直接转换成时间收益。

## 5. 已执行的CPU语义检查

脚本：`../empirical/round24_cpu_semantic_checks.py`。紧凑结果：`../empirical/ROUND24_CPU_CHECK_SUMMARY.json`。

Toy为`H=W[input_ids]@R; logits=H@W.T`，R固定，完整CE向同一W的两条路径传播。不是仅凭随机两梯度相加。用完整梯度求和后一次AdamW作reference，比较延迟row-tiled调度。

4个seed×2个形状×3种row tile×2种label mask，48项检查；覆盖重复输入ID、lookup未访问行、尾tile及非零AdamW历史状态。**不是48个独立真实workload**。

| 检查 | 结果 |
|---|---|
| FP64正例 | 48/48通过；仅toy atol=rtol=1e-12 |
| 总梯度最大绝对差 | 2.7755575615628914e-17 |
| 更新W最大绝对差 | 3.469446951953614e-18 |
| 65参数有限差分 | 最大差6.099153473937413e-11，过预设2e-9 |
| 两路各自AdamW两次 | 被拒，W差约1.0198e-3 |
| 先改W再计算dH | 被拒，dH差约1.6976e-4 |
| 各自clip再合并 | 被拒，梯度差约6.7659e-4 |

只支持该toy下调度语义可行及负例有判别力。没有证明BF16逐bit、真实CCE filter/cast兼容、训练收敛、CUDA性能或实际显存节省。Toy forward仍物化logits，reference也保存全梯度，**不可把本脚本当内存/性能实现**。未支持all-ignore mean、global clip、accumulation、AMP overflow、distributed reduction和真实dropout/checkpoint recipe。

## 6. 先选行为，再映射已有模型

所需行为是实际tied参数、大V且相对短T、dense head与sparse lookup两路贡献、明确旧W读边界及逐坐标optimizer。因这些性质才考虑已有模型，不因为权重已下载。

固定Qwen2.5-0.5B-Instruct config给出V=151936、d=896、tie_word_embeddings=true。[S06] 它只提供形状锚点；实际storage alias、训练batch/labels、两路梯度、optimizer状态和recipe尚未资格化。

| 形状量级 | 计算结果 |
|---|---:|
| W元素数 | 136134656 |
| 一份BF16完整梯度 | 259.65625 MiB |
| 一份FP32完整梯度 | 519.3125 MiB |
| 示例T=2048的BF16末层H | 3.5 MiB |
| U≤2048的FP32 lookup梯度上限 | 7 MiB |
| 2048项FP32 LSE | 0.0078125 MiB |

两种梯度精度不能相加。表没有worklist、tile scratch、额外activation存活、allocator和moments；不是peak saving，不能除以带宽冒充时间oracle。峰值在其他阶段时，即使少一个数组也未必降低完整step峰值。

## 7. 最小后续检验草案，不是执行授权

| arm | 定义 | 作用 |
|---|---|---|
| B0 | 与训练recipe兼容的强CCE/CE backward、合法共享梯度归约、相同fused AdamW | 不退回dense logits或旧zero-fill弱基线 |
| S1 | 仍存完整梯度；真正last contributor之后立即提交/释放，尽可能融合合法合并与更新 | 普通hook/遍历融合是否已经足够 |
| S2 | 第4节晚生成、分块合并、一次更新 | 少物化的利益能否覆盖重算与状态保留成本 |

第一次实际执行只宜选一个预冻结真实training batch/shape，另留未调试内容样本作以后独立验证；不铺模型/词表/batch/tile矩阵。重复、顺序、warmup、预算、噪声规则及新数值合同仍需在性能前冻结，本研究笔记不暗中授权这些步骤。

必须检查loss、dH、共享总梯度、W、m/v/step、下一forward和alias。FlashOptim state压缩或master精度改变不能只给candidate启用。实际recipe需要clip/accum/overflow时不得静默关闭：S1保持合法；S2要么支付额外统计/重算和全局提交成本，要么停止等待新科学设计。FORGE比较关闭clip不授权修改我们的训练算法。[S01,S02]

9月30日DP-SGD权重绑定论文目前只读原始摘要；其untying/ghost-clipping属于不同训练模型比较，不能作为本方案保持同一模型的数值修复。[S13]

### 四层评价

- 目标族：同语义head统计/dH/dW、lookup归约与一次optimizer commit，不能只报最后一个快kernel。
- 净成本：重算、H/LSE保留、索引/归约、同步、cast、状态读写、launch/drain全部计入。
- 覆盖/非目标：真实baseline时间权重、non-target中位/最差退化、内存时间线；NSYS duration和wall不混。
- 完整边界：training step时间、peak allocated/reserved memory及下一步正常执行。没有整应用5%统一否决；时间/容量分开，必要时报告Pareto取舍。

当前只有数组量级，没有合法时间oracle。以后不允许把整个dW GEMM或整个AdamW删掉称为gradient发布headroom；原生无法干净隔离时，直接做有限S1/S2反事实，不为了完美oracle另造平台。

### 停止/保留

输入/alias/数值未资格化是UNKNOWN，不是negative。S1已提供同等收益则保留简单软件、不推硬件。S2新增成本吃掉时间且无容量利益，则停止该固定方案，不换模型挽救。仅容量改善可保留范围化容量结果，不写时间positive。只有强软件后仍有稳定、可解释的限制及不同能力/成本优势才再讨论硬件；现在没有。

## 8. 当前节点和授权

本轮研究准备完成，**所有lane仍无新节点任务**。F/G仍在109，E仍在174-new；GPU锁仍为`/data/c16/locks/c16_gpu_campaign.lock`。164为大数据authority，174不stage大trace。未发启动/续跑命令、未reset/merge实验分支。

## 9. 外部原始来源及阅读深度

S01 FORGE，v1 2026-06-22；正文§2.2、Appendix A/G关键部分，非全文逐字审计：
https://arxiv.org/html/2606.22932v1

S02 FlashOptim README，commit 43548ceebbbdb869c4ea9db7b21bba1cf9ae7004，2026-07-09；固定文档Gradient Release及精度范围：
https://github.com/databricks/flashoptim/blob/43548ceebbbdb869c4ea9db7b21bba1cf9ae7004/README.md

S03 CCE，commit 3de376c106a1916bc5e1b619f9c77c87a461ee1c，2026-09-11；cce.py物理110–235行；不称全仓库审核：
https://github.com/apple-aiml-research/ml-cross-entropy/blob/3de376c106a1916bc5e1b619f9c77c87a461ee1c/cut_cross_entropy/cce.py

S04 PyTorch官方optimizer-in-backward教程，2026-10-02读取，未执行：
https://docs.pytorch.org/tutorials/intermediate/optimizer_step_in_backward_tutorial.html

S05 FBGEMM官方TBE training API，2026-10-02读取，重点backward/update与NONE模式：
https://docs.pytorch.org/FBGEMM/fbgemm_gpu/python-api/tbe_ops_training.html

S06 Qwen固定config，revision 7ae557604adf67be50417f59c2c2f167def9a775，完整配置字段：
https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/blob/7ae557604adf67be50417f59c2c2f167def9a775/config.json

S07 AWS/vLLM作者技术文章，compound sparsity/joint tuning小节，非最新源码替代：
https://aws.amazon.com/blogs/machine-learning/efficiently-serve-dozens-of-fine-tuned-models-with-vllm-on-amazon-sagemaker-ai-and-amazon-bedrock/

S08 vLLM源码，commit e34489a54348717c84891e313b5066854b967225，2026-09-23；物理1–480行，未运行：
https://github.com/vllm-project/vllm/blob/e34489a54348717c84891e313b5066854b967225/vllm/lora/ops/triton_ops/fused_moe_lora_op.py

S09 S-LoRA v3，§5.3等异构rank/布局能力范围：
https://arxiv.org/html/2311.03285v3

S10 InfiniLoRA v1，2026-04-08；§5.2/§6机制、平台与workload部分，合成到达不作自然路由：
https://arxiv.org/html/2604.07173v1

S11 tLoRA v2，2026-02-13；rank-aware nano-batching等正文关键部分，训练非推理：
https://arxiv.org/html/2602.07263v2

S12 Spira v2，引言/方法概述及作者artifact入口，不声称排除全部稀疏卷积残差：
https://arxiv.org/html/2511.20834v2

S13 Is Weight Tying Still Beneficial for Decoder-Only LLMs in Private Settings Under DP-SGD? v1，2026-09-30；仅原始摘要，本轮未取得正文：
https://arxiv.org/abs/2609.40335

项目authority（repo swayhrl/accel-sim-framework）：
- A01 ad06a071464f698760459c895d8587d020214eee，plans/STATUS_AFTER_R23G_REVIEW_2026-10-02.md。
- A02 同ref，empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv；相对本研究材料根目录。
- A03 用户主handoff AWMA_PROJECT_HANDOFF_CONTEXT_2026-10-02_R23G_ACTIVE；旧running状态由A01覆盖。
- A04 ec1ccad7bbcead8853cd97840a2007d96f325aa3，docs/vm_tlb/review_packs/AWMA_CCE_ZERO_INIT_REMOVAL_109_V1/FINAL_DECISION.md。

工具边界：容器直接获取少量公共源码时DNS失败，改用GitHub connector固定版本只读；没有落地完整外部源码镜像。源码可读不是109运行资格，检索未发现也不是新颖性穷尽证明。
