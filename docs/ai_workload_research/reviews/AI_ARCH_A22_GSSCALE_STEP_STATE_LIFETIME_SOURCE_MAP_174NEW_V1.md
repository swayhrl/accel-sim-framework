# Round A22｜GS-Scale 每步状态寿命与 CPU–GPU 交接 source 地图

**执行者：Codex Lane T / 174-new / Round A22；2026-10-14（Asia/Shanghai）。**
**性质：CPU/source-only；CODE_ONLY / PAPER_AUTHOR / INFERENCE / UNKNOWN 分层。没有训练、GPU、模拟器、安装、场景下载或跨节点接触。**
**裁决：SOURCE_LIFETIME_MAP_COMPLETE_WITH_INPUT_GAPS；真实 per-step 时间、active-set 复用率及硬件剩余均 UNKNOWN。**

## 1. 独立权威、范围和来源

A22 独立分支初始 HEAD 为 20h 固定协调提交 **47acc712aff232bbb4685746ea68e9cb12bcc0a9**，未从 A21 branch 派生/merge。A21 的只读冻结输入为 [Lane T A21 源审@9575a674e5aa5af60e5803c07399fb64ae2c8488](https://github.com/swayhrl/accel-sim-framework/blob/9575a674e5aa5af60e5803c07399fb64ae2c8488/docs/ai_workload_research/reviews/AI_ARCH_A21_GSSCALE_REAL_SCENE_SOURCE_ADMISSION_174NEW_V1.md)，其 Rubble 场景资产 SHA/训练相机顺序与 109 平台仍待资格化；本报告不代填。代码固定为 [SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932](https://github.com/SNU-ARC/GS-Scale/tree/6471e958f7e318f4870234d8107e0aa91c2d6932)，**不是** [GS-Scale 论文](https://arxiv.org/html/2509.15645)实际运行 commit 的已证明身份。

仅核四份实现文件的入口、状态和屏障（行号为固定 GitHub blob 的物理行，不是网页抽取后的压缩行）；未读可选的 optimized_split.py、未全仓 clone、未运行任何代码。

| 文件 | 固定 blob SHA | 本轮关注 |
|---|---|---|
| [examples/simple_trainer_hybrid_optimized.py](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/simple_trainer_hybrid_optimized.py#L264) | e37d13e3f7514aa81320994dab9853b06a9bb275 | create_splats_with_optimizers_in_hostmem、rasterize_splats、gpu_forward_backward、prologue、Runner.train 的 selected source lines |
| [examples/simple_trainer.py](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/simple_trainer.py#L201) | c16b7b34e277401f675d0f6c9554f73c88df6660 | GPU-only create_splats_with_optimizers、Runner.train 数据/渲染/反传 |
| [examples/simple_trainer_hybrid_baseline.py](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/simple_trainer_hybrid_baseline.py#L247) | 9993a462219d32aa5bd372b3d520f24bdb5fdd28 | naive CPU frustum_culling、rasterize_splats 的 host gather/H2D 与 backward D2H |
| [cpu_adam/src/cpu_adam.cpp](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/cpu_adam/src/cpu_adam.cpp#L208) | f1b40eb4283cfd95c9b26b01448d7275f5aa0958 | calculate_update_ids、update_counter、adam_deferred_update、adam_for_next_with_counter |

## 2. CODE_ONLY：一个稳态 step 的 producer → state → consumer

先规定状态：优化版 [create_splats_with_optimizers_in_hostmem L296–374](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/simple_trainer_hybrid_optimized.py#L296) 把 **means/scales/quats 和它们的 Adam** 留 GPU，把 **opacity/SH 与 CPU Adam moments** 留 host；初始点又经过 Morton 重排。README 的概括性“所有 Gaussian 在 host”不能替代此执行分支的实际选择。valid_ids 是当前数组索引；未经 birth/death 追踪，不是跨 densification 的永久 ID。

| 顺序/producer | 当步产生或持有的 state → consumer | 源码锚点与确定性 |
|---|---|---|
| 0. 初始/前步准备 | prologue 先取 camera、K、像素和 image_id；首步反传后预取下步 camera；训练循环带 shuffle=True，迭代结束重建 iterator → 后续 culling | simple_trainer_hybrid_optimized.py:Runner.prologue:L731–750、L834–850；Runner.train:L985–1009、L1133–1148。**CODE_ONLY**，真实 camera 序列 UNKNOWN |
| 1. 可见集产生 | 下步 camera/K 与更新后的 GPU geometry → frustum_culling_gpu → 当前 row valid_ids；经 blocking valid_ids.to(cpu) 得 host 索引 → host opacity/SH gather | simple_trainer_hybrid_optimized.py:Runner.train:L1140–1151、L1221–1243；prologue:L849–906；rasterize_splats:L602–630。D2H ID 复制标 non_blocking=False，是明确就绪边 |
| 2. 发布 GPU 输入 | GPU geometry 以 valid_ids gather；host SH/opacity 经过 pinned buffer 与 .copy_(..., non_blocking=True)，forwarding 先算下一轮需要的 weight_new → 当前步 GPU render | simple_trainer_hybrid_optimized.py:rasterize_splats:L602–661；Runner.prologue:L900–956；Runner.train:L1231–1292；cpu_adam.cpp:adam_for_next_with_counter:L382–457。**可能**重叠拷贝/计算，源码未给实际 overlap ms |
| 3. 当前 GPU 消费 | GPU thread 读当前 camera、active geometry 与已发布 opacity/SH → rasterization、L1+SSIM loss、backward；GPU means/scales/quats Adam step → render/grad/results | simple_trainer_hybrid_optimized.py:gpu_forward_backward:L664–728；Runner.train:L1023–1031。GPU thread 末尾有 torch.cuda.synchronize；可确定任务依赖，不能由 Thread 存在推满额并行 |
| 4. 上一轮 CPU update 并行支路 | main thread 在 GPU 当前步运行时读取 **前一轮** valid_ids_cpu_prev、CPU 梯度/weight/moments；calculate_update_ids 把有效 ID 与 counter==15 合并 → adam_deferred_update 三类 host 参数 → update_counter | simple_trainer_hybrid_optimized.py:Runner.train:L1033–1069、cpu_optimizer_parallel:L382–418；cpu_adam.cpp:calculate_update_ids:L208–274、adam_deferred_update:L300–379、update_counter:L277–297。该代码**允许** host update 与当前 GPU thread 时间重叠，未测剩余等待 |
| 5. 汇合/提交 | main thread 的 CPU update 完成后显式 torch.cuda.synchronize() + subthread.join() → 读取 results 与当前梯度；GPU info/radii/means2d、opacity/SH grad D2H 复制 → 后续 CPU strategy/next state | simple_trainer_hybrid_optimized.py:Runner.train:L1073–1125。grad.copy_(..., non_blocking=False) 与 GPU→CPU info 读取构成明确同步候选；**同步存在≠已知耗时** |
| 6. 动态生灭分支 | strategy.step_post_backward_only_update 决定 densification；若触发，CPU 端本轮强制全参数更新、step_post_backward_wo_update、重新 cull 并重置 counter；否则让上一轮 ID/update 延迟进入下一步 | simple_trainer_hybrid_optimized.py:Runner.train:L1092–1110、L1159–1237；prologue:L808–906。最后一步强制 flush；数组索引/总 Gaussian 数可变化，ID 连续性必须另建映射 |
| 7. 下一步可见性 | 新 camera + 最新 GPU geometry cull，host state/forwarded weight 随新 valid_ids 复制；返回下一轮 thread 可读张量。下一轮 launch 前又有 torch.cuda.synchronize() | simple_trainer_hybrid_optimized.py:Runner.train:L1133–1151、L1238–1292、L1017–1031。此发布顺序是正确性约束，不能把全部同步当可删除 oracle |

**时间轴含义：** prologue 的 step0 在进入循环前执行；稳态 step t 的 GPU thread 消费已准备好的 t 输入，而 main thread可同时更新 t−1 的 host 状态。thread 完成后的同步、当前梯度回传、下步 camera/cull/forwarding 才为 t+1 建数据。把 CPU update、GPU kernel duration 与 H2D/D2H 各自时间简单相加会重复计算可能重叠区间。相反，把全部 CPU update 免费隐藏也违背源码的显式 join 和 blocking D2H。CODE_ONLY 仅证明结构，不证明具体关键路径、每步 ms、并行度或 cache reuse。

## 3. 三类最小观测字段与合法时间分母

| 类别 | 最小字段与必须记录的边界 | 当前结果 |
|---|---|---|
| **DATA_IDENTITY** | Rubble 原档/合并 COLMAP/缩图的 SHA、图像文件名↔camera intrinsics/pose/point cloud、train/test 排序列表；step、rank、data-loader seed/RNG、camera image_id、初始 splat 排列与作者固定代码/依赖版本 | A21仅锁 URL/源码处理；真实文件 hash、训练相机序列 **UNKNOWN** |
| **STATE_LIFETIME** | stable Gaussian ID + birth/death/densification epoch + 当前 row 映射；每步 camera→valid ID 集、counter/optimizer step、前一次 CPU update 序号、H2D 参数与 D2H grad 的实际字节及 ready/consumed 事件；还要把 densification 前后映射分段 | 目前源码只有当前 row valid_ids 与 counter；**跨步 reuse率、失效事件、CPU state实际活跃比例 UNKNOWN**。8.28% 作者平均当步活跃不是时间复用 |
| **TIMING_WALL** | host monotonic 的完整 step 起止、data prep、CPU Adam、阻塞/同步/线程 join；CUDA event 记录 GPU cull/gather/render/backward/H2D/D2H 的同一时钟域区间，另记录 host pinned/总 RAM 与 GPU allocated/reserved peak；明确 epoch wall 和到固定 PSNR/SSIM/LPIPS 门的真实总 wall | source 的 train 终点 ellipse_time 与 peak allocated/reserved 仅为部分字段；无本机 per-step host wait、copy bytes、event overlap、质量门时序，全部 **UNKNOWN** |

时间需分三种独立目标：**同 scene/相机/有效 Gaussian 规模的 complete_step_wall 与 epoch_wall**；**在 16GB 限制下能否完成及 CPU/GPU peak**；**达到固定质量门的 time_to_PSNR/SSIM/LPIPS**。GPU-only 若 OOM 只供容量判断，不能做时间比的分母。优化版的保存区间 [Runner.train:L1308–1327](https://github.com/SNU-ARC/GS-Scale/blob/6471e958f7e318f4870234d8107e0aa91c2d6932/examples/simple_trainer_hybrid_optimized.py#L1308) 记录从 global_tic 开始的 ellipse_time 与 GPU allocated/reserved，**不等于**每步关键路径分解，也没有 host peak 和 copy bytes。

## 4. 同语义强基线与数值边界

| 路径 | 已知软件行为 | 合法比较前提 |
|---|---|---|
| **GPU-only gsplat** | simple_trainer.py:create_splats_with_optimizers:L201–282 创建全 GPU 参数/Adam；Runner.train:L567–700 取相机、render、loss/backward，并继续 GPU optimizer | 小到能 fit 的**同一真实 scene 与 Gaussian 轨迹**方可比完整 wall；不同 densification/质量轨迹则单列 |
| **naive host** | simple_trainer_hybrid_baseline.py:frustum_culling:L247–295 在 CPU 选 ID；rasterize_splats:L566–630 传所有活跃参数，Runner.train:L829–863 回传各梯度 | 只作消融，不取它相对优化版的收益当新硬件余量 |
| **GS-Scale strong host** | optimized.py:L314–374 selective residency；L602–728 GPU path；L1023–1292 overlapping host step、forwarding 与 deferred update | 强 host 对照。固定同一输入/采样、densification schedule、训练质量、precision/optimizer，测同步与 CPU/host-link 净代价 |

PAPER_AUTHOR：论文 §4.3/§5.5 称 deferred Adam 为小 ε 的近似，Table 3 Rubble 的 PSNR Original26.63/GS-Scale26.62、SSIM与LPIPS四舍五入相同；**质量相近不等于 bitwise 的参数/梯度/optimizer state 相同**。C++ 的预计算 correction 路径与 final denominator 必须分别看：cpu_adam.cpp:adam_deferred_update:L328–376 在权重恢复近似中处理 ε，最终 Adam denominator 仍含 ε。densification/裁剪会改 ID 集和训练工作量；opt-in image split 会多次 cull/梯度累加。不同软件/数值/scene 产生的 Gaussian 数与质量不能用单个 speedup 排序；本 A22 未读取 split 实现，也不把作者“质量不变”转成运行级证明。

## 5. 最小未来观测设计、反例和 STOP

**Minimum future observability instrumentation（设计，不可启动）：** 在单独获批的真实训练合同中，先在**不计时的诊断运行**记录固定相机序列、稳定 Gaussian ID 的 birth/death 与 row 映射、每步 active-set 集合、counter/CPU optimizer 序号、实际 H2D/D2H 字节及数值/质量；这些 probes 不作为正式 wall 样本。随后在保持 scene/模型/强 GS-Scale 配置、正确性门及采样序列相同的有界正式窗口，用 host monotonic 与 CUDA event 捕捉完整 step/epoch 和必要屏障/拷贝重叠，另外记录 host/GPU peak 与 time-to-quality；报告 probe 开销、样本数量和未插桩 wall。**本报告仅提出观测目标，不提供运行命令或 GPU 授权。**

**唯一保留的可证伪问题（INFERENCE，未准入）：** 强 GS-Scale 后，真实自然 camera/active-set 下，CPU Adam 随机状态服务或 next-state 发布是否仍占可观的 complete_step_wall，且无法由现有 forwarding/overlap、camera order 或普通 batching 消除？竞争解释：GPU culling/renderer、同步 D2H 的 ID/grad、densification 长尾、host pinned/copy、CPU state cache、数据加载以及 ε/训练质量差异。反例/STOP：若 CPU 更新与传输已完全被 GPU 覆盖、可见 Gaussian 的稳定跨步复用并不存在、或强 host 对照在同语义和完整 wall 下没有可分辨的剩余，则停止硬件 cache 构想；若 scene/ID 数值身份不能冻结，先止于 SOURCE_IDENTITY_BLOCKED。不能从代码同步点推“新增 cache 可省多少 ms”，也不能从作者不同设备改变资源配比推单变量 P13。

**SOURCE_LIFETIME_MAP_COMPLETE_WITH_INPUT_GAPS。** 当前得到 per-step 的代码顺序与必要发布边，而非本机性能、真实 ID 寿命、质量或硬件 headroom。GS-Scale 已给普通 host offload、GPU cull、CPU Adam forwarding 与 deferred update 的强软件近邻；任何后续硬件机制要先通过实际强 baseline 后剩余关键 wall 的资格门。

**UNATTENDED_20H_CLOSEOUT（A22阶段）：** 独立分支 hrl/aiarch-a22-gsscale-step-state-lifetime-174-v1；起点 47acc712aff232bbb4685746ea68e9cb12bcc0a9；2026-10-14 约 02:00 CST 开始。A21 固定提交只读引用，未 merge；本阶段仅本报告写入，GPU/模拟器/109/164 接触及场景/权重/依赖下载均为 0，A21+A22 worktree 合计约 5MiB，RSS 峰值未单独采样。实际 commit/tree/blob 以发布后 fetch-back 回执和最终回答为准（单份报告不能包含自身 SHA）。A22 发布后整个 Lane STOP，不启动 A23/A24 或任何附加阶段。
