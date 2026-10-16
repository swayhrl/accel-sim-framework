# Round A69｜Q-S真实点云训练层组：源码入口、强软件与映射寿命

**日期：2026-10-16；执行者：ChatGPT／AI-ARCH Discovery。**

**本轮范围：** 根据用户对A68后续计划的批准，执行文献、固定Git源码和控制端纯算术审查。未连接109/174-new/164，未启动CUDA、模型、编译、Codex或模拟器，未下载点云数据/权重，未接受数据条款。科研协调起点为`177dc378cd949ec9bfc45a244a6cb33251fadfd3`，首次回读与协调分支identical。A67全驻留软件反证和A61/A65数值STOP不变。

## 0. 裁决与本轮新增认识

**保留一个具体、可执行性待实机确认的Q-S候选：ScanNet/OpenScene真实坐标、RGB、语义标签，经WarpConvNet的PointToVoxel和MinkUNet34，选首个编码层组`inner_module.block1`（两个BasicBlock、四个32→32、3×3×3卷积）研究结构映射与派生布局的自然消费寿命。**

这是源码路径已明确的候选，不是已获得真实训练样本、数值PASS或性能headroom。当前还没有场景实体SHA、已采集activation/gradient、数据使用批准记录或109后端ABI/资源资格。

本轮有三项实质新增：

1. **Spira的公开端到端入口是前向性能测试，不是直接可用的训练输入。** 场景坐标来自加载的npy，而特征由`torch.randn`产生；模型新建后`eval().half()`，整段在`no_grad()`中，无该入口的checkpoint加载、真实标签损失或反向。其价值是映射/数据流基线，不应把它当作真实ScanNet训练三方向基线。[S1–S3]
2. **真实训练入口确实存在，但文档默认值与固定源码不一致。** 在线ScanNet说明写MinkUNet18、增强默认关闭；固定`examples/train/scannet.py`实际配置MinkUNet34、batch12、默认`default_train_augmentations`、16-mixed+GradScaler。未来必须冻结实际配置，不能用文档中的默认值拼接实验。[W1,W2,D1]
3. **四个卷积不等于四份映射；映射也不随一层前向结束就失效。** 同分辨率层通过`replace()`传递cache，核心autograd context保留kernel_map与本层特征/权重；正向mask、反向mask和grouped参数又是按需生成的不同视图。应按独立空间对象、共享存储和最后消费者建账，而非层数乘buffer大小。[W3,W4,W6–W10,W12]

**阶段判断：源码级候选保留；实物输入/运行资格待确认；没有新GPU授权和硬件机制立项。**

## 1. 核验范围与版本

| 对象 | 固定版本/阅读范围 | 证据边界 |
|---|---|---|
| WarpConvNet | `NVlabs/WarpConvNet@f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1`，tree `9a62603c27ace7c5565cbc829611056ecfc2bf7c`；训练入口、数据loader、MinkUNet、PointToVoxel、卷积helper、cache、geometry替换、autograd与mask派生布局 | 只读选定函数，不是整库正确性/性能审计；未build或执行 |
| Spira | `SPIN-Research-Group/Spira@aee69c61f3e001f72828a6d5a70f6a1200166f65`，tree `179e68010075f87921281b000d72c96d8410b0aa`；end_to_end、loaders、前向functional接口 | 公开入口事实；没有断言全仓库绝无其他反向实现 |
| Spira论文 | arXiv:2511.20834v4，2026-04-23；MLSys官方摘要；重点§5.5、§6.1及PDF第9页Figure7/评估设置 | 官方MLSys PDF直取失败，实际视觉核验来自arXiv v4第9页，不称其与正式PDF逐字节一致 |
| TorchSparse | `mit-han-lab/torchsparse@385f5ce8718fcae93540511b7f5832f4e71fd835`，tree `a19872192375a21fbac0f6f40fb6cab93f7130d3`；conv3d调度、cache共享、训练参数 | 独立训练后端候选；没有审完所有CUDA或本机数值 |
| ScanNet使用条件 | 官方ScanNet_TOS.pdf单页正文及截图 | 官方需同意条款/批准的入口已明确；当前未查得项目批准记录不等于证明用户没有许可 |

未重新计入A62/A63已经审过的全部文献作为本轮“新论文”。A69的主要增量来自具体真实模型路径与状态寿命的源码对应，而不是增加论文数量。

## 2. 为什么Spira不能直接承担这次完整训练比较

`end_to_end_experiment.py`使用`torch.no_grad()`，新建SparseResNet/SparseResUNet等模型并转FP16、eval；默认输入通道4。`loaders.py`为各库分别生成随机FP16特征，坐标按库要求转换（TorchSparse路径还交换轴顺序）。因此：

