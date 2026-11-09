# 174-AI-ARCH｜CPU-only 历史接班与节点核对

Goal：`AI_ARCH_174NEW_API_TAKEOVER_CPU_ONLY_V1`。核查日期：2026-11-09。结论：**174-new 的长期资料入口已建立；A4-N 原中文报告仍为不可恢复的局部缺口（PARTIAL_DOCUMENT_INTEGRITY）**。这次只承接证据与节点上下文，没有恢复旧实验或启动新科研任务。

## 证据与身份

- 固定交接：`308d97d76ca557d1e9750c8bb0f56aeef90cbee3`，tree `b594e1d3f42dffe8bb5b8d16160c673ec7c3ca20`，四文件按指定顺序完整读取。15项原报告、10份相关独审和工作流验证记录已按固定对象读取；5份生产者 receipt 同时定点读取。节点资产逐项见 [NODE_TASK_ASSET_INDEX.json](NODE_TASK_ASSET_INDEX.json)，它是 `DERIVED_INDEX`，不重建科学结论。
- 受信 `hrl-174-new` 的非敏感配置指向 `root@10.208.130.174:2239`；现场为 `root`、hostname `huangrulin-sshfs-174`、mount namespace `mnt:[4026535153]`。身份由 SSH 路由、账户、namespace、`/root/workspace/accel-sim-framework` 仓库和15个指定工作树共同绑定；hostname 单独不作证明。
- 主仓库 origin 为 `https://github.com/swayhrl/accel-sim-framework.git`；主工作树是 C16 分支，核查时 HEAD `5a8bcd63638847c0f2a0951046ec9cb2ba1994a2`，未在其中切换或改动。顶层 `AGENTS.md` 明定适用于 VM/TLB `hrl/vm-core-v0` 及后代；本轮AI-ARCH接班遵循用户Goal及AI-ARCH协调边界。
- 15个174-new AI-ARCH工作树实际存在，当前 HEAD、节点本地分支和固定执行commit逐项相同；15个固定tree在节点对象库可核。一次 GitHub SSH ref 读取显示15个执行分支及工作流分支均仍指向固定commit。15个工作树的 `git status --porcelain --untracked-files=normal` 均为空；未见新的本项目已跟踪/未跟踪工作树文件或超前提交。此结论仅限这些工作树，不覆盖节点其它项目。

## 历史任务承接

下表的“原结果”由生产者报告给出；“审查/更新”来自固定独审或更晚已知正式状态，不是本轮重新执行的实验。原分支、完整commit/tree、报告、receipt和审查精确路径见资产索引。

| ID | 原执行成果与承接边界 | 审查及后续状态 |
|---|---|---|
| A4-T | MegaScale-MoE训练扩展与强软件源审；没有合格的新小训练pair | A5仅接受限定源结论；STOP，不重开分布式训练 |
| A4-N | NequIP/Sobek自然对象源审；原中文实质损坏 | A5为`PARTIAL_DOCUMENT_INTEGRITY`，仅独立可核的Si输入、配置、兼容性事实可用；无native准入 |
| A10-T | TorchTitan激活生命周期、SAC/offload/paged stash 源码能力 | A11接受`SOURCE_ONLY_NO_VALID_SMALL_TRAINING_PAIR`；作者H100结果非4080实测 |
| A21 | GS-Scale/Rubble真实场景来源及输入合同 | 当时`PENDING_ASSETS`是历史时点；109后续A26GR1/Q1更新了资产事实，不能沿用旧缺件状态 |
| A22 | GS-Scale状态寿命、deferred更新和producer/consumer源码地图 | A25接受有范围源码映射；不等于CPU、链路或完整训练瓶颈实测 |
| A23 | GSArch/GS-Cache最近邻与强GS-Scale边界 | A25未认定硬件headroom；GSArch当时仅摘要，不能补造全文/PPA |
| A30-T | 完整MoE routed operator、自然route与FP8边界 | A32保留H200/SM90a条件性源候选；SM89未合格、无native授权 |
| A30-N | PixArt-Σ/DiSC post-opt资源源审 | A32确认`NO_HARDWARE_PROBE_READY`；专用硬件模拟比例非本机GPU残余 |
| A45-S | 稀疏ANNS的GloVe100/CAGRA单探针提案 | A46仅接受`PROPOSAL_ONLY`；109后续CAGRA质量`NO_GO`，旧建议不复开 |
| A58 | SmolVLA并发与GraphSAGE/GraphBolt源资格 | A59为条件提案；109后续GNN已执行并`PARKED`，VLA串行服务不当并发 |
| A70-N | Qwen3.5 GDN/KV状态与运行时反证 | A71接受范围内0候选；`SOURCE_SCOPE_ACCEPTED_NOT_NATIVE_NEGATIVE` |
| A70-P | Qwen3-VL视觉到语言交接与强软件 | A71接受范围内0候选；不代表所有VLM无瓶颈 |
| A73-H | TC/SFU同面积功耗交换与完整模型机会成本 | A74缩窄问题；后续PPA/SM100模型缺口仍在，`PARKED`，无模拟准入 |
| A75-D | Wan2.2生成周期、CFG/专家切换与缓存软件 | A76接受`SOFTWARE_NEARBY_NO_SURVIVOR / STOP`，限源码范围，不是native负例 |
| A77-S | Accel-Sim资源轴与Native↔Simulator身份审计 | A78接受`MODEL_AUTHORITY_NO_GO`与配对不成立；0准入轴、0pilot，非性能负例 |

