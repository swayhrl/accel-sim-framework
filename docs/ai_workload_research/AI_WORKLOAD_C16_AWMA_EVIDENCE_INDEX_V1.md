# AI负载体系结构研究：C16 × AWMA跨项目证据索引（V1）

**截点：**2026-10-13（以当前可读取的固定Git commit/ref为依据）  
**用途：**为`AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md`提供事实入口、适用范围与禁止外推项；将来新论文、实验或发现更新为新版本，不覆盖已冻结记录。  
**仓库：**[`swayhrl/accel-sim-framework`](https://github.com/swayhrl/accel-sim-framework)。此索引仅审读已提交的Git结果、交接与研究笔记；**未在本轮SSH读取node164 raw、运行模型、复现实验或测量GPU**。历史材料所称原始数据SHA/独立复算等，均应按各自原文件注明的验证级别理解。

## 0. 阅读方法与证据分类

- **[N] 真实GPU实验**：在原始测量范围内成立；若只有软件/算子局部区间，不能自动变成整模型效果。
- **[S] 模拟器/模型实验**：由冻结模拟配置支持；不是直接的RTX4080真实硬件时间/性能值。
- **[R] 重算/独立审查**：审查哪些raw、commit、字段应以具体报告为准；审查层级可低于独立运行节点复验。
- **[C] 源码/静态归纳**：证明实现或逻辑结构，而不是动态成本。
- **[L] 公开论文**：只能引用作者的特定实验组、平台和方法；不是本项目的GPU验证。
- **[P] 研究计划/待测问题**：没有对应新实验数据；并不授权执行。
- **[STOP]**：某一实验条件、数值合同、身份条件或当前机制造成停止；不自动等于科学假设被证伪。

**“关闭”分类：**`NEGATIVE_MEASURED`（实际负收益）/`SOFTWARE_ABSORBED`（强软件已覆盖主要机会）/`LOW_HEADROOM`（机会太小）/`IDENTITY_OR_NUMERIC_STOP`（准入失败）/`UNOBSERVABLE`（当前时间/因果无法判断）/`PARKED`（未来假设，非执行候选）/`SCOPED_POSITIVE`（真实正面但有限制）/`SIM_MECHANISM`（模拟器中有范围成立）。这些标签彼此不应替换。

### 当前恢复/协调入口

| 入口 | 固定对象 | 适用范围 |
|---|---|---|
| **C16最新终态** | [`635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f`](https://github.com/swayhrl/accel-sim-framework/commit/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f) | `NO_NEW_PROBLEM_READY_FOR_NATIVE_VALIDATION`，10候选0主/0备，2个PARKED；并非AI全域没有问题 |
| **C16 Stage A独立收口** | [`ccd6928bfb420d1e4c554ec0e377bb8fbe377501`](https://github.com/swayhrl/accel-sim-framework/commit/ccd6928bfb420d1e4c554ec0e377bb8fbe377501) | 四DQ均不完整，MP02 B1合法子结果，0 formal survivor |
| **C16旧机制探索综合** | [`ca6c33ae0431d91aa7c6a43cbb79522402dd7580`](https://github.com/swayhrl/accel-sim-framework/commit/ca6c33ae0431d91aa7c6a43cbb79522402dd7580) | E1、Split-K、转换缓存、FFN等成熟阶段分类 |
| **AWMA最新已发表handoff** | [`29ce051f982f3854bd4392a94e4195c59340123b`](https://github.com/swayhrl/accel-sim-framework/commit/29ce051f982f3854bd4392a94e4195c59340123b) | R27R3事前执行合同，不表示结果PASS |
| **AWMA当前文献/科学状态笔记** | [`f0a6ec310c09cd011fffbe8a5ca22d6effacdf6b`](https://github.com/swayhrl/accel-sim-framework/commit/f0a6ec310c09cd011fffbe8a5ca22d6effacdf6b) | 最新独立科学审阅已接受R27R3有限STOP；原始实验authority仍在R27R3 execution commit，协调分支不构成新授权 |
| **AWMA R27R3最新可见结果** | [`7bd31fae4c54e121d54743a803d978ee02a64959`](https://github.com/swayhrl/accel-sim-framework/commit/7bd31fae4c54e121d54743a803d978ee02a64959) | [独立审阅](https://github.com/swayhrl/accel-sim-framework/blob/d6e9bbfb562814bcd5dc5adb444d3c572e7f446b/docs/vm_tlb/literature_notes/awma/empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md)接受`R27R3_B0_REFERENCE_NOT_REPEATABLE`，B0两次fresh process完整梯度25/262,668,288元素超原容差；组件归因与容量未运行 |

## 1. C16证据条目（按问题归类，不按Codex轮次）

| 编号 | 对象/实验与结果 | 证据类型/科学状态 | 最重要的限制 | 固定来源 |
|---|---|---|---|---|
| **E-C01** | MP01 BF16 Prefill局部时间权重：gate/up约51.82%、attention约16.64%；MP05 AWQ B1 gate/up约35.45%、attention约21.38% | [N][R] `SCOPED_POSITIVE` | 都是各自合法Graph-OFF局部时间份额；MP05不是只改变精度的BF16比较，不能当compiled whole-run权重 | [Stage A final](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/STAGEA_TERMINAL_SYNTHESIS.md) |
| **E-C02** | Qwen3-30B、DeepSeek、OLMoE选定MoE计算路径和访存采集；三条模型线可支持算子/地址的有界分析 | [N][C] `SELECTED_SCOPE` | 逐任务/逐模型选定采集不等同完整模型的同进程cache/TLB时序或请求级性能 | [C16发现归档](https://github.com/swayhrl/accel-sim-framework/blob/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f/docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_RESET_174NEW_V1/EXISTING_OBSERVATION_ARCHIVE.tsv)；其他lineage原raw索引需逐项追溯 |
| **E-C03** | MP02 BF16 B1，Mode A编译+Graph 354.598206ms，Mode B编译无Graph 361.456543ms；A相对B低1.8974169% | [N][R] `SCOPED_POSITIVE` | 各5次正式请求；仅B1同点request-level对照，B4没有合法配对；这不是GPU利用率或新硬件oracle | [独立consumer](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/DQ2_FINAL_STATUS.md) |
| **E-C04** | E1量化权重驻留：up投影若干局部收益，但共享配额与扩大算子覆盖没有稳定整段收益 | [N][S] `LOCAL_ONLY` | 不能从局部命中率推出所有FFN或完整Decode加速 | [旧探索证据账本](https://github.com/swayhrl/accel-sim-framework/blob/ca6c33ae0431d91aa7c6a43cbb79522402dd7580/docs/vm_tlb/review_packs/C16_AI_WORKLOAD_EXPLORATION_WAVE_TERMINAL_SYNTHESIS_174NEW_V1/C16_ACCEPTED_EVIDENCE_LEDGER.tsv)；[shared实验](https://github.com/swayhrl/accel-sim-framework/commit/1e701f013fc174b5b4df9febb5c33500f9ea586e) |
| **E-C05** | M1缓存保护真实模拟窗慢0.2054%，目标up局部慢0.2777%；M1F选择器目标零成本整窗上限0.9557% | [S] `NEGATIVE_MEASURED/LOW_HEADROOM` | 仅冻结连续模拟窗口和当前策略，不排除全部AI缓存研究；M1F未做完整时间运行 | [M1](https://github.com/swayhrl/accel-sim-framework/commit/71324d46435293edab3b7a0ff6ee999e675be0d0)、[M1F](https://github.com/swayhrl/accel-sim-framework/commit/5f7a2b831d87606c693c29934bb520b8ccf02d43) |
| **E-C06** | W4 Split-K容量敏感：K2560→3072时DRAM 4.04×、运行时间1.60×；GROUP_M16使split1 L2 hit约95.95%；M64 split1快于split8约4.93% | [N] `SOFTWARE_ABSORBED` | 真正的异常存在；新cache-aware Split-K增量被成熟分组/局部性映射大幅压缩；不是所有矩阵形状 | [容量](https://github.com/swayhrl/accel-sim-framework/commit/6d226cd99946d3bd7b41c5ee005285183efbb915)、[分组终审](https://github.com/swayhrl/accel-sim-framework/commit/a3a36e64ae4a3a316df2bf4dfc9cac95caf8e164) |
| **E-C07** | Q30 MoE E3：自然N=11.577ms，均匀U=11.638ms（接近实验波动）；合成热点H=6.473ms | [N] `DIAGNOSTIC_ONLY` | H改变激活集合/语义工作，不是自然分派的“免费”优化上限；没有自然全请求证据 | [C16 E3归档](https://github.com/swayhrl/accel-sim-framework/blob/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f/docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_RESET_174NEW_V1/EXISTING_OBSERVATION_ARCHIVE.tsv) |
| **E-C08** | FFN合法wall=28.4797%而非模块时间和44.5747%；简单elementwise理想删减仅整Decode 0.221%；gate/up理想重叠上限7.893%；双流V2实测74.216→81.434ms、慢9.73% | [N][R] `NEGATIVE_MEASURED` | 直接双流性能在当前D0–D3为负；观察到竞争但不足以唯一解释全部减速；不否定其他异构交接 | [headroom](https://github.com/swayhrl/accel-sim-framework/commit/30b3016a7ad5b5ef86a3494c784e072938dee6c5)、[V2](https://github.com/swayhrl/accel-sim-framework/commit/e8a2553f5c7a9861ddd2a31ae50e79e79d78d3a7) |
| **E-C09** | vLLM已有merged gate/up强基线；本轮跨运行时严格比较336次有14次未通过冻结数值容差 | [C][N] `SOFTWARE_EXISTS/IDENTITY_OR_NUMERIC_STOP` | 不能把不合格的两种实现直接作性能排名；也不能推断vLLM错误或所有merge无价值 | [strong guard](https://github.com/swayhrl/accel-sim-framework/commit/3c3f667bbab8f3ae227dc3bc8eaa6c642b97a453)、[native](https://github.com/swayhrl/accel-sim-framework/commit/6c92e9cd868df48594f1c80f8f2294e404af6933) |
| **E-C10** | RTX4080 W4小M有效tile填充例子为6.25%；资源限制表现为混合计算、访存与调度状态 | [N][C] `SCREEN_NOT_MECHANISM` | 低填充不等于可节省93.75%的时间；Marlin/QUICK/FLUTE强近邻需先检查 | [Ada multiview](https://github.com/swayhrl/accel-sim-framework/commit/5a8bcd63638847c0f2a0951046ec9cb2ba1994a2) |
| **E-C11** | Stage A四问全部`QUESTION_INCOMPLETE`，正式survivor=0；MP03 B4两次attempt未形成合法formal Mode B | [R][STOP] `OBSERVABILITY/IDENTITY` | 不能表述为“四问为负”或“没有新架构现象”；Mode B无observer正确性PASS另行保留 | [Stage A总收口](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/FINAL_DECISION.json) |
| **E-C12** | DeepSeek选定GEMVX中约50%逻辑权重字节重复，主要位于相同warp/CTA，不是cross-CTA证据 | [C][N] `TRAFFIC_NOT_TIME` | 没有证实多余DRAM流量或完整时间损失；不能从50%计算潜在加速 | [DeepSeek revisit](https://github.com/swayhrl/accel-sim-framework/commit/d23e0fd263cd9ff2b144f3d023ab60c567afb6f4) |
| **E-C13** | Q30/OLMoE/DeepSeek选定地址页/权重与KV静态分析 | [C] `UNOBSERVABLE_TIME` | 页面集合和VA足迹不是TLB miss或translation stalled-time；同进程动态序列缺失 | [C16 VA与translation方向终态](https://github.com/swayhrl/accel-sim-framework/commit/9759c08f3bb6e9abd134591007a27ed5bf8c23b1) |
| **E-C14** | Python module hooks在compiled Mode B报告0/4608；现有compiler artifact与runtime name仅1/96直接唯一映射 | [C][R][STOP] `LEVEL_0_UNRESOLVED` | 不能由静态FX顺序、kernel名字、FLOPs恢复Attention/FFN时间及handoff chronology | [Lane7复审](https://github.com/swayhrl/accel-sim-framework/commit/ab3df70e3a18eea6292af71334f9a2727066c5b3)；[Stage A综述](https://github.com/swayhrl/accel-sim-framework/blob/ccd6928bfb420d1e4c554ec0e377bb8fbe377501/docs/vm_tlb/review_packs/C16_STAGEA_TERMINAL_INDEPENDENT_CONSUMER_174NEW_V1/STAGEA_TERMINAL_SYNTHESIS.md) |
| **E-C15** | 14条历史观察归档、10个问题筛查，0 PRIMARY、0 BACKUP；PC03自然MoE/PC04异构tile仅parking lot | [R][P] `NO_NATIVE_GOAL_READY` | 是当前准入结论，不是领域穷尽搜索；没有新GPU合同 | [Reset final](https://github.com/swayhrl/accel-sim-framework/blob/635b2f22cbe1bed5ac45de04b258a5f5e9bc6d4f/docs/vm_tlb/review_packs/C16_PROBLEM_DISCOVERY_RESET_174NEW_V1/FINAL_DECISION.json) |
| **E-C16** | W4 M64严格转换重复75%，目标在自然decode中的时间权重1.74%；隔离local“oracle”0.8262×（比baseline慢），预展开1.0929×改变了表示/内核 | [N][C] `LOW_HEADROOM/NEGATIVE_MEASURED` | 不能把重复量直接换算成收益；预展开不是免费保持同语义cache结果 | [重用审查](https://github.com/swayhrl/accel-sim-framework/commit/9ff9e9b3580d8d24a56c8d3beebc41e9f4975f47)、[native隔离](https://github.com/swayhrl/accel-sim-framework/commit/797477f2c7f365bac1930808125957a8c06af091) |

## 2. AWMA证据条目（保留物理/软件/数值各自等级）

| 编号 | 对象/结果 | 证据类型/科学状态 | 最重要限制 | 固定来源 |
|---|---|---|---|---|
| **E-A01** | Q05 Prefill Attention地址翻译：10k固定周期中理想翻译进度+56.55%，50k+76.55%；125个L1 miss请求者与19个新翻译、106个合并对应 | [S] `FIXED_WINDOW_SENSITIVITY` | 是固定周期完成指令的差，不是完整内核加速；I0不是可实现机制 | [Q05 characterization](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_TLB_PTW_CHARACTERIZATION_174NEW_V1/README.md)、[historical handoff](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md)（后者仅用早期阶段事实） |
| **E-A02** | 实机/模拟交叉校准曾出现敏感度方向/幅度不匹配；RTX4080-Ada模拟基准后来有范围通过12个正确性点 | [S][N] `MIXED_ALIGNMENT/QUALIFIED_SCOPE` | 10/80是模型相对延迟；并发行为仍有残差，不能当SM89硬件精确模型 | [cross-calibration](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1/README.md)、[limitations](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/KNOWN_LIMITATIONS.md) |
| **E-A03** | Pre-L1重复翻译请求合并：有限2 entries/SID、32 waiters/entry，开发范围的服务抑制与部分性能positive；后续形成有范围论文资格化 | [S][C] `SIM_MECHANISM/PAPER_SCOPED` | 不证明普遍加速、RTX4080真实时间、最终新颖性或真实芯片PPA；部分目标还退化 | [机制资格化](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_PREL1_COALESCER_PAPER_QUALIFICATION_V1/FINAL_QUALIFICATION.md) |
| **E-A04** | 独立REDUCE验证：L1物理服务从130次降为10次，但主方案cycles仍7716不变 | [S] `INDEPENDENT_SERVICE_SUPPRESSION` | 只证实服务抑制跨到一个独立目标；时间中性是真实观察，不能自动称加速 | [holdout结果](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_PREL1_COALESCER_MINIMAL_INDEPENDENT_HOLDOUT_VALIDATION_V1/FINAL_DECISION.md) |
| **E-A05** | R19同表示FP8准备与计算重新组织，部分局部时间效应被软件融合吸收 | [N][C] `SOFTWARE_POSITIVE/RESIDUAL_MIXED` | 不是“FP8无问题”，也不能把预处理全部免费移除；需核每项同表示与后端 | [Round22证据表](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv)（R19F1/F2） |
| **E-A06** | CCE first-contributor软件方案对完整loss/backward有约11.85%窄范围改善 | [N] `SCOPED_SOFTWARE_POSITIVE` | 属于现有软件组织能力；不能把所有改善都归于清零操作移除，也不能自动作为新硬件问题 | [Round22 ledger](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv)（CCE_zero_init） |
| **E-A07** | R20迭代工作表方案固定条件完整求解约慢66.6%；另一hybrid路径数值合同失败 | [N][STOP] `NEGATIVE_MEASURED/NUMERIC_STOP` | 只有固定always-worklist是合法负结果；hybrid不是性能负结果，不能拼凑 | [Round21 source review](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/rounds/2026-10-02_ROUND_21_POST_R20_PROBLEM_DISCOVERY.md) |
| **E-A08** | R23G结构化生成在线选择：将union、CPU判定与真实路径切换计入后，九组LIVE_HEAD降低15.5%—33.8% | [N][R] `SCOPED_SOFTWARE_POSITIVE` | 12条源记录仅9个不同prompt/schema组合；完整生成未形成稳定的普遍收益，非硬件 | [R23G review](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/R23G_LIVE_DISPATCH_REVIEW_2026-10-02.md) |
| **E-A09** | R24共享embedding/head梯度：分块S2不物化完整V×H梯度，目标峰值较B0减773.06MiB；局部计时相对B0两正一负 | [N][R] `CAPACITY_POSITIVE/TIME_MIXED` | 一步、单模型、局部目标；后改final classifier不等于事前无歧义PASS；不代表整步峰值 | [R24 review](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/R24_TIED_WEIGHT_NATIVE_REVIEW_2026-10-02.md) |
| **E-A10** | R25更强C1对照：S2目标峰值Qwen减535.777MiB，Llama减1350.030MiB；时间Qwen约快0.933%，Llama约慢0.130% | [N][R] `CROSS_MODEL_CAPACITY_POSITIVE/TIME_MIXED` | 是目标族局部容量与短训练轨迹；非全参数训练/收敛/端到端加速 | [R25 review](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/R25_TIED_WEIGHT_BROADER_VALIDATION_REVIEW_2026-10-02.md) |
| **E-A11** | R26集成5步训练，重复一条序列：C1 B70 PASS/B71 OOM；S2 B71 PASS/B72 OOM（各端点3/3）；B70整步峰值S2高3.828MiB、时间MIXED | [N][R] `SCOPED_CAPACITY_POSITIVE` | 仅tied-W训练，重复batch数据，增加一个物理B；不是多样数据、收敛、全参数训练或速度positive | [R26 accepted review](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/R26_TIED_WEIGHT_CAPACITY_REVIEW_2026-10-02.md) |
| **E-A12** | R27R2新WikiText-2多样输入bank资格通过；B1四步C1/S2总梯度对B0全部FAIL；没进行容量试验 | [N][R][STOP] `NUMERIC_NOT_QUALIFIED` | 不能改称“多样输入容量负结果”；归因尚未证明且当时没有定位失效元素坐标 | [R27R2 independent review](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/R27R2_VARIED_BATCH_CAPACITY_REVIEW_2026-10-13.md) |
| **E-A13** | R27R3原生RTX4080，固定Llama-3.2-1B BF16 tied-W、WikiText-2 bank k0、B1，B0-vs-B0两次fresh process；完整梯度262,668,288元素中25处超`atol=rtol=1e-2`（行198有12处，行284有13处），最大超限(198,604)：5.40625→5.3125，差0.09375、容差0.06406；其它检查PASS，STOP在参考重复性门 | [N][R][STOP] `B0_REFERENCE_NOT_REPEATABLE_ACCEPTED` | 不证明B0数学错误或C1/S2数值来源；未做组件归因、修正、多样输入容量或32步；原R26重复输入的一physical batch结论不变。reviewer核对Git20/20 SHA和25元素表，node164 raw仅执行侧回读 | [execution](https://github.com/swayhrl/accel-sim-framework/commit/7bd31fae4c54e121d54743a803d978ee02a64959)；[accepted AWMA review](https://github.com/swayhrl/accel-sim-framework/blob/d6e9bbfb562814bcd5dc5adb444d3c572e7f446b/docs/vm_tlb/literature_notes/awma/empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md)；[coordination sync](R27R3_INDEPENDENT_REVIEW_SYNC_2026-10-13.md) |
| **E-A14** | 非LLM几何/图网络：R21源码分析图的receiver/source双向遍历、排序、CSR、prepared cache；R22实测分族与完整区间响应符号不一致 | [C][N] `PARTIAL/UNOBSERVED_NET_COST` | 不证明每步必重建，未找到合格的真实完整能量/力计算残余；当前无硬件题 | [R21 problem-discovery](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/rounds/2026-10-02_ROUND_21_POST_R20_PROBLEM_DISCOVERY.md)、[R22 status](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/plans/STATUS_AFTER_R22_FGE_RESULTS_AND_R22F1_AUTHORIZATION_2026-10-02.md) |
| **E-A15** | AWMA Round09跨执行组织、GNN/稀疏、推荐、训练优化器、可靠性的27项资料调研 | [L][C] `LITERATURE_AUDIT` | 19项关键正文、1项部分正文、6项摘要、1项artifact；不是27篇全文逐字精读，更不是本机验证 | [Round09](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_09_BROAD_SIDE_RESEARCH.md) |
| **E-A16** | R101 Newton–Schulz小tile局部融合在固定五步下有正响应；另一L512缓存/写回方案减少写量但不一定更快 | [N][S] `MIXED/CONTEXT_BOUND` | 训练状态对象/数学重组、native与simulator观察不同，不自动等于普遍硬件效果 | [Round22 ledger](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv)（R101各条） |
| **E-A17** | R19 fast-weight/TTT第三方artifact：特定two-chunk五层范围有约23.43%软件优化收益 | [N] `SCOPED_SOFTWARE_POSITIVE` | 局部算法/软件重组，不证明某个硬件瓶颈或普遍TTT改善 | [Round22 ledger](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/empirical/ROUND22_FAMILY_BOUNDARY_LEDGER.tsv) |

## 3. 外部论文/近邻索引（不属于C16/AWMA的实测结果）

| 编号 | 论文或已核来源 | 它提供的问题线索 | 能限制什么“新颖性”叙述 | 注意事项 |
|---|---|---|---|---|
| **E-L01** | [NanoFlow（OSDI 2025）](https://www.usenix.org/conference/osdi25/presentation/zhu-kan)、[Bullet](https://arxiv.org/abs/2504.19516) | 服务时计算/内存/网络工作并不天然充分重叠；朴素并发不一定有效 | 一般性nano-batching、分区调度、朴素overlap | 作者服务平台与C16低batch单4080不同；数字不得迁移 |
| **E-L02** | [Kitsune](https://arxiv.org/abs/2502.18403)、[MPK（OSDI 2026）](https://www.usenix.org/conference/osdi26/presentation/cheng) | 细粒度数据流、任务持续执行和跨算子流水 | “GPU原来算子串行，所以将其流水化”并非空白 | 区分架构扩展、编译器和runtime，核不同平台/指标 |
| **E-L03** | [VTC（OSDI 2026）](https://www.usenix.org/conference/osdi26/presentation/hu-muyan) | 虚拟张量/索引映射消除跨算子实际数据搬运 | 一般性的layout转换和消除中间张量存储 | 具体硬件新问题仍需证明VTC等强实现未覆盖 |
| **E-L04** | [Sobek（2026）](https://arxiv.org/abs/2607.18074)及AWMA审查的ALCHEMI强邻居构建 | 等变卷积的大中间边张量可通过调度重组消除；图准备/失效仍值得区分 | 不能拿naive e3nn的巨大中间数据当所有GNN必然硬件瓶颈 | 作者特定operator与导数阶；AWMA并未在本机重跑作者实验 |
| **E-L05** | [DirectKV（OSDI 2026）](https://www.usenix.org/conference/osdi26/presentation/luo) | GH200/GB200等CPU–GPU高速互联平台的KV容量与跨层数据访问 | “多一层CPU KV offload”本身已有软件与kernel设计 | GH200 NVLink-C2C不等同4080 PCIe，不能外推吞吐 |
| **E-L06** | [AWMA Round09原文审查](https://github.com/swayhrl/accel-sim-framework/blob/0b8310ee4afe8429b3ed2de381594794ee12ae31/docs/vm_tlb/literature_notes/awma/rounds/2026-09-27_ROUND_09_BROAD_SIDE_RESEARCH.md) | 图稀疏、3DGS、优化器、推荐、可靠性、编译与数据生命周期 | 先查已有强实现/数值语义，避免新瓶颈只是旧库功能 | 不同资料阅读深度不同；摘要层项目不能当原文全证据 |

## 4. 从问题图谱回查证据（便于避免重复调研）

| 问题图谱ID | 已有强证据/负例 | 还缺什么才可能转成新的科学问题 |
|---|---|---|
| P01 规模—瓶颈转换 | E-C03/C06/C10，E-L01/L02 | 合法跨规模同语义对照、模型/平台身份、真实时间与资源归因 |
| P02 低M/低比特 | E-C06/C10/C16，E-A05 | 在同量化格式和最强现有内核下可量化的剩余时间损失 |
| P03 重用/驻留 | E-C04/C05/C12 | 自然连续执行中保留的价值、竞争/负效应与真正时间headroom |
| P04 翻译并发与合并 | E-A01/A02/A03/A04，E-C13 | 平台校准/真实目标时间权重，硬件增量新颖性 |
| P05 MoE动态工作集 | E-C02/C07/C13 | 自然、同语义、完整请求/算子body可比的数据与时间上限 |
| P06 跨算子交接 | E-C08/C09，E-A14，E-L02/L03 | 一对具体已有强内核、必要完整交接成本和合法净时间对照 |
| P07 在线稀疏选择 | E-A08，E-L01 | 更广泛真实输入覆盖、非目标副作用、硬件难以替代的软件限制 |
| P08 训练梯度生命周期 | E-A09/A10/A11/A12/A13 | 先闭合B0数值重复性，再谈多样输入容量/长期训练与可推广性 |
| P09 数值语义和执行自由度 | E-C09，E-A12/A13 | 精度约束成因、对任务质量的真实要求以及不同合法实现成本 |
| P10 动态图准备 | E-A07/A14，E-L04 | 真实模型/几何、合法重建事件、必要导数阶和完整能量/力时间 |
| P11 KV/异构层次 | E-C13，E-L05 | 明确平台与请求分布、合法自然KV驻留/迁移及SLO指标 |
| P12 并发Serving | E-C08，E-L01/L02 | 真实到达、资源争用强基线和符合目标的SLO/吞吐实验 |
| P13 资源扩展规律 | E-A01/A02，E-C06/C10 | 先建立跨负载/资源轴的公平模型与验证，不能从单点外推 |
| P14 非LLM动态状态 | E-A14/A15/A16/A17，E-L04/L06 | 真实应用输入、强实现、训练/质量语义及最小辨识性测试 |

## 5. 关键的不一致、旧索引过时与非转移边界

1. **AWMA旧`CURRENT_STATE.md`日期为2026-09-17，不是当前执行真相。** 到2026-10-13的R27R3结果应先看最新执行commit与对应独立审查；不要用旧README顶部宣称R27刚获授权。
2. **R27R3已完成独立科学审阅。** `7bd31fa…`的两次原生B0控制在原逐元素数值合同下有25个失败位置，审阅接受`R27R3_B0_REFERENCE_NOT_REPEATABLE`有限STOP；原因仍未知，不能据此判C1/S2实现出错或回写R26的历史结论。审阅位于[`R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md`](https://github.com/swayhrl/accel-sim-framework/blob/d6e9bbfb562814bcd5dc5adb444d3c572e7f446b/docs/vm_tlb/literature_notes/awma/empirical/R27R3_B0_REFERENCE_REPEATABILITY_REVIEW_2026-10-13.md)。
3. **C16与AWMA历史材料有“时间顺序”差异。** AWMA Round22旧账本曾把C16量化转换的“局部净时间未测”列为缺口；随后C16正式做了转换原生隔离oracle，报告0.8262×。引用该问题时以**后来的对应专题终态**为准，而不篡改旧账本。
4. **AWMA Pre-L1和C16静态VA不是同一种证据。** 前者有指定simulator内部服务抑制与正确性，后者只有特定选定地址行为；不能合并成“AI全模型TLB受阻”。
5. **局部正面与完整应用是两个层次。** R23G在线head、R25目标区域显存、R26 batch可行性、C16 MP02 Mode A/B，均不能未经测量升级为整模型速度、生产环境或者硬件效益。
6. **硬件问题并不自动从软件正结果诞生。** GROUP_M16、CCE、R19 FP8、R23G online、R25 compact gradient与Kitsune/VTC等已有能力都是未来strong baseline，应主动防止“软件能做”被改名为“硬件新发明”。
7. **模拟器能量、服务次数、cycles与实机GPU时间分开。** Pre-L1中的130→10服务次数与0 cycles改善是一组同等重要的事实；当模拟器模型失配时，只能给出适用范围内的机制结论。
8. **训练的数学与数值不能靠推理正确性验收。** 短期token一致与逐梯度/优化器状态一致是不同合同；长期收敛/任务质量又是另一层。

## 6. 新研究的证据入库最小模板

```text
problem_id:
source_id + exact_commit_or_paper_version:
evidence_kind: [N/S/R/C/L/P]
workload/model + revision:
train_or_inference + phase:
GPU/deployment + backend + precision:
input/realness + dynamic context:
controlled_variable + comparison:
primary_metric + denominator + timing_boundary:
correctness/numeric contract:
observed outcome + variability:
strong software nearest neighbor:
local headroom / scope headroom (or UNKNOWN):
non-target effect (or UNKNOWN):
accepted/diagnostic/proposed status:
claim boundary and stop rule:
independent validation identity:
raw Git/164 path + SHA receipt:
```

工作流程：**发现新论文或实验→先查图谱中的问题ID→查本索引是否已有直接负例/强软件能力→只增加真正的新变量/新证据→独立审查后提高科学状态**。不得用论文作者数字替代我们自己的原生结果，也不得因两个项目进入同一总主线就重跑冻结的旧实验。

## 7. 当前资源/授权备注（非运行状态监控）

- C16：Stage A与原Reset已闭合，没有新原生执行授权。
- AWMA：R27R3已由原项目独立审阅并接受参考重复性STOP；协调分支仅同步E-A13，**没有新AWMA GPU合同**，不触碰已关闭的109任务。
- 109/RTX4080：共享`/data/c16/locks/c16_gpu_campaign.lock`，涉及CUDA/JIT的活动保持独占；174-new只在具体任务需要时做CPU/模拟分析；164保留large raw与模型权重authorities。
- 总主线合并仅意味着研究规划和索引统一；**没有任何实验合同、holdout资格、scientific authority或论文结论被重新授权或追溯修改**。

**V1小范围维护记录（2026-10-13）：**仅将原先标作待独立审阅的R27R3 E-A13更新为已接受的有限B0-reference-repeatability STOP，并更新当前authority指针。建立V1时的原始状态仍保存在协调分支commit `d0a8a83329ae1094b41048c3d06820170dc42484`；没有改写其它科学结论。