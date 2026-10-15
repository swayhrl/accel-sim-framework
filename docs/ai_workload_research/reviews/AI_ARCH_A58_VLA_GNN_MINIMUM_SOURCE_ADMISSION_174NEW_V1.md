# AI-ARCH A58｜VLA/GNN 最小源码资格审查（174-new）

**裁决：`SELECT_GNN_CONDITIONAL_GPU_PROBE`；仅为未来合同草案，`PROPOSAL_NOT_AUTHORIZED`。** VLA 多请求 GPU 并发资格未成立。GNN 有固定公开真实任务和完整原生训练步，但现有 GraphBolt 示例没有启用缓存；运行版本、数据许可、显存/主存和数值质量仍为门槛。任一门槛失败即 `NONE_SELECTED_OR_SOURCE_GAP`，本轮不转投 GPU。没有 GPU 性能、训练精度或硬件剩余问题的实测结论。

## 执行与既有边界（G0）

- 固定 repo HEAD `70f640573fc2434b39df35204dffb901f9214109`；独立 worktree/branch `hrl/aiarch-a58-vla-gnn-source-admission-174new-v1`。只用 174-new 上单个短时 CPU worker；未访问 109/164、GPU 锁或任何 CUDA 接口，未下载权重、数据或依赖。开始/复核时主机 swap 2 GiB 满、overlay 剩 79 GiB、主机 I/O pressure `full avg10≈40–43%`；本任务 cgroup `io.pressure` 和 `memory.pressure` 均为 0、未见自身阻塞。因而限为轻量串行源码/元数据读；若转为实际争用，应 `RESOURCE_DEFERRED_STOP`。
- 已读 `COORDINATION_PROTOCOL.md`、`CURRENT_STATE.md`、A51–A55 Discovery 和 A57 独立裁决。A57 新于当前状态快照：A50G 的 index/reload 恢复可用，但固定 GloVe 校准 `recall@10≥0.95` 在六配置、2,000 查询上均失败；没有可采信性能测量，CAGRA 停止，不再提出第三次 GPU 排故。本报告不重审其结果。
- A51–A55 已给出 VLA 的 prefix KV reuse/flow 多步、vla.cpp 合成 benchmark/串行服务，以及 GNN 的 GPU 采样、UVA、cache/async 邻近软件和 SDGraph 等近邻；不把通用 cache/CTA 共调度重命名为新硬件贡献。

## G1｜SmolVLA 身份、真实输入与并发资格

