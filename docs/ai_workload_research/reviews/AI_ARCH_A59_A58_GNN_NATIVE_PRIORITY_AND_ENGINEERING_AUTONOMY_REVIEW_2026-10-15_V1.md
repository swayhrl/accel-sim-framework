# Round A59｜A58独立审查、GraphSAGE强软件入口与Codex工程自主权

**审查者：ChatGPT／AI-ARCH Discovery；2026-10-15。协调起点：`df909271e656bd4ff298ff082ff26b01a591df07`。** 只读GitHub固定提交、OGB/DGL/RAPIDS官方源码与发行说明；本窗口没有SSH174/109、没有下载OGB图、没有运行CUDA/模拟器。

## 0. 审查裁决与证据分级

**`ACCEPT_A58_SOURCE_ONLY_CONDITIONAL_GNN / VLA_GPU_CONCURRENCY_NOT_QUALIFIED / A59_ONE_BOUNDED_NATIVE_DISCOVERY_WITH_GATES`**

- A58固定执行branch：`hrl/aiarch-a58-vla-gnn-source-admission-174new-v1`，完成提交`9560b28ee85618a9059e309cb640c210b4575dfc`，tree`e84d94baa9751265fb90d5b37da345bd8c6a0f9a`，报告Git blob`4bf580e1f7a000633ea3ffaca91e8ab3fd4d1812`。从Goal`70f640573fc2434b39df35204dffb901f9214109` ahead1/behind0，HEAD identical、只增单一报告。报告SHA256`1bb846e859ed6d9a92f7cd7f41b3fe819a3e76148e87a98677661dc16dd88560`来自执行者；本窗口独立核Git blob，**未再单独计算该SHA256**。
- 执行者报告174-new CPU-only、单worker、无GPU/下载/安装，宿主swap满而host I/O压力较高；该数据为174回执，不是控制端SSH实时复测。完成后STOP。
- **VLA：** LeRobot已公开SmolVLA原权重与LIBERO元数据，但`lerobot/smolvla_base`和`vrfai/smolvla-libero-gguf`不是同一个checkpoint；LeRobot remote服务单会话、vla.cpp REP按请求串行，不构成真正多个独立VLM/Action在GPU上的co-execution证据。因此针对用户指定**多请求竞争**问题是`VLA_NO_GO_OR_PARTIAL`，不是整个VLA/边缘AI不值得研究。
- **GNN：** 固定DGL例程`dmlc/dgl@3d16000b4170fa741ed9e9667f22ba84d3493026/examples/graphbolt/node_classification.py`提供ogbn-products 3层GraphSAGE完整训练步，GraphBolt源码有cache/async功能，但普通例程未开启全部功能。OGB真实输入、软件二进制ABI、cache fallback数值/稳态wall仍为`NOT_QUALIFIED`。接受`SELECT_GNN_CONDITIONAL_GPU_PROBE`作为下一研究对象，而非已测硬件残余。

## 1. 本窗口新增的直接强软件源码反证

