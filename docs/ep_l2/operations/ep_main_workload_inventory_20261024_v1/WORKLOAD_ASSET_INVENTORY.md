> 后续范围扩展（2026-10-24）：本页保留18组历史已命名输入的时点记录；双账户完整目录核查已找到更多候选，且今天新增的真164输入映射改变了native资产准备状态。当前账户资产以[严格核查报告](../ep_main_account_workload_audit_20261024_v2/ACCOUNT_WORKLOAD_AUDIT.md)为准，科学接受状态不自动改变。

# EP-L2 workload资产清点（2026-10-24）

本轮为只读资产盘点。18个精确输入变体、14个benchmark程序、4个suite；不以kernel数、S/F、不同binary或输入尺寸重复计算独立workload。没有启动模拟、native测试、编译、搬运trace或修改科研账本。

已对原174的18份精确commandlist/相邻run.sh作小文件读取，对159个commandlist指定trace文件及175个已知结果/控制路径作stat。18组输入的159个body当前都存在且可读，逻辑总量26,880,893,839B（约25.03GiB）。这不是新完整body内容校验或NAS物理占用证明。除当前exact ensure可核的Vector/GEMM外，没有搜索全NAS或声称其它资产已迁入174-new。

## 已跑过与可准备程度

“原57”指20261019机制研究的57次实际启动；不与145条混合canonical记录相加。该57中44个执行行COMPLETE_VALID、8FAILED、3RESOURCE_LIMIT、2INCOMPLETE；44个接受结果索引/25对，包含另列的补充接受，原失败行保留。MAIN6/7及独立SGEMM探索1项的分组不变。

| 精确输入 | suite | kernel启动数 | trace body GiB | 旧B0索引 | 原57实际启动 | 原57接受结果索引 | 当前准备状态 |
|---|---|---:|---:|---|---:|---:|---|
| convolutionSeparable | CUDA SDK/Samples | 2 | 6.375 | 有历史Legacy引用 | 18 | 13 | 旧EP接受；待物化/原生资格 |
| FWT_11_19 | CUDA SDK/Samples | 16 | 0.387 | 有历史Legacy引用 | 0 | 0 | 仅旧B0；需新资格 |
| FWT_7_21 | CUDA SDK/Samples | 19 | 1.663 | 有历史Legacy引用 | 4 | 2 | 旧EP接受；待物化/原生资格 |
| scan | CUDA SDK/Samples | 33 | 4.963 | 有历史Legacy引用 | 0 | 0 | HOLD |
| vectorAdd_4M | CUDA SDK/Samples | 1 | 0.096 | 有历史Legacy引用 | 9 | 5 | EP原生已验证 |
| sad | Parboil | 3 | 0.208 | 有历史Legacy引用 | 4 | 4 | 旧EP接受；待物化/原生资格 |
| sgemm | Parboil | 1 | 2.064 | 有历史Legacy引用 | 3 | 3 | 旧EP接受；待物化/原生资格 |
| spmv | Parboil | 1 | 0.032 | 有历史Legacy引用 | 0 | 0 | HOLD |
| 3mm | PolyBench/GPU | 3 | 2.718 | 有历史Legacy引用 | 0 | 0 | 仅旧B0；需新资格 |
| gemm | PolyBench/GPU | 1 | 1.034 | 有历史Legacy引用 | 0 | 0 | 共享输入就位；缺EP资格 |
| BFS_graph1MW_6 | Rodinia3.1 | 24 | 2.696 | 未见 | 0 | 0 | 候选；资格未闭合 |
| BFS_graph4096 | Rodinia3.1 | 16 | 0.011 | 未见 | 0 | 0 | 候选；资格未闭合 |
| BFS_graph65536 | Rodinia3.1 | 20 | 0.175 | 未见 | 0 | 0 | 候选；资格未闭合 |
| btree | Rodinia3.1 | 2 | 0.754 | 有历史Legacy引用 | 0 | 0 | HOLD |
| cfd_097k | Rodinia3.1 | 5 | 0.253 | 有历史Legacy引用 | 8 | 8 | 旧EP接受；待物化/原生资格 |
| dwt2d | Rodinia3.1 | 10 | 0.394 | 有历史Legacy引用 | 11 | 9 | 旧EP接受；待物化/原生资格 |
| Hotspot_1024_2_2 | Rodinia3.1 | 1 | 0.970 | 未见 | 0 | 0 | 候选；资格未闭合 |
| Hotspot_512_2_2 | Rodinia3.1 | 1 | 0.242 | 未见 | 0 | 0 | 候选；资格未闭合 |

