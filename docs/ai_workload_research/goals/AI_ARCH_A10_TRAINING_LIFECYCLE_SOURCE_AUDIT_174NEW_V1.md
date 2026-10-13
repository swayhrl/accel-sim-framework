# Round A10｜训练激活生命周期强软件源码资格审查

**执行者：Codex Lane P／174-new CPU/source-only（新独立窗口）**  
**科学协调与独立审查：ChatGPT／AI-ARCH Discovery**  
**Goal：`AI_ARCH_A10_TRAINING_LIFECYCLE_SOURCE_AUDIT_174NEW_V1`**  
**任务状态：PREPARED_GOAL / AWAITING_LANE_P_START（写入本Goal≠Codex已经启动）。**

## 0. 独立性与科学目的

109的**Lane M**现有`AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1`从固定NequIP、真实Si结构、CPU/GPU构图到四条件原生观察，**已由用户报告正在执行**。本Goal完全独立，不需读取Lane M进程、改其环境/缓存/模型、监测进度或动其GPU锁。

**研究问题Q-T10：** 2026年TorchTitan/GraphTrainer已经提供联合图级的激活保存、重计算、CPU卸载，以及MoE静态capacity-padded activation的paged stash之后，什么资源生命周期限制仍可能构成新的P01/P13发现性问题？能否从**公开训练输入＋现有强后端**得到有意义而不偷换模型的最小科学对象？

目标是**强软件能力资格矩阵与输入身份核查**，不是实现Offload、重复跑作者H100 benchmark、复现Slackswap、调配CUDA或开GPU任务。即使结论是`NO_SINGLE_GPU_TRAINING_PAIR_QUALIFIED`也是合格交付。

## 1. 唯一协调/历史入口（先去重）

