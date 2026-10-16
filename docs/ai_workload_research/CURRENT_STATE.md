# AI-ARCH｜当前科研协调状态

**最新快照：2026-10-16 / Round A79新Native-only现象发现Goal已冻结并发布，109新执行分支READY_FOR_USER_DISPATCH，尚未收到实际GPU启动回执。** 用户本轮已明确同意以高效率开展小型受控原生测量。**这次许可限于A79唯一自然工作量敏感度合同；不自动许可模拟器、Profiler、C16/AWMA旧任务恢复或硬件机制。** Git文档创建不等于已在109启动Codex进程。

前序冻结： [A78完整科研裁决](https://github.com/swayhrl/accel-sim-framework/blob/50a7269df1ede4616c3539219e4eaa1f7a44e2b5/docs/ai_workload_research/reviews/AI_ARCH_A78_A77_W_S_RESOURCE_PAIRING_INDEPENDENT_REVIEW_2026-10-16_V1.md)、[A78 CURRENT_STATE](https://github.com/swayhrl/accel-sim-framework/blob/50a7269df1ede4616c3539219e4eaa1f7a44e2b5/docs/ai_workload_research/CURRENT_STATE.md)。A77的W/S双CPU审查均STOP：W77=`NATIVE_ONLY_ELIGIBILITY`，两历史真实Qwen2.5-3B原生请求锚点，0资源扫描ready；S77=`MODEL_AUTHORITY_NO_GO`，0合法模拟资源轴/0pilot。两者Native↔Sim`PAIRING_NOT_ESTABLISHED`；新A79不修这个问题。

## 1. A79唯一连续执行合同（新授权范围）

**[A79完整Goal｜Qwen2.5-3B BF16自然文本长度×生成阶段Native-only](goals/AI_ARCH_A79_QWEN25_3B_NATIVE_ONLY_NATURAL_LENGTH_PHASE_SENSITIVITY_109_V1.md)**，Goal固定发布HEAD：`7094d4b2d29980c2d2d8d97a9abb6fddb3283c9f`。

| 字段 | 固定值 |
|---|---|
| 建议节点／GPU | 109 RTX4080 SM89，固定历史UUID`GPU-ce6cba36-415b-4e27-40e2-bded6bc1ee59` |
| 新独立分支 | `hrl/aiarch-a79-qwen25-3b-native-workload-sensitivity-109-v1` |
| 科学问题 | **同一个Qwen2.5-3B-Instruct BF16、同强compiled Graph Mode A**下自然输入长度和生成阶段变化的**完整CUDA-event请求wall**；不声称硬件资源因果或纯ITL |
| 模型与源 | `Qwen/Qwen2.5-3B-Instruct@aa8e72537993ba99e69dfaafa59ed015b17504d1`、历史vLLM 0.30.0、WikiText-103 A00/A01冻结源；512原token hash必须完全一致，2048须CPU新冻连续原文字节前缀，sealed B输入不碰 |
| G1历史anchor | **A00 L512/O32** B1，Mode A，engine maxlen544，2warmups/5formal；历史354.598205566ms仅作漂移诊断，old C16不重启 |
| G2统一容量控制 | 另一fresh引擎`max_model_len=max_num_batched_tokens=2080`；A00和A01各4个先冻点，`L∈{512,2048}×output∈{1,32}`，每点2warmups/5formal，不因结果增删配置 |
| 科学准入与停止 | 模型/旧vLLM/code/Graph identity、公开WikiText许可事实、本机资产只读、输入/数值/新编译cache隔离、实际独占PID/显存、合法长度点。输入变更、旧缓存污染、数值错误或GPU共享资源冲突STOP。 |
| 硬预算 | GPU非阻塞共享锁持有总墙钟≤**720s**、全Goal≤**45min**、GPU任务NVML≤**15400MiB**、CPU树RSS≤**16GiB**、新增disk≤**3GiB**、2次引擎初始化、权重或真实数据下载/安装0；Profiler、模拟器和额外GPU exploratory run 0。 |
| 交付 | `util/ai_workload_research/a79_qwen25_3b_native/`新增隔离工具、`docs/ai_workload_research/runs/AI_ARCH_A79_QWEN25_3B_NATIVE_WORKLOAD_SENSITIVITY_109_V1/`的raw/数字/环境/numeric/GPU receipt与FINAL_REPORT。只能新增本A79文件，Git发布并远端回读后STOP。 |
| 当前实际状态 | `READY_FOR_USER_DISPATCH`，文档与Git branch已创建，**未通过本窗口在109启动Codex或模型**。 |

**额外科学口径：** G1历史`max_model_len=544`与G2统一`2080`引擎配置不同，不能直接替换时间基线；G2内部C01/C02...才适合长度/生成量相互比较。A01是独立文本控制非封存holdout，不能把2048新token序列冒充历史512输出参考。没有长文本另一后端独立数值oracle时，重复token一致只能标局部可重复性，不能写“数学正确性全面PASS”。即使有差别也仅是`NATIVE_WORKLOAD_SENSITIVITY`，不是TC/L2/DRAM或“扩展规律”已证。

## 2. 执行与其他项目冻结

- 109的本Goal子进程必须在自身GPU campaign锁`/data/c16/locks/c16_gpu_campaign.lock`非阻塞成功后初始化CUDA；完整NVML自身PID及terminal清理，任何外部GPU占用fail-closed。锁冲突不得轮询、等待或打断其它任务。
- 工程修补、缓存隔离、CPU tokenizer、报告等全部在一个连续Goal预算内解决；普通工程问题无需另开ChatGPT小轮，科学contract越界才STOP。新缓存必须独立，禁止清空C16旧AOT cache或修改旧C16 runner。只读历史权重资产与输入，旧承认scientific STOP依旧不变。
- 当前没有AWMA、ISCAS、C16、A61/A65/A67 GNN、A69 Q-S、A70—A77旧Lane的额外执行权；S77外部performance core未闭合以及T1 0.5B单kernel trace绝不能与3B完整请求拼接。
- 109实际启动/完成时机以**用户或Codex执行回执**为准；本ChatGPT仅发布Goal及协调审查，不声称自己直接控制109机器。收到A79最终commit/tree/raw即可独立交叉复算，无需提前开第二条重复GPU任务。

**当前A79：已批准/发布一条新GPU科学合同，待用户把固定HEAD指令派给109 Codex；本窗口没有真实GPU占用或运行回执。**
