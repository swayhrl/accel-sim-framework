# 负结果、阻塞、被替代证据与“不要重复做”清单

来源ID见`SOURCE_INDEX.md`；完整条目见`WORK_LEDGER.tsv`。本文件不把所有非正结果都称为“失败”。

## 1. 真正做过，但没有达到科学/性能门槛

| 工作 | 已得到什么 | 没得到什么 | 当前处置 |
|---|---|---|---|
| Residency intervention [S28] | local timing/DRAM material | strict reversibility未全部通过 | 保留PARTIALLY_SUPPORTED；不升格唯一L2因果 |
| CUDA targeted persistence [S30] | isolated/natural local timing收益 | strict natural DRAM materiality未通过 | raw一致但producer/consumer规则分歧永久保留 |
| Shared residency [S31] | 多目标局部收益 | material whole-decode收益 | LOCAL_ONLY；不是pipeline错误 |
| N28 coverage scaling [S32] | whole-decode方向正 | 注册门槛内的material收益 | POSITIVE_BUT_SUBTHRESHOLD；不可只引用“positive” |
| Operator-family expansion [S33] | up局部价值保留 | 扩gate/up/down后系统收益 | NOT_SUPPORTED；完整FFN扩覆盖已试过 |
| B8/B16/B24/BFULL closure [S34] | 28/28 up local material，语义账目闭合 | 系统净收益及唯一微架构原因 | OFFSET_LOCALIZED；不是“驻留从来没用” |
| BFULL L0 attention代表NCU [S34a] | 该范围计数可审 | 复现aggregate attention slowdown | 代表范围近乎不变，不能代替全部attention |
| E3 natural vs uniform [S25] | 冻结场景下balanced代理足够 | 支持继续深抓的差异 | 关闭当前E3；不推广到所有路由时间结构 |
| Host加速 [S35] | 多个候选bounded exact | 可采用的≥5%repeatable加速 | 全线NO_SAFE_MATERIAL_GAIN，candidate回退 |
| Lane7 split8→split1 [S41] | upM256改善28.88% | 两M256都material且M1不退化的全局H1 | OPERATOR_SPECIFIC；停止自动扩split参数扫描 |
| Lane6相邻集合检验 [S40] | 合法OLMoE单层32-step分析 | 超出当前shuffle范围的额外lag1信号 | 有限non-detection；不可写成不存在所有时间相关性 |

这些项目均留下可复用证据或排除了具体解释。没有系统收益不表示原始数据无效，更不构成重跑原矩阵的理由。

## 2. Host实验逐项保留

数值保持原文件`candidate_speedup_fraction`/`host_speedup_pct`口径；正值表示源表中的host改善。没有改换参照或把wall time当模拟GPU周期。[S35/S35a]

| 候选/对照 | 源表host变化 | 结论 |
|---|---:|---|
| MEMSTAT0 | -0.5913% | REJECT_NO_GAIN |
| 配置PTXLINE0 | -0.4173% | REJECT_NO_GAIN |
| guarded config0相对同binary config1 | -1.4897% | REVERTED_NO_GAIN |
| runtime interval 10000 | +1.7172% | REJECT_BELOW_5_PERCENT |
| 预解压 | +0.3565% | REJECT_BELOW_5_PERCENT |
| tmpfs compressed | -0.4455% | REJECT_NO_GAIN |
| CPU300 affinity | -1.1099% | 仅保留隔离用途，不是加速 |
| combined相对current authority | -16.9899% | REJECT |
| 同combined相对pristine same-build | -9.6848% | REJECT，同一组合的另一个参照 |
| LTO/PGO | 未构建 | NOT_BUILT_DIMINISHING_RETURNS，不是实测负结果 |

原`CANDIDATES.tsv`的header和整组数据重复了一遍。本总账显式按相同candidate/comparison去重；保留原文件不改，不把重复行计成重复实验。`QUALIFICATION.json`中每个比较只有一组对应条目。

本轮读取到的prefix为16 kernels，终局cycles/instructions/CTA为87146/613280/57；没有completed target range。故exactness是该prefix内的行为一致性，不是完整目标保护决策的动态证明。[S35b]

## 3. 没有完成formal执行的工程阻塞

| 阶段 | 实际阻塞 | 当时已经可用的部分 | 后继/当前边界 |
|---|---|---|---|
| gpt-oss V29 [S17] | native MXFP4/SM89路径不满足要求 | 资产/授权不等于运行可用 | formal NOT_RUN；没有性能负结论 |
| OLMoE V32 [S18] | exact S2 token freeze未证 | native BF16容量PASS | 模型/routing/formal未执行；后续修输入 |
| OLMoE V34 [S19] | fresh static路径audit缺失 | native S2、natural routing、rank1 replay PASS | 32-step routing不是因为formal失败就无效 |
| OLMoE V35 [S20] | actual cuBLAS SM89 selector未闭合 | 静态工具探索 | canary/formal NOT_RUN |
| OLMoE V36 [S21] | 跨进程actual-JIT variant漂移 | NVBit动态attribution | 转variant-aware方案 |
| OLMoE V37 [S22] | bounded重试未得到variant B | 16次全为A | 不宣称B不存在；正式范围限定A |
| OLMoE V38 [S23] | warp-regsource/JIT selector lifecycle未闭合 | complete static/dynamic audit | formal NOT_RUN；后续V39/V40工程链 |
| OLMoE V40 [S24] | 后续canonical/provenance修复完成 | 243-shard最终独立重算与ACK | 这是后继成功，不删除早期blocker记录 |