- GitHub仓库：`swayhrl/accel-sim-framework`。
- 在开始时fetch/核对`hrl/ai-workload-research-coordination`上本Goal和`CURRENT_STATE.md`、`COORDINATION_PROTOCOL.md`、`AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md`与[Round A6训练T1–T4](../literature/AI_ARCH_ROUND_A6_NEQUIP_PATH_AND_PUBLIC_TRAINING_2026-10-13_V1.md)。最新协调HEAD为本Goal发布后再报告，**不得假设现有Lane M Git HEAD或实时状态**。
- 既有[Lane T训练source review固定提交`a1a70180736499687435b1e2d99984d4ebba4c53`](https://github.com/swayhrl/accel-sim-framework/blob/a1a70180736499687435b1e2d99984d4ebba4c53/docs/ai_workload_research/reviews/AI_ARCH_A4_TRAINING_SOURCE_REVIEW_174NEW_V1.md)：**不重审**MegaScale-MoE 352B。
- 方法参照候选分支`1a7f8d5d6f01326da161f52447eee013d1a630ec`中的两套Skill markdown，**只读方法、不开CLI自动Skill安装、多Agent和hooks**。

## 2. 直接固定源码：只查与问题有关的实际调用

**源码快照（代码能力，不是作者2026年6月报告的确切运行版本）：**[pytorch/torchtitan@8a75afd90773fe410340e0709b0b1af427c4af58](https://github.com/pytorch/torchtitan/tree/8a75afd90773fe410340e0709b0b1af427c4af58)。逐个抓指定文件，记录blob/ref及确切symbol位置，不全仓克隆。

优先最多10个相关文件，先审：
1. `torchtitan/experiments/graph_trainer/configs.py`的`GraphTrainerCompileConfig.memory_policy`、`cpu_offload_*`与`PagedStashConfig`。
2. `torchtitan/experiments/graph_trainer/memory_policy.py`的`tag_with_memory_policy_pass`与`MUST_SAVE / PREFER_RECOMPUTE / MUST_CPU_OFFLOAD`，核不同policy是否共享相同前向与数值合同。
3. `torchtitan/experiments/graph_trainer/cpu_offload.py`：selection、event/wait、重用内存池/forward-backward边界。**不要把“源代码注释说完全隐藏传输”提升为已实测**。
4. `torchtitan/experiments/graph_trainer/paged_stash_memory_policy.py`只查引导说明、静态capacity因果对象、overflow/opt-in条件及关键函数，不需要阅读/转写整个158KB文件。源码自称是**Megatron-Core 0.19.0移植**，需与真实应用区分；内置round-robin debug是synthetic routing，不能拿来代表自然MoE调度。
5. `torchtitan/experiments/graph_trainer/passes.py`与`torchtitan/experiments/graph_trainer/README.md`核组合顺序、版本需求、GraphTrainer主要运行对象。
6. `torchtitan/components/data/text_datasets.py`与实际公开recipe配置：核自然C4或明确数据输入接口的字段、是否已经固定revision/tokenizer、是否有可在单RTX4080 16GB做**完整合法训练步**的小公开模型。不应为了硬凑结果把debug模型称为8B的等价缩小。
7. 如确有必要，最多检查一项小型单元测试或作者recipe以辨别数值/overflow/运行模式（**代码存在≠测试已在本机通过**）。

**作者直接原文（本任务只用作具体实验对象定位，不重新精读整篇）：**[PyTorch DevLog@74462e4bd312dbd9763358dc528968754b7bc536](https://github.com/pytorch/devlogs/blob/74462e4bd312dbd9763358dc528968754b7bc536/content/distributed/2026-06-23-cpu-offloading.md)，约10KB，8×H100 96GB的Graph-based CPU offloading，明确区分Llama3、Qwen3与DeepSeek-V3的budget、defer、token身份及原始指标。

**重要“软件已解决”对照：**GraphTrainer的`sac_and_offload`与`sac_and_paged_stash`，第二项是静态capacity factor的MoE不同机制，不可与普遍CPU卸载合并计功或声称是新硬件空白。SimpleFSDP结果沿用A6、不重复广泛调研。

## 3. 必须实际回答的六个审查问题

1. **三种资源明确分开**：保存占HBM，重算增加GPU算术/同步，offload占CPU DRAM/host-link带宽；paged stash减少静态padded token存储但引入pages/overflows。哪些现有policy已经实现了竞争方案？哪些只是代码/注释能力？
2. **真实输入资格**：C4或其它公开输入的revision、split、shuffle/token packing、tokenizer、起点与数据顺序是什么；若源文件无法证明，明确标记`MISSING_REAL_TOKEN_IDENTITY`。不得拿随机input冒充自然训练的任务比例或完整训练真实性。
3. **最强同语义基线**：同一模型/训练步下，对`SAC/save`、`SAC+offload`、`paged-stash`哪些可以合法相互比较；哪个本质只服务MoE capacity-padding而不可比；是否需要改变optimizer/pipeline schedule/EP，不能强行使它们等价。
4. **单卡与多卡不能偷换**：报告中8×H100 NVLink C2C/NUMA/通信对应源码或平台范围；RTX4080 16GB只为可能的未来本机诊断，不得继承300GB/s link或多卡PP/EP。给出真实可选的单卡模型或`NO_4080_FIT_ESTABLISHED`（不能靠模型参数量凭空推断显存PASS）。
5. **数值与完整时间**：是否有bitwise/numeric source constraints；需同时报train-step throughput、GPU peak HBM、host peak和host link copy与计算overlap，不能仅用activation saving百分比宣称速度。
6. **因果与可停止**：从现成能力中给最多一个**真正未测且可证伪**的训练资源转折候选（或否定），含竞争解释和最小资源条件；不建议普通“再做一份offloader”机制。

## 4. 严格资源与软件隔离

- 执行地点：**174-new，CPU/source-only**，新独立worktree（若已有git工作树只做小size独立分支），在开始时检查磁盘、swap、进程；此前174根盘满、swap满，若不够只用远端GitHub API读取固定source，省下本地文件写入，不清理现有其它任务文件。
- 一个Codex窗口，**不启动多子Agent**。不运行torch/JIT模型、CUDA、NVBit、Accel-Sim、模型下载、训练脚本或数值kernel；不连接109/164或操作其锁/缓存；不修改AWMA/C16/Sobek/DTC-L1执行工作区。
- 本任务不pip安装任何框架、不全量clone TorchTitan、不编译任何源码；只允许必要的轻量GitHub读取和少量Markdown记录。原始源码/证据可用GitHub固定ref查看。
- 只有普通路径/读取包装问题可在小范围solve-and-continue。发现论文/软件版本不同，分别冻结事实，不为了报告漂亮而改动源模型或凭空计算显存。

## 5. 单一交付与STOP

**只新增一个**Markdown：
`docs/ai_workload_research/reviews/AI_ARCH_A10_TRAINING_LIFECYCLE_SOURCE_FEASIBILITY_174NEW_V1.md`

内容：来源表（固定blob/确切只读范围）、功能矩阵（save/SAC/offload/paged-stash）、公开实际model/input身份、样本与设备适用性、已有强软件覆盖、至多一张可证伪问题卡及最低成本验证反例。每一个实测数值明确标`PAPER_AUTHOR_NATIVE_8H100`或`AUTHOR_CODE_ONLY`，未披露/未核实分开。结论标签限：`STRONG_SOFTWARE_CAPABILITIES_CONFIRMED_SOURCE_ONLY`加`SMALL_TRAINING_PAIR_FEASIBLE_SOURCE_PENDING`或`NO_VALID_SMALL_TRAINING_PAIR`。

在**自己独立branch**提交/推送，仅写本文件，远端fetch-back SHA与Git status审查后STOP；不合并/更新协调分支，ChatGPT窗口随后独立审阅。若压根没有充分证据/源码不可达，报告`SOURCE_BLOCKED`并按证据STOP。不得请求/自动启动任何GPU、模拟器、training或新的GraphTrainer性能campaign。
