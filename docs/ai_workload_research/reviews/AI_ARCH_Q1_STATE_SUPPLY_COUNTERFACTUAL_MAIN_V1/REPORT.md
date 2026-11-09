# Q1 状态供给反事实：CPU-only 独立研究报告

2026-11-09。**决策：建议仅保留一个后续判别对象——晚期 T16 的 `shN` 状态 GPU 驻留，严格保留原 deferred 更新和下一 camera 的版本边界。** 当前证据支持提出可证伪实验，不支持宣称它能装入 109 的当前共享容量、能加速 OFF 完整窗口或已满足数值资格。本轮只做 CPU 源码审查、已关闭记录复算和条件模型；没有新训练、GPU 调用、checkpoint 恢复或生产代码改动。该结论为 Main 报告，**待 AI-ARCH-5 科学审查**。

## 固定身份、方法和范围

- 执行 `5787826ca21f7af958e6e1c1f828d62fd58a1ec4`；工程交接 `00abf55d44ad02a18d529eb0afe4d02dc0ceadfe`；已获科学窗口接受的有限独审 `06355f73caaa6f38697d9acac94ac81a47c27e62`。前者是本报告的 Q1 数据 authority，独审是有限结论 authority。
- 固定原 trainer `simple_trainer_hybrid_optimized.py` SHA-256 `17e70b64…f4808a`，CPUAdam C++ `cpu_adam.cpp` SHA-256 `f3f32bc0…19ce9f`，CPUAdam binary `c451fda9…37a55`；源代码与 binary 身份由 Q1 `BINARY_IDENTITY.json` 绑定。原 trainer 路径是 `/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014/software_sources/gsscale/examples/`，C++ 在同资产 `cpu_adam/src/`。
- 输入为 Rubble/downscale4、原 T16、晚期 `N=6,720,398`。`C_D(next15140)`、`C_V(next15240)`、`C_FINAL(next15301)` 的固定状态检查与 frontier 沿用执行和已接受独审；本次没有重新读取约 19.5 GB 私有 tensor。`STATE_SUPPLY_MAP.csv` 列出对象和代码位置，`SOURCES.json` 给出这次实际读取的小文件字节与 SHA；`recompute.py` 用标准库复算容量与诊断局部区间。

## 数学、版本与不可省的工作

GPU 常驻 `means/scales/quats`，其梯度、Adam moments 和逐步 `optimizer.step()` 均在 GPU（trainer 314–340、354–371、669–728）。CPU 持有 `opacities/sh0/shN` 的参数、dense 梯度、两份 moments；CPU optimizer 的 step 为各参数组状态。`opacities` 转发前要应用 sigmoid；`shN` 有 45 个 FP32 系数／Gaussian。不能将全部训练状态描述成 CPU 更新，也不能用标准 GPU `torch.optim.Adam` 直接替换三类 CPU 参数。

以当前 camera 为 `t`：GPU 子线程处理 `t`，主线程使用上一步保存的 `valid_ids_cpu_prev`、梯度和计数器执行 CPU deferred 更新。`calculate_update_ids` 在全量 `N` 上取 `U=V(t-1) ∪ {id | counter[id]==15}`；对 U 调用三组 `adam_deferred_update`，之后全量 counter 加一、U 清零，并只清前一可见集合的梯度（trainer 1023–1075、C++ 208–297）。CPU step 在主线程增加；C++ 用 step 的 bias correction 和每 ID 的 counter 计算跳过期的 moment 衰减／补偿（C++ 300–379）。零梯度不代表可以丢掉延迟年龄、历史 moment 或 pending 版本。

