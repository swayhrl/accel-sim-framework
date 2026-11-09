# AI-ARCH｜174-new历史工作调查与API接班上下文

日期：2026-11-09。对象：新API Codex会话 `174-AI-ARCH`。

## 0. 接班目标与当前主线

这次接手的是174-new曾经承担的AI-ARCH源码研究、科学资格判断、轻量分析、局部工程知识及其固定证据。不是恢复所有名称含174、C16或AWMA的旧任务，也不是建立第二个109 GPU执行者。

当前PRIMARY是3DGS GS-Scale/Rubble。用户最新确认，Main＝API会话“AI-ARCH交接-1”已经在执行 `AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1`，研究保留原deferred语义时将shN更新/预测生产迁至GPU的实际净收益。实际启动HEAD、窗口、进度、formal数量均未知；用户会带回结果。本次174接班不得查询或干预109活动raw、进程、GPU锁、预约、源码、cache、checkpoint或Image-Lab，不重发或改变其Goal。

已经建立的authority：

| 角色 | 固定commit | 含义 |
|---|---|---|
| Q1真实完成轮 | `5787826ca21f7af958e6e1c1f828d62fd58a1ec4` | 原生执行、完整late状态与正式样本；执行身份不变 |
| 109完整工程交接 | `00abf55d44ad02a18d529eb0afe4d02dc0ceadfe` | 资料/资产入口，不替代执行身份 |
| 已接受独立审阅 | `06355f73caaa6f38697d9acac94ac81a47c27e62` | 20正式样本复算及有范围的晚期窗口结论 |
| shN CPU-only反事实研究 | `be7fe374c1402498eeab3d3f3be97a9eb01667ab` | 科学窗口接受其有范围源码与容量分析，并修正后续holdout合同 |
| 本包所依导航快照 | `b9e74381b3ca36d43d439a29a811c509af15bb8a` | 历史导航，不是实时任务监控 |

Q1已有C_D(next15140)、C_V(next15240)、C_FINAL(next15301)。两段原T16相对T8的完整窗口时延分别低12.1397%/12.1350%，但T16本来就是基线。起始状态恢复与后续轨迹数值等价分开，训练质量PASS没有建立。ON中的CPU Adam和转发占比不能直接当OFF可回收收益。shN参数与两份moments的3.379784GiB是静态内容量，不是候选实际峰值。当前没有硬件候选晋升。

C_D/C_V已参与研究选择；下一轮从C_FINAL继续的自然窗口是新holdout提案，不能倒退沿用旧验证窗口或旧时延。具体执行合同已交Main；174不追加验收门或修改活动规则。

Qwen V11归档为负载分析基点并PARKED；Hybrid/KV保持SECONDARY，不能因接班自动恢复资格调查；MoE是H200/SM90a条件路线。其它旧STOP及独立项目权限保留。

## 1. 长期研究与组织规则

AI-ARCH研究模型结构、真实输入、阶段、软件部署与GPU/CPU资源如何共同决定性能、容量和扩展性，不预设都是Cache/TLB瓶颈。现象驱动和计算/状态表示驱动两条研究路线均允许；发现性实验不必先证明硬件有效，但需具体假设、强对照、可识别变量与反证。

源码能力、作者论文、我方native、模拟、独立重算、理论估算分别标注。逻辑payload、实际物理流量、局部时延、完整应用收益、质量和PPA不能互换。强软件已覆盖某个直觉，不等于整个领域没有问题；工程STOP不等于性能负例。

用户、科学聊天窗口、节点执行端分工：用户决定授权并转交任务；科学窗口负责裁决与设计；Main/174-AI-ARCH各自在获准节点执行、维护证据并返回固定报告。两端聊天不自动同步。每节点一个长期AI-ARCH窗口，内部可有独立CPU子Agent，但共同文件串行写，GPU只能有一个获准owner。

本轮174只是CPU-only接班，没有新科研实验、模型下载或模拟器授权。普通路径/索引/包装问题在本Goal内有界解决，不为每一小步新开Goal。

## 2. 本轮Git调查覆盖与核查强度

检索了仓库中 `aiarch` 和 `ai-arch` 历史分支命名；沿固定导航的reviews目录，回读A5、A11、A25、A32、A46、A59、A71、A74、A76、A78中与174-new相关的部分；另读A70N/P、A73H、A75D、A77S的原执行收据相关段落、工作流验证记录和10月13日交接的节点章节。

