# Round A56｜A50G完整CAGRA构图完成但包装失败：独立科学审查与恢复门

**审查者：ChatGPT／AI-ARCH Discovery；2026-10-15。起点协调branch `hrl/ai-workload-research-coordination@8502b7dcecc28b4762ffcb03afcabb11026a2436`。** 本轮GitHub只读核原始执行报告/原始日志/元数据/数值&时间结果、实际执行与修正版脚本、cuVS 26.10发行源码，再写新的协调审查。不连接109/174、无GPU/模拟器/数据下载/安装；执行回执只能证明运行侧资源和clean，Git回读不等于重新执行。

## 0. 科学裁决

**`A50G_ACCEPT_SCOPED_FULL_NATIVE_BUILD_FIELDS_PASS / POST_BUILD_WRAPPER_ERROR / SERIALIZED_INDEX_NOT_AVAILABLE / ZERO_SEARCH_SAMPLES / STOP`**。

- **G0 PASS、G1分门部分PASS：** 用官方GloVe-100-angular已冻结完整1,183,514×100单位FP32 base、真实109 RTX4080、cuVS/RMM 26.10默认Resources/default CuPy allocator/stream，**唯一一次真实full CAGRA cosine/IVF-PQ、degree64/intermediate128**确实返回并同步；五项属性`trained=true,size=1,183,514,dim=100,graph_degree=64,dtype=float32`均正确。`new dataset dimension100 vs index0`正常首次附着warning不作为错误。这个结果比A47R2的1024 synthetic tiny确实更进一步：原输入/平台上“大规模构图入口可以返回”得到本机实证。
- **G1剩余和G2/G3仍未测：** 立即进入下游B1/AUTO准备时，`np.frombuffer(pinned).reshape(1,100)`遇到请求400字节、实际公开buffer512字节（128个FP32）的对齐差异，出现ValueError；尚未调用任何`cagra.search`、`cagra.save`或`load`。子进程退出丢失GPU索引对象，任何恢复必须再次完整构图，**旧Goal的一次性构图额度已用，不可直接重跑**。四正式点均0个样本、recall和GPU数值全部`NOT_RUN`。执行报告的历史`INDEX_RELOAD_OR_NUMERIC_NO_GO`应结合其`precise_cause=POST_BUILD_ENGINEERING_STOP_UNIQUE_BUILD_CONSUMED`解释为**未进入数值检查的工程阻断**，不是“计算结果数值不匹配”。
- **不产生硬件结论：** 本机没有AUTO/SMALL搜索时间、完整wall差异、图实际邻居ID/质量验证。不能把CPU/显存及构图预算收据解释为CAGRA搜索性能或硬件headroom；AUTO可能已充分也可能没有，完全未测。
- **工程修正的可信范围**：发布方保留已执行`tools/aiarch_a50g/native_executed.py` blob`9e1dc842a3de2be8b7e4e81dec9e13337bf267d6`和未执行修正版`tools/aiarch_a50g/native.py` blob`c6a2d49b3afce46949c85a28c5462c39cbce0dae`，其`Buffers`三种pinned view都加显式`count`、B1/B256配置检查前移到full build前、五字段合格后`立即save/hash`。`ENGINEERING_REPAIR.json`还声明CPU round-up 512B→128 elems的B1和B256形状测试PASS。**这只验证包装修复的CPU语义，未验证新修正版在实际CuPy pinned、保存、重新加载与GPU搜索中的路径**。不要把修正版代码已commit当恢复结果PASS。
- **建议下一步：** 基于已经观察到full build≈3.19秒的native返回、已冻结输入/环境/查询分组及一次定位明确的包装缺陷，**只值得再做一次有界的、先前烟测且成功时先立即持久化索引的默认资源连续实验**。不是再次用新轮次只读证明buffer count语义，也不继续排RMM/非默认stream。

## 1. Git和真实raw交叉核验