- 真实坐标可以支持空间稀疏结构、映射与前向执行的分析；随机特征并不让这类性能测试自动失效。
- 但该入口没有给出原场景RGB、标签驱动loss、实际训练activation/gradient或任务精度依据，不能写成“已获得真实训练状态”。
- 该脚本端到端范围中，Spira的`inputs.order()`和`add_all_kernel_maps()`就在CUDA计时区间内；不能再用“作者没有计预处理”作为新动机。
- Spira v4第9页明确全网提前构建与逐层缓存最终具有近似映射内存足迹，作者给出的平均约40MB是其评估场景的全局存储映射，不是我们的SMEM/L2压力或训练峰值。[P1,S1,S2]

**采用方式：** 将Spira作为同语义坐标映射/前向数据流的强反证；训练主路径先由已有反向的WarpConvNet承担，TorchSparse作为独立后端候选。没有必要为了比较而新开发一套Spira backward。Spira的SparseResUNet42与本轮MinkUNet34不能仅因都叫UNet就视为相同模型。跨库前向比较需要显式校准坐标轴、偏移/权重排列、下采样与输出行顺序，不能只按tensor位置直接allclose。

## 3. 真实输入与梯度从哪里来

固定WarpConvNet代码的来源链是：

```text
OpenScene预处理ScanNet场景 (coords, colors, labels)
  → ScanNetDataset读取对应train split
  → 每场景train_transform（实际增强实现与随机实现需冻结）
  → DataToTensor / Points
  → PointToVoxel(voxel_size=0.02, MEAN pooling)
  → MinkUNet34：编码→跳连→解码→逐点unpool
  → output.features 与真实labels的cross_entropy(ignore_index=255)
  → GradScaler.scale(loss).backward()
  → AdamW.step / GradScaler.update
```

其中`PointToVoxel`使用`to_unique`将输出回到原始点位置；损失在原始点标签上计算，不是将多个点的标签随意均值成一个体素标签。`ScanNetDataset`默认本身不预降采样，调用端没有传入其`voxel_size`，主要体素化发生在PointToVoxel中。[W1,W2,W5]

### 3.1 固定源码中的实际默认配置

| 字段 | 源码实际值 | 本轮状态 |
|---|---|---|
| 模型 | MinkUNet34，in_channels=3、out_channels=20、in_type=voxel | 已读 |
| batch / voxel | batch12；0.02 | 已读；**不是建议109直接按12运行** |
| 精度 | 16-mixed、autocast及GradScaler | 已读；FP16/BF16/FP32不能混称同一路径 |
| 初始卷积 | 基类默认init_kernel_size=1 | 已读；不能照名称猜成3×3×3 |
| 增强 | `data.train_transform`构造默认增强，colors_in_unit_range=True | 调用已读；本轮未逐项审核该函数所有变换实现 |
| 损失 / optimizer | 逐点交叉熵、ignore255；AdamW lr0.001；StepLR | 已读 |
| 训练状态 | 新建模型；本脚本虽然声明ckpt_path，已读main未使用它加载checkpoint | 不假称pretrained或trained checkpoint已绑定 |

**不把已训练checkpoint设成所有发现实验的必需前置。** 在取得合法真实场景后，冻结随机初态、实际增强和标签，通过真实loss产生梯度，可以明确作为“真实输入上的初始化/早期训练”研究结构路径；这不同于给独立卷积随便塞随机feature或随机上游gradient。要主张成熟训练阶段、模型质量或状态敏感的性能，则另需相应checkpoint/轨迹与验证。此为本轮方法设计，不是已有实测结果。

### 3.2 数据可达性不等于已获执行资格

loader公开OpenScene的ScanNet预处理zip URL，并在split缺失时自动下载；`.pth`读取采用`torch.load(weights_only=False)`。**本轮没有实例化Dataset或下载/解包/反序列化任何数据。** 未来应先确认ScanNet许可批准或合规共享链、固定场景与来源hash、安全解析及目录边界；不能因URL公开或库代码Apache2就宣布数据许可PASS。已检索的项目历史中未找到该批准/场景实体记录，状态保留待确认，不反复探测同一下载链接。[W2,D2]

### 3.3 训练示例不是现成的性能测量器

`train()`在DataLoader交付batch之后才开始本步计时，并在每步调用`loss.item()`更新进度/日志。它适合确认数据与梯度语义，不能直接将`train/time`当作覆盖数据迭代、保持异步重叠的完整训练wall。未来数值/生命周期观察与独立未插桩计时应分别执行；源码已有训练loop不等于measurement contract已通过。[W1]

