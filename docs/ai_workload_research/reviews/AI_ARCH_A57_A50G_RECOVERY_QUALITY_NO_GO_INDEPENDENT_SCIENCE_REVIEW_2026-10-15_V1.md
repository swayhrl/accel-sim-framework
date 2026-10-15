# Round A57｜A50G恢复执行质量门NO-GO：独立审查、逐查询复算与科研方向裁决

**作者：ChatGPT／AI-ARCH Discovery；2026-10-15。协调基点 `2bfe48907777a45c0561d392958d556dd260bd98`。**

## 0. 总裁决

**`ACCEPT_A50G_RECOVERY_G0_G1_NATIVE_PASS / ACCEPT_FIXED_QUALITY_NO_GO / FORMAL_PERFORMANCE_NOT_RUN / PARK_QA_AT_FIXED_QUALITY`。**

A50G恢复实验是真实native，并不是旧A50G wrapper STOP重复报告。它经过一次新的完整GloVe构图，确实对同一serialized CAGRA index做save/reload和完整查询/数值验证，在原始2000-query calibration下六项固定参数全低于预冻结`recall@10>=0.95`。实际`B1 AUTO=0.9117`、`B1 SMALL h9/h11=0.8178`、`B256 AUTO=0.8178`、`B256 SMALL h9/h11=0.8178`。无合法公共h，四正式点`NOT_RUN`、`0`个性能样本；**没有AUTO/SMALL时间差和硬件headroom结论**。

这是**固定索引+固定查询+固定软件参数下的质量门**，不是“cuVS不支持0.95召回”“ANNS没有新硬件机会”或“GPU没有性能瓶颈”的全局结论。可以接受`QUALITY_NO_GO`为合法STOP且不以临时调低阈值、额外hash/iteration scan补救本轮性能比较。执行者原样保留失败及原始NPZ。

## 1. Git身份、分支澄清、回执

