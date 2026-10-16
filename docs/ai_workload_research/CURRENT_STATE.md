# AI-ARCH｜当前科研协调状态

**最新快照：2026-10-16 / Round A78；A77两个CPU-only资格Lane均已STOP并完成独立科研审查。** S77=`MODEL_AUTHORITY_NO_GO`、0个准入资源轴、0个合法Pilot点；W77=`NATIVE_ONLY_ELIGIBILITY`、2个历史有效原生请求锚点、0个资源扫描ready的基准。**综合：`A77_PAIRING_NOT_ESTABLISHED / SOURCE_REVIEW_ACCEPTED / STOP`，目前不启动资源6点扫描，也不是GPU硬件性能的负结果。**

[Round A77准备期导航](https://github.com/swayhrl/accel-sim-framework/blob/48921695a53b5d5db84f5ef43914d343385aad19/docs/ai_workload_research/CURRENT_STATE.md)保留。此前A70/A73/A74/A75的科学STOP、C16/AWMA/ISCAS/GNN/Q-S/3DGS所有原raw、执行分支、资源权限不改。

## 1. 本次独立交叉审查权威

**[Round A78完整独立审查](reviews/AI_ARCH_A78_A77_W_S_RESOURCE_PAIRING_INDEPENDENT_REVIEW_2026-10-16_V1.md)**，首次发布commit`fc9af7ba7935d3c57424e8806b0f6601570f7a4a`。

| 执行Lane | 精确原始authority | 科学终态、可保留范围 |
|---|---|---|
| **W77／109** | [REPORT](https://github.com/swayhrl/accel-sim-framework/blob/4fa849b16ff7828959486ccafe404c86a9115918/docs/ai_workload_research/discovery/A77_W_NATIVE_WORKLOAD_AUTHORITY/REPORT.md)，commit`4fa849b16ff7828959486ccafe404c86a9115918`，tree`e24eb81a96c4475ee1ef43824b71e35e35fbc4c3` | `NATIVE_ONLY_ELIGIBILITY`。历史`Qwen2.5-3B-Instruct` BF16 TP1及WikiText103冻结自然文本512-token prompt；MP01 B1 512+1：ON/OFF 40.236/39.907ms，3 formal；MP02 B1 512+32 compiled：ON/OFF 354.598/361.457ms，5 formal。两卡均只提供合法CUDA-event请求wall，**不是资源轴ready**，未重启旧Stage A。 |
| **S77／174-new** | [REPORT](https://github.com/swayhrl/accel-sim-framework/blob/c837d5d85a78c70cb1a0deb28cb8279940510785/docs/ai_workload_research/discovery/A77_S_SIM_RESOURCE_AUTHORITY/REPORT.md)，commit`c837d5d85a78c70cb1a0deb28cb8279940510785`，tree`423c73f8f0545ccc78fba73e46d6980ce9025df5` | `MODEL_AUTHORITY_NO_GO`。AWMA Ada翻译模拟资格原样保留；实际GPGPU-Sim performance core完整身份/ISA/数学/并发校准未闭合。A HMMA specialized initiation和B L2数据/填充服务均`UNVERIFIED`且未准入，条件6点中的`baseline`也未执行。 |

共同固定Goal`9902ead45ed61d54bd5eb0e2a998e2ccc4ba3285`；两Lane均仅新增各自四文件，Git commit相对共同Goal ahead1，远端execution HEAD identical，原始commit parent/tree与用户回报一致。独立读原始REPORT/JSON/TSV/RECEIPT并复核关键Git源码和原始C16/AWMA计时。W证据29条12列、S轴2条18列，ID各自唯一，无字段数异常。本审查只读GitHub与控制端算术，没有登入109/174/164，没有重算执行者私有数据/二进制全部SHA，也没有运行GPU/模拟器。

## 2. 不能绕过的四个配对缺口

1. **模型不是同一个：** W77 Native为`Qwen2.5-3B-Instruct@aa8e7253...`；S77历史T1 SASS trace标为`Qwen2.5-0.5B-Instruct`一个Prefill GEMM occurrence。模型、编译后端、输入、kernel边界和时间分母没有同一身份。不允许把0.5B单kernel cycles换算成3B完整请求ms。
2. **编译归因不成立：** C16 Stage A MP02完整compiled ON/OFF有合法B1请求计时，但Python模块hooks 0/4608，96个不同runtime kernel名仅1个可唯一静态归family，B4 Mode B formal=0；四DQ仍`QUESTION_INCOMPLETE`。MP01 Graph-OFF family时间权重不能移植到MP02 compiled Graph-ON请求。
3. **AWMA翻译基准与通用资源验证不同：** [已接受限制](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_RTX4080_V1_BASELINE_PROMOTION_V1/KNOWN_LIMITATIONS.md)仅`QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES`；[cross-calibration](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/review_packs/AWMA_NATIVE_SIMULATOR_CROSS_CALIBRATION_V1/CROSS_CALIBRATION_ANALYSIS.md) M1→M2 Native −4.584%而sim +86.5202%，不能当TC/L2/DRAM fidelity。
4. **资源旋钮未闭合：** S77提出的HMMA specialized initiation改动未核实际frozen binary/final core，L2 data/fill width一并计费。独立审阅的**公开scaffold** `dzwduan/gpgpu-sim_distribution@dc56ca74fa51d333cacb6a8aac91bce804301ae1` 的`gpu-cache.cc`使用整数fill`atom_size/data_port_width`，32B atom下32→64B可能产生0 fill cycles。该事实不能无证据归咎AWMA实际二进制，却足以拒绝以scaffold参数进行合法2×资源实验。

**科学决议：** `PAIRING_NOT_ESTABLISHED`，不新建第3轮的相同source-only模拟器调参审查、不为获得曲线修旧AWMA或放宽C16 Stage A身份；上述6点矩阵全部BLOCKED_NOT_EXECUTED。所有资源敏感度和本机GPU可优化空间依旧`UNKNOWN`。

## 3. 接下来唯一值得单独审预算的任务——Native-only先发现现象（未授权）

**研究提案**：若准备继续推进，放弃本条0.5B SASS↔3B Native合并，使用W77的3B-BF16强compiled Mode A及冻结WikiText自然文本，设计新的、**不继承C16执行合同**的小型Native-only workload-sensitivity诊断。首先关数据输入许可、A00/A01冻结SHA、当前GPU资产与runtime数值资格；新鲜B1 512+32完整请求在explore/independent文本能否复现合法wall，再按真正原文连续前缀审预选的较长输入和1-vs-32输出。不得伪造原B4强模式或自然在线会话；不能把改变自然请求长度当改变物理GPU资源容量。

结果最多支持`NATIVE_WORKLOAD_SENSITIVITY`与将来需哪个资源控制变量的方向选择，不是纯TC/L2带宽瓶颈因果。若需要NCU/NSYS应单独批准，插桩与未插桩完整wall分开；不能硬把generic compiled kernel名字当Attention/FFN family。停止条件、输入许可、109资源与共享GPU锁、进程树、权重资产、下载和wall上限都必须在新独立Goal冻结，不把本导航当GPU授权。

**下一步不建议再派4个Codex同时重复阅读同一AWMA/C16资产；先由协调者决定是否值得一个很小的、有独立holdout和实际GPU计时价值的native-only Goal。未取得新用户批准则继续STOP。**

## 4. 项目冻结和资源

A70四条source-only 0候选、A73 W输入PARKED/H仅来源假说、A74-C SM100固定PPA PARKED、A75 R/D source 0候选、A61/A65/A67 GNN、A69 ScanNet、C16 Stage A与AWMA现行所有authority保持不变。109共享`/data/c16/locks/c16_gpu_campaign.lock`仍在实际GPU任务中排他，A78未访问该锁或164权重仓库。

**当前实际状态：S77/W77都STOP；A78独立审查完成；资源轴0、合法6点0、历史Native锚点2、GPU/模拟器新执行0。**