## 4. 选定自然层组及匹配对照

**主组：`PointToVoxel.inner_module.block1`。** 对固定MinkUNet34，`planes[0]=32`、`layers[0]=2`，由两个BasicBlock组成：

| 相对路径 | 输入→输出通道 | 卷积核/stride | 自然作用 |
|---|---:|---|---|
| `block1.0.conv1[0]` | 32→32 | 3³ / 1 | 第一残差块的第一卷积 |
| `block1.0.conv2[0]` | 32→32 | 3³ / 1 | 第一残差块的第二卷积 |
| `block1.1.conv1[0]` | 32→32 | 3³ / 1 | 第二残差块的第一卷积 |
| `block1.1.conv2[0]` | 32→32 | 3³ / 1 | 第二残差块的第二卷积 |

上游是`conv0`（1³、3→32）与`conv1`（2³、stride2、32→32），得到相对初始体素步幅2的空间支撑。四个卷积中间是BN/ReLU与残差加法，不改变该组的空间支撑；两个BasicBlock无通道变换投影。四个3³卷积的权重元素合计`4×27×32×32=110592`，不含BN参数。这是源码尺寸算术，不是实际workload活跃体素N或MAC数。[W3,W4,W12]

**为什么选它：** 它在真实网络自然出现，不需人工重复一个kernel来制造复用；四个同支撑消费者方便检查第一次构建与后续命中；C32且K27与现有mask/grouped/explicit执行入口可对应；不是因其已经测到高占比才选。实际N、每offset边数E、耗时与全模型权重均UNKNOWN。

**一个必要结构变化对照：** 相邻`conv2`（2³、stride2）进入新分辨率，随后`block2`（首块32→64、后续64→64）。它用来检查跨分辨率失效和构建，而不是把所有层强行算成同一个cache key。该对照不需要立即扩成全参数网格。

**不要在block1结束就认定映射寿命结束。** 该组输出`out_b1p2`作为encoder skip保留，并被`convtr6(...,out_b1p2)`和随后block7使用。源码支持后续空间支撑和cache复用的可能性；具体map对象是否相同、转置是否新wrapper而共享底层数组、最后消费者次序仍需实际记录，不能仅凭两个shape相同就合并对象。

## 5. 从构建到最后消费者：已有软件已经做了什么

1. `generate_output_coords_and_kernel_map`对非生成、非转置stride1直接沿用输入坐标支撑，查询`IntSearchCacheKey`；未命中时才`generate_kernel_map`并put。当前key包含kernel/dilation、方向、stride-mode和in/out offsets，不是完整坐标内容hash；因此未来记录还要绑定真实坐标与行顺序、所有者，不能把cache拿到另一个场景继续用，也不能仅凭key设计断言库在正常路径上错误。[W6,W7]
2. `Geometry.replace`传递extra attributes中的cache对象；`Sequential`对BN/ReLU处理feature，再replace回geometry。四层共享同支撑时，不能将每个module引用算成独立结构存储。[W8,W12]
3. `IntSearchResult`保存基础in_maps/out_maps/offsets，并有lazy `_mask_data`、`_reverse_mask_data`、`_reduced_mask`、`_grouped_params_cache`。基础语义映射与消费者需要的执行布局不是同一个“已就绪”状态。[W9]
4. `mask_gemm`已有正向pair_table+mask+argsort缓存，以及融合反向pair_table/mask构建和缓存。反向不是每层必重新生成，也不能把这类融合/共享再包装成新机制。[W10]
5. `UnifiedSpatiallySparseConvFunction`用`save_for_backward`保留本层feature/weight，并在ctx引用kernel_map；反向分别组织dgrad和wgrad，不能假定前向最优布局对两者同样最优。[W11]
6. 转置卷积会尝试从decoder或encoder skip的cache取正向map，交换in/out引用生成反向视图；源码已有这个重用入口。TorchSparse的conv3d也共享`output._caches=input._caches`，将training传给建图/转置路径并分派多种dataflow。因此“首创跨层mapping cache”不是剩余问题。[W6,T1]

本轮区分四种结束时刻：最后语义读取、最后GPU消费完成、Python/框架所有权释放、allocator可复用。源码只能给出依赖和引用关系；没有任何一个时刻已被实测。不能把某个属性仍存在当作显存一直活跃，也不能把`del`当成GPU已完成。

## 6. 一个可复算但不等于瓶颈的布局成本

对该组非生成stride1的K=27、N_in=N_out=N；在mask路径正反两套布局均物化、互不别名时：