GPU 完成 `t` 后，三组梯度从 GPU 叶子按可见集 D2H，写入 CPU dense 梯度（trainer 1113–1157）。下一 camera 经 GPU frustum culling 得到 `V(t+1)`，ID 回 CPU；`adam_for_next_with_counter` **预测下一步可见参数**，读取 CPU 参数、梯度、moments、counter，按 SHN 约 180000 行分块写入 pinned host staging，再 H2D 到 GPU 消费张量；sh0 和 opacity 也生成、转发（trainer 1241–1292；C++ 382–460）。这段包含修正计算、gather、物化、转换及 enqueue，并非纯 copy。代码的 `eps=1e-15/sqrt(BS)` 是 Adam 分母常数（原类默认 `1e-8` 被构造实参覆盖）；`counter==15` 是强制更新年龄规则，两者不能混为一个“epsilon 门”。C++ 还启用了 FTZ/DAZ；更换后端或浮点次序须独立判数值。

正常晚期闭合窗口的版本 frontier 是 GPU 已处理 `t`、CPU 已应用至 `t-1`、CPU 仍存 `t` 的 pending 梯度、下一 camera `t+1` 已准备。`C_FINAL` 明确为 GPU `15300`、CPU 至 `15299`、pending `15300`、prepared `15301`。计时的 50 个目标 camera 加一个 closure 步闭合目标 credit，并保留合法下一步 pending；不把末态说成全训练队列清空。densification 路径会全量 CPU 更新并重置 counter，晚期 `refine_stop=15000` 内的方案不能直接外推早期峰值。

## 观察、候选软件反证与净收益

三组 ON 诊断的完整 51-camera Host 窗口中，发现 T16 的 CPU Adam 为 `3.4156 s`、全部参数转发 `2.5410 s`，两者合计 `75.5867%`；验证 T16 为 `3.3056/2.4346 s`、合计 `74.6992%`。逐 tag 重算的 `shN` **转发 Host 函数区间**为发现 T16 `2.1425 s`、验证 T16 `2.0462 s`；它包含 C++ 预测生产，未测其单独 H2D 硬件服务，也不是可直接回收的完整应用时间。`CPU Adam` 没有按 shN 与另外两组分开的计时。显式 join/sync 并集仅约 `0.0130/0.0080 s`；自然 pipeline 已经有重叠，清除一个函数耗时不保证窗口同幅降低。

原实现已有可见集索引、`shN` 分块 pinned staging、CPU预测 `adam_for_next_with_counter` 与 CPU/GPU 重叠。单纯“增加分块”“省一次 ID scan”或“改为普通 GPU Adam”分别被现有实现、约 `2.5%` 的 ID 选择区间、以及 deferred 语义约束限制。CLM 的 camera/visibility reuse 和调度、TideGS 的异步工作集已有近邻；本轮没有将它们移植成同语义实测，也不把想法重新命名为硬件创新。`SOFTWARE_EXCLUSION.md` 的 SOURCE_ONLY 范围保留。

唯一候选是将 `shN` 的参数、moments 与必要 pending 梯度在 GPU 维护，以相同 `U`、counter 年龄、step/bias 和前瞻式 `V(t+1)` 生成 GPU 消费版本；opacity/sh0 和 GPU 原有三组保持原路径。它可能省去 `shN` CPU update、pinned 预测物化及 H2D，但会新增 GPU deferred 更新、counter/ID 协调、状态迁移和可能的重叠损失。属于**数学形式拟保留、后端及浮点次序变化，数值资格尚待验证**的类别；不是本轮已经等价的软件优化。跨 camera 仅凭重复 Gaussian ID、相邻 camera 或聚合 `U/N` 无法推算版本命中率，缺 ID/版本轨迹则缓存收益为 unknown。

以同一 OFF 闭合窗口的关键路径定义净收益条件：

`removed_CPU_critical_path + removed_required_transfer_service > new_GPU_deferred_and_forward_work + new_ID_counter_metadata_conversion + lost_CPU_GPU_overlap + capacity_side_effects`。

上式各项在当前证据中未被同钟、同语义配对量化，故 `FOOTPRINT_AND_CONDITIONS.json` 保留 null。ON Host 区间只定位劳动所在；不能从 OFF 减去 ON 75%，不能将逻辑 H2D/D2H bytes 除标称带宽，也不能用未校准 CUDA event 减 Host monotonic。

## 去重容量条件