旧B0索引记录了精确输入、Legacy cycles和旧Framework/Core；不代表当前B16/main61/r5资格。两处历史final26 closeout Git路径未找到，故本清点不重新宣布26/26接受。更早C5c 22/26及银行归因HOLD不能升级为当前正式结果。

## “可以跑”的四层含义

1. **输入存在**：本轮18个已知输入都通过原174文件级元数据存在/可读检查；不等于内容语义或当前runtime兼容。
2. **具备历史EP接受基础**：Conv、CFD、DWT、SAD、FWT_7_21、Vector的main61主结果与SGEMM独立探索；精确source/config/input/资格各自固定，不跨谱系继承。
3. **当前174-new输入已就位**：EP_VECTORADD_S；以及同一GEMM输入的共享DTC_AD_GEMM真164映射。Vector有main61 S迁移与r5 F的原生接受证据；GEMM共享输入尚不构成EP资格。
4. **可获准启动**：当前EP没有未消费cohort预算。盘点不授予启动或迁移权；每次仍须新精确规格、当前native资格、资源/空间和明确预算。

因此，Vector是当前EP原生已证明的输入；GEMM可先复用共享输入身份。Conv/CFD/DWT/SAD/FWT/SGEMM有历史科学基础，但其输入还需精确物化及本轮native规格。其余不能仅因文件存在而列为ready。

## 明确保留的HOLD与准备缺口

- **Btree mil.txt**：非零active-mask/full32地址解释与native popcount消费存在语义冲突，原input_scope_HOLD未解除。
- **SpMV Dubcova3**：IADD3指令记录缺一个源寄存器；旧B0 cycles、文件小或descriptor压力均不替代当前完整输入资格，不能静默补trace。
- **Scan NO_ARGS**：shared/nonmemory扩展地址尾格式不支持；33次kernel启动、约5.33GB body，当前仍HOLD。
- **BFS graph65536 / graph4096 / graph1MW_6**：已有确切trace元数据。graph65536有20个kernel的F包与C的host边界准备交付；完整body/指令/原子域/host更新与alias及runtime资格尚未闭合。不能继续说C未交准备包，也不能把交付当作资格。
- **Hotspot512_2_2 / 1024_2_2**：当前都是1个kernel的输入，仅为结构网格候选，不能称为已覆盖跨kernel迭代复用。
- **3mm、FWT_11_19**：有旧基线输入/历史结果索引，缺当前EP输入/profile/runtime资格。
- **GEMM**：数据在真164可共享复用；不能把DTC的L1科学接受借给EP-L2。
- **stencil/histo/histogram及新ML/WMMA发布**：只是旧调研中的方向，无本次确切EP输入选择和资格，未计入18个资产。

## “真实吗”与平台边界

这些资产来自CUDA SDK、Rodinia、Parboil、PolyBench/GPU的经典样例/科学计算基准。Vector/Scan/Conv/FWT属于CUDA样例，PolyBench偏参数化kernel微基准；Rodinia/Parboil提供应用领域背景，但冻结trace不自动证明生产端到端代表性。

每个输入的capture run.sh字面内容、文件SHA和完整commandlist保存在JSON；CUDA目录名、visible device编号或SM70 header都不是准确采集GPU/driver/toolchain证明。原capture精确源码revision和数值payload/输出的缺口保留UNKNOWN；本轮没有重新采集或数值验证。

模拟目标是Volta派生H0研究配置，不能称RTX4080实验。Tag几何16way来自研究overlay，与采集GPU及当前执行主机分开。当前已准入资产中没有现代AI完整应用。

## 数据与结果去向

- 原18组trace位于JSON列出的原174精确路径；当前确认存在/可读，不做body重hash或搬运。
- 原57点的result dir/raw/接受控制引用，本轮175个精确路径全存在；只是stat，不重新接受旧结果。
- E057完整结果和本轮Vector r5结果已有真164归档及native恢复入口，见JSON对应字段/上一轮RECOVERY_POINTER。其它旧结果不能一概宣称已完整归档。
- 新原生迁移EP Q1停、Q2接受另记2次；本轮Vector r5科研1次另记，help资格另列，不回填原57。
- 所有源KEEP，释放0B。DTC其它工作负载、C16/AWMA等其它项目不纳入本次EP清单。

机器可读主表为WORKLOAD_ASSET_INVENTORY.json；完整历史索引见HISTORICAL_RUN_INDEX.json，46份历史资格的精确profile/source指针见RUNTIME_PROFILE_QUALIFICATION_INDEX.json。全部原始15份证据的精确Git HEAD/blob/SHA见SOURCE_REFERENCES.json。

下一步可据此逐项选择“补资格”“精确物化”“继续HOLD”或“仅保留历史”；本轮不替用户启动任何条件。