- 正向：int32 pair_table为`27N`项，mask为`N`项，argsort为`N`项，共`116N bytes`。
- 反向：相同数量级，再`116N bytes`。
- 六个逻辑数组合计`232N bytes`。

这个计算只来自已读shape/dtype。[W10] 它**不包括**基础紧凑映射、grouped参数、sort scratch、权重、activation、gradient和allocator空洞；不是相对其它后端的净新增，底层别名必须去重。四个卷积共享同对象时不能再乘4。若AUTO没有选择mask/dgrad相应分支，这个布局未必全部生成；不能用它预先宣称超过L2或形成DRAM瓶颈。真实N未取得，本轮不给MB估计。

它提出的只读发现问题是：**在现有跨层复用、三方向选优之后，长期保留全部派生布局是否仍比按自然生命周期保留/准备更划算；最优计算布局的准备和同时存活代价是否足够重要？** 这不是已经证明需要硬件，也不能靠“图已在GPU”推导问题已消失——与A67不同，这里关注GPU内部结构准备和消费，而不是预设主机供数。

## 7. 完整边界与最小反证设计（仅提案）

不直接执行作者100epoch训练脚本，不一次搭齐三套大环境。数据使用/实体确认后，一条未来有界Goal可连续完成以下工作；资源预算需在样本大小、ABI明确后另定，不能借用A67额度。

| 条件 | 固定内容与用途 | 防止误判 |
|---|---|---|
| 自然完整训练路径 | 一个获准真实train场景、固定增强/初态；完整forward、真实标签loss、backward；记录block1四消费者与上下游 | early-training不能写trained质量；上游gradient不可用randn代替 |
| WarpConvNet强路径 | 前向/dgrad/wgrad分别保留其合法选优，原cache复用生效；已安装SM89真实可用候选待查 | 不只拿explicit fallback当强软件；AUTO选优时间不能混入稳态kernel |
| 数值参考 | 相同coords、offset次序、features、weights、实际上游梯度；explicit等可解释路径 | 坐标行序/布局先对齐；不继承GNN的容差、Adam门或精度 |
| 映射/布局提前就绪诊断 | 同一个实际实例的等价结构视图预先准备，记录改变了哪些初态 | 只测敏感性；不是现实机制或严格上界，cache/并发初态可能改变 |
| 结构变化对照 | conv2进入下一分辨率，保留自然输出支撑 | 不以人为flush/每层重建制造大量重复开销 |

必须分账：编译/算法选优cache、每个新坐标对象的语义map、各执行布局准备、实际fwd/dgrad/wgrad、释放及allocator占用。编译/选优可跨输入复用，不代表某一场景map可以跨输入复用；重复同一场景warmup不能悄悄抹掉每新场景真实构建成本。

模块观测/张量复制会干扰时序，因此数值/生命周期观察与未插桩完整wall分开。真实三方向比较使用相同上游梯度时属于局部执行因果；完整训练若允许不同累加顺序，必须按预注册数值/质量合同评估，不将实时路径的所有小浮点差异都变成长线编译器课题。

**预先停止条件：** 正常map复用/消费者选优已吸收差异；提前就绪诊断几乎不改善目标层组；全部空间只是别名重复计数；差异主要是Python封装、调优冷启动或普通软件缺陷；合法真实数据/实现或数值不能闭合。不能只因当前整模型覆盖率低就否定明确的kernel-family机会，但要同时报告全模型权重与非目标副作用；本轮尚未测到任何局部正结果。

## 8. 当前准入表与下一动作

| 项 | 当前状态 |
|---|---|
| 具体模型与四卷积自然层组 | 源码明确 |
| coords/RGB/labels到真实loss和gradient的生成链 | 源码明确 |
| 跨层map cache、反向布局、三方向后端 | 已有能力确认；实际选择待实机 |
| Spira能否直接作该完整训练基线 | 本轮审查的前向入口不满足；仍保留前向反证 |
| ScanNet许可批准/合规共享链 | 本轮未查得项目记录；待确认，不等于认定没有 |
| 一个具体场景、增强实现和样本实体SHA | 未取得 |
| 初始或已训练模型状态、真实中间gradient实体 | 未运行/未捕获；初始化训练可明确作为独立scope |
| 109 SM89软件闭包、峰值资源和数值 | 未验证 |
| 时间/容量headroom、新机制新颖性 | 未成立 |

**本轮已完成源码阶段，不再为同一范围另开重复“继续读代码”的轮次。** 下一项真正必要的输入是ScanNet既有使用批准/合法共享情况和一个具体场景的可信实体；随后才可一次形成有界native资格与自然层组筛查合同。若用户没有相应使用权限，应走官方批准，不自动抓公开镜像，也不为维持进度偷偷改成另一数据集。A69不发布GPU Goal。