在同一固定DGL Git HEAD中另有[`examples/graphbolt/pyg/node_classification_advanced.py`](https://github.com/dmlc/dgl/blob/3d16000b4170fa741ed9e9667f22ba84d3493026/examples/graphbolt/pyg/node_classification_advanced.py)，blob`57de89011a4880842a0d939478b6b81744bf022d`。已直接读取其数据流水、训练步骤、缓存命令行与source：
- `--mode pinned-pinned-cuda`把graph/feature pin到CPU内存、GPU负责计算。
- `--gpu-cache-size`接`gb.gpu_cached_feature(...)`，该缓存有fallback；`--num-gpu-cached-edges`＋`--gpu-graph-caching-threshold`经`sample_neighbor`启GPU graph cache。
- `overlap_graph_fetch`、`overlap_feature_fetch`及异步采样覆盖流水；`train_step`包含GraphSAGE、loss、zero_grad、backward、Adam更新。
- 使用`@torch.compile`，其JIT编译及优化/数值差异与真正稳态GPU计算必须分账。

**重要限定：** 高级例程用PyG SAGEConv，而普通例程用DGL GraphSAGE；二者不能当不需核验的同算法等价速度对照。优先在**高级例程自身**内部启用完整cache+overlap与必要的cache OFF诊断，避免跨模型实现混淆；若PyG或torch.compile实际环境无法合法配置，可事前在一个经核准的官方DGL发行版内选择DGL原例程＋最小缓存接线，但不得把旧master的API可用性当目标二进制支持证明，后端一旦冻结不能为寻找正结果临时切换。

**发行与强软件现状：** DGL 2.4 CUDA GraphBolt发行需要配套CUDA wheel/PyTorch次版本；NVIDIA最后DGL容器在25.08停止支持，RAPIDS`cuGraph-DGL`已移除、后续推荐`cuGraph-PyG`。**2026年不能把历史cuGraph-DGL默认作为新的强软件配置**。选择DGL/GraphBolt只是本次受限研究，不代表覆盖所有最强图AI系统。

## 2. 真实输入与论文证据边界

[OGB官方节点分类](https://ogb.stanford.edu/docs/nodeprop/)定义`ogbn-products`：2,449,029 nodes、61,859,140无向edge、100维特征、47类别，train/val/test按照sales-rank 8%/2%/90%。[固定GraphBolt BuiltinDataset源码](https://github.com/dmlc/dgl/blob/3d16000b4170fa741ed9e9667f22ba84d3493026/python/dgl/graphbolt/impl/ondisk_dataset.py)从DGL官方图归档下载并可能加反向边，**不能把无向边数等于有向CSC数组长度**。

可计算feature FP32 payload`2449029×100×4=979611600B`；若双向弧约123.72M、int64索引则约`989746240B`，还不含indptr、模型激活、标签、cache、fallback、数据预处理/展开临时文件。**没有109 runtime memory或DGL archive metadata之前，不能保证4080 16GiB和8GiB额外磁盘足够。** 对OGB图像/标签实体权利应按官方实际数据来源和条款判断，不拿DGL源码许可自动覆盖Amazon-derived数据。找不到合法研究使用条款/authority即合法STOP。

**新的可证伪Q-G：** 在强GraphBolt graph+feature GPU cache和async/UVA overlap**真的开启且数值/采样一致**时，是否存在暴露在自然`sample→feature-ready→forward/backward/optimizer step`完整wall的等待？cache关闭组只能诊断缓存效果，不是声称竞争者的最强软件。单独分段计时的同步会破坏overlap，所以必须先拿未插桩完整训练步，再将单独诊断视为解释，并记录诊断干扰。发现资源压力不等于产生了硬件新机制。

小于完整训练收敛的`≤64自然batch×2 seeds`只可验证数值、短程训练、流水与局部端到端壁钟，**不能宣称已核全训练的验证精度或用户任务准确率**。若GPU特征命中率低且strong path仍无可测暴露等待、或收益只来自cache OFF弱控制，就`NO_HARDWARE_HEADROOM_EVIDENCE`停止。

## 3. 用户要求与新工程授权原则

用户明确：“如果不涉及大方向的问题，其实可以授权codex去自己解决，提高效率，别每次都这么反复迭代。”以后首选**一科学问题、一连续Goal**，把合法路径上的CPU源码资格、官方wheel下载/隔离安装、真实数据合法下载与解包审计、cache参数/API包装与fallback正确性、GPU数值canary、自然batch观察、资源监控、Git归档集中委托一个Codex窗口完成；不人为一门一轮索要确认。

允许Codex对**不改变已选真实工作负载/数据/训练语义/比较科学对象**的CLI/path、版本包装、GPU operator已存在API调用、manifest/cache、样本读取、轻量脚本与分析出错，在新Goal**累计CPU/GPU/网络/盘/时间硬预算**内有界solve-and-continue，并归档每次修补的diff、失败与正确性复核。小问题不设反复的一次一Goal审查关口；预算到了/原生正确性失败/真实输入不能准入应STOP。

**不得默许的变化**：原任务dataset及split/精度/feature、采样fanout/分布、3层GraphSAGE与optimizer、预先确定质量gate、training wall分母、强软件选择冻结后改变、改GPU硬件/driver/系统环境、网络/数据超额度、新模型/额外图/二次下载、实验后改参数找正结果。这些是实质科学或权限变化，Codex必须STOP并报告，不得按“工程修复”混过去。

174刚反馈swap与host I/O压力；下一个真实数据/依赖准备应交独立109新worktree，避免174和AWMA冲突。同期源文档整理可用控制端，不创建额外重量Lane。之前109的A50G质量NO-GO已STOP，新任务并行性不允许重开它。

## 4. 科研选择与下一Goal

唯一选Q-G：同一个连续、有界的109 GraphSAGE/ogbn-products原生供数实验，CPU元数据/依赖/真实图门先行，在原GPU锁上完成输入与软件数值canary及`≤256`个自然训练steps的强缓存ON与同语义OFF对照，分开未插桩完整wall与插桩诊断；身份/质量/资源不达则STOP、下门NOT_RUN。不因单纯缓存未命中或采样异步时间变化直接宣布硬件Cache/SMEM头寸。

建议数据/依赖下载和新磁盘各有**独立上限**，装依赖只在新venv；无法验证发行版GraphBolt GPU ABI时STOP，而非源码编译整套DGL/驱动升级。这是下一Goal的工程授权边界，而不是本轮已执行的GPU结果。