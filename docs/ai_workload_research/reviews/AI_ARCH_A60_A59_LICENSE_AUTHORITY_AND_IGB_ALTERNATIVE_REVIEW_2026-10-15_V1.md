# Round A60｜A59许可门双收据独立科学审查与IGB真实GNN替代入口

**审查者：ChatGPT／AI-ARCH Discovery，2026-10-15。Git协调起点`16bfafa66a1068f542b08c00eb417f218f1f611b`；本窗口只读GitHub、作者公开原文记录、固定数据发布源码及许可证。无109/174 SSH、GPU锁、CUDA、依赖安装、数据集下载和维护者外部通讯。**

## 0. 科学与数据使用裁决

- **A59原合同：`ACCEPT_DATA_LICENSE_NO_GO / G0_STOP / G1_G3_NOT_RUN`**。G0证据显示OGB官方指向的Amazon原许可`https://s3.amazonaws.com/amazon-reviews-pds/license.txt`在109及控制端均HTTP403，有限的其他官方入口不足以验证本次`ogbn-products`许可范围。**403不证明数据不存在、权利被撤销或训练违法**；但合同要求适用来源可核，因而无数据下载、训练和GPU初始化是科学正确的STOP。
- **后续单独CPU许可核查：`ACCEPT_AUTHORITY_PARTIAL_OGB_APPLICABILITY_UNRESOLVED`**。维护原STOP，不以文献“用于学术研究”替代针对派生实体的可固定许可。按独立报告，McAuley等上游[论文PDF](https://snap.stanford.edu/data/amazon/productGraph/sigir_draft.pdf)第2页明确写有`We have made this dataset available for academic use`；其正式完整PDF字节`9307397B`、SHA256`4019c64f9f8437d41321bd4018d898c956ae189198baf5edd7501b7fb29c8723`由109执行者保存并复核。**本窗口未取得论文原始PDF字节后独立重算SHA/版式，仅核报告/receipt及其来源链接**。
- [OGB #499](https://github.com/snap-stanford/ogb/issues/499)经GitHub connector再次查为**open、零评论**；2025-03-14由非维护者提`https://aws.amazon.com/asl/`作为替代建议，没有维护者确认具体`ogbn-products`适用。原followup排除可读的Amazon多语言评论数据许可（**另一数据集**），也不将Amazon Software License仅凭名字认定适用。
- 因此准确口径不是“ogbn-products从来不能用”，而是**`SOURCE_UPSTREAM_ACADEMIC_USE_POSITIVE / SPECIFIC_OGB_LICENSE_AUTHORITY_UNRESOLVED`**。不值得再为同一失效URL开第三轮CPU搜索或让109做重复原样HEAD。

## 1. Git身份和两份执行权威

| 项目 | 固定Git信息 |
|---|---|
| A59原native admission branch | `hrl/aiarch-a59-graphsage-products-bounded-native-109-v1` |
| A59原最终commit/tree | `0e52f088d21e0a88ff471cdf5ad76a7a539cf616` / `7b05f50e296df1d2e78894859e6e8642761076a2` |
| 原FINAL_REPORT blob | `509c5cf7d23800c57c5189edd92944996be60d99` |
| license CPU补充branch | `hrl/aiarch-a59-license-authority-cpu-109-v1`，**不合并回原STOP** |
| license补充commit/tree | `81db397d477222b90dee56d31cd6cf66982d627c` / `f1887f38fde6b35ec8e43fe87c252a4c215067f3` |
| 补充FINAL_REPORT blob | `311d757fe1372998697ba003072748b8736ffcc3` |
| 分支状态 | GitHub比较证实原A59及独立license分支均与上述final SHA identical；license branch从原A59final分出ahead1，20新增文件；原A59从初Goal到final额外2个commit |
| 第三方通讯 | `REVIEW_REQUEST_DRAFT.md`存在但**未发送**，本窗口也未代发 |

[原A59固定报告](https://github.com/swayhrl/accel-sim-framework/blob/0e52f088d21e0a88ff471cdf5ad76a7a539cf616/docs/ai_workload_research/runs/AI_ARCH_A59_GRAPHSAGE_PRODUCTS_NATIVE_109_V1/FINAL_REPORT.md)；[后续许可核查固定报告](https://github.com/swayhrl/accel-sim-framework/blob/81db397d477222b90dee56d31cd6cf66982d627c/docs/ai_workload_research/runs/AI_ARCH_A59_LICENSE_AUTHORITY_CPU_109_V1/FINAL_REPORT.md)；[未发送询问草稿](https://github.com/swayhrl/accel-sim-framework/blob/81db397d477222b90dee56d31cd6cf66982d627c/docs/ai_workload_research/runs/AI_ARCH_A59_LICENSE_AUTHORITY_CPU_109_V1/REVIEW_REQUEST_DRAFT.md)。

### 运行资源资格

原A59合同`G1–G3 NOT_RUN`，GPU初始化/持锁/训练均0，图数据和wheel下载0；元数据控制端/109保守计量约16.4MiB，新文件约3.33MiB。license CPU补充的HTTP/relay/保守元数据总账户约12.37MiB、新盘约22.51MiB、CPU RSS采样峰约57.44MiB、GPU=0。**这些是执行者原始receipt，不是本ChatGPT现场重测**。唯一论文数据许可身份仍未PASS。

## 2. 新独立发现：IGB数据集有**明确单独的数据授权文档**

本窗口实际读取[IllinoisGraphBenchmark/IGB-Datasets固定官方Git源码](https://github.com/IllinoisGraphBenchmark/IGB-Datasets/tree/fc36357f2c1d861870b4c13a58f73da2b93d1e73)，HEAD`fc36357f2c1d861870b4c13a58f73da2b93d1e73`：

- `LICENSE`，Git blob`931d368d8f65923bb22d8d059da3d45ab3afac1c`，**直接明确`applicable for all software codebases`，不转用作数据许可**。
- `ODC-By-1.0`，Git blob`dab29a14b77b9cd9b523e4aeaaf6fdb2aaa3624b`，直接写明**`applicable for all the data shared publicly in IllinoisGraphBenchmark (IGB) project`**，授予ODC-By-1.0数据/database权利并要求归属；**该许可自身Section2.4不覆盖每个独立内容本身可能受到的其它权利**。我们只能断定`IGB_PUBLIC_DATABASE_LICENSE_IDENTIFIED`，不能泛化为全部来源材料的权利均排除争议。若仅把作者官方发布的数值节点特征/图做本地研究、结果以统计归档、**不传播原数据**，仍应记录版权/来源说明及实际适用范围，而不是声明“完全无任何法律疑问”。
- `igb/download.py` blob`478bf8d1f24ebefa4aed43cca44ced7dd4e39210`，官方下载`igb_homogeneous_tiny.tar.gz`与`igb_homogeneous_small.tar.gz`固定Amazon S3地址，并公开MD5 `tiny:34856534da55419b316d620e2d5b21be`、`small:6781c699723529902ace0a95cafe6fe4`。目前只有**源码提供的预发布MD5/URL**，没有109实际文件SHA或HTTP header/bytes/展开安全审计。
- `igb/dataloader.py` blob`b4b6e342df4511ef99a488336b57502fff754fe4`：`small`节点`1,000,000`、feature维1024、可选`synthetic=0`真实NLP embeddings（synthetic=1会随机化，**绝不能作为真实AI负载同身份**）；作者有DGL图、labels与train/valid/test mask生成/加载逻辑。真实原生输入/边序/类别、split seed及具体loaded graph identity还没有run准入。
- [IGB论文](https://arxiv.org/abs/2302.13522)与独立的[IEEE/VLDB相关GNN系统实验表](https://www.vldb.org/pvldb/vol17/p1227-park.pdf)一致给出`IGB-tiny 100000 nodes/547416 edges`、`IGB-small 1000000/12070502 edges`；small的1024维FP32特征仅payload下界`4,096,000,000B ≈3.815GiB`，另graph约0.185GB作者论文总下界约4.1GB。tiny作者README展示压缩下载约0.36GiB、展开约0.39GiB；**small的实际压缩字节和新磁盘峰值尚未确认，不把估计当HTTP Content-Length**。
- 对GraphBolt的接入**不是天然等价**：DGL的`igb-hom-small` BuiltinDataset虽然在官方源码列表中，但它可能是再包装图，不能未经核对把其实体byte/split/方向与IGB原作者`igb_homogeneous_small`做相同数据认定。初次科学合同应选择**原IGB官方实体＋一条确定性GraphBolt转换路径**，保持作者graph/embedding/label/seed/split语义，再对强cache/async做配对；若转换实现涉及新科学采样/训练语义，应单独标明不能与原ogbn-products结果对比。

**科学价值排序**：IGB-tiny适合low-cost数据/num/GraphBolt功能canary，但图与feature较小，不能用其cache hit证明百万级exposed供数代价；IGB-small真实feature约4GB、更有机会暴露PCIe/miss成本，优先在**实际许可、归档、RAM/VRAM/disk预算门**之后作为下一单图发现对象。选择IGB是一项**新的真实科学输入变化**，不能视为A59未完成部分自动继续执行；原OGB`DATA_LICENSE_NO_GO`不被取消或覆写。

### 必须在IGB-small实验前排除的两个强软件反证

1. **完整GPU驻留可能优于pinned＋GPU Cache**：IGB-small作者发布的full FP32特征约4.096GB、graph及metadata约0.2GB，而RTX4080物理16GB、本合同计划任务显存上限12GiB。它们的**静态数据大小**可能装得下，但训练batch与multi-hop活跃节点/内存池、CUDA context可能导致真正负载OOM，不能凭静态和就判PASS。新实验必须先独立进行**全GPU-resident GraphBolt图/feature强路径的预算/语义资格**：若可合法执行，full resident是强软件竞争基线，而不能仅将pinned缓存ON对比pinned缓存OFF。如果全驻留已充分隐藏供数开销，结论应为`SOFTWARE_FULL_RESIDENCY_SUFFICIENT`；不能人造内存压力后称有硬件价值。
2. **GIDS已经覆盖直观GPU缓存/前视重用思想**：[PVLDB 2024 GIDS原论文](https://www.vldb.org/pvldb/vol17/p1227-park.pdf)（作者Jeongmin Brian Park等），第8页（PDF页索引7）Table3列IGB-small 1,000,000节点、12,070,502边、1024维，Section4.1介绍GPU软件cache、跨mini-batch window buffering和CPU/GPU/存储分层；作者的吞吐与模拟环境不能直接外推109。这是**强相关已发表系统近邻**，后续不能把“为GNN采样增加GPU cache或窗口预测”包装成新硬件首创。更有价值的问题是：现有GraphBolt强软件和必要时的全驻留之后，RTX4080完整训练步到底还暴露了哪种**未被隐藏**的等待。

因此A61的正式发现必须允许`FULL_RESIDENT_GPU`、`PINNED_CACHE_ON`及`PINNED_CACHE_OFF_DIAGNOSTIC`三类软件路径（驻留如果可行），且总样本仍不超原预算；若驻留不合预算，应记录证据和`FULL_RESIDENT_NOT_QUALIFIED`，而不是静默省略。科学对象与三臂选择需在任何正式timing前冻结。

## 3. 下一步效率：停止许可循环，准备一个**新科学合同**而非新小门

本轮建议：
1. OGB项目`#499`已有断链议题，已准备[一份简洁适用性询问草稿](https://github.com/swayhrl/accel-sim-framework/blob/81db397d477222b90dee56d31cd6cf66982d627c/docs/ai_workload_research/runs/AI_ARCH_A59_LICENSE_AUTHORITY_CPU_109_V1/REVIEW_REQUEST_DRAFT.md)；若用户愿意，可由用户直接发给维护者/权利方，**本窗口没有用户明确外发指令，不代发**。此信不应阻塞对具有单独数据许可证的新科学对象做研究规划。
2. 把一次合法IGB-small准入与`GraphSAGE强GraphBolt＋PyG/DGL cache ON/OFF诊断`合并成一条连续、有硬预算的**A61候选GPU科研Goal草案**：CPU核真实官方授权/压缩实体size和许可→独立资产安全下载（总量与盘严格计）→原作者语义的图/split与GraphBolt等价转换→109共享锁/单卡数值和缓存frozen gate→≤256自然短训练步的未插桩完整wall与分段诊断→raw/Git/STOP。普通接口/wheel/runner错误允许Codex在一条Goal内有界solve-and-continue；科学对象/许可变更、无法压缩包展开、安全/预算失败必须STOP。
3. **在取得用户对“从ogbn-products变为IGB-small”这一科学对象变更的明确选择之前**，A61可以发布为`PREPARED_AWAITING_SCIENTIFIC_SCOPE_APPROVAL`但**不可运行GPU/下载新图**。用户的既有“默认确认”减少工程小审批，不等于替代选择新的图源/模型训练任务可静默执行。OGB #499回信可能另行解决原问题，但不用为了等待它反复CPU搜索/邮件。
4. 如果IGB-small官方压缩字节/展开实体超过可接受的累计硬限，合法选择`IGB_SMALL_ASSET_BUDGET_NO_GO`、保留初步资格，不**自动**降到IGB-tiny后宣称等价体系结构发现。换tiny可作为单独更小scope的正确性probe，不是同一实验悄然缩图。

**本轮没有新增任何实际GPU Goal或Codex执行，不改变历史A50G、A58、A59以及C16/AWMA。**