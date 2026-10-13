# Round A10｜训练激活生命周期强软件源码资格审查

**实际执行者：Codex Lane T / 174-new / Round A10。日期：2026-10-13。**
**性质：CPU/source-only；SOURCE_AUDITED、PAPER_AUTHOR_NATIVE_8H100、OUR_INFERENCE 分层。没有本机训练、CUDA/JIT、模拟器或数值执行。**
**裁决：STRONG_SOFTWARE_CAPABILITIES_CONFIRMED_SOURCE_ONLY / NO_VALID_SMALL_TRAINING_PAIR。**

## 1. 权威、资源及固定来源

本独立分支 hrl/aiarch-a10-training-lifecycle-source-174-v1 的初始 HEAD 与固定起点 **dbfb51c9504e10759c34ccb9df85bed739dfce4f** 相同；A4 [Lane T 报告@a1a701807](https://github.com/swayhrl/accel-sim-framework/blob/a1a70180736499687435b1e2d99984d4ebba4c53/docs/ai_workload_research/reviews/AI_ARCH_A4_TRAINING_SOURCE_REVIEW_174NEW_V1.md)仍 STOP，未改其 worktree。启动前 174-new：512 逻辑 CPU，load 约 413，cgroup CPU pressure some avg10≈4.57%、full 0；RAM available 336 GiB，2 GiB swap 已满，根盘可用约 13 GiB；容器进程表无高 CPU 任务。故仅作固定小文本读取与本报告写入，不查询 109 Lane M 运行状态。

先对照 [协调分支@edaca375ed1aed5c338a1af100dc737cfb37c9b1](https://github.com/swayhrl/accel-sim-framework/commit/edaca375ed1aed5c338a1af100dc737cfb37c9b1) 的 Goal、CURRENT_STATE、[协调规则](../COORDINATION_PROTOCOL.md)、[问题图谱](../AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md)、[Round A6 T1–T4](../literature/AI_ARCH_ROUND_A6_NEQUIP_PATH_AND_PUBLIC_TRAINING_2026-10-13_V1.md)及 A10 最近邻报告去重。该协调快照仍写旧计划执行者 Lane P；用户本次明确改为 Lane T，未改变科学合同。候选方法提交 1a7f8d5d6f01326da161f52447eee013d1a630ec 的两份 Skill Markdown 只读作审计方法，未安装 Skill、启动 Agent 或 hooks。

**固定代码快照：[pytorch/torchtitan@8a75afd90773fe410340e0709b0b1af427c4af58](https://github.com/pytorch/torchtitan/tree/8a75afd90773fe410340e0709b0b1af427c4af58)。** 下表是恰好十个相关文件的有界 symbol/行审，不是全仓阅读。blob SHA 由固定 ref 的 GitHub 文件读回。

| 文件（固定 ref） | blob SHA | 实际检查范围 |
|---|---|---|
| [graph_trainer/configs.py](https://github.com/pytorch/torchtitan/blob/8a75afd90773fe410340e0709b0b1af427c4af58/torchtitan/experiments/graph_trainer/configs.py#L100) | 639fbc0c8421ac71ff3eddfbd00a5b5b789412b6 | L100–155 PagedStashConfig；L183–249 memory_policy、offload knobs、数值开关 |
| [graph_trainer/memory_policy.py](https://github.com/pytorch/torchtitan/blob/8a75afd90773fe410340e0709b0b1af427c4af58/torchtitan/experiments/graph_trainer/memory_policy.py#L258) | b0656300177797128354c50b7c373a37dd1de609 | L114–124 default SAC，L258–350 tag_sac_policy，L407–458、L589–629 策略注册 |
| [graph_trainer/cpu_offload.py](https://github.com/pytorch/torchtitan/blob/8a75afd90773fe410340e0709b0b1af427c4af58/torchtitan/experiments/graph_trainer/cpu_offload.py#L355) | aa557f1a381d2497c928c0ad54658d82c6120b9b | 顶部接口/NUMA注释，L172–200 eligibility，L355–439 selection，L445–591 offload/reload/wait，L605–末尾 defer/prefetch |
| [graph_trainer/paged_stash_memory_policy.py](https://github.com/pytorch/torchtitan/blob/8a75afd90773fe410340e0709b0b1af427c4af58/torchtitan/experiments/graph_trainer/paged_stash_memory_policy.py#L6) | 819ee0399fd9f9b55b0d62c9296c83d764fb8559 | **仅** L6–120、L2031–2041、L2405–2420、L2814–2824、L2873–2905、L3261–3324；未通读 3362 行大文件 |
| [graph_trainer/passes.py](https://github.com/pytorch/torchtitan/blob/8a75afd90773fe410340e0709b0b1af427c4af58/torchtitan/experiments/graph_trainer/passes.py#L205) | 426fd4745aad6c126d47df67455760988735780c | L205–241 pass 次序和开关 |
| [graph_trainer/README.md](https://github.com/pytorch/torchtitan/blob/8a75afd90773fe410340e0709b0b1af427c4af58/torchtitan/experiments/graph_trainer/README.md#L1) | dcefc30ad92c101c6d64ab763e594725db623f62 | L1–37 主要模型/版本，L56–96 GraphPP 边界，L159–180 numerics/预编译限制 |
| [data/text_datasets.py](https://github.com/pytorch/torchtitan/blob/8a75afd90773fe410340e0709b0b1af427c4af58/torchtitan/components/data/text_datasets.py#L30) | 2aae2da673ad23ab010f9250cf9258b10fc05eb1 | L30–56 text→shift labels，L218–248 C4 配置 |
| [data/sources.py](https://github.com/pytorch/torchtitan/blob/8a75afd90773fe410340e0709b0b1af427c4af58/torchtitan/components/data/sources.py#L125) | e84e5f9430a77c8c3e00a173a5188a7db012636c | L125–176 revision/stream/DP shard，L207–255 cursor、shuffle/repeat 状态 |
| [recipes/graph_trainer/llama3.py](https://github.com/pytorch/torchtitan/blob/8a75afd90773fe410340e0709b0b1af427c4af58/torchtitan_recipes/graph_trainer/llama3.py#L18) | a0bf65e277190c69b061cdff7c17885641abd018 | L18–42 8B 主入口与 c4_test/autoresearch 派生 |
| [recipes/models/llama3.py](https://github.com/pytorch/torchtitan/blob/8a75afd90773fe410340e0709b0b1af427c4af58/torchtitan_recipes/models/llama3.py#L32) | b28c4abcab9d3f5d38cd2f5ecf9852daab3a446a | L32–66 8B 模型、optimizer、tokenizer 路径、C4 packing；L68–103 70B |

作者原文仅用于实验对象定位：[PyTorch DevLog@74462e4bd312dbd9763358dc528968754b7bc536](https://github.com/pytorch/devlogs/blob/74462e4bd312dbd9763358dc528968754b7bc536/content/distributed/2026-06-23-cpu-offloading.md)，blob **223b3655bb695767d46bdf3014426ee86f6c9b36**，查文本 L6–96。它是 2026-06-23 作者技术报告，不代表上述 2026-10 固定 TorchTitan 快照就是作者的运行 commit。A6 的 SimpleFSDP、TorchTitan v3 组仅沿用已审范围，未重读/复现。

## 2. 四类生命周期策略与已覆盖的强软件

| 策略 / 同一训练步的资源账 | SOURCE_AUDITED 能力与位置 | 科学边界 |
|---|---|---|
| save / no AC | memory_policy 的 none 将前向激活保存；付 HBM 容量 | 不等于零时间成本；容量要按完整 step 的 peak HBM 算 |
| SAC / recompute | default 按算子标 MUST_SAVE 或 PREFER_RECOMPUTE，并强制保存副作用、FSDP 必需值和跨层依赖；full/eager/min_cut 也在配置中 | 重算消耗 GPU 算术与同步，可能改变实际调度；仅改变 policy 不是物理资源单变量 |
| SAC + CPU offload | sac_and_offload **先运行 default SAC**，仅从幸存 MUST_SAVE 中选连续、>=4KiB、非 view/collective 的候选；按大小优先和每 rank CPU 预算选择。apply_cpu_offload_pass 插入 ao.offload/reload/wait_tensor，保留 view replay、D2H defer 与 H2D prefetch | 从 HBM 转移到 host pinned DRAM、双向 host link、等待及 pool；源码的 async/event 路径是功能事实，注释“可隐藏”不是本机或任何条件的零开销实测 |
| SAC + MoE paged stash | sac_and_paged_stash 在标注的 routed_experts 区域，把静态 capacity-padded activation 的 live rows 存到跨层共享 pages，backward reload；先有 default SAC，stash 接管该区域，源码自称移植自 Megatron-Core 0.19.0 | 只适用静态 capacity dispatcher；pages、预取、可选 host spill 和 overflow 有成本。默认 CPU factor=0，即**不作普通 host spill**；不是通用 CPU offload 替代物 |

[passes.py L219–239](https://github.com/pytorch/torchtitan/blob/8a75afd90773fe410340e0709b0b1af427c4af58/torchtitan/experiments/graph_trainer/passes.py#L219) 的次序为 policy tag → CPU offload pass → selective remat → paged stash pass；后一项必须在 remat 后才能避免 backward 仍引用原 padded tensor。**同一配置字段一次只选一个 memory_policy**，不把两个策略的收益机械相加。Paged stash 的示例用 round-robin debug routing、4 GPU 和可选 PP；精确平衡不是自然 MoE 路由分布。默认 deferred overflow 在出错后跳过设备端 optimizer update，但 step/LR/数据位置继续前进并最终报错；blocking 模式每步同步并可禁 paging 重跑。溢出情形不属于透明同语义 A/B，fused Adam/AdamW 限制也不能忽略。

## 3. 公开输入、模型与同语义比较资格

代码中的 **c4** 为 HuggingFace streaming 的 allenai/c4、en/train；TextProcessor 逐文档加 BOS/EOS 后给右移 input/label。公开 llama3_8b recipe 通过 ConcatThenSplitPackingConfig 选 c4，最大 context 8192、AdamW、1000 steps、tokenizer 资产路径 ./assets/hf/Llama-3.1-8B；GraphTrainer 8B 入口继承它。来源接口可接 revision，但 c4 配置没有填；当前十文件未固定 C4 数据 revision/具体 shard 与样本 IDs、shuffle seed 和完整跨 rank 读取顺序，也未固定该 tokenizer 目录的文件 SHA。source 提供 cursor checkpoint 与 DP shard 方法，不等于原作者 token bank 可回放。**MISSING_REAL_TOKEN_IDENTITY** 指这些未冻结身份；不是否认 C4 是公开自然语料。c4_test 是 tests/assets/c4_test/data.json 的测试路径，autoresearch recipe 也继承此测试集，不能当自然 C4 训练性能输入。

| 比较 | 源码可构造的同语义条件 | 当前资格 |
|---|---|---|
| default SAC ↔ sac_and_offload | 固定同一模型、真实 token/packing、optimizer、precision、compiler mode、完整 step 与数据顺序；offload 继承 default SAC，仅调整保存位置/拷贝 | **SOURCE_SUPPORTED / 未执行**；作者 DevLog 报 bitwise claim，但本窗口无逐梯度或 optimizer state 对照 |
| none/save ↔ default SAC | 同一模型与步可比较容量和重算代价，须分别验 loss、梯度、状态与完整时间 | **SOURCE_SUPPORTED / 未执行**；不同 remat 与编译可改变数值路径，不预宣称 bitwise |
| default SAC ↔ sac_and_paged_stash | 必须同一 **MoE static-capacity dispatcher**、route/token、EP/PP schedule、optimizer，且两臂无 token drop/overflow，或把 blocking rerun 算入完整 step | **CONDITIONAL_SOURCE_ONLY**；不能用 dense Llama8B 与 MoE debug 路由比较，也不能用 paged arm 代替普通 offload |
| sac_and_offload ↔ sac_and_paged_stash | 仅在相同自然 MoE static-capacity 工作负载及全部上述条件下，作为两种不同资源支出的端到端 arm 比较 | **NOT_ESTABLISHED**；现有不同实验组不能直接排名，单一 memory_policy 也不自动组合二者 |

GraphTrainer README 主运行例是 Llama3-8B、Qwen3-14B、DeepSeek-V3 671B Dist-MoE，并要求最新 PyTorch nightly；本次查到的自然 C4 主 recipe 为 Llama3-8B。没有已核证据证明这套完整训练步、optimizer 状态、编译图及有效 batch 能在单 RTX4080 16GB 完成。**NO_4080_FIT_ESTABLISHED / NO_VALID_SMALL_TRAINING_PAIR**，不以“参数约 8B”推显存 PASS，也不把 debug model 改名为 8B 的等价缩小。单卡无法继承多 GPU PP、EP、NCCL 和 pipeline 生命周期。

## 4. 作者实测、设备边界与必须同时量的指标

**PAPER_AUTHOR_NATIVE_8H100：** DevLog 声明所有结果在 8×H100、单卡 96GB：dense 模型约 10% peak GPU memory saving 对应 <1% TPS loss；更激进的 Llama3/Qwen3 节约约 33%/38% 对应约 20% TPS 损失。Llama3-8B 的 bs=1、seq=8192、defer=8 有约 12GB budget 附近 TPS cliff；Qwen3-14B 为 bs=4、seq=4096；DSv3 报 8-way EP，defer>=3 可有 24%+ overhead 或 NCCL timeout。这些模型、batch、sequence、并行和预算不同，不能拼成单变量跨模型曲线。作者还报告 view replay 与 pinned pool 消除了部分普通软件开销，并声称数值 bitwise identical；未给本窗口可审的 8H100 逐步输入 token、梯度/状态参考与独立运行日志，故不升为本地数值 PASS。

DevLog 将约 300GB/s 写作“PCIe”；固定 cpu_offload.py 的 NUMA 注释举 **GB200 NVLink-C2C** local 约 350GB/s、cross-NUMA 约 120GB/s 为例。本文未核作者 8H100 的精确 host-link 拓扑；这几种口径不能合成“RTX4080 PCIe 300GB/s”，亦不能用它们预测单卡完成时间。GraphTrainer configs.py 还明确 full Inductor 可能改变 bitwise numerics，numerics_changing_optim 是独立开关；paged stash overflow 会改变有效 update 与数据进度合同。

有意义的受控比较至少同时记录：同一有效 token/optimizer step 的 TPS 与完整 train-step wall（含同步与必要拷贝）、GPU peak HBM、host pinned/总 peak、D2H/H2D 实际字节/时间与计算 overlap、重算时间、等待/overflow/token drop、loss/梯度/optimizer state 数值及较长训练质量。节约 activation 字节或代码中有 async 操作，不足以宣称速度、数值或硬件剩余。

## 5. P01/P13 判断、最小反例与 STOP

**最多一张保留问题卡 Q-T10-R（OUR_INFERENCE，未准入）：** 在同一已验证真实训练步和强 SAC+offload 软件下，改变合法工作量后，完整 step 的时间/容量转折究竟由 host-link 服务、数据 ready 窗口不足，还是重算算术主导？竞争解释含 pinned pool/NUMA、tensor 选择、compiler kernel、optimizer 与数据 packing。最低成本先补公开小模型的模型/初始状态与 C4 revision/tokenizer/顺序、确认单 4080 完整训练步可行，并定义同一后端 numeric A/B；这些源身份/fit 任一失败即 **STOP**，不跑性能。若将来真实执行，需同时有上节分母与三个可区分指标，并保留相同策略 vs 每设备重新选优两种资源响应。仅在一张 GPU 上改 budget/seq 是 P01 负载/软件响应，**不是** P13 的物理 SM、HBM 或 host-link 扩容实验。

当前没有合格单卡训练 pair；普通“再实现 offloader”及 static-capacity page stash 均已有成熟代码近邻。**STRONG_SOFTWARE_CAPABILITIES_CONFIRMED_SOURCE_ONLY / NO_VALID_SMALL_TRAINING_PAIR。** 科学审查至此停止。 本报告不申请 GPU、训练、模拟器、下载或新 GraphTrainer campaign。后续最小缺口为自然 token 字节身份、可完成整步的小公开模型、同配置数值资格及完整时间/容量/链路测量合同；由协调窗口独立审阅后另行决定。