据此定位 **15项174-new科研任务＋1项工作流验证**。这是本轮检索覆盖，不保证穷尽节点所有未发布工作。下面“已接受”指固定独立审查中的限定结论，本次没有重做这些科学审查、重新查全部论文或核验大型raw。各行的精确原报告/分支/tree/审查路径见 `EVIDENCE_INDEX.json`。

未把仅由ChatGPT完成的协调审查，按文件名误归为174执行；也未把109的A24、A45H、A70O、A74C、Qwen/Q1真实执行归为174成果。

## 3. 174-new历史科研任务台账

| ID／历史Lane | 工作及可复用成果 | 固定执行commit | 历史终态与当前接班处理 |
|---|---|---|---|
| A4-T／Lane T | MegaScale-MoE分布式训练扩展、作者实验组、强软件与本机可识别性 | `a1a70180736499687435b1e2d99984d4ebba4c53` | 有范围源码审查完成；没有合格的新小型训练实验；保留，不重开分布式训练 |
| A4-N／Lane N | 非LLM/NequIP自然输入、模型与Sobek兼容性 | `e355f096eeac44328d7463ef3256cc649ec9cb03` | 原报告中文实质丢失；A5仅接受可独立核实的有限源结论。需要有界查找可读原件，不推测补文 |
| A10-T／Lane T | TorchTitan训练生命周期、SAC/重算、offload/paged stash语义与配对资格 | `859eb16a51c7bf085d6e39a9000de198c0f4e710` | 源码能力成立，但无合法的小型同语义训练pair；STOP，不把作者H100结果当4080实测 |
| A21／Lane T | GS-Scale真实Rubble来源、原训练设置与输入准入 | `9575a674e5aa5af60e5803c07399fb64ae2c8488` | 当时待真实资产；后续109的A26GR1/Q1已更新资产事实，不沿用旧缺件状态 |
| A22／Lane T | GS-Scale单步状态生命周期、参数类型分置、deferred与producer/consumer关系 | `3b46ae8f94b5a72d1af4e06d352058bd2140abe6` | 有范围源码映射；不是实测CPU/链路瓶颈。是当前shN研究的历史来源之一 |
| A23／Lane N | GSArch/GS-Cache最近邻、训练与渲染边界、强GS-Scale软件 | `c096521d06483517bf6772689e5cc2c513186173` | 最近邻源审完成；当时GSArch仅摘要、未证明硬件headroom；不补造全文/PPA |
| A30-T／Lane T | MonoMoE完整算子边界、自然route/FP8格式及H200条件设计 | `1a8b9317de4c16e3dd19018f7f42cae1ebf5750e` | H200/SM90a条件候选，未native；109/SM89不能替代，没有租卡/迁移任务 |
| A30-N／Lane N | PixArt-Σ/DiSC post-opt资源、算法/质量与GPU实现配对 | `6f78a2e1e9a2fdb04bc9468f4b2d5594bc3229a6` | 证据不足、source-only STOP；专用硬件模拟不是本机GPU残余 |
| A45-S／Lane S | 稀疏计算与ANNS筛选，GloVe100/CAGRA最小原生提案 | `e0236f9e34f25dc7c96d048b31754bcb74e05764` | 一项条件式提案完成；后续109 CAGRA已质量NO_GO，不恢复旧建议或第三次排故 |
| A58 | SmolVLA并发与GraphSAGE/GraphBolt源资格 | `9560b28ee85618a9059e309cb640c210b4575dfc` | VLA串行服务不能当GPU并发；GNN当时条件候选。后续109 GNN已独立执行并PARKED，不复开 |
| A70-N／N-A70 | Qwen3.5-4B GDN/KV状态、allocator/checkpoint/ReplaySSM、容量算术 | `5076223db5db0256fd0ccacec50b5347a0cab8c5` | 范围内0候选；软件反证与尚未测量的动态成本都保留，不是native性能负例 |
| A70-P／P-A70 | Qwen3-VL视觉→语言交接、缓存/Graph/分块Prefill/分离服务 | `f2399777a30f4fdafa26858b3cd418e497538db2` | 范围内0候选、STOP；不是所有VLM无瓶颈，不启动新媒体/模型下载 |
| A73-H／H-A73 | TC与exp/SFU等资源的同面积/功耗交换、软件重调和完整模型机会成本 | `06b17a72f683316a4088292a4b424c9d97c7437c` | 原有源码问题经A74收窄；后续PPA/SM100模型仍缺，PARKED；不免费翻倍资源或启动模拟 |
| A75-D／D-A75 | Wan2.2真实生成周期、CFG/专家切换、cache软件及质量边界 | `6421e6768ff3df2ec20cddd87b3aa28b932c113a` | 源范围软件近邻反证、0候选STOP；不是Image-Lab视频工作流，也不接管其服务 |
| A77-S／S77 | Accel-Sim资源轴及Native↔Simulator身份审计 | `c837d5d85a78c70cb1a0deb28cb8279940510785` | MODEL_AUTHORITY_NO_GO，0准入资源轴、0pilot；不恢复六点扫描 |

