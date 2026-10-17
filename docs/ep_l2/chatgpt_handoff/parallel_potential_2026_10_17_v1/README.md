# EP-L2 并行性能潜力实验与论文续接

本包落实2026-10-17用户新增要求：充分并行测清完整数据访存乐观性能、L2和上下游瓶颈，以及参数/结构条件下EP-L2能实际发挥的性能。首轮预声明50个新实验cells，最多72次新增完整应用启动；原R19的D2/L25八次运行独立续行。所有数量都是计划，发布文档不代表已经启动。

## 直接使用

先读 [PARALLEL_CONTRACT.md](PARALLEL_CONTRACT.md)，再给原Lane窗口对应Goal。Lane5采用 **CONTINUE增量续接**，保留当前现场、旧计数、旧deadline和已有接受结果；Lane6此前EN-v7 Goal已完成，执行一个新的短增量Goal。

| Lane | 文档 | 首要产出 |
|---|---|---|
| 1 | [LANE1_GOAL.md](LANE1_GOAL.md) | 先交付现binary的D2/L25；再滚动集成新结构/Ideal release |
| 2 | [LANE2_GOAL.md](LANE2_GOAL.md) | 等1168总容量S64、U_CAP16、finite bank P2 |
| 3 | [LANE3_GOAL.md](LANE3_GOAL.md) | ROP40、L1_32、ICNT2、Q4下WAD256及受影响检查 |
| 4 | [LANE4_GOAL.md](LANE4_GOAL.md) | 立即恢复分层Ideal，加完整数据访存最小正延迟参考 |
| 5 | [LANE5_GOAL.md](LANE5_GOAL.md) | 唯一registry扩展至4sim，原R19续接，四线就绪任务滚动实测/接收 |
| 6 | [LANE6_GOAL.md](LANE6_GOAL.md) | 从EN-v7增量接收新结果、当前图和未来图接口、成本差分 |

矩阵：[EXPERIMENT_MATRIX.csv](EXPERIMENT_MATRIX.csv)。每个逻辑cell在producer资格、精确runtime身份和资源准入齐备后才可启动；应用完成并通过独立科学接收后才可进入正式结果和论文。不得将计划行直接复制成已完成实验。

## 本次审查确认的最新进展

截至10:43:05UTC：H0五组保留1.0016002037656606；D4原两组0.9997553732076547；Q4两组0.994794657046569；D4 vectorAdd与SAD也均已接受。R19累计12启动/12接受，快照无活动sim，尚等Lane1的D2/L25 producer才能跑已选8次。来源：[Lane5状态](https://github.com/swayhrl/accel-sim-framework/blob/73d3e3eedbfd92643db2f674a49e16605d3e2260/docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/STATUS.md)。

EN-v7已在 [1740009d1579b2402b32076f4f65f27619396c01](https://github.com/swayhrl/accel-sim-framework/commit/1740009d1579b2402b32076f4f65f27619396c01) 发布，作为母稿。当前新增论文接收是Q4 FWT、D4 vectorAdd和D4 SAD，不再等待这三对实验完成。

## 提高效率的具体变化

- 四条科学问题同时准备/执行，不以已有小收益或完整TVD/RO为共同门槛。
- 中央最多4个长sim，仍共用8CPU/32GiB和既有RAM/磁盘下限；独立worktree同时开发和写作。
- Lane1先逐条件释放现成D2/L25依赖，不等大模块；新feature逐项就绪逐项release。
- 单个完整pair/Ideal端点就绪就接收、发布；文稿增量更新，不等全部矩阵，也不反复重写机制正文。
- 结果同时给绝对cycles、同条件B/U、局部与下游压力及成本；理想空间不冒充EP-L2收益，负结果完整保留。

新的campaign期限为首次注册T0后24小时与2026-10-18 14:00UTC（北京时间22:00）两者较早者，最多72次启动。旧R19仍以2026-10-17 17:09:16UTC（北京时间10月18日01:09:16）和cap24为限。该期限是本轮实验执行窗口，不是对投稿截止时间的重新定义。