工作流验证单列：`hrl/ai-arch-codex-workflow-bootstrap-20261013-v1@1a7f8d5d6f01326da161f52447eee013d1a630ec` 的固定记录为 `MANUAL_WORKFLOW_ACCEPTED_WITH_SCOPE / CLI_SKILL_DISCOVERY_UNVERIFIED / STOP`。该commit的GitHub报告可读；174节点当前共享对象库和工作树清单中未定位该对象/工作树。手动模板可复用，旧CLI自动发现不因本次接班晋级。

## 节点新核到的材料与缺口

- A70-N、A73-H、A75-D、A77-S的私有 `FINAL_READBACK.json` 在各自精确输出根仍可读，文件内commit/tree与固定索引一致。本包 `NODE_READBACKS/` 存放四份**原样小文件副本**，资产索引登记节点原路径、字节数和SHA-256；没有改写旧执行分支。A70-P历史 `/tmp/aiarch-a70p-vlm-pipeline-174new-v1` 目录现为空，未找到同名readback，其Git报告/receipt仍可用。
- A75-D私有`selected_manifest.json`（7项）和`wan_manifest.json`（10项）在原位，SHA与生产者receipt相同。A77-S的`git-source-manifest.json`（84项）和`public-download-manifest.json`（7项）也在原位；只登记bytes/SHA和来源，不把缓存提升为新的科学证明。这些非Git原件保留在节点；未发现需要发布的新科学提交。
- A4-N原报告节点文件与固定Git字节一致：10,477字节、全ASCII、2,334个字面问号、SHA-256 `26ce76b3d1ba5beeb03ddf3439c33f96ee65282313097a8db1b050f6562ebdf3`。仅在该任务工作树、报告目录、该分支短log及已命名远端ref作有界查找，未见真实可读原件或后续修订；不从上下文补造中文。A5独审支持的有限源事实仍可用。其它未定位的私人日志/副本存在性未作全盘断言。
- A77-S仅登记AWMA固定framework `29ce051f982f3854bd4392a94e4195c59340123b` 的ISA/trace代码与两份SM89配置Git blob、已发表binary SHA `a866c219b7d71a3075e032c9179bcd679074d6f2e9f1750b435170aabb413b24`。实际外部performance core的完整source/patch/binary闭链仍未知；现场binary路径/存在性未核。公开scaffold的L2取整疑点不可归咎于实际AWMA binary。T1的0.5B单kernel与W77的3B完整请求不是同一配对对象。
- 一次被动 `/proc/*/cwd` 抽样未发现cwd落在上述15个AI-ARCH工作树或命名输出根的进程；未读取进程环境、GPU锁或其它项目任务，也不把抽样写成“整机无活动任务”。没有需由本窗口接续或干预的已确认174-AI-ARCH活动任务。

## 当前边界与接班判定

用户确认Main（`AI-ARCH交接-1`）正在109执行`AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1`；实际HEAD、GPU准入、进度、formal数未知。Q1既有执行authority仍是`5787826ca21f7af958e6e1c1f828d62fd58a1ec4`。本轮未登录109/164、未进入mnt164、未读取活动raw/锁、未启动CUDA/NVML/JIT、模型、Profiler、模拟器/RTL、build或GPU任务；未改Main上下文、总协调分支、旧实验工作树和Image-Lab。

本节点现有固定报告、工作树与重要私有回读足以支撑174-AI-ARCH长期承担**以后另行明确授权的CPU源码审查、资产定位和独立分析**。A4-N丢失的原中文是不可替代的局部缺口；A70-P私有readback和A77实际core/binary闭链未恢复。未来任何native、GPU、模拟器或资源轴研究都要新合同；本Goal到此STOP。