### 3.1 最重要的模拟器边界

S77调查了TC initiation service和L2 data-port width两个源码候选轴，但没有准入实验。外部性能核实际源码与binary绑定未闭合，公开参考实现的L2整数取整可能使带宽翻倍不再是合法等比例服务变化；该参考源码问题不能自动判定为实际AWMA binary的缺陷。

更根本的是：历史Simulator T1是Qwen2.5-0.5B单Prefill kernel，Native W77是Qwen2.5-3B强compiled完整请求，两者不是同一模型、输入、实现或计时分母。AWMA已接受的地址翻译资格不能扩写为通用TC/L2/DRAM模型资格。

因此本次接班可登记174上已有core/config/binary的路径、Git身份和固定收据，仅作资产定位；不build、不run、不改参数，不读取大型trace，不把“找到文件”升级为科学配对通过。

### 3.2 A4-N文字损坏

A5独审记录：原e355报告中文被字面量问号替代；哈希一致只能证明损坏文件传输一致。此次直接回读原分支ref仍指向e355；本轮没有核到可读V2，但不能据此宣称任何其它分支或节点都不存在副本。

新窗口只在自己的相关worktree、有限输出目录、既有Git对象或明确日志入口寻找可读原件/后续发布记录。找到原件时保存来源、bytes/SHA和恢复过程，作为新恢复副本发布，不覆盖原损坏commit；找不到时保留缺口，使用A5已接受的有限结论，不按上下文重写丢失内容，也不重新执行整个非LLM研究。

## 4. 工作流验证：与科研成果分开

固定分支 `hrl/ai-arch-codex-workflow-bootstrap-20261013-v1`；入口commit `1a7f8d5d6f01326da161f52447eee013d1a630ec`，其验证起点为 `289143ffc322c6accda020c8c1617563ff8ce9a9`。

这是两个研究Skill/模板和隔离工作流的有界验证，不是新的模型或模拟器实验。手动读取/应用可复用；自动CLI Skill发现当时因缺配置要求的环境变量而未验证。不要把feature flag、help或配置存在当实际运行PASS，也不为API接班修旧CLI认证、索要/输出密钥、升级全局Codex、安装hooks或重跑长canary。当前API会话用实际已有能力，不需要继承旧VS Code插件版本。

## 5. 174-new节点与本地路径：已知线索，不是当前存在性证明

历史SSH alias：`hrl-174-new`。多个174原收据的hostname是 `huangrulin-sshfs-174`；旧交接曾记容器端口2239。相同hostname/IP片段不能区分原174与174-new，不能据此跳到原174账户。以本机现有SSH配置/受信host key、用户/容器身份、仓库/worktree共同确认。

历史主仓库：`/root/workspace/accel-sim-framework`。以下路径直接来自固定执行收据：

