# Round10｜R81/R82横向审查与下一轮并行候选

日期：2026-09-27。维护：ChatGPT。本文为结果审查、最近邻复核与下一轮设计，不等同执行结果。

## 1. 已完成结果的横向结论

### R81：异构合法词表

Accepted:
- branch `hrl/awma-r81-legal-vocab-exploration-v1`
- commit `69e74fe74e18d1f3a71bfac0d097ce49234327a9`
- state `R81_SOFTWARE_OPPORTUNITY_NO_ARCH_CLAIM`

独立复核接受。

关键事实：
- 12个冻结请求、207个grammar timestep，A0/A1/A2/A3 token轨迹/stop完全一致，12/12 JSON schema有效。
- 三组legal-union中位数均约147068/151936 = 96.8%词表。
- union<1%局部状态：A3 direct-ragged相对A0 head-region节省约44.8%–53.4%。
- union>50%主导状态：A3比A0慢约6.7%–27.5%。
- full generation：C0 +3.62%，C1 +0.98%，holdout -0.73%；未形成可靠完整生成收益。
- A2 indexed-union在宽union时gather/metadata代价很高。
- A1仅为FlashSampling风格greedy适配，不是论文实现上界。

解释：
真实局部软件切换机会存在，但当前fixture中宽合法集占主导，架构残差没有形成。后续若做dense/ragged自适应dispatch属于software follow-up，不优先占体系结构探索资源。

R81冻结为：
`CLOSED_FOR_ARCH / SOFTWARE_ADAPTIVE_DISPATCH_OPTIONAL`.

### R82：片上layout转换

Accepted:
- branch `hrl/awma-r82-layout-transfer-exploration-v1`
- commit `385f38271466a01e7f9cedfe638355195057b7c8`
- state `R82_CURRENT_SOFTWARE_SUFFICIENT_IN_SCOPE`

独立复核接受。

关键事实：
- Triton 3.8强基线仍产生真实shuffle/shared/barrier，不是IR no-op。
- qualified P1 fixed-split-256中stage1/stage2各保留一个inter-warp conversion。
- C1与B0 bitwise exact。
- 7组paired：B0 0.021401601ms，C1 0.021452799ms，+0.239%，小于约1.25%–1.68% CV。
- C1虽将stage2 SASS STS 6→3，但register/shared/barrier/shuffle不变，未带来可复现收益。
- 剩余conversion跨warp ownership，不能合法用warp-only shuffle或删除CTA barrier。
- FLA GDN有55个真实conversion，但当时精确binary→launch multiplicity未闭合；后续R54 V1R2已闭合Hub greedy语义，但这并不会自动产生layout因果收益。
- PTX `movmatrix.sync.aligned.m8n8.trans.b16`只解决warp内受限8x8/b16转置，SM75+可用；不解决R82剩余inter-warp exchange。

解释：
当前软件lowering对qualified目标已经足够，且FIBER/Linear Layouts/Tensor Seeks Layout是直接近邻。除非未来有新的真实跨warp primitive成本证据，不继续R82。

R82冻结为：
`CLOSED_CURRENT_SOFTWARE_SUFFICIENT_IN_SCOPE`.

## 2. Round09候选复核

### Q92 稀疏结构寿命：暂不提升

最近邻进一步变强：
- PIT已直接处理dynamic sparsity的runtime tiling/format问题；
- UniSparse支持格式表示、转换和计算代码生成；
- SparseX (CGO 2026)直接强调不同SpMM库的preprocessing overhead在低复用/动态sparsity时不可忽略，并做overhead-aware运行时选择；
- AsyncSparse/Fused3S/IO-aware GNN又覆盖异步执行、融合和准备复用。

因此“结构寿命决定format preprocessing是否值得”本身已不是足够窄的新问题。没有新的AI-specific state transition或硬件局部残差前，不开GPU lane。

状态：
`Q92_DEFER_CLOSEST_WORK_TOO_DIRECT`.

### Q93 TT部分共享：不提升

FlowTT已经把部分TT索引共享/中间收缩复用作为核心。缺全文/artifact和训练失效规则。当前不下载推荐数据，不开执行lane。

状态：
`Q93_FULLTEXT_ARTIFACT_REQUIRED`.

### R82 FLA GDN继续线：不提升

R54 V1R2已经解决Hub backend greedy语义，但R82的关键问题不是只剩语义：
- exact dynamic cubin multiplicity仍需重新绑定；
- qualified P1目标没有响应；
- FIBER直接覆盖更广的thread/register decoupling；
- current Triton已执行minimal conversion。

没有新的软件可实现对照或明显mechanism response前，不继续投入。

