# Round22｜R21A与历史结果的kernel-family分层复审

日期：2026-10-02。回顾性证据审查，不是新GPU执行授权。

## 0. 主结论与审查范围

应重审，目的不是把所有STOP翻成positive，而是区分：目标计算是否更快、必要准备后是否仍有净收益、真实覆盖率和非目标退化、以及相对强软件是否真的需要硬件。完整应用不到5%不能直接否定局部机制；孤立kernel变快也不能把排序/list/同步归到“其他kernel”后不计成本。

本轮直接读取R21A、R81、R19F2及projection计时、CCE、R19 fast-weight、R17R1、R101R5与R20收口的远端文件。早期P1/P2、R51—R54、R82、translation/resource/UVM及C16采用已上传handoff、文本和历史账本。34行是问题/结果边界记录，不是34个新实验。未SSH重算node164全量raw；节点校验/锁释放/clean状态按执行receipt记录。没有新CUDA、NSYS、NCU或模拟器运行。

## 1. R21A原STOP成立，但TP族性能尚未测

Authority：`62af34149d45e9862d5a1e255e2a51ca88a3c4c7`；本轮读取Git对象确认tree为`162600044e971a571a69cf207e97afacc30e2b43`。

固定OAM-S:0.1包SHA `63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa`；sitraj第55帧/共110帧，64 Si原子，1394有向周期边。Natural图receiver已分组但组内sender不单调。

第一次transpose-only deterministic诊断energy符合、forces失败且保存了输出；采用固定源码的receiver/sender复合排序并同步重排edge/cell shifts后恢复原5e-5数值合同。这不是人为增加排序。两层共享prepared graph/permutation。A0与Dready采用同AOTInductor ASE CUDA模式、float32、TF32 OFF；30个formal输出全部数值合格。deterministic名称不等于已证明整个模型逐bit复现。

### 1.1 从DREADY_TIMING逐组重算

| 原组号 | A0 median ms | Dready median ms | 耗时下降 | 差值µs | 3×较大MAD µs | noise gate |
|---|---:|---:|---:|---:|---:|---|
| 0 | .591520 | .455464 | 23.0011% | 136.056 | 264.609 | FAIL |
| 1 | .481776 | .459110 | 4.7047% | 22.666 | 21.795 | PASS |
| 2 | .475401 | .455085 | 4.2734% | 20.316 | 29.697 | FAIL |

4.7047%是三组相对改善的中位数。第一组A0更慢且离散，不可凭空归因warmup、频率、共享进程或host开销。3×MAD是原工程筛选，不是给定置信水平的显著性检验。不能改门槛到4%、丢掉组或反复采到通过。原`R21A_RESULT_MIXED_NEEDS_REVIEW`保持。

RUN_RECEIPTS写明`durable_per_execution_lock_timestamp_receipt_present=false`。这是逐次锁时段证据缺口，不证明未持锁，也不是噪声根因。未来runner自动补记录，不为包装单独重跑。

### 1.2 未回答的问题

现有表没有成对TP forward、force backward、fixup/reduction和非TP族时间，也没有在线排序/permutation成本。故可能是TP明显变快但被覆盖率稀释，也可能TP仅略快，或部分计算收益被其他节点变化抵消。三者均未区分。代码未改不证明其他族性能不变。

新账本：numerics qualified；complete ready-state mixed；family response UNKNOWN；mandatory online prep UNKNOWN；non-target regression UNKNOWN；holdout NOT_RUN；hardware need NOT_ESTABLISHED。旧STOP保留，不直接开Donline。

## 2. 最应保留的历史局部positive

### R81：直接支持分类型分析，但不是非目标中性

`69e74fe74e18d1f3a71bfac0d097ce49234327a9`的原预分层数据显示，union<1%词表时A3 head耗时降低C0 53.4%、C1 45.3%、H0 44.8%；union>50%时却分别慢27.5%、7.1%、6.7%。完整生成C0慢3.62%、C1慢0.98%、H0快0.73%，无稳定整体增益。

因此局部软件机会真实，应从“总体没有收益”叙事中保留；但不能删宽状态或宣称其他部分不降。下一步最多先用已有数据检查在线legal set可得性、公开dense/direct-index能力和选择开销。事后每步挑最快arm只能叫retrospective oracle。

输入是12个author-crafted B4请求，不是生产到达分布；H0有不同内容但非跨模型证明。Kestrel/FlashSampling/XGrammar能力不是新意。

### CCE：关闭硬件动机，不等于软件成果为零

`ec1ccad7bbcead8853cd97840a2007d96f325aa3`：first-contributor将完整算子8.171520→7.202816ms，耗时下降11.85%，消除full dC zero-fill且无等价full-size pass。有效软件positive。锁调度也变化，所以不能把全部0.968704ms等于旧0.751779ms fill；完整训练step未测。

### R19 FP8：projection层也有软件收益，强软件后残差仍不稳定

`7b87638e74164cdffc21c0d280324bcb048b6a8d`：本轮由Stage-B projection原表重算，S1→S2三组中位降时24.00%、18.55%、19.94%。不是只有MLP总时间一个数。