- **真正发布分支**：`hrl/aiarch-a50g-glove100-default-native-full-109-v1`，最终commit **`995f557c569e7d6ef3fbdbec87481e664993291f`**，Git-data tree **`38d83cace03c4f7d214754fe2fcc90afbf976ce3`**，报告blob **`b0cfb7e7e7d1fb752077cc105ac5261c5b2be53f`**。
- 历史A50G旧STOP `d74ba0225516e60aa1c18b7ee87c88abfc34e0c9` → 本终态branch **ahead2/behind0**，新工作仅独立 `.../AI_ARCH_A50G_GLOVE100_CAGRA_DEFAULT_FULL_109_RECOVERY_V1/` 证据及`tools/aiarch_a50g_recovery/`。当前branchHEAD与最终commit一致。报告称最新直接执行授权为独立用户对Codex的“那你改正。然后接着做”，按执行回执记录一次新增完整构图；**本ChatGPT窗口未接入该Codex会话，只能核Git和报告，不能独立核那段指令所在对话**。
- **另一个未执行branch**：此前本协调窗口准备过`hrl/aiarch-a50gr1-glove100-checkpointed-native-109-v1`，经比较HEAD仍等于Goal准备提交 `d96432bb3adb995827c46dfb62e99a4544246ed4`。它**不是本次执行分支**；既然真实恢复已做并QUALITY_NO_GO，这份旧A50GR1启动提案应记`SUPERSEDED_DO_NOT_START`，不重复送109，防止第三次构图。
- [固定完整原始报告](https://github.com/swayhrl/accel-sim-framework/blob/995f557c569e7d6ef3fbdbec87481e664993291f/docs/ai_workload_research/runs/AI_ARCH_A50G_GLOVE100_CAGRA_DEFAULT_FULL_109_RECOVERY_V1/FINAL_REPORT.md)；[GATES](https://github.com/swayhrl/accel-sim-framework/blob/995f557c569e7d6ef3fbdbec87481e664993291f/docs/ai_workload_research/runs/AI_ARCH_A50G_GLOVE100_CAGRA_DEFAULT_FULL_109_RECOVERY_V1/GATES.json)；[固定校准JSON](https://github.com/swayhrl/accel-sim-framework/blob/995f557c569e7d6ef3fbdbec87481e664993291f/docs/ai_workload_research/runs/AI_ARCH_A50G_GLOVE100_CAGRA_DEFAULT_FULL_109_RECOVERY_V1/raw/calibration.json)；[CPU二次复核](https://github.com/swayhrl/accel-sim-framework/blob/995f557c569e7d6ef3fbdbec87481e664993291f/docs/ai_workload_research/runs/AI_ARCH_A50G_GLOVE100_CAGRA_DEFAULT_FULL_109_RECOVERY_V1/raw/independent_cpu_verification.json)。
- 原执行者称所有新文件SHA/工作区clean/旧资产未变/共享锁已释放，本窗口在Git层核final树、blob与原始元数据；**无现场SSH/进程/GPU采样复测**。

## 2. 本次证据等级与来源

| 门 | 原native证据 | 科学接受范围 |
|---|---|---|
| G0 | 原作者完整GloVe HDF5 `485413888B`、SHA `544af1d5e84e112cd4749571dcfd8ca109818a572f850af75a3a09e093a953c4`，全base `1183514×100 FP32`、原2000/8000 split、固定cuda/cuVS 26.10/default resources | **PASS：输入、版本与资源身份**；不能从metadata推断模型性能 |
| G1 native index | 新一次构图、五字段PASS、立即save `776387032B` SHA `205aa012e08ef9fa28b9b1a82126aab7396fcd33d02e64fe552c219ff2efc65c`、load到预建Index与owning Dataset、前后搜索ID和distance**字节一致** | **PASS：原生索引保存/重载与返回结果一致**；logical graph逐边hash UNKNOWN |
| G1 numerical | 返回ID在base范围且无重复；对返回IDs基于FP64完整数据复算距离误差max约`2.061e-7`，32-query完整base CPU GT-threshold一致 | **PASS：距离数值与输入GT身份**，**不等于approximate Top-k召回质量已足够** |
| G2 quality | 同样2000条calibration query，六组固定设置、tie-aware threshold`GT kth10+0.001`、原`>=.95`及同B`<=.005` | **FAIL/QUALITY_NO_GO**，没有合法h，h-selection/report质量不再执行 |
| G3 performance | 所有B1/B256×AUTO/SMALL正式点 `NOT_RUN`，无计时samples | 无性能或硬件因果证据；不能对比性能值 |

**资源接受**：新增恢复持锁11.853784秒，前次3.959299秒，累计15.813083秒；RSS采样峰`2833670144B≈2.639GiB`，VRAM采样峰1600MiB，新盘总`795963392B≈0.741GiB`（含776387032B index），下载/安装0，旧资源账未重置。实际峰值仍可能漏采样；未看到越界证据。

## 3. 本窗口新增**独立逐查询复算**：B1 AUTO优势广泛，而非少数单点

本窗口**直接读取**本次固定`raw/calibration.json`中两个2000-query配置的`query_ids`和`per_query_hits`，验证各2000 query ID在相同位置一致；每条命中数差`delta=hits_B1_AUTO-hits_B1_SMALL_h9`重新累计：

| 2000校准query分类 | 条数 |
|---|---:|
| B1 AUTO命中更多 | **728** |
| B1 SMALL h9命中更多 | **4** |
| 命中一样 | **1268** |
| B1 AUTO净多的Top10合法命中 | **1878** / 20,000个可能命中 |
| B1 AUTO vs SMALL 0/10查询 | **1 vs 37** |
| B1 AUTO vs SMALL 10/10查询 | **1358 vs 1117** |

总净质量提高 **0.0939 = 9.39个百分点**，与reported 0.9117−0.8178完全闭合；B1 AUTO另外多了1886个正向命中，SMALL少数查询有8个反向更好命中。该统计是**同一已测数据的独立聚合**，不是新native或GPU样本。此处只据逐查询hit count分类，**不能仅由相同hit数判断两个结果的邻居ID集合是否完全一致**；但固定报告提供五单CTA路的neighbor/distance**SHA完全一致**，支持这五路返回的矩阵字节一致。

单查询AUTO更高recall并不足以证明多CTA硬件并发或Cache机制价值，因为一切涉及执行算法/候选保留/中间topk合并等**软件工作量**也同时不同；我们甚至没有合法同质量time。

## 4. 源码解释强弱分级：AUTO与SMALL不是同算法单变量资源实验

独立直接读取官方`NVIDIA/cuvs@24ee1bf1cb17cad0ac611e39643af39ee1870124`：

- `cpp/src/neighbors/detail/cagra/search_plan.cuh` blob `da42f637dcd6fd1b299c425d353c77b3f1fe2f85`：若非persistent且AUTO，满足`itopk_size<=512 && max_queries>=num_sm*2`时选SINGLE_CTA，否则MULTI_CTA。已观察RTX4080 76SM，对B1，`1<152`→MULTI_CTA；对B256，`256>=152`→SINGLE_CTA。**这是固定源码加实际配置推导(`SOURCE_DERIVED`)，没有设备kernel轨迹，不可写`DEVICE_OBSERVED`。**
- `cpp/src/neighbors/detail/cagra/search_multi_cta.cuh` blob `8a0ccbf69f25e57f3d6173358019cea142e291e4`：`itopk128`会被拆成每CTA内部32、`ceil(128/32)=4 CTAs/query`等不同的intermediate候选合并语义；`search_single_cta.cuh` blob `8fd50a15496df3172aa4ed383b025a74f2d9301c`使用不同局部状态。这说明AUTO B1 vs强制SMALL**同时改变候选并行组织和hash搜索历史**，并非“硬件SMEM容量只有一个变量”。
- 在预冻结`hashmap_min_bitlen=9/11`不同而5条single CTA/批量AUTO输出完全同SHA时，合理结论是**这些具体bitlen设置并未在该冻结数据集上改变返回结果**。不能反推出hash容量从来不影响performance、或执行路径在硬件上逐指令完全一致。

**直观误读必须禁止**：若在B1强制SMALL比AUTO更快（这次根本未计时），它也不能与AUTO质量0.9117直接组成同质量性能比较；B256 AUTO与SMALL目前质量同为0.8178但低于共同科学门，不允许单独把这一组作为合法正式性能点。不能通过事后将recall质量门降到0.80/0.90“挽救”本轮四点，也不应在当前STOP结果下自动增加max_iterations/itopk/search_width/图degree等新的科学搜索坐标。

## 5. 研究裁决与最小下一步

**本轮无需再叫109做同一CPU verifier**：它已经对10组实际NPZ的query IDs/FP64距离、tie recall、strict recall、SHA、保存前后搜索ID/距进行单独重算，且本窗口对2000条逐查询质量差又做了独立统计。新开一次相同`CPU_RECHECK`只会增加轮次，不增加科学认识。

因此：
- **Q-A当前固定质量合同：`PARKED_QUALITY_NOT_QUALIFIED`**。保留唯一index和完整NPZ、先停止追加GPU、NCU/NSYS/trace/模拟器。未来若仍想研究CAGRA，就应从**软件算法质量前沿**重新提出明确独立的质量优先合同：冻结质量阈值仍>=0.95，通过合法算法/工作预算单独选优后再做独立report holdout。该任务将改变已停止合同的调参轴，须重新说明独立投资、强软件对照和holdout，不能自称原四点补测。仅在Q-A比其它真实神经网络问题更有独立价值时才考虑。
- **优先新领域真实AI-ARCH Discovery**：延用[A51–A55联合发现](../literature/AI_ARCH_A51_A55_CROSS_DOMAIN_AI_WORKLOAD_DISCOVERY_2026-10-15_V1.md)，下一个一个CPU/source-only联合准入任务重点查看VLA真实模型/合法输入/多请求GPU共执行能力及GNN GraphBolt原训练供数路径。不要因为VLA存在一个单线程REP服务端便声称其有真实跨请求GPU scheduler瓶颈。
- **没有GPU重新授权**：A50G恢复结束后旧已准备的A50GR1 Goal已经不该送给109；即使它在Git独立branch上的HEAD没变，也绝不能把“Goal就绪”当新有效待执行许可。
- **正式论文需求**：本结果目前提供“算法/服务质量与运行配置耦合”的负面发现，离新硬件机制、仿真归因、性能评价仍远；如外部报告，应明确Native real index vs source-derived planner vs未测时间三个证据等级。

**本审查只读、无SSH/运行；历史A50G/GloVe结果及其具体停止合同不改写。**