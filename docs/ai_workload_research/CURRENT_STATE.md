# AI-ARCH｜当前科研协调状态

**最新快照：2026-10-16 / Round A69，Q-S真实点云自然训练层组的源码资格审查完成。** 维护者：ChatGPT／AI-ARCH Discovery。本页为科研导航，不是节点实时监控；文档发布不产生GPU、Codex或节点作业授权。

**历史导航完整保留在[CURRENT_STATE@A68](https://github.com/swayhrl/accel-sim-framework/blob/177dc378cd949ec9bfc45a244a6cb33251fadfd3/docs/ai_workload_research/CURRENT_STATE.md)。** 本次将不断叠加的旧待办快照改为固定历史指针；没有删除或重写任何原始Goal、运行报告、raw、独立审查或实验branch。旧导航中的“待启动”仅代表当时状态，不能覆盖以下已接受终态。

## 1. 当前研究对象：Q-S源码候选已具体化，尚无原生准入

完整交付：[A69 Q-S ScanNet/MinkUNet34源码资格、强软件与映射寿命](literature/AI_ARCH_A69_QS_SCANNET_MINKUNET34_SOURCE_ADMISSION_2026-10-16_V1.md)。报告首次发布commit：`ddb127907f37c97c94e9db7aa764d1cf3cb3dfa6`。

- **选定自然对象**：ScanNet/OpenScene真实coords、RGB、labels，经WarpConvNet PointToVoxel、MinkUNet34，研究`inner_module.block1`的两个BasicBlock、四个32→32、3×3×3、stride1卷积。相邻conv2→block2作为空间支撑变化对照。实际场景、活跃体素数、时间权重、activation/gradient实体均尚未取得，不称已通过原生数值或性能门。
- **真实梯度生成路径已从源码核清**：场景输入→实际增强→体素均值池化→完整模型→unpool回原点→真实标签交叉熵→反向。可明确以冻结初态的早期训练作为未来发现范围，不强制先做全模型收敛；但不得将独立卷积的随机feature/随机上游gradient称为真实训练状态。已训练checkpoint及任务质量主张需要相应额外证据。
- **强软件边界**：Spira当前公开E2E脚本用场景坐标、随机FP16特征、eval/no_grad前向；可以反证映射/前向数据流，不能直接作为MinkUNet34完整训练基线。WarpConvNet已经跨层传递map cache、为autograd保存映射、缓存正反向布局并分别优化dgrad/wgrad；TorchSparse也有跨层/转置map复用。不得将已有映射缓存或反向构图重命名为新机制。
- **本轮精确问题**：这些已有复用生效之后，多种执行布局的准备、同时存活及最后消费是否仍造成重要时间或容量代价？四个module引用不等于四份映射，层前向完成也不等于映射生命周期结束。代码中的对象大小不是L2压力或性能headroom。
- **执行前缺口**：本轮未查得项目ScanNet许可批准/合规共享记录及一个可信场景实体；这不等于认定用户没有许可。尚未验证109 SM89后端ABI、实际样本资源和数值。loader可能自动下载，禁止因实例化Dataset而意外抓取整包或接受条款。下一步先确认现有数据权限与场景，再一次设计新的有界原生资格/筛查合同；当前没有新GPU Goal。
- 固定源码：WarpConvNet `f9474304bbfe94bf7ffe0f8dbbcc468c1ff0ceb1`；Spira `aee69c61f3e001f72828a6d5a70f6a1200166f65`；TorchSparse `385f5ce8718fcae93540511b7f5832f4e71fd835`。各已读文件blob与具体边界见A69报告。在线说明与训练源码默认值有差异，以将来明确冻结的实际配置为准，不拼接默认参数。

## 2. 已冻结GNN证据：A61／A65／A67

| 阶段 | 原生authority | 已接受结论与范围 |
|---|---|---|
| A61 | `37120f98186b83a946f4812755523f5d73245491` | 官方IGB-small、eager FULL/ON资格通过；编译更新复合断言失败，旧差异未捕获；原STOP保留 |
| A65 | `3cdf0489b0b3a2cbbb4081e6dd13044f7ec70f79` | 新冻结batch三路中A/B通过，C的1/665619更新元素超原门；微小梯度差经Adam放大，未证Torch bug；退出PID收据缺口仍保留 |
| A67 | `c425819d1f41e0cbd3053315cd5590697e808a3c`，tree `5ae9be2bf51ba959b9588a8111ae28bf6f03af84` | `SCOPED_FULL_RESIDENT_SOFTWARE_ALTERNATIVE / STOP`；两个seed的12次eager完整训练步均FULL快于OFF快于ON；本小图缓存硬件供数路线停止追加实验 |

A67六窗口：seed20261015 FULL/ON/OFF为0.310875/1.788362/1.125985秒；seed20261016为0.435467/1.771150/1.100231秒。1资格＋12warmup＋72formal=85次更新，原图与4.096GB真实FP32特征可全驻GPU。两seed短窗、独立合法采样非逐边配对，准备成本另账；不证明所有GNN皆可驻留、具体PCIe瓶颈、编译强路径资格或最终收敛。

A68独立重算六wall SHA256为6/6 PASS；本次41条PID快照中33条OWN_LIVE_PID、8条空，无第三方记录，终态已退出释放锁。A67新监督闭合不回写A65历史缺口。[A68完整科学审查](reviews/AI_ARCH_A68_A67_IGB_SMALL_EAGER_FULL_RESIDENCY_INDEPENDENT_REVIEW_2026-10-16_V1.md)、[A66审查](reviews/AI_ARCH_A66_A65_SAME_BATCH_NUMERIC_AND_STORAGE_INDEPENDENT_REVIEW_2026-10-16_V1.md)、[A64审查](reviews/AI_ARCH_A64_A61_GNN_NUMERIC_STOP_INDEPENDENT_REVIEW_2026-10-16_V1.md)与[图谱P15](AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)保留。

## 3. Lane、权限与后续动作

- **109 Lane M**：用户最后回报A67 COMPLETE/STOP；本窗口未获新GPU任务、数据下载、清理或编译授权，不重新启动A61/A65/A67。
- **174-new Lane N、164**：本轮无新任务、资产扫描或数据传输；既有独立项目工作不受影响。
- **ChatGPT Discovery**：A69源码阶段完成；等待真实场景与使用权限信息以判断是否形成新原生合同，不为同一已读范围重复开多轮源码资格。
- **A62/A63稀疏权重训练**：继续文献/source条件储备，无新GPU准入。A26GR1/3DGS、A50G/CAGRA、A59数据门等历史原始结论和保护资产见固定A68导航，不重新解释或自动恢复。
- **C16、AWMA、ISCAS**：各自科学authority和资源授权不继承；不合并实验HEAD，不动当前独立执行。

统一遵循[协调协议](COORDINATION_PROTOCOL.md)：真实科学问题→强软件反证→必要时有界原生发现→独立审查；允许普通工程同Goal有界solve-and-continue。源码能力、作者实验、我们的推导与本机native分开。局部kernel-family、自然覆盖率与端到端价值分层判断，既不凭buffer数量立硬件机制，也不以单一端到端百分比淘汰所有候选。

**当前无新109／174／164执行任务；A69是已完成的源码研究交付，不是实验启动通知。**