但S2→D0投影残差为−0.659%、4.891%、4.555%，符号不一致；完整MLP也无稳定剩余残差。因此分小区域后没有找出被总体掩盖的稳定强残差。保留精确软件fusion收益，不恢复硬件线。该实现不是stock TE，旧BF16↔FP8失败不改。

### R19 fast-weight

`4ef10349b198d6989ab666309fbe95ce8993bc56`：五层两chunk局部区域2.079488→1.592320ms，23.43%软件收益；更新后consumer未观察到独立state-read惩罚。保留positive，但非完整TTT推理、非官方paper checkpoint，也不证明全部必要math不可优化。

### R101 S128

上传9月29日handoff记录`cfbe6503585fa1b10d979db5d26fb9be3a80e563`：F128/K128 .493408/.623488ms，降时20.86%；layer12约20.09%。应保留计算族融合结果。它同时改变动态指令、CTA、kernel分解和访存，不是纯cache机制。L512后续结论不能抹除不同shape的S128 positive。

## 3. 需要修正的旧停止理由

### C16 conversion reuse

上传材料记M64重复75%、M32 50%，CTA内复用已被strong kernel处理；剩余跨CTA共享涉及膨胀表示、发布、fanout与生命周期。natural up-projection scope时间权重约1.74%，旧流程据此取消局部oracle。

新解释：低覆盖率只限制该应用总收益；局部conversion族可实现净收益未测。不能据此断言族无价值，也不能从75%重复推导时间空间。表示膨胀/管理成本和最近邻仍是实质约束。先查已有局部数据，不自动恢复dequant cache项目。

### R17 CAGRA

直接重读`29ecc6e5e37005046b1a563c830bed9ae58af656`：质量合格MULTI_CTA和Resources复用成立。Q1 .215ms小于整Q32 .531ms，不证明Q1无残差；mode会改变搜索工作。纯GPU-active time未资格化。账本应写“强基线建立、GPU-local目标未归因”，不是图搜索全局最优。旧运行STOP不变。

### C16 duplicate / Split-K / E1

same-warp/static-MREF逻辑字节重复是真实结构而非性能反事实；cache吸收/scoreboard/候选时延未知。本轮上传的Split-K摘要没有足够的配对表，不补写提速数字。E1应按M、实现、dtype、算子角色分类，RAW/AWQ不是纯bit数因果；本轮未取全终态数据，只列为已有数据重分类对象。

## 4. 不会因改分组而翻转的边界

- R102和R52：真实输入/失效authority不足，不是性能negative；分类补不出payload。
- R53：packing改变token/cache轨迹，safe bucket恢复轨迹后合法减工0；不能挑快kernel绕开语义变化。
- IBP：P1/P2/P3会混入训练层迁移、GEMM拆分或前后向重写；因果对照未成立。
- VLA RTC/VJP：VJP真实，buffer复用无material收益；必要math与可移除state成本未分离，不是全VLA negative。
- P1 fixed-split-256：指定bitwise合同下成本约+.887%，本来就是局部强软件结果，不是被全模型稀释。
- P2 selector：online-ready差主要是selector计算，不能把必要评分算作indices发布浪费。
- R51：greedy版本没有规定交接增量且chunking有开销；R54主要是host/runtime；R82固定C1慢.239%且低于噪声，C2不资格化。均需限制scope，但没有新positive依据。
- pre-L1 coalescer：部分目标局部有效，classic intra-warp覆盖主要收益。有效与新颖性不足可以同时成立。
- resource/UVM：限定有效配置/容量/策略；耦合无效配置和缺测fault不能当性能negative。

### R101模型/Native层次仍要分开

M1 writeback降92.09%而cycles仅降.5027%；partition-side S1约.726%；有per-kernel raw时可以离线细分，无则未知。O2/P0 62.13%、P1 8.31%是模型服务位置干预，不是有限硬件收益。R101R5三目标Native以math-pipe为主，ordinary LDG/ST post-L1没有对应主导证据。问题在模型对应，不是一个总体平均值；分族规则不自动恢复这条硬件线。

### R20仍关闭，但不捏造hybrid负例

always-worklist固定304-worker完整solver稳定慢66.6%，为有效候选negative；list/worker循环/sync本来属于它的成本，不能只报晚期快片段。

late-only hybrid预检通过，formal B0 exact-niter失败，三组不完整。90个样本不是不存在，但不得事后删失败组成确认性比较。O2=11.77%仅是跨run零成本估计，不是实测或所有机制严格上界。本次不重跑、不放宽数值门槛、不改R20预算关闭。

## 5. 评价方法修订

四层同时报告：目标kernel/语义工作集合；必要准备后的净族成本；baseline覆盖率与非目标退化；完整operator/应用。

family建议：phase × semantic operation × implementation × shape/regime × dtype × direction × necessary context。fusion改变kernel数时比较相同语义工作集合，不强迫symbol一对一。