## 3. 推进R101：固定Newton–Schulz映射的中间态生命周期

来源：
- HiMuon `tang0389/himuon @ af89eda9a0176effed99e1fe19cc1f8a1a2c9588`.
- `himuon.py`已有cross-layer batching、plan/buffer cache、完整optimizer-step CUDA Graph。
- 对满足`M*N <= 16384`的tile，`ns5_smem`将5次NS迭代留在一个CTA的SMEM/register路径。
- 更大tile走`_newton_schulz_3kernel`：每次迭代显式产生A/B/C并跨多个kernel继续，作者已用torch.compile/CUDA graph降低host launch问题。

因此强软件边界非常清楚：不能用“减少Python launch”作新意。剩余待验证问题是：

> 固定同一个finite Newton–Schulz map、固定tile语义后，当tile越过当前single-CTA on-chip容量边界时，跨迭代中间矩阵的HBM materialization是否形成真实、稳定且值得硬件支持的成本？

这与HiMuon改变tile size的算法收益不同。本轮只比较同shape、同公式的执行实现；不把T=128与T=256的不同optimizer map直接当性能因果。

### R101最小证据链

1. 源码/最近邻锁定。
2. 复用Qwen2.5-0.5B accepted模型和冻结文本，生成真实gradient/momentum矩阵；不下载新模型。
3. 选2–3个真实projection shape，冻结一个momentum snapshot。
4. 对可融合shape，同shape比较author fused `ns5_smem`与强制3-kernel exact finite map，建立“中间态留片上”机制响应。
5. 对越过容量阈值的shape，用作者3-kernel+graph作为强baseline，核HBM bytes、kernel critical path和optimizer-step占比。
6. 有界探索一个不改变NS公式的software orchestration/proxy；不能通过减少NS steps或改tile-local map获得收益。
7. 只有真实大tile路径存在material residual，且小tile同shape融合proxy证明中间态retention有因果响应，才进入architecture review。

注意：作者代码本身已经有persistent ns5选项、小tile融合、cross-layer batch和graph，必须作为strong baseline。

## 4. 条件推进R102：precision-gated权重变化检测/打包

来源：
- SparseRL-Sync / Helix `scitix/helix @ 867f76a82822dd87413da4fec617b7f8e7cf6414`.
- 开源`get_sparse_diff_indices`当前实现为
  `curr != prev -> nonzero -> int32`，源码明确TODO使用Triton。
- 后续`index_select`、bucket合并、copy形成payload。
- 论文问题是BF16/部署表示的lossless变化稀疏，而不是FP32梯度本身稀疏。

这说明存在一个明确software gap，但还不能直接叫architecture gap。更重要的是，目前公开repo没有绑定可直接复用的真实训练dump。

因此R102分两级：

A. source/input authority gate：
- 首先搜索公开artifact、本地资产或可确定性重建的真实训练更新；
- 必须有before/after exact low-precision weight snapshot或原始训练dump；
- 不能用随机构造的1% mask作为AI workload evidence。

B. 若真实input authority闭合：
- 先复现现有`!= + nonzero + index_select + bucket`；
- 实现一个有界fused Triton compare/compact软件baseline；
- 计完整encode path、scan/compaction、payload与bit-exact reconstruct；
- 若fused software关闭成本，结论为software sufficient；
- 只有fused后仍留下稳定GPU-local compaction/metadata residual，才讨论硬件。

若没有真实update authority，R102停在input gate，不浪费109。

## 5. 下一轮并行策略

推荐两个独立Codex窗口：

- **Lane H / R101**：109 Native主线，允许GPU。
- **Lane I / R102**：先source/input authority；只有authority闭合后才允许GPU canary/formal。

两lane所有CUDA操作仍使用：
`/data/c16/locks/c16_gpu_campaign.lock`.

CPU/source/build可并行；独立worktree/env/cache/raw。

R101与R102机制不同：前者是dense matrix-function中间态生命周期，后者是representation-induced sparse change detection/compaction。这样可以避免再次并行两个本质相同的mask/layout问题。

## 6. 新增来源

- HiMuon: https://arxiv.org/abs/2606.27216 and https://github.com/tang0389/himuon
- SparseRL-Sync: https://arxiv.org/abs/2605.07330 and https://github.com/scitix/helix
- SparseX CGO26: DOI 10.1109/CGO68049.2026.11395201
- PIT: SOSP23 dynamic sparsity compiler
- UniSparse: arXiv:2403.05802
- NVIDIA PTX movmatrix: PTX ISA, introduced PTX 7.8, requires sm_75+, m8n8/trans/b16 only
