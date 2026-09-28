# Lane 6：OLMoE多输入路由的独立重算与结论审查

日期：2026-09-28。
执行节点：**174-new**；复用Lane 6窗口。
角色：CPU-only独立分析；禁止GPU、GPU锁、CUDA初始化、新采集及模拟器运行。
任务ID（仅机器字段使用）：`C16_OLMOE_MULTIROUND_INDEPENDENT_CONSUMER_174NEW_V1`。

本文件是待下发合同，不代表consumer已经运行。向用户汇报必须用清晰中文，说明发现、限制与下一步，不用英文内部状态名代替结论。

## 1. 本轮要回答的问题

109已经完成一次加载模型、六个session的路由采集。本轮不再采数据，一次完成：

1. 从164原始文件验证采集身份、连续生成、六个session与4096条路由记录；
2. 独立复算原计划的全部指标和producer实际分类规则，记录相同与不同之处；
3. 区分TEXT中的强11步结构、CODE/STRUCTURED的其他周期，以及PROSE仅略超单点参照的情况；
4. 给出证据能支持的中文结论，而不是直接继承producer较强的分类名称。

**当前审查判断，不是预定分析结果：**TEXT的历史专家集合和输出token得到重现具有实质价值；但PROSE Layer1 lag11=0.171341仅比其shuffle p95=0.164213高约0.00713，主峰在lag1，不能直接视为与TEXT的强周期等价。必须同时保留效应大小、主峰位置、测试范围和单prompt限制。

原协调合同把p05/p95定义成描述性区间，不是预注册显著性检验。不要看到结果后修改原规则，也不要将附加统计写成原来已经注册的门槛。下面新增检查统一标为“结果可见后的解释稳健性诊断”。

## 2. 固定来源

仓库：`swayhrl/accel-sim-framework`。

原采集合同：
- coordination commit `378df585cba4c21ac5864c374976e271ae44e9a3`。
- `docs/vm_tlb/chatgpt_handoff/c16/olmoe_routing_provenance_multiround_109_v1/C16_LANE7_OLMOE_ROUTING_PROVENANCE_MULTIROUND_109_V1.md`。

最新producer：
- branch `hrl/c16-olmoe-routing-provenance-multiround-109-v1`；
- scientific commit `35bc117a961ad55114f9d75752beb29f6acadc59`；
- final commit `27b923db5922e2f986d2f9e815050bdbad0c3bd2`；
- final tree `782a2b2b43d7cd96579f7b10d095de314f492945`；
- review pack `docs/vm_tlb/review_packs/C16_OLMOE_ROUTING_PROVENANCE_MULTIROUND_109_V1/`。

先读其中的SOURCE_AUTHORITY、GENERATION_CONTRACT、DURABLE_PROVENANCE、NEXT_174_CONSUMER_CONTRACT，以及已提交runner和analysis代码。producer的结果TSV只供最后对照，不能替代原始输入重算。

保留的旧结果：
- Lane 6 V1 `0017527afba6861a4a0cfee95cce7b2a0397f284`；
- Lane 6 post-hoc `72fdd0f89aa0d4d4ae8b0d55daea492fbae2f293`；
- V34 producer `ab26365dc663268b0799818db6687ed466e8c925`；
- V40 descendant `85563ec6f55a0ad743d21483aa49c24fdb5cf3bf`。

不覆盖producer和上述历史结果。新建独立worktree/branch，建议从Lane 6 `72fdd0f...`建立：
`hrl/c16-olmoe-multiround-consumer-174new-v1`。
不要大范围merge其他分支；按固定commit只读需要的文件。

## 3. 164原始数据与身份核对

科学RUN_ID：
`C16R_olmoe-routing-provenance-multiround-v1_20260928T092536Z_c91846a955f5`

持久化RUN_ID：
`C16R_olmoe-1b-7b-0125-instruct_routing-provenance-multiround_prefill2048-decode64_passive-hooks_all-layers_20260928T092536Z_c91846a955f5`

根目录：`/root/share/mnt164/huangrulin/c16_ai_workload/`。
使用`raw/<持久化RUN_ID>`、`catalog/entries/<持久化RUN_ID>.json`、`reports/transfer_acks/<持久化RUN_ID>.TRANSFER_ACK.json`。

预期SHA256：
- RUN_MANIFEST：`07ce90441cecfc29d2669c306084913e8b704234cd4e065c403a01fc4487ac9b`；
- catalog：`0007fd2f1ed22449ae683bb4644acf914dd921b51854e8a5566eb731d6f3784e`；
- ACK：`1f2740893326c192d645ac050a82b648e97f6bd9db1004b903e7f8d9b2d37901`。

