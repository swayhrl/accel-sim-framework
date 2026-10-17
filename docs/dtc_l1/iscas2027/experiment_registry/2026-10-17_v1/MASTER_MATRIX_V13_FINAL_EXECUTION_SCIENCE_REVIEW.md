# DTC-L1 / ISCAS2027 实验台账V13：全部合法执行收口后的科学审查

日期：2026-10-17。性质：独立ChatGPT科学审核与论文收敛意见；**不修改**Lane A/B/C/D分支、运行环境、结果或冻结定义；不建立新Goal，也不授权新仿真。以前V1–V12均保留。

## 1. 证据与验收

- Lane A原174最终执行分支：`hrl/iscas2027-dtc-service-closure-174-v1`，GitHub实际HEAD `f5c37d6edcce832a72cb0830021bffa78df6cc13`（独立核对分支，HEAD与用户提供的完整SHA一致）。最终包 `docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/final_closure_v1/`，终末检查点 `checkpoint_20261016T2133Z/`。
- 原始44注册行严格结果：**41 PASS_CHECKED_SCOPE，0 RUNNING，3 original Hotspot admission HOLD**。原12个负载保留，11个合法原输入TRAD96/IO256/OO128主三臂数值完整，第12个原Hotspot不具完整合法三臂。保持 `GM12 NONE`；不算替代GM11、不从图中消失被HOLD的负载。
- 完整合法派生输入：Hotspot V2五臂strict/resource PASS，bundle `dd0da35f5a3e3a2467a1cd23a53ce3966cd7eb6ee31035733e26f48dc532c169`；Btree条件E-list六臂strict/resource PASS，bundle `6e59d31e018befcdd8d9244e6c90d09ab8dd51c665c77785857b690f051ed585`。都为独立lineage，不替代原44行、不解除capture/native适用性HOLD。
- `FINAL_INTEGRITY_AUDIT_V1.json`为 `PASS_FINAL_EVIDENCE_INTEGRITY_WITH_SCIENTIFIC_HOLDS_UNCHANGED`：核41条强严格证据、24条复用canonical、36条历史收据/raw身份、全部11派生attempt、109的285个payload/15 native case、既有有限服务测试与默认OFF检查。 `ORIGINAL_INPUT_REVALIDATION.json`核629个原文件当前9,162,136,500字节及原完整body关联。以上是GitHub所报独立审计的范围；本会话并未SSH直接遍读174 raw数据。
- `AUTHORITY_NATURAL_TERMINATION_V2.json`记录原唯一scoped coordinator自然exit0、无自产simulator、41PASS+3held、其原lock/authority保留。用户另报告最后non-force push、fetch-back HEAD/tree与worktree clean；GitHub HEAD已核一致；外部 `FETCH_BACK_LATEST.json` 不在Git，不能称本会话直接读过外部收据。`FINAL_VALIDATION.json`当时把F1标为`ACTIVE_FINAL_PUBLICATION_REQUIRED`，这是最后push之前阶段状态，不能据此推断仍有simulator正在跑。
- 旧有限模型及派生修正失败记录不擦除；技术结果不是native GPU、等面积或全ISA验证。正文不要移植历史FAST64 1.326×/1.592×，也不要移植原博士论文4.7%为当前面积。

## 2. 最终原输入完整数值：相对增强传统C+

定义相同原输入`S(DTC,C+) = cycles(TRAD96)/cycles(DTC)`，每一行同一完整kernel ROI。数值比值保留回退；仅11合法原三臂，不作任何几何平均。