无重叠简化模型：目标占f、目标耗时减少g、非目标增加r、新增共享成本占h，则整体降时约`f*g-(1-f)*r-h`。目标占15%、降时30%，即使其他不变也只整体降时4.5%；不应据5%否决局部机制。若“快30%”指1.3x，则目标降时为1−1/1.3，整体降时3.4615%，整体speedup约1.03586x，不能混淆。

NSYS duration sum不是wall份额；NVTX归属应按launch/API correlation，不按CPU/GPU时间重叠。有并发时禁止重复计费。profile与formal分开，跨run估算明确标注。3×MAD只保留为原合同解释，不泛化为统计定理。

新的family/net/system/hardware/operational状态分列。强软件可做并不禁止未来硬件研究，但新硬件必须再证明成本、范围、吞吐、能效或通用性增量。一次公开算法换后端不自动成为硬件贡献。

本次重分组为RETROSPECTIVE；历史gate和标签不改。新subtype/门控须在新验证前冻结；旧discovery不能重叫holdout。现象与机制驱动小原型并行原则仍保留，不把完整应用评价前置成所有探索的许可门槛。

## 6. 下一步优先级（设计建议，非执行Goal）

1. R21A：复用帧55和合格compiled source，先固定TP forward/backward/fixup及非TP成员，做最小成对族级观测。必要时加sorted-atomic控制以区分排序局部性和deterministic聚合本身。准备从natural graph计入，不换OAM大小、不打开旧holdout、不搭MD平台。
2. R81：CPU重算已有稀疏/宽状态和权重，检查在线选择信息与近邻能力；无成本选择最快arm只能叫oracle。
3. C16 conversion/E1：核已有分族计时与代表性缺口；数据无则UNKNOWN，不因重复率好看开cache。
4. CCE、FP8、fast-weight、S128汇入软件positive证据库。输入/数值未资格化和R20保持原STOP。

## 7. 可追溯来源

### 本轮直接读取

同一repo `swayhrl/accel-sim-framework`：

- `62af34149d45e9862d5a1e255e2a51ca88a3c4c7` / `docs/vm_tlb/review_packs/AWMA_R21A_OEQ_GRAPH_READINESS_109_V1/`：FINAL_DECISION、DREADY_DECISION、DREADY_TIMING、README、DETERMINISTIC_GRAPH_CONTRACT、RUN_RECEIPTS、RAW_DATA_INDEX与Git commit对象。
- `69e74fe74e18d1f3a71bfac0d097ce49234327a9` / `docs/vm_tlb/review_packs/AWMA_R81_LEGAL_VOCAB_EXPLORATION_V1/DECISION.md`及commit中的CONTROL_STRATIFICATION_SUMMARY。
- `ec1ccad7bbcead8853cd97840a2007d96f325aa3` / `docs/vm_tlb/review_packs/AWMA_CCE_ZERO_INIT_REMOVAL_109_V1/FINAL_DECISION.md`。
- `7b87638e74164cdffc21c0d280324bcb048b6a8d` / `docs/vm_tlb/review_packs/AWMA_R19F2_FP8_SOFTWARE_COUNTERFACTUAL_109_V1/`：FINAL_DECISION、STAGE_B_TIMING_P。
- `4ef10349b198d6989ab666309fbe95ce8993bc56` / `docs/vm_tlb/review_packs/AWMA_R19_FASTWEIGHT_109_V1/FINAL_DECISION.md`。
- `29ecc6e5e37005046b1a563c830bed9ae58af656` / `docs/vm_tlb/review_packs/AWMA_R17R1_GRAPH_SEARCH_109_V2/FINAL_DECISION.md`。
- `48f5bf24a2136521e272ed4d1da18ba5aa5f798e` / `docs/vm_tlb/review_packs/AWMA_R101R5_NATIVE_POST_L1_DOWNSTREAM_109_V1/FINAL_DECISION.md`。
- `0c6cda2f680fa93ed5ea7d4b098eef5044a8a0c4` / `docs/vm_tlb/chatgpt_handoff/awma/r20r5_hybrid_native_v1/STATUS_AFTER_R20R5_FINAL_CLOSURE.md`。
- `18005684c6ca0f0e6804b10ecfb411d80ae83e26` / 文献README及ROUND18_AWMA_BOUNDARY_LEDGER。

### 继承资料

用户上传9月29日主handoff第6—7节、AWMA-3/4/5/6、C16 conversion和cross-lineage终态、kernel采样/前序规则与本会话报告。没有冒称本轮逐个重读所有raw。Split-K/E1完整终态配对表明确未取得。

### 外部方法核查

NVIDIA Nsight Systems AnalysisGuide/UserGuide与Nsight Compute ProfilingGuide（2026-10-02读取）。只用于核查duration、关联、graph观测与replay/cache方法，不替代私有实验材料。

## 8. 执行状态

本次仅发布审查报告、边界账本与方法规则，不修改旧execution branch或review pack，不下发GPU/模拟Goal。局部有效、软件已解决、覆盖率低、近邻已覆盖、输入/数值未知是不同终点，以后不统称“没有研究机会”。