| 关口 | 固定证据与等级 | 裁定 |
|---|---|---|
| 模型/权重 | [官方 `lerobot/smolvla_base` model card](https://huggingface.co/lerobot/smolvla_base)、[文件树](https://huggingface.co/lerobot/smolvla_base/tree/main)：Apache-2.0，公开 `model.safetensors` 约 907 MB、config 和预/后处理配置；模型总文件约 915 MB。卡片示例以 LeRobotDataset 一帧调用 `select_action`，base 为可微调权重。证据：发布元数据；精确不可变 Hub revision、文件 SHA、自然 solver steps/action chunk/camera shape 均 `UNKNOWN`，不得由默认值跨版本推定。 | 有真实模型身份，运行参数未冻结。 |
| GGUF 强实现 | [`vrfai/smolvla-libero-gguf` 卡片](https://huggingface.co/vrfai/smolvla-libero-gguf)说明来自 `HuggingFaceVLA/smolvla_libero`，不是 `lerobot/smolvla_base`；量化/转换及任务专门微调均可能改变输出。固定 [vla.cpp 架构](https://github.com/VinRobotics/vla.cpp/blob/cff0cfb5e9e6cab31671d46082f7bdbff078816e/docs/ARCHITECTURE.md)和 [bench](https://github.com/VinRobotics/vla.cpp/blob/cff0cfb5e9e6cab31671d46082f7bdbff078816e/src/serving/vla-bench.cpp)有实作，但 bench 为合成像素/token/state/noise。证据：原作者源码/卡片。 | 与官方 base 不构成等价速度/质量对照；权重、dtype、tokenizer 和输出一致性 `UNKNOWN`。 |
| 真实观测 | [LeRobot LIBERO 文件树](https://huggingface.co/datasets/lerobot/libero/tree/main)公开 data/meta/videos、Apache-2.0 标记，约 1.94 GB；官方模型卡展示 `lerobot/libero` 单帧示例。仅核文件清单，未下载 episode。相机数量/分辨率、任务文本/state schema、帧/请求时间戳、模型预处理映射、动作成功率均尚未绑定或 `NOT_MEASURED`。 | 有可追溯真实数据入口；B1 固定样本未获准。 |
| 真正多请求 GPU overlap | 固定 LeRobot [`remote_inference/README.md`](https://github.com/huggingface/lerobot/blob/53feaef37b67e8f4c23b6953e880ff535e39d6fe/src/lerobot/remote_inference/README.md)明确一个服务进程接纳一个 session，并发模型共享和 batching 在实现范围外；[`server.py`](https://github.com/huggingface/lerobot/blob/53feaef37b67e8f4c23b6953e880ff535e39d6fe/src/lerobot/remote_inference/server.py)为会话 worker；固定 [vla.cpp server](https://github.com/VinRobotics/vla.cpp/blob/cff0cfb5e9e6cab31671d46082f7bdbff078816e/src/serving/server.cpp)为 REP `recv→predict→reply` 串行。证据：固定源码/文档。 | `SERIAL_SERVER_NOT_A_GPU_CONCURRENCY_BASELINE`；两个客户端不证明 GPU 并发。 |

可定义但尚未测量的边界为 `predict total`（同输入预处理至动作产出）、`prefix/expert phase`（需在固定 [LeRobot SmolVLA 实现](https://github.com/huggingface/lerobot/blob/53feaef37b67e8f4c23b6953e880ff535e39d6fe/src/lerobot/policies/smolvla/modeling_smolvla.py)打点）、`request arrival→reply complete`（包含队列与网络）。前者不能代替后者；CPU 会话异步不等于两请求 VLM-prefill 与 expert GPU 重叠。GPU 互斥/重叠 `UNQUALIFIED`。因此 VLA 本轮 `VLA_NO_GO_OR_PARTIAL`；单请求 phase characterization 也不在本次 GPU 授权内。

## G2｜GraphSAGE/ogbn-products 原生训练边界

- [OGB 官方节点数据说明](https://ogb.stanford.edu/docs/nodeprop/)：`ogbn-products` 有 2,449,029 节点、61,859,140 条无向边、100 维词袋 PCA 特征、47 类；销售排名决定 train/valid/test，指标为 accuracy。无向边在特定 loader 中可能存为双向弧，不能把 61.86M 直接当 CSC `indices` 长度。原始特征若 FP32，仅值数组约 979,611,600 B（**估算**）；若双向约 123.72M 弧且 int64，仅 index 数组约 989,746,240 B（**估算**），另需 indptr、labels、batches、激活、cache 与 allocator。无法由这些下界断言 4080 的 16 GiB 可容纳。数据实际字节、镜像内容 SHA、Amazon 原始许可全文、host pinning 可用量均 `UNKNOWN/NOT_VERIFIED`；本轮未下载数据。
- 固定 [`dmlc/dgl@3d16000` GraphBolt 示例](https://github.com/dmlc/dgl/blob/3d16000b4170fa741ed9e9667f22ba84d3493026/examples/graphbolt/node_classification.py)直接指定 `ogbn-products`、3 层 mean GraphSAGE、hidden 256、fanout `10,10,10`、batch 1024、Adam lr 1e-3/weight decay 5e-4、cross entropy。原生一步为 `ItemSampler → sample_neighbor → fetch_feature → copy_to/DataLoader → SAGE forward → loss → zero_grad → backward → optimizer.step`；验证/全图推理须与训练步分时标识，不能截取 sampling kernel 作为全训练速度。seed、特征 dtype、replace=False、deduplicate、边方向及 split 的运行身份尚待锁定；示例 shuffle 未固定 seed。
- 固定 [sampler 源码](https://github.com/dmlc/dgl/blob/3d16000b4170fa741ed9e9667f22ba84d3493026/python/dgl/graphbolt/impl/neighbor_sampler.py)具有 `overlap_fetch`、`asynchronous`、`num_gpu_cached_edges`、`gpu_cache_threshold`；示例在 pinned 模式启 `overlap_fetch`，非 CPU storage 启 `asynchronous`，**但没有传非零图缓存容量**。[GPUCachedFeature](https://github.com/dmlc/dgl/blob/3d16000b4170fa741ed9e9667f22ba84d3493026/python/dgl/graphbolt/impl/gpu_cached_feature.py)具有查询、miss fallback、替换和 `read_async`；[GPUGraphCache](https://github.com/dmlc/dgl/blob/3d16000b4170fa741ed9e9667f22ba84d3493026/python/dgl/graphbolt/impl/gpu_graph_cache.py)有 miss 计数、threshold 和 async query。能力由源码证实，**示例未实际接入 GPU feature cache，也无命中率/隐藏延迟数据**。强软件合同必须小规模接线并验证 fallback 正确；不能把原示例当缓存已启的最强基线。
- [RAPIDS cuGraph-PyG 26.04 API](https://docs.rapids.ai/api/cugraph/legacy/api_docs/cugraph-pyg/cugraph_pyg/)与 [NeighborLoader API](https://docs.rapids.ai/api/cugraph/nightly/api_docs/api/cugraph-pyg/cugraph_pyg.loader.neighborloader/)表明存在 PyG loader，常见默认 `replace=False`、`subgraph_type=directional`；但后一页是 nightly，版本与具体 26.04 行为不可混用。需锁 cuGraph-PyG 可安装发布版本及 SHA、PyG/PyTorch/CUDA/driver ABI，且核采样方向/概率、去重、feature gathering、label split 与 mean 模型一致后才可对照。[cuGraph-GNN 项目](https://github.com/rapidsai/cugraph-gnn)说明 cuGraph-DGL 自 25.08 移除，不可当当前合法替身。本轮未访问 109，4080 驱动/ABI、GraphBolt 二进制、cuGraph-PyG 同任务可运行性皆 `UNKNOWN`。
- 数值门：同 OGB 原始 split、相同特征/label/edge 方向与任务 loss；锁随机 seed、fanout、batch、层数、replacement、epoch/optimizer schedule。不同 sampler 不强求逐 bit 邻居相同，但需核每层邻居分布、度数/重复率与固定小批输出的数学语义，多个种子训练 accuracy 不低于预先冻结的原生基线容差。**容差需在首次 GPU/数据前登记；本轮无 accuracy 数值，不能临时设门以迁就结果。** 更换 graph/labels/synthetic features 即失去真实任务资格。

## G3｜科研投资矩阵与唯一后续草案

| 判据 | Q-V：SmolVLA | Q-G：GraphSAGE/ogbn-products |
|---|---|---|
| 真实身份/许可/字节 | 官方 checkpoint 与公开 LIBERO manifest 有；GGUF 非同 checkpoint；B1 schema/Hub SHA 未锁，约 0.9 GB 权重、约 1.94 GB 数据均仅发布元数据 | OGB 官方真实 split/task 有；图双向存储/FP32 等需锁，原数据/许可全文 `UNKNOWN`，估算特征与 index 下界各约 0.9 GiB |
| 软件/版本与完整 native wall | LeRobot/vla.cpp 固定源码；单会话或串行 REP，无法提供两个独立 GPU 请求 overlap；action success 未测 | 固定 GraphBolt 有完整训练步；cache/async API 有但例程未全接线；可用 binary/4080 ABI 未证实 |
| 数值/质量与强软件 | 官方 base 与 GGUF LIBERO 微调版不可横比；多请求调度前提失败 | 原 split、采样分布、训练 accuracy 可设门；须先验证 cache miss fallback 和强软件路径 |
| 独立 holdout/负例与 STOP 成本 | 独立 episode/不同到达间隔可设计，但需要新并发 server，超出本次最小入口 | 固定 train seeds、保留 OGB validation/test；低命中热点和低 fanout 可作负例；若步骤仍被隐藏或质量不等即停止 |
| 综合裁定 | `VLA_NO_GO_OR_PARTIAL` | **唯一有条件候选**；不是已准入 GPU |

**未来唯一最小实验合同草案（`PROPOSAL_NOT_AUTHORIZED`）：** 在资源/许可/ABI 前置门全部绿灯后，以官方 `ogbn-products` 原始 split 的固定小训练窗口（例如 64 个自然 batch、batch 1024、3 层 fanout 10/10/10、固定 seed；评估仍走独立 validation）研究 **强 GraphBolt 缓存+异步供数之后，采样/特征 miss 是否仍暴露在完整训练步关键路径**。一条主路径：同固定 DGL 实现的 pinned/UVA `overlap_fetch` + async、非零 GPU graph cache、GPU feature cache 和正确 fallback；第二条仅在固定 cuGraph-PyG 发布版、等价采样/模型/质量/ABI 均证实后作为强软件对照，否则省略，不填合成弱基线。缓存预算按显存实测余量缩减，不预设 16 GiB 可装入；无新的硬件机制实现。

建议 **≤10 个发现点**：①数据/软件 SHA、许可与 ABI；②完整 step wall（迭代器取数至 optimizer step，含同步）；③sampling wall；④feature-ready 等待；⑤graph/feature cache 命中及 fallback 字节；⑥GPU critical path 与 CPU/PCIe 等待是否被重叠隐藏；⑦peak GPU/host RSS/pinned；⑧邻居分布/重复率；⑨固定 seed validation accuracy；⑩独立低热点或低 fanout 负例。计时分开 warmup、训练窗口与初始化/数据载入，同时报告 end-to-end 准备+训练 wall；不把异步 enqueue 时间当完成时间。质量先于性能。若强路径中暴露等待接近测量噪声、相较有效强软件无可重复 headroom，或只靠关 cache 才见改善，则 **negative STOP**，不得声称 GPU 资源限制或硬件空间。

**建议资源边界，均非授权：** 单张 4080 排他锁、最多 1 个 GPU 进程；首次只做环境/数据/许可 canary，随后 ≤64 自然 batch × 2 路径 × 2 固定 seeds（最多 256 步），建议 GPU 活动 ≤30 分钟、额外磁盘 ≤8 GiB、host RAM ≤16 GiB；若真实 dataset、预处理或库安装超过该界即先改合同求授权。本 A58 不触碰锁、不下载、不安装、不运行。硬 STOP：资源与 AWMA 冲突、许可不清、OGB 任务身份不清、发布版 ABI 失败、强 cache 接线失败、OOM、数据/采样/accuracy gate 失败、任何 GPU 等待无法与完整 step 对齐。不得自动启动。