| workload | C+ cycles | IO256 cycles | OO128 cycles | C+/IO | C+/OO | Input scientific scope |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| ATAX | 30,981,690 | 83,797,212 | 50,796,515 | 0.370 | 0.610 | FROZEN_DECODED_INPUT_SCOPE_ONLY |
| BICG | 25,353,488 | 93,312,525 | 47,533,116 | 0.272 | 0.533 | 同上 |
| GESUMMV | 99,700,244 | 193,506,220 | 142,770,419 | 0.515 | 0.698 | 同上 |
| GEMM | 1,511,333 | 1,457,468 | 1,377,919 | 1.037 | 1.097 | 同上 |
| DWT2D | 247,588 | 241,794 | 237,887 | 1.024 | 1.041 | 同上 |
| Gaussian | 3,379,152 | 3,799,499 | 3,798,174 | 0.889 | 0.890 | 同上 |
| MRI-Q | 362,244 | 361,574 | 361,439 | 1.002 | 1.002 | 同上（很小差别） |
| NN | 6,087 | 6,132 | 6,132 | 0.993 | 0.993 | 同上，NN不是神经网络 |
| Btree | 186,621 | 247,940 | 173,210 | 0.753 | 1.077 | FORMAT_APPLICABILITY_REVIEW_PENDING |
| 2DConvolution | 1,559,265 | 626,642 | 592,346 | 2.488 | 2.632 | FORMAT_APPLICABILITY_REVIEW_PENDING |
| LUD | 1,072,561 | 1,091,956 | 1,086,574 | 0.982 | 0.987 | FORMAT_APPLICABILITY_REVIEW_PENDING |

**裁决：** 当前数据可支持具体负载/预算/服务合同下的结构取舍，却**不支持**无条件的性能优势。对来源未额外报上述格式风险的8个原输入，GEMM与DWT2D有相对C+的小幅优势，MRI-Q基本持平；ATAX/BICG/GESUMMV严重回退，Gaussian/NN也回退。最大正收益2DConvolution有未解决的生产格式歧义，不能作为已经证实的native应用收益。不通过剔除负载或重新选择baseline得到更好平均。

## 3. 两组独立派生输入结果

**Btree条件E-list、相同新bundle/cap32768：**

| arm | cycles |
| --- | ---: |
| B16-N | 430,680 |
| TC80-N | 351,430 |
| C+ | 188,570 |
| IO256 | 250,523 |
| OO128 | 175,133 |
| IO128 | 250,523 |

C+/IO = 0.752705；C+/OO = 1.076725。原冻结解码的**相同cap32768** C+186621/IO247940/OO173210/IO128 247940；两种定义的角色排序均 `OO128 < C+ < IO128 = IO256`（cycles越小越好）。这说明已审**两种具体解释间的相对排序有限稳定**，不证明历史capture producer/ELF/native equivalence。原B16/C80 cap8192，不能把它们与新cap32768臂跨输入比较归因于地址。更不能拿新C+除旧OO来计算加速比。

**Hotspot V2、另一独立新bundle/cap32768：** C16 152914、C80 107774、C+82873、IO256 85718、OO128 84456；C+仍优于IO/OO，而两种DTC优于小传统。原Hotspot三个禁止launch与原两条strict numeric仍保留；不插回原44。

## 4. 机制、成本和边界

- **BICG同128深度**：IO128 93,312,525 / OO128 47,533,116；两者同真实有限Core、完整输入、128 PIB、640物理行，退休均2,097,152条可缓存warp指令、收集均19,922,944个32B sectors。ready-to-complete均值IO3560.700145、OO3.926686 cycles/可缓存warp指令；64SM含尾部与空闲周期的PIB平均4.98/2.23。这个证据支持完成策略对等待及状态寿命的重要影响，不能声称两者同总面积或严格因果百分比分解。OO仍比C+慢。
- **BICG传统WAIT128控制**：16KiB常规L1、32 MSHR不变；PIB-full事件8804793→0但周期79,721,847→84,049,733（约5.43%回退）。这反对“仅扩大PIB必然提速”的单一结构解释。非绑定cap和inactive preference的差异按正式收据限定。
- **Btree派生同128深度**：IO128 250,523 / OO128 175,133；fully-ready-to-complete 169.435000 / 10.295819；本结果仅为有来源约束的派生定义，额外metadata/area未知。
- **GESUMMV最终服务验证**：TRAD96 99,700,244，IO 193,506,220，OO 142,770,419 cycles；最后IO自然exit0、190,918,656 active-thread指令、30 strict/31 supplementary checks。2,048 retained clean physical lines是符合合同的驻留状态，并非漏排空；509,134次合法Tag替换后重新分配是机制成本，不是响应identity出错。IO与OO 256/128深度，不是单因素ordering ablation。
- 64SM服务模型的lookup/allocate/lower/inject/refill/collect/retire配额、response ownership和反压已显式建立，均为**前置有限模型假设**，并非RTX4080真实硬件端口测量。DTC真实数据=80KiB physical+16KiB ordinary side=96KiB，逻辑16KiB Tag仅覆盖非额外数据；C+亦96KiB数据但等待结构/控制/元数据并非等面积。现无完整五设计RTL/DC/SRAM宏/频率结论。
- 现代DTC容量/端口HOLD；旧SASS现代baseline-only只能叫模型反事实。SpMV、LayerNorm仅109native已验，DTC simulator NOT_ADMITTED。LUD/2D旧地址歧义仍未闭合，2D有界调查STOP；没有任何自动重启科学授权。

