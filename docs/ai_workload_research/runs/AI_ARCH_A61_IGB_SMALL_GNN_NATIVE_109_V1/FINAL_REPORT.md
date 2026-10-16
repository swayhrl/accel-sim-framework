# Round A61｜IGB-small真实GraphSAGE：输入、全驻留及eager数值PASS，编译更新资格STOP

**科学终态：DATA_OR_NUMERIC_NO_GO。** 精确原因是`COMPILED_UPDATE_QUALIFICATION_JOINT_PREDICATE_FAILED`，首次报告参数`layers.0.lin_r.weight`。实际完成G0、FULL_RESIDENT_GPU与PINNED_CACHE_ON的单自然batch容量/输入/cache/eager数值验证；随后请求编译的训练步返回后，更新一致性复合断言失败。没有放宽门限、切eager绕过、追加GPU诊断或正式训练。**G2六个正式seed/arm点、完整训练wall与独立供数等待诊断全部NOT_RUN。**

## 授权、身份和输入

作者[IGB论文v2](https://arxiv.org/pdf/2302.13522)说明图关系来自MAG，标签结合MAG和SemanticScholar，标题/摘要经Sentence-BERT形成1024维embedding，并发布RoBERTa相关数值特征。本轮只使用固定MD5/SHA的作者数值资产，不重新生成embedding、下载NLP权重或传播原始文本。

用户2026-10-16明确批准从ogbn-products换为官方IGB-small及A61全部预算，覆盖Goal的历史待审批状态。分支`hrl/aiarch-a61-igb-small-gnn-native-109-v1`，固定启动`9be1d85b0ce105026e7fc4206a0380a98ffb4d1e`，Goal blob`1c721d0ccd685b8aa231f623b4c24f576e4697ac`。新worktree/venv/output/cache；未merge协调或旧执行分支，未重开A59/A50G/C16/AWMA。

Contains information from **Illinois Graph Benchmark (IGB)**, made available under the [ODC Attribution License1.0](https://github.com/IllinoisGraphBenchmark/IGB-Datasets/blob/fc36357f2c1d861870b4c13a58f73da2b93d1e73/ODC-By-1.0). Attribution: Khatua et al., *IGB: Addressing The Gaps In Labeling, Features, Heterogeneity, and Size of Public Graph Datasets for Deep Learning Research*, KDD2023. 作者固定source`fc36357f2c1d861870b4c13a58f73da2b93d1e73`；数据ODC与代码MIT分别核验，ODC2.4不被解释成覆盖所有独立内容权利。实际archive仅数值npy和未使用的ID映射，无额外限制文本或原文摘要；范围限本地、非原数据再分发科研。

唯一作者archive **3865024231B**，预发布MD5 **`6781c699723529902ace0a95cafe6fe4`**与作者值一致，新增SHA256 **`fa237780a84b7d1956c180564a9d080d61b43b32b2bf2810b3960f1ab028a919`**。一次完整数据传输，无另一图、DGL重打包或tiny替代。完整tar只读扫描7成员后才安全提取，展开 **4307401738B**；拒绝链接、特殊文件、逃逸及冲突路径，提取前核峰值与64GiB空闲。archive和原npy保留私有只读；未使用的ID映射对象未反序列化。

真实特征 **1,000,000×1024 FP32**、`synthetic=0`；19类标签域0..18。原有向边数组 **12,070,502×2 int64**，无原始自环。按作者loader的remove-self-loop/add-one-self-loop规则增加1,000,000自环，得到 **13,070,502条有向CSC边**。保持方向和重复边，不加反向边、不coalesce。不能把原论文原边数与这个派生自环图混称相同计数。所有原输入与派生CSC/edgekeys SHA均保存并在停止后重核。

作者`torch.randperm`按seed20261015形成60/20/20split，600000/200000/200000ID；独立CPU检查三个集合完整覆盖、不相交。两训练seed20261015/20261016从官方gb.ItemSampler shuffle顺序冻结68个自然batch前缀，所有路径计划共享相同seed-node批次。实际异步邻域hash不同，不能称严格逐边配对；全训练收敛/test accuracy均未评价。

## 软件与实际门

官方DGL2.4.0+cu121 wheel SHA`9490d57a29457bf7bf2709db4871423baa5f7c2ccd933d4f866c2d336fe6fc74`，Torch2.2.0+cu121，PyG2.6.1，Python3.10.12，NumPy1.26.4，SymPy1.12。newvenv只读绑定明确选择的既有官方Torch/CUDA/Triton发行包；逐文件RECORD/SHA与mtime在运行前后核验 **10686项**。其余依赖装入新venv，原环境未写；offline闭包缺Pydantic已用官方wheel补齐并pipcheck通过。没有升级驱动/CUDA/核心库或源码构建整套DGL。实际GraphBolt CUDA采样、feature/cache、forward/backward/Adam已运行，不把CPU metadata当ABI通过。

唯一计算实现为官方高级例程同一 **PyG mean GraphSAGE**：3层、hidden256、ReLU非末层、B1024、fanout10/10/10、FP32、crossentropy、Adam lr.003/weightdecay0/defaultbetas/eps1e-8。没有与DGL_SAGE拼接速度。matmul highest、TF32关闭；GraphBolt自身默认expandable-segment分配行为及warning原样保留。预先固定feature cache128MiB、graph cache1,000,000edges/threshold1、pinned/UVA/overlap/async，没有性能后视扫容量。

| 门或路径 | 实际结果 |
|---|---|
| G0 | PASS：权利范围、官方字节/安全解包、真实npy、CPU转换、兼容闭包 |
| G1 FULL_RESIDENT_GPU | PASS：完整原FP32features和CSC在GPU；真实B1024一步输入/forward/loss/gradient/Adam资格 |
| G1 PINNED_CACHE_ON eager | PASS：真实cache创建、hit/miss/fallback读回、图采样边方向/合法fanout、模型数值 |
| G1 编译训练步 | 返回后更新复合谓词FAIL；整体G1未通过 |
| G1 PINNED_CACHE_OFF | NOT_RUN：STOP发生在此前 |
| G2/G3 | 正式窗口、独立等待诊断、供数性能归因全NOT_RUN |

FULL真实批次采得349419输入节点，PINNED_ON初批349010，cache replay349367；同seed nodes、不同合法异步采样历史。每层所有采样边都核在实际有向图内，fanout=min(10,degree)，低度节点全部邻域多重集核对，特征按自然IDs采样读回完全相等。缓存正确性重放只重复已实际采样自然IDs，未造新热点且未用于正式计时。图cache确有命中：重放后totalqueries145833/misses120518；feature重复查询值exact。上述比率仅功能阶段，不是稳态cache性能。

## 数值、容量和失败的准确含义

数学oracle仅取实际自然batch前16个seed的依赖闭包，以CPU FP64执行同mean/root线性/ReLU及loss/gradient；训练始终FP32。FULL与PINNED_ON最大forward绝对误差均约 **1.426e-8**，最大参数gradient误差分别 **7.935e-9 / 6.342e-9**，各自首次Adam更新与解析式最大差均 **7.451e-9**，全部满足事前门。不能把参考FP64当成训练精度变更。

FULL复制原features **4,096,000,000B**及全部CSC到GPU，Torch峰值allocated **8631624192B**、reserved **8698986496B≈8.102GiB**。这证明当前真实batch在安全显存范围完成了完整更新；不是只按4GB静态表估算，也不证明未测32batch窗口的性能/所有峰值。

随后`torch.compile(train_step,dynamic=True)`处理同一PINNED_ON minibatch，函数返回且前面的finite/loss一致性检查未触发；在比较更新后参数时，复合条件 **`n==n2 AND allclose(parameter_pair,atol1e-6,rtol1e-4)`**首次在`layers.0.lin_r.weight`报告FAIL。**这是未通过资格，不能断言已定位编译器数值bug。** 断言前没有分别落盘第二参数名、实际最大差/差值元素、两模型初态hash或完整比对张量；确切根因、名称问题、输入生存期/比较器问题均未被排除。生成的Triton缓存及SHA保留，但没有设备trace或“全图融合”证明。

记录不足也意味着不能凭hash重新构造当时全部实际邻域/失败pair；原始canary统计、输入/边hash、程序、阶段/API/error和合法状态均已归档，没有补造原始数值。CPU自审只读核验身份与代码，不追加GPU来绕开科学STOP。CPU解析注记还指出首步Adam在近零gradient处会放大微小扰动，因而更新门与gradient门的敏感性需审阅；这只是数学提示，**不是已测失败gradient或根因**。原门限未改变，未将numeric failure当普通compile不可用而切eager。

实际资格optimizer更新 **3步**（FULL eager、PINNED_ON eager、请求编译各一步）；正式updates **0**。三个loader功能batch加编译复用，不是192/256步正式训练。两seed×FULL/ON/OFF六点每点formal样本0、wall/供数等待NOT_RUN。GPU锁64.68s等数值是资源账，不能叫training latency。**CONVERGENCE_NOT_EVALUATED；无性能或硬件收益结论。**

## 资源、独立性和近邻

累计持原非阻塞GPU共享锁 **64.680326s/1800s**，所有自有GPU子进程退出后释放。采样task-tree RSS峰 **10165702656B≈9.468GiB**，NVML process显存峰 **8588MiB≈8.387GiB**；采样可能漏瞬时峰，另有Torch allocator精确峰、.70内存份额和早停余量。CPU有效affinity0,2,4,6，Torch4threads/DataLoader0workers；锁外准备2733.433s<3h。

实测HTTP正文 **4358839564B≈4.059GiB**，其中图3865024231B、依赖493295201B；加16MiB控制端metadata保守预留仍<6GiB，各子预算通过。新盘归档前10582495232B≈9.856GiB（含保留压缩包、展开、CSC、环境和cache），同FS空闲69815947264B>64GiB。最终Git增量/报告分配再回读核验。没有原数据/大环境/编译binary入Git/164；旧A59/A50G工作区HEAD/clean、使用过的旧缓存hash/mtime均复核不变，无AWMA/C16干预。

[PVLDB2024 GIDS](https://www.vldb.org/pvldb/vol17/p1227-park.pdf)已有GPU软件cache、windowbuffering、CPUconstantbuffer与GPUinitiatedstorage技术。其IGB-small是部分microbenchmark；主要E2E任务包含更大图，hidden128/B4096与本轮不同，不能搬其速度作本轮测量或把缓存/预取重新命名为新机制。A61确实补上了可行FULL_RESIDENT容量canary这一强对照入口，但未取得完整训练wall，无法判`SOFTWARE_FULL_RESIDENCY_SUFFICIENT`或`SCOPED_EXPOSED_SUPPLY_COST`。

## 唯一最小下一建议，未启动

仅建议一个独立审查后的**同输入数值控制canary**：一次自然B1024采样后冻结确切features/子图/labels，用同一保存初态分别跑eagerA、eagerB和compiledC。分开核参数名/dtype/shape、gradient和更新，保存每参数实际pair/maxabs/maxrel及异常元素；eager/eager用于排除FP32非确定性下限。原门限、精度、模型、图和核心版本不改，至多3实际updates+1保留retry，无正式性能窗口。建议新scopeGPU锁≤180s、CPU≤4、RAM≤12GiB、VRAM≤12GiB、新盘≤128MiB、下载安装0；这是基于本轮64.68s及实测容量的有界提案，不是已授权后续或保证运行时间。

若保持原门仍失败则STOP；任何调整numeric contract必须独立科学审查并明确批准，不在看见结果后放宽。**本轮不提出硬件研究建议，不自动启动后续Goal。**

## 发布与STOP

只提交本独立A61branch。原始数据与编译cache保留私有，报告/源版本/合法正负收据/SHA供独立复审。单次完整报告提交、push、fetch-back核exact commit/tree/allnewblob/SHA、worktreeclean与进程/锁收尾；最终readback独立保存以免自引用。STOP。