校验manifest列举的35项及对应大小/哈希；不要把manifest自身、READY、传输回执等包装文件混入该35项计数。核SCIENTIFIC_RUN_ID_BINDING明确连接两种RUN_ID，不要把较短科学ID的quarantine目录当正式raw。

模型固定：`allenai/OLMoE-1B-7B-0125-Instruct@b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e`。
模型receipt SHA：`01319b411b07ccd7b53c4f653bd5986a51604d9c2c16be7412257e994ff49d13`。

本次runtime：Python3.12.3、torch2.7.1+cu126、transformers4.55.0、BF16、SDPA、DynamicCache。
- modeling_olmoe.py SHA：`413888fc3be7e037727586f25900b629cc5dbc06b227a4f0d42c67cacb597bc7`；
- executed runner SHA：`81cacc3cbccdd8726562e94175f114ca86b81caeb1dd3bf5e49f57789fa43d47`；
- input-freeze manifest SHA：`2550314fd25b26c9553100854ebc3d05549487ff4f5dd0427cbd44113d7b8567`。

只核小型receipt，不重新hash全部模型权重、不在174留模型副本、不安装GPU runtime。

四个token文件各2048 IDs：
- TEXT `bba8ad1051b3e96039933d65ad8d77af3877f5603ae743b5e123d82c64de88e5`；
- CODE `107ef30b6f1bab3052bdd909b734ac538fa5aa4944c5094ac3b66c25fc3247f2`；
- STRUCTURED `ec5cd4d780ee8b16829eb9c71c002996a114bf84b5209511cf75d0c8469fdad4`；
- PROSE `e798d58332299434f0b945238c047340e6070cf881bd677fdfc62c369e24f2e4`。

## 4. 生成与观测语义核验

session：T0_NOHOOK_A、T1_NOHOOK_B、T2_TEXT_ALLLAYER、C1_CODE_ALLLAYER、S1_STRUCTURED_ALLLAYER、P1_PROSE_ALLLAYER。

逐session核：fresh prefill、64个连续decode step、greedy、自然EOS记录，没有跨session KV继承。每个step应满足：
- step1输入等于prefill输出；后续输入等于前一步输出；
- cache length before=2048+step-1，after=before+1；
- 每层step/token字段与session对齐；
- 捕获session覆盖16层×64步，不重不漏；四个capture总4096行；
- expert ID范围0..63、每步8个不同专家，权重有限、normalization与dtype语义有依据；
- 两个no-hook session无路由行；T0/T1/T2的prefill输出、长度、完整输出token序列精确相同。

这只证明该TEXT测试中输出不被hook改变，不扩大成所有输入/内部状态逐bit不变。

当前hook在gate输出上重新执行softmax/top-k，未直接截获MoE本体内部selected_experts。源码核对其数学路径、dtype、norm_topk与冻结模型一致；注明“由同一gate输出按同算法记录”，不要冒充直接记录所有expert kernel实际发射顺序。现有数据无法排除tie相关细节时保留限制，不为此自动重跑GPU。

## 5. 原计划完整重算（主交付）

用session JSON和routing JSONL计算，不导入producer的统计函数作为独立实现。小型通用hash/读取函数可复用。

- prompts：full及tail256的lag1..32 token equality，n=2/4/8重复描述；
- 每capture、每层：lag1..32的pair count、overlap、Jaccard、retention、ordered/unordered重复数；
- whole-step shuffle：seed20260928，1000次，复现producer所用NumPy default_rng和quantile线性插值；相同seed重置方式明确记录；
- 同input token与同output token的关联分别计算；按原统计使用lag1..32内的pairs，不能偷偷换成全部pairs后比较；
- 各层与输入的峰值、lag11、超p95计数；
- V34 Layer1前32步：unordered/ordered top-k、输出token、输入token分别对齐；hash对比需先核dtype/shape/字节序列化方式，不能无依据写hash_serialization_comparable=true。

同一session的16层不是16次独立生成；64步不是64个独立prompt；PROSE只有一个固定技术文本样本。TEXT的lag22可能是lag11的谐波，两者不是两次独立发现。

原producer机械分类函数是：TEXT Layer1 lag11超p95，且三个替代输入中至少一个同位置也超p95，即输出跨输入分类。独立复现这个函数的结果并原样登记，但另设“中文科学解释”字段，不能把机械分类直接当强周期泛化证明。追查是否在GPU前文件明确冻结了该数值分类规则；找不到则写未找到，不根据final代码倒推已经预注册。

## 6. 结果可见后的补充诊断（同轮完成、不新增采集）

这些检查为了防止过度解释，**不是修改原成功门槛、也不是新的预注册验证**。统一保留原输出和新增结果。

### 6.1 强度、峰形与稳定性

对每个输入Layer1列明：lag11 actual/null median/p95、差值、排序、相邻lag10/12、主峰及其数值。对16层给出同口径，不只数是否过线。

前32步与后32步分别计算lag11及已知主峰11/16/14/1（可计算时）。这里只是同条序列内的稳定性描述，不能将后半段称为新的独立holdout。所有数值照实保留，不加结果导向阈值。

### 6.2 区分预先关注的比较与全谱筛选

主问题原本关注Layer1/lag11，因此其替代输入比较范围是CODE、STRUCTURED、PROSE三项，不把它说成事后从2048项挑出的主检验。
但“16层×32lag哪里有过p95”和“PROSE有3层过线”属于相关的多项筛查，需要单独校准：

- 固定Layer1/lag11的三个替代输入：报告置换上尾比例 `(1+count(null>=actual))/(1000+1)`及Holm三项校正值；明确whole-step交换性只是该描述性null，不推出自然语言总体概率。
- 各session的全层/全lag：同一个时间置换同时用于全部16层，保留层间相关性。复用1000次置换，计算每次lag11上超原p95的层数分布，对比实际层数；另报告全谱最大“actual Jaccard减该cell null median”在置换下的最大值参照。
- 不独立打乱各层来制造独立样本；不增加置换次数直到弱信号过线；不把新校正用于覆写原producer分类。

### 6.3 输入token条件下的残余时间关系

仅对Layer1做一个简单补充：在相同input_token_id的step组内交换整条routing record，保留每组route集合及token时间序列；1000次、同seed。计算lag11及上述已知主峰的参照，帮助判断时间关系是否超出重复token关联。

若几乎没有可交换组，或所有组内route相同导致null退化，报告无法辨认额外作用，不强行判为有/无独立信号。即使超过条件化参照，也不叫token因果证明：hidden state还包含上下文。

无需新统计框架或模型拟合；优先复用64×64相似度矩阵和同一批置换，向量化CPU计算。

## 7. 交付与解释

新目录：`docs/vm_tlb/review_packs/C16_OLMOE_MULTIROUND_INDEPENDENT_CONSUMER_174NEW_V1/`。
保持精简：
- AUTHORITY_AND_SEQUENCE_CHECKS.json
- RECOMPUTED_METRICS.tsv（可分lag及token两份，避免巨型嵌套JSON）
- PRODUCER_COMPARISON.tsv
- ROBUSTNESS_DIAGNOSTICS.tsv / TOKEN_CONDITIONAL_CHECK.json
- HISTORICAL_COMPARISON.tsv
- SCIENTIFIC_INTERPRETATION.md（中文）
- FINAL_DECISION.json
- SHA256SUMS
以及一个CPU consumer脚本与最小tests。

中文结论必须分别回答：
1. 当前采集是否可用；
2. 原TEXT的专家集合/输出序列复现到什么层次；
3. 主要时间结构是否随输入改变；
4. PROSE的11步现象是突出峰、弱超线还是尚不可判定；
5. 是否有独立于token重复的额外描述性证据；
6. 现有结果是否值得新增GPU实验；允许明确回答暂不值得。

不能写“MoE固定11步”“跨模型规律”“缓存复用已被证明”。不得因producer标题较强而预设新分析必须否定它；也不得因p95超线就宣布泛化成立。

## 8. 资源、停止与调度

单CPU worker、BLAS/OMP线程1、轻量内存；4.8MB raw可以读入，但不扫描其他大trace或模型。不触碰Lane4 worktree/process/binary/config/output，不读partial。

GPU完全不需要；禁止要求109重新采集、重新生成或安装新后端。普通路径/格式/派生包装问题由accepted来源确定性解决，重建件注明派生；真正缺失不可恢复的科学身份/原始记录才停止。

若数值与producer不一致，保留raw及双方差异，继续完成不受影响检查，不为迎合结果修改原始记录。

完成commit→push→fetch-back exact commit/tree→clean→中文汇报→STOP。发布故障切换已配置的可用Git通道，不重跑数据。producer结果、旧Lane6结果均不修改。

109/Lane7当前OLMoE采集已经交付。后续split-K访存状态实验的handoff此前尚未由用户下发；本consumer不代为下发，也不阻塞用户随后让109独立执行该任务。Lane8的Qwen3 KV任务保持其现有安排。

## 9. ChatGPT本轮审查范围

已核远端producer commit/tree/lineage、关键runner、analysis、生成合同、来源与持久化回执、分类理由。尚未直接读取node164四个routing JSONL或重算4096行，故没有把本轮源码审查称为独立raw验收。本文新增统计属于结果可见后的解释检查；不修改采集、不偷偷增补预注册成功标准。