## 5. 论文收敛建议（不自动追加仿真）

**审稿结论：EXECUTION_CLOSED_WITH_HOLDS；SCIENCE_CONDITIONAL；PUBLICATION_NOT_YET_READY。**

1. Results Fig：原12输入名称均可见；11原主三臂的可合法数值独立绘出，并对Btree/2D/LUD明显标注source format pending；原Hotspot标HOLD，不绘不存在的C+；禁止总体GM或派生输入混入。数值、来源状态和C+/DTC性能回退必须同时可见。若技术页容不下，可将论文主表明确限定有效域并把条件样例单独说明，但任何排除、重命名集合必须经用户科学决定，且不得暗示它是原12均值。
2. Conditional sensitivity：一个简短Btree新旧同cap角色排序对照；Hotspot V2以有来源限定的独立例子给出C+略快，可合并为图注/短段；不拿条件模拟当native验证。
3. Mechanism：优先BICG matched128与WAIT128控制；强调OO减少fully-ready等待但仍低于C+，不能把buffer事件数写成stall周期比例；2D matched结果只有机械意义/格式HOLD。
4. Hardware与timing：本轮主要**缺口**。等待用户的对应当前资源向量和服务假设的RTL/DC/存储宏/时序材料，包括C16/C80/C+/IO/OO各个端口成本、PIB/状态/重命名/collector/旁路计价。Area、Fmax/WNS、宏面积须同工艺/时钟/端口合同。不能沿用原博士旧4.7%、也不能未经综合声称等面积/低功耗。若不能交付，论文主张须退为有限服务架构建模与条件性能取舍，不得伪称完成硬件评估。
5. 摘要和结论在实际证据/成本闭合后最后改写；不将“平均MLP提升/现代GPU收益/性能普遍改善”写为当前测得事实。架构方法仍可讲分离Tag查找可见性和物理数据引用寿命，以及顺序/显式引用两种实现，但它们源于原学位论文第4章，必须恰当注明来源。
6. 当前英文稿仍指定 `DTC_ISCAS2027_LATEX_V0_7_STYLE_SOURCE.zip`；本次对话没有取得该实际压缩包及主PDF，不假称已经直接修改或编译LaTeX。

## 6. 下一决策

执行已收口，**不继续计算/补发仿真**。当前真正需要用户提供或审定的是：（i）硬件RTL/DC/宏面积与时序数据，（ii）论文主图中条件Btree/2D/LUD与原Hotspot的公开表达和结论边界，（iii）最新英文LaTeX源包用于正式合稿。能写的输入方法、机制及Results负例无需等硬件完成即可先整理，但不得填造PPA或GM。

关键固定入口：
- [Lane A最终证据](https://github.com/swayhrl/accel-sim-framework/tree/f5c37d6edcce832a72cb0830021bffa78df6cc13/docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/final_closure_v1)
- [最后完整检查点](https://github.com/swayhrl/accel-sim-framework/tree/f5c37d6edcce832a72cb0830021bffa78df6cc13/docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/checkpoint_20261016T2133Z)
- [Btree派生完成](https://github.com/swayhrl/accel-sim-framework/tree/f5c37d6edcce832a72cb0830021bffa78df6cc13/docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/btree_derived_complete_v1)
- [Hotspot V2完成](https://github.com/swayhrl/accel-sim-framework/tree/f5c37d6edcce832a72cb0830021bffa78df6cc13/docs/dtc_l1/iscas2027/service_closure_174_v1/review_pack/hotspot_derived_complete_v1)