## 9. 来源与固定源码索引

以下链接为原作者/官方源，Git blob来自本轮连接器回读；引用范围限已读函数。W3末尾其它模型类被返回预算截断，不影响本轮已读MinkUNetBase/MinkUNet34；未称整文件所有模型已审完。

| ID | 固定源码路径 / 来源 | Git blob或版本 |
|---|---|---|
| W1 | [WarpConvNet examples/train/scannet.py](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/examples/train/scannet.py) | b339f5bfc0670b128a713872ec72b1af5f672d49 |
| W2 | [dataset/scannet.py](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/dataset/scannet.py) | 0e973fd4bbe946287044c916daec8e387f65269f |
| W3 | [models/mink_unet.py](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/models/mink_unet.py) | 7663a74b3f3cc6e88f32cffc1dbb3cf0fe25b695 |
| W4 | [nn/modules/sparse_conv.py](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/nn/modules/sparse_conv.py) | 0d26b1dc6ef8f16a5fbf1a2a389bcc814d879c47 |
| W5 | [nn/modules/sparse_pool.py](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/nn/modules/sparse_pool.py) | 94d8a4cf4b07591f19f01a6aceae920f68536754 |
| W6 | [sparse_conv/helper.py](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/nn/functional/sparse_conv/helper.py) | 8573c6f77ebd69e2cf9dd727670a12f70711c104 |
| W7 | [coords/search/cache.py](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/geometry/coords/search/cache.py) | 7071383cc08259df1b3ba5d37b417f374ed32544 |
| W8 | [base/geometry.py](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/geometry/base/geometry.py) | 463552a1697d148053cee8974c36bf65d92dbc55 |
| W9 | [coords/search/search_results.py](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/geometry/coords/search/search_results.py) | 15c5f661cf36822307156450a13c4923648dde2a |
| W10 | [detail/mask_gemm.py](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/nn/functional/sparse_conv/detail/mask_gemm.py) | 2e1fa0bbcd5618c29f8db50cfb4d18806df8a2b5 |
| W11 | [detail/unified.py](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/nn/functional/sparse_conv/detail/unified.py) | 9dd2b97819ee36a12c0732018f86872a39445c77 |
| W12 | [nn/modules/sequential.py](https://github.com/NVlabs/WarpConvNet/blob/f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1/warpconvnet/nn/modules/sequential.py) | ffeb14b99bf1a07985499fa4174f33865750d028 |
| S1 | [Spira scripts/end_to_end_experiment.py](https://github.com/SPIN-Research-Group/Spira/blob/aee69c61f3e001f72828a6d5a70f6a1200166f65/scripts/end_to_end_experiment.py) | b724a82a658f94f39d7ff28b58c6c9f8839723d5 |
| S2 | [Spira scripts/loaders.py](https://github.com/SPIN-Research-Group/Spira/blob/aee69c61f3e001f72828a6d5a70f6a1200166f65/scripts/loaders.py) | caa9747c42108b50617212e4798ed5e81df04420 |
| S3 | [Spira functional/convolution.py](https://github.com/SPIN-Research-Group/Spira/blob/aee69c61f3e001f72828a6d5a70f6a1200166f65/source/spira/nn/functional/convolution.py) | 667f9dab3c9ea96d7f382ab38dd0f9f7606eb11c |
| T1 | [TorchSparse conv/conv.py](https://github.com/mit-han-lab/torchsparse/blob/385f5ce8718fcae93540511b7f5832f4e71fd835/torchsparse/nn/functional/conv/conv.py) | b8d4e13a8cd6b0f509c4b9cf51772d5073ffa102 |
| P1 | [Spira arXiv PDF](https://arxiv.org/pdf/2511.20834v4)，[MLSys正式摘要](https://proceedings.mlsys.org/paper_files/paper/2026/hash/7972f3735e104a54715922aa416fde1b-Abstract-Conference.html) | v4；PDF第9页已截图核验 |
| D1 | [WarpConvNet ScanNet在线说明](https://nvlabs.github.io/WarpConvNet/examples/scannet/)，[internals](https://nvlabs.github.io/WarpConvNet/user_guide/sparse_convolutions_internals/) | 在线描述，配置与源码不一致处以W1为执行设计依据 |
| D2 | [ScanNet Terms of Use](https://kaldir.vc.in.tum.de/scannet/ScanNet_TOS.pdf) | 官方单页正文与截图；未代用户接受 |

**终态：Q-S一个自然层组与真实训练生成链已从源码落定；强软件边界与生命周期记账完成；实际样本和运行资格尚未通过，本轮无新GPU任务。**