这些阻塞不能当成“MoE没有局部性”“该模型不值得研究”的证据。反过来，V40成功也不赋予未formal的variant B资格。

## 4. 旧证据不是当前主比较的输入

### R4与R5

R5 README明确将R4定量数据排除于科学结论。保留R4作为工程历史，不再次作为速度/流量对照。[S03]

### 早期RAW/AWQ部署比较与clean E1

V10是matched semantic-module deployment comparison，但自然部署输入不同。Clean E1另行冻结byte-identical FP16输入；它不是把V10的不同输入事后修正为同一输入。两条证据分别保存。[S09/S26]

### NCU V1与V2

V1保留为`COLD_CACHE_KERNEL_REPLAY_DIAGNOSTIC`；V2才是后续使用的application-replay/cache-control-none semantic证据。不得从两者各选有利字段混成一个实验。[H0/S27]

### 历史selector checksum与canonical selector

OLMoE旧selector序列化的精确producer未durably retained。历史opaque checksum继续是opaque；V40 raw TSV和canonical V1给出新的可重算绑定。不能声称重新算出了旧checksum，也无需为其反复重开旧流程。[S02/S24]

### 原始SHiP与C16 SHiP-SW-style

早期baseline prep因软件region/signature等合同不唯一而PARTIAL；随后得到明确C16适配并完成qualification。最终使用的是`C16_SHIP_SW_STYLE_V1`，不是声称逐bit复现原始MICRO SHiP或完整AutoScratch。保留训练时点、signature、有限表与critical-only范围，不能在论文中用一个通用“SHiP”名字抹平。[S36/S38/此前已审实现]

## 5. 仅准备/设计，不是已跑且无效

- M1F prototype和real-trace activation：已具备实现/激活资格，未授权full timing。[H0]
- P_all/P_stable/DRRIP/SHiP-SW：已实现与bounded qualification，没有完整性能排序。[S36]
- Exact-generation observer：实现合格，没有完整D1→D2 survival数据。[S36]
- Lane3 terminal evaluator：已准备并修复binary exact gate，没有正式消费Lane4 terminal packet，也没有Paper V2。[S37]
- LTO/PGO：考虑过但没有构建。[S35a]
- M1Q、更多B8/B24/BFULL模拟器长跑、更多split factors、完整QUICK/MARLIN/FLUTE移植：不是本阶段已执行实验，不自动授权。[H0/S39/S41]
- 三模型32-step all-layer routing capture：Lane6只产生计划，当前未执行。[S40]
- Period11审计：已完成，但只能记为`POST_HOC_DIAGNOSTIC_ONLY`。OLMoE Layer1 lag11信号很强且与next-token重复高度关联；generation runner/KV transition/sampling/seed/EOS/stopping provenance缺失，来源仍`UNRESOLVED`。不是预注册正结果、不是跨模型规律、不是cache机会证明。[S42]

## 6. 已有结果要求保留的三个“未知”

**未知不是零。** Activation重复供数在源码存在，但现有总量不能赋予tensor级动态归因；QUICK类shared往返也不因暂不移植而等于零成本。[S39]

**范围不足不是模型排序。** Q30四步×全层、OLMoE32步×一层、DeepSeek单点不支持“哪个模型更有temporal locality”的排名。[S40]

**结构风险不是已观测原因。** M1 target-only结构分析、balanced placement、stable selector global fit都不能替代完整自然窗口下的generation survival与周期结果。[H0/S36]

## 6a. Period-11结果为何仍属于“需要限制使用的正信号”

Lane6 V1只对相邻顺序做了原注册描述性control；后续完整lag 1–16 post-hoc审计发现lag11是唯一高于其shuffle p95的lag，mean Jaccard 0.928042。21组(t,t+11)中15组unordered集合完全相同，另5组达到7/8 near-repeat；19组记录了相同next token。但router-input与router-logits SHA相等均为0。[S42]

这说明“没有额外相邻信号”与“存在lag11结构”可以同时成立。需要保留三条限制：第一，这是看见V1后才发现并正式审计的post-hoc现象；第二，next token是routing后的输出关联变量，不是已证明的routing输入原因；第三，V34没有保存足够的generation runner/KV状态转移语义来判断这是自然内容循环还是capture/replay方法学造成的周期。故不能将其升级为`MOE_TEMPORAL_LOCALITY_PROVEN`或period-11缓存策略。

## 7. 何时才值得重新打开

重新打开已关闭路线必须写出：新的独立输入/实现/资源条件，或原证据存在的具体矛盾；仅有“这次也许能更快”不够。工程blocker只有合法runtime/authority变化后才重开；性能负结果只有新的可区分变量或新scope后才重开。

当前无新的执行授权。Lane4继续原任务；Lane6 post-hoc已闭合并停止；Lane7保留窗口但不自动运行下一实验。若未来补MoE routing capture，应先明确它是在闭合period11来源还是做跨模型独立验证，不能直接以post-hoc峰值作为机制设计依据。