| 任务 | worktree | 输出/临时入口 |
|---|---|---|
| A70-N | `/root/workspace/accel-sim-framework-aiarch-a70n-hybrid-state-discovery-174new-v1` | `/root/workspace/aiarch-a70n-output-20261016/tmp` |
| A70-P | `/root/workspace/accel-sim-framework-aiarch-a70p-vlm-pipeline-discovery-174new-v1` | `/tmp/aiarch-a70p-vlm-pipeline-174new-v1` |
| A73-H | `/root/workspace/accel-sim-framework-aiarch-a73h-gpu-architecture-counterfactual-174new-v1` | `/root/workspace/aiarch-a73h-output-20261016/tmp` |
| A75-D | `/root/workspace/accel-sim-framework-aiarch-a75d-wan22-video-dit-discovery-174new-v1` | `/root/workspace/aiarch-a75d-output-20261016/tmp` |
| A77-S | `/root/workspace/accel-sim-framework-aiarch-a77s-simulator-resource-authority-174new-v1` | `/root/workspace/aiarch-a77s-output-20261016`及其`tmp` |

早期A4/A10/A21等的本轮已读资料未提供足够精确的实际worktree全路径；不得按命名规律伪造。让新窗口使用 `git worktree list --porcelain` 与相关ref定位，再记录实际路径。

历史174资源记录多次出现2GiB swap已满、磁盘/I/O压力。不同日期的可用盘14/38/71/79GiB等都是当时快照，不作为当前余量；先做轻量当前资源读数再决定本轮解析并行度，不复制权重、trace或大状态。

旧共享挂载 `/root/share/mnt164/...`只作为路径归属线索；本轮不进入该挂载、不SSH164、不执行递归du/find穿越挂载。109模型/状态只引用Git索引，不连接109查存在性。

## 6. 本次需要节点补查的明确缺口

1. 实际连接是否为174-new、主repo/object store与相关worktree是否仍存在。
2. 表中15项任务的本地HEAD与固定发布是否一致；有差异先看自身任务的commit/path diff，不reset。
3. 已关闭输出中的FINAL_READBACK、原文小缓存、私有来源索引是否仍可定位；不要求重新hash大raw。
4. A4-N是否有可读原件或后续V2；没有就保留文字缺失。
5. 是否有未发布的AI-ARCH自身科研文档、收据或代码；保持原件，另做来源绑定，不自动补写历史PASS。
6. Git检索之外是否还有确属AI-ARCH的工作。旧C16/AWMA等只建立边界/引用表，不接管。
7. 是否有仍存活且能明确归属AI-ARCH的本地任务；只读核身份与状态，发现则不干预、不接续、不改合同，单列报告。

Git分支存在不表示任务仍运行；旧报告STOP也不能证明今日节点无其它任务。bootstrap未验证的旧CLI能力不是接班阻断条件。

## 7. 知识与写入所有权

Main仍负责109主线和总协调。174-AI-ARCH先维护自己的节点上下文和独立结果，不与Main并发写同一个文件。

建议新API本机工作根（须实际创建或核实，不声称已存在）：
`D:/Codex/Token-API/workspaces/174-AI-ARCH/`

本轮知识入口：上述目录的 `CONTEXT.md`。它应有当前节点身份、任务索引、已接受/待审区别、已关闭和活动任务、资源边界、固定来源、未决项与下一动作。

不要写Main的 `D:/Codex/Token-API/workspaces/AI-ARCH/CONTEXT.md`。若D盘不可访问，使用新建独立174工作区中的CONTEXT.md并把快照发布Git；明确实际位置，不假装同步成功。

也不直接写 `hrl/ai-workload-research-coordination` 的CURRENT_STATE/README/authority索引。本轮将可供Main采纳的更新单独交付，待用户带回后由科学窗口审查。旧T/N/S/H/D是历史逻辑Lane，不要再开启五个竞争窗口。

## 8. 本包来源与适用范围

固定资料主要位于：
- `b9e74381.../docs/ai_workload_research/reviews/`（本包索引逐项列出相关独审文件）；
- 各条执行commit自身的 `reviews/` 或 `discovery/` 目录；
- `1a7f8d5.../docs/ai_workload_research/codex_workflows/`；
- `b9e74381.../docs/ai_workload_research/AI_ARCH_DISCOVERY_HANDOFF_CONTEXT_2026-10-13_V1.md`的节点章节；
- 109当前完成基点与最新用户运行确认。

不需要为接班重新阅读所有旧论文、重算全Q1或复制完整仓库历史。完整交接的标准是：证据入口可用、节点归属清楚、遗留差异有账、无竞争写入/执行、上下文可持续维护；不是把过去所有STOP重新做成PASS。