对晚期 `N=6,720,398`、FP32、SH degree 3，`shN` 每 Gaussian 45 个 float。若全量 GPU 驻留，`shN` 参数＋两份 moments 的唯一 dense storage 是 `3.379784 GiB`；若同时持有 full dense gradient，则为 `4.506378 GiB`。CPU 三组参数＋两份 moments＋dense gradient 为 `4.906945 GiB`，另有 N 字节 counter。GPU 已有三组参数＋moments 至少 `0.751063 GiB`，梯度如同时存活再计 `0.250354 GiB`。这些只按不同 storage 相加，原状态检查报告的 storage alias group 为空；view、pinned staging、GPU 消费张量和 snapshot 文件不能被当作同一类或重复加。实际分配、reserved 与 NVML 口径互不等同。

必需条件是 `max_t [Σ 同时存活的唯一 GPU storage bytes + allocator/framework reserve] <= 当轮共享门实际可用容量`。`shN` resident 在迁移期是否与原 CPU 副本同活、dense pending 是否可合法替成 sparse、`V(t+1)` 张量、raster workspace、临时转换、峰值相位和共享占用均未知。W1 的自身 NVML 峰值 `3778 MiB` 与 W2 的 `3482 MiB` 是**旧执行峰值**，不是反事实同时峰值或现在的空闲空间。下界低于 16 GiB 只能表示尚未被容量排除；不能授予可行或早期 densification 适用结论。

## 唯一最小判别方案（仅设计，未执行）

**竞争解释。** H1：`shN` 的 CPU 更新／预测／转发位于晚期 T16 的关键路径，保留 deferred 语义的 GPU 驻留可降低完整 OFF 窗口。H0：新增 GPU 工作、版本协调、真实传输、驻留容量或失去重叠抵消收益；原 T16 已经隐藏大部分该工作。现有 ON/OFF 分池与未校准时钟不能区分。

**受控变量。** 只变 `shN` 的 owner/更新与前瞻生产位置；原 T16、固定 trainer 数学、Rubble 输入、自然 camera 序列、GPU `means/scales/quats` 和 CPU `opacity/sh0` 路径保持。以原 T16 做强基线，分别在 C_D 发现窗和 C_FINAL 独立自然 camera 验证窗恢复同状态；每窗目标 50 camera＋1 closure，确认 target credit 闭合且 pending 下一步只消费一次。OFF 完整时间与 ON 局部诊断分池，记录同一时钟域的 Host 并集、独立 CUDA event、实际迁移/更新/forwarding 字节与时段、逐存储 ID 的峰值同时存活、共享可用容量及清理收据。预先固定数值判据，验证状态、counter、moment、参数、梯度、camera 与质量；原数值敏感性不因新方案而改写。若浮点顺序改变，必须先明确可接受的数值资格；未通过即 STOP，保留差异。

**判别与停止。** 容量／数值门失败则停止该候选，不改 dtype 或算法凑门；通过后，只有两段 OFF 窗口在预冻结误差与资源边界下有完整净收益，并能解释新增 GPU 工作与失去的重叠，才支持继续软件研究。收益为零或负、或原 CPU 工作未落在关键路径，则转为软件/调度结论或范围性 STOP，不升硬件候选。尚未有新资源窗口与具体 GPU Goal；未来执行须由 AI-ARCH-5／用户裁决，走原 Image-Lab 共同 flock、预约、loaded gate、实时身份与结束清理。当前不启动。

## 限制与保留项

本轮没有独立测 shN CPUAdam 子段、真实 DMA／DRAM、逐 ID 版本轨迹、候选同时存活峰值、GPU kernel 代价、长程质量或早期 densification。旧 V1/R1/R2、W1 STOP、Q1 数值敏感性、共享桌面活动遥测缺口和 W2 终止 RSS 缺口均保留。Q1 只支持已接受的晚期原生窗口有限结论；`NO_HARDWARE_CANDIDATE_PROMOTED` 与 Hybrid SECONDARY、Qwen PARKED、MoE 条件路线不变。