| 条目 | 独立读回 |
|---|---|
| 执行branch | `hrl/aiarch-a50g-glove100-default-native-full-109-v1` |
| 原启动commit | `ea32eb190cf9697556f3560263b7a637563c69e7` |
| 最终commit | [`d74ba0225516e60aa1c18b7ee87c88abfc34e0c9`](https://github.com/swayhrl/accel-sim-framework/commit/d74ba0225516e60aa1c18b7ee87c88abfc34e0c9) |
| Git-data tree | `13a7487e6b40e653a8bc0cfa799c325ef224e46c` |
| 报告blob | `a403428cd9eac33a8b1e4f0bce7553d3be82fd837` |
| `raw/build_qualify.log` blob | `08a7d404985a3c4639defff7776873df744e79e7` |
| `raw/build_observation.json` blob | `0ab82c497a1c7f16032d6e3f3ff5f03f5b34e99b` |
| 修改范围 | 启动→最终ahead1/behind0、**21个全新证据/本次工具文件**，没有动原协调/其它accepted实验；最终branch HEAD与commit`identical` |

固定报告：[A50G FINAL_REPORT](https://github.com/swayhrl/accel-sim-framework/blob/d74ba0225516e60aa1c18b7ee87c88abfc34e0c9/docs/ai_workload_research/runs/AI_ARCH_A50G_GLOVE100_CAGRA_DEFAULT_FULL_109_V1/FINAL_REPORT.md)；[原日志](https://github.com/swayhrl/accel-sim-framework/blob/d74ba0225516e60aa1c18b7ee87c88abfc34e0c9/docs/ai_workload_research/runs/AI_ARCH_A50G_GLOVE100_CAGRA_DEFAULT_FULL_109_V1/raw/build_qualify.log)；[修正版未运行源码](https://github.com/swayhrl/accel-sim-framework/blob/d74ba0225516e60aa1c18b7ee87c88abfc34e0c9/tools/aiarch_a50g/native.py)。

**独立代码判断**：原`native_executed.py`中`Buffers.__init__`的query、ID、distance pinned view均缺`count`；`native.py`中的三种view均有`count=b*100/b*10`、校准1792和报告2048的host pinned区域也加`count`；已读`supervisor.py`只是按固定阶段`build_qualify→measure0/1/2`串行启动，旧代码故障后不做二次full build。新功能代码保存步骤已在`build`五字段PASS后、在功能`evaluate()`之前，此序列属合理但尚未跑通。

## 2. 更完整的执行前反证：不应再让包装问题浪费唯一build

原CPU资格只做版本/AST/参数字段，没有真正生成B1 GPU pinned views，因此发生实际运行包装错。**下一Goal除原有CPU验证外，必须在唯一完整base GPU build之前进行小型、明确标为engineering smoke的GPU链路**（若新合同批准）：

1. 只读复用冻结原venv及原数据，new branch/worktree/预算。静态固定全部`Buffers(1),Buffers(256)`、校准1792与正式2048的query/ID/distance pinned views，要求其长度/shape/dtype、contiguous、C/H2D/D2H传输实际roundtrip在原冻结CuPy14.0.1 GPU路径PASS。验证会占本轮GPU锁，但不占真实full-base build额度；没有合法CUDA/包版本则STOP。
2. 至多**一次1024×100合成tiny CAGRA构图**验证`cagra.save(include_dataset=True)→cagra.load(Index(),out_dataset=Dataset())→同步→索引字段→合法实际search B1/B256与结果范围/距离基本一致`。tiny结果仅是API包装资格，不是完整GloVe search/recall，也不允许重新引入非默认stream/pool。若tiny save/load/search不合格，**STOP，不消耗真实完整构图**。这属于上一轮缺少的决定性契约完整性审计，不是增加一条科学负载。
3. small smoke通过之后，**才**在同一GPU持锁/统一45min累计额度里允许**一次**完整官方base CAGRA build。字段PASS后**立即save/include_dataset/hash成功落盘**，绝不能先调用任何search/Buffers/质量逻辑；新的checkpoint便是可恢复边界。必须在save完成后记录bytes/hash并验证同版本load/owner。保存失败导致没有合法checkpoint，full build额度已消费，后面STOP；不得再建图。
4. 首次checkpoint存在后，后续search/校准/测时若只遇合法确定性包装错误，可在**同一个Goal/共享锁总额度内**限定最多两次工程修补并以fresh process**load-only**继续；不得第二次full build、改变输入/搜索参数/recall/预冻结query或偷偷挑结果。真实数值/质量失败、未知native SIGSEGV、ABI变化一律STOP，不用工程恢复绕过。
5. 继续保留原A50G `G2质量门、G3四正式点（B1/B256 × AUTO/calibrated SMALL）和完整`host wall`分母；三fresh processes/10 ABBA blocks以及source/no-report-peek。完整失败也写`NOT_RUN`，不能声称硬件无机会。

**这个恢复设计不需要新模型/索引算法或数据集**，只增加第一次合法GPU smoke和新一次full build额度。更高层硬件、NCU/模拟器全部维持冻结。

## 3. 资源成本与接受边界

A50G历史采样：GPU锁`3.959299s`，RSS采样`2,817,036,288B=2.624GiB`，GPU显存采样`1600MiB`、新文件`5,771,264B≈5.50MiB`、CPU准备`278.173s`、下载/安装`0`、无外部锁争用。模型/真实GloVe全图数据已经在109就位。**这些值不证明save/load与正式search的峰值**，下次新盘2GiB、RAM8GiB、VRAM12GiB、GPU锁45min仍是受控预算，不是估计必定能过。

**固定接受分层：** `FULL_BUILD_FIELDS_PASS`、`INDEX_SERIALIZED_AND_RELOADED`、`NUMERIC_AND_RECALL_QUALIFIED`、`FOUR_SCOPED_NATIVE_POINTS`、`RESOURCE_CAUSAL_ATTRIBUTION`是不同门。前一门完成不自动代表下一门；同时只要已获批准，工程包装正常应在同一Goal有界solve-and-continue，不能再写一个“等待确认的回合”人为拆分已批准科学过程。

## 4. 后续选择与科学价值

**推荐唯一下一真实执行：A50GR1**（固定默认Resources的GloVe完整search任务，前置tiny save/load/search smoke，单次full build立即checkpoint，之后load-only恢复，四点同质量）；不把原A50G已STOP的剩余GPU锁时间当重新可用，必须以新独立预算执行。用户此前明确“后续默认确认，有意见再说”，且本次场景/节点/精度/质量门/上限都与已披露上轮相同；在这项**范围不扩大的新实验**中可直接附完整Codex Goal与一键复制指令，仍不能声称用户已经启动109。

**止损：** 如果tiny smoke失败（又有API包装/库不合格）、full build native失败或save/load失败且无合法checkpoint，**停止该软件路径当前平台排障，回到A51–A55 Q-V/Q-G源审选择下一方向**，不再连续授权A50GR2尝试用更多构图次数“碰运气”。若成功且AUTO足够，收口ANNS Q-A，继续神经网络方向。即使SMALL稳定胜AUTO也首先是软件配置差异，若要硬件资源因果必须另审一次有价值的instrumented/模拟器独立合同。

**权限**：本A56审查是Git/source-only，不是新的GPU运行。真实A50GR1必须按新Goal和原shared GPU lock独立执行，并在实际Codex回执之后才标RUNNING/STOP；AWMA/C16及其它node history不受影响。