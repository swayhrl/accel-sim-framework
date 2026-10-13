# Round A8｜Lane M环境门STOP独立科学审查

**执行者：ChatGPT／AI-ARCH Discovery**  
**核查日期：2026-10-13**  
**审查结论：`ACCEPT_SCOPED_ENVIRONMENT_STOP / SCIENCE_NOT_EVALUATED / NO_AUTOMATIC_GPU_RETRY`。**  
**核查等级：`GITHUB_FIXED_COMMIT_REVIEW / GITHUB_ONLY_NOT_RAW_REVALIDATED`。**

> 此报告仅独立审阅GitHub上已提交的执行包、固定源代码/数值约束及公开PyPI发布元数据；没有登录109、164，未初始化CUDA、安装包、重跑wheel、复核164上实际大包字节，亦不接受任何新的GPU执行授权。

## 1. 冻结身份、Git祖先与范围

- [Lane M执行结果固定提交 `06674a961632c107681ac146d735d932dde112d6`](https://github.com/swayhrl/accel-sim-framework/commit/06674a961632c107681ac146d735d932dde112d6)，tree `346c22bb688bc84405510777241c9322b47fd1a9`，parent `860037b6882f16162e88f280e17c575414379b6e`（准备代码提交）。
- 执行分支`hrl/aiarch-nequip-static-batch-109-v1`已核对HEAD为上述固定提交；相对审批起点`cb1081328303f2655cbf1a3f3042cc01abe83b2c` ahead 2、behind 0；Git diff显示35个被提交的路径（含代码及STOP小报告）。
- [原V1合同](https://github.com/swayhrl/accel-sim-framework/blob/cb1081328303f2655cbf1a3f3042cc01abe83b2c/docs/ai_workload_research/goals/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1.md) Git blob `0101a33c27090ee5ef4f0f29ad5d98b492e6280b`与报告`RUN_IDENTITY.json`一致；本轮审查没有修改原合同或原STOP。
- 执行者实际报告文本仍用最初`Lane N-109`的历史标签；用户之后已经将node109窗口确定为**Lane M**，这是同一A8科学任务。不要为改名字改写固定执行提交。原`Lane N/174-new`及`Lane T/174-new`仍是独立STOP线。

固定执行包位于：
`docs/ai_workload_research/review_packs/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1/`

主要逐项读取：`FINAL_REPORT.md`、`FINAL_DECISION.json`、`STOP_RECEIPT.json`、`WHEEL_AVAILABILITY_CONFIRMATION.json`、`WHEEL_GATE_FAILURE.log`、`ENVIRONMENT_LOCK.json`、`RESOLVED_REQUIREMENTS.lock`、`INPUT_MANIFEST.json`、`NUMERIC_AND_EDGE_CHECKS.json`、`RESOURCE_USAGE.json`、`DELIVERY_SELF_CHECK.json`、`NODE164_CLOSEOUT_PUBLICATION.json`、`SHA256SUMS`。

## 2. 科学STOP本身是否合法？

**是，严格限于V1合同的wheel-only前置条件。**

- 一次dependency resolver产出**82个已锁定发行版本**，包括`hydra-core==1.3.7`、`omegaconf==2.3.1`和其依赖`antlr4-python3-runtime==4.9.3`。
- 发行哈希锁中的ANTLR项只列发布源码包SHA256 `f224469b4168294902bb1efa80a8bf7855f24c99aef99cbefc1bcd3cce77881b`；`WHEEL_GATE_FAILURE.log`在`--only-binary`受控wheel-only路径下出现`No matching distribution found`。
- Lane M的`WHEEL_AVAILABILITY_CONFIRMATION.json`显示4.9.3 **PyPI官方发行**仅117,034字节`antlr4-python3-runtime-4.9.3.tar.gz`，无官方wheel。本窗口独立核对[PyPI固定版本页面](https://pypi.org/project/antlr4-python3-runtime/4.9.3/)及[版本JSON](https://pypi.org/pypi/antlr4-python3-runtime/4.9.3/json)，文件名/大小/hash与报告一致。
- **不能扩充为“世界上不存在4.9.3 wheel”**：[piwheels第三方仓库](https://www.piwheels.org/project/antlr4-python3-runtime/)发布了同版本的通用`py3-none-any` wheel，但它不是V1使用的PyPI源及锁定的发布hash；本轮没有下载或运行，不作为恢复途径。
- 原V1明确“leaf依赖没有可用wheel→STOP，禁止更换版本/重新搜索分辨率”。因此Lane M没有额外改装ANTLR、替换Hydra/OmegaConf、编译随机源码包或继续跑GPU，符合科学合同。

**严谨分类**：`V1_WHEEL_POLICY_GATE_BLOCKED`，而非`PYTHON_PACKAGE_UNINSTALLABLE`、`MODEL_NUMERIC_FAILURE`或`NO_ARCHITECTURAL_PHENOMENON`。

## 3. 已经真实完成的工作与没做的工作

| 项目 | 已接受的有限证据 | 不能升级的主张 |
|---|---|---|
| 执行身份/资源 | 用户批准的V1起点、node109 SM89/RTX4080、driver580.178.04和现有CUDA12.6信息在运行identity中可见 | 来源为已提交109环境收据；不是本窗口现场再次probe |
| 模型ZIP与Si原文件 | 官方模型MD5`399a98bf36fc4550bc85d48f35451c6c`、模型SHA256`63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa`；Si 784,661字节、SHA256`c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770`，索引0/109及正式32帧未变化 | 是报告的字节身份PASS；**未验证**模型对象dtype、cutoff、单位、实图邻居、力/应力的同语义数值 |
| Python包与预编译 | 新Python3.11.17、依赖版本/hash锁、80余发行包的静态计划与官方LibTorch依赖文件准备 | 没有完整core install、官方AOT导出或执行时兼容性PASS |
| 数值资格 | 固定5次FP32对照和逐元素5e-5门槛仍在V1；当前未运行 | 没有eager/OEQ/compiled输出或几何/有向周期边集合的PASS |
| N-C2、N-G2、N-G4、N-G8 | 各自`NOT_RUN_ENVIRONMENT_STOP`；每臂0样本、0 fresh process、0 block | 不准提供任何速度比、性能排序、微观硬件瓶颈或负结果 |
| 归档 | 109 producer报告164归档原包56项与closeout 22项经路径/size/SHA readback通过；Git文件与manifest可相互定位 | 本ChatGPT未通过164 SSHFS直接复算其归档原raw；保留`GITHUB_ONLY_NOT_RAW_REVALIDATED` |

**定点完整性复核**：本ChatGPT独立从GitHub远端读取并重新计算`FINAL_REPORT.md`、`FINAL_DECISION.json`、`STOP_RECEIPT.json`、`WHEEL_AVAILABILITY_CONFIRMATION.json`、`ENVIRONMENT_LOCK.json`的UTF-8 SHA256，**5/5与`SHA256SUMS`完全一致**。不能由此宣称对全部20项或164大包进行独立重算；其余SHA闭合仅为执行者报告的自检。

模型包内部来源记录显示`nequip 0.15.0 / e3nn 0.5.6 / torch 2.7.0+cu128 / openequivariance 0.4.2.dev4`，而拟运行组合为固定NequIP源码、`e3nn 0.6.0 / torch 2.10.0+cu126 / OEQ 0.7.0`。这是**后续可能的包内加载/自定义源码兼容风险**，不是现阶段已经观测的兼容性失败。未来仅能在冻结语义下核验，不能悄悄修改checkpoint/模型/精度。

## 4. 资源边界的独立核账

| 资源 | Lane M报告的具体事实 | 审查意见 |
|---|---:|---|
| 模型＋Si下载 | 6,423,337 bytes | 小于V1 12MiB门槛 |
| 依赖下载“保守上界” | 3,333,112,827 bytes（约3.11GiB） | 包含非任务流量/保守余量，不当作精确pip净下载 |
| 任务目录增量 | 主归档后约1.25GB | 小于25GiB门槛 |
| GPU锁占用 | **0秒** | 没有进入GPU阶段；两个锁可用性探针未单独计时 |
| GPU显存/正式运行 | **0MiB / 0秒** | STOP发生在wheel门 |
| RAM | 受监督wheel阶段RSS峰值约92.6MiB | **整个resolver阶段峰值未测**；不得由92.6MiB推出完整任务RAM已独立封顶 |

没有从已记录资源字段看到GPU锁或下载上限超标；RAM总峰值缺直接监测，归类`RESOURCE_RAM_PEAK_PARTIAL`，不能宣称所有资源计量均独立完成。

## 5. 方法学结论

- 本次是**事前受控的工程打包失败**，没有进入物理仿真、NequIP eager/OEQ测量、基准输入可用性验证或真实效果归因。
- V1必须保留为正式`ENVIRONMENT_BLOCKED / NOT_EVALUATED / COMPLETE_STOP`。**不能通过回填样本、补算速度或在原分支继续执行把它改成PASS。**
- 但是，仅因`4.9.3`在**官方PyPI**没有wheel，就完全放弃Q-N6也不符合发现性研究效率。可考虑对固定**官方sdist**做一次极小、可审计的CPU-only wheel构建例外，再在新的V1R1合同下继续原实验；这是一个显式合同边界变更，不是“忽略停止门”。
- 不能推定仅此一个依赖没有wheel：当前wheel-only步骤在首次缺失处停止，**其它81项的wheel完整性未逐项取得PASS**。
- 优先保留现有解析/环境/下载缓存/模型身份；不要重跑原46分钟准备、全量重新解锁82包、扫描不同版本/供应商，或让多个GPU agent并行竞争已有锁。
- 技术上[`antlr4-python3-runtime 4.9.3`的PyPI源码包](https://pypi.org/project/antlr4-python3-runtime/4.9.3/)可作为候选**受控源码构建输入**；公开存在同版本wheel是可构建性线索，不是本机已构建成功的证明。纯Python构建、runtime导入及依赖组合仍应作为有界测试，不在本报告伪报PASS。

## 6. 下一步建议：Round A9｜同版本wheel打包例外与一次性资格恢复（执行者：ChatGPT主审；候选Codex Lane M／109）

**只建议一个合并阶段，而不是分成重复环境烟测和新完整campaign。**

1. 保留V1原终态与归档。另建立V1R1独立分支，从固定V1 STOP提交出发，**不修改历史文件**。
2. **唯一预审例外**：允许从PyPI官方`antlr4-python3-runtime-4.9.3.tar.gz`（SHA256固定`f224469b…77881b`）以原固定Python3.11.17及现成pip/setuptools/wheel在隔离目录**尝试一次**本地wheel构建。成功后记录构建命令、环境、输出wheel SHA、metadata、tag，验证版本/可导入性/安装来源，添加独立`V1R1_DERIVED_WHEEL_LOCK`；**保留原82个发行版本、输入、模型、精度、实现选择、数值门及A8 4个条件不变**。源码包构建失败则STOP，不因失败换成不同ANTLR版本。
3. 在不触GPU的情况下先核**整个冻结依赖集合**的wheel与文件/hash可取得性，避免一个源码包例外后又在别的叶依赖停门。若第二个未批准的源码包缺失，`ADDITIONAL_WHEEL_BLOCKED`并STOP，不自动连锁放开。
4. 若上述CPU资格通过，且获得**新的明确GPU恢复执行授权**，才在109按原共享锁继续必要的模型加载/编译/数值canary/四条件计时/自检/归档，严格保留V1原有边界和STOP，不补做不合格观察。恢复阶段不重开DTC/AWMA/C16。
5. 资源以V1已有消耗为基数登记剩余额度，尤其依赖下载此前保守计为3.11GiB，若**沿用原8GiB总上限**，则整个恢复路线新增依赖下载最多约4.89GiB；不得因新分支悄悄将历史消耗清零。109 GPU持锁上限原有90分钟（前轮0秒），观察阶段原15分钟；同一科学对象不允许额外模型/holdout。
6. 交付明确两层：包装例外`SOURCE_WHEEL_BUILT/NOT_BUILT`、正式科学`PASS/ENV_BLOCKED/NUMERIC_STOP/NO_RESOLVABLE_RESPONSE`分别记录；负/零结果也保留。

**当前授权判断**：用户只明确授权过**V1**并且它已经执行到正式STOP；本文件不批准V1R1启动或GPU继续。需要用户明确同意V1R1**唯一源码打包例外与有界恢复**，或者先单独批准仅CPU的小打包测试。综合效率优先推荐在一条新Goal中完成（前置CPU打包、通过后有界GPU阶段），避免重复多窗口启动。

## 7. 冻结不变

- Lane M执行branch`hrl/aiarch-nequip-static-batch-109-v1`保持原正式STOP commit；不合并入协调分支。
- Lane N/174和Lane T/174的旧STOP、C16 Stage A和AWMA R27R3的科学authority全部不变。
- 不修改当前`AI_WORKLOAD_ARCHITECTURE_PROBLEM_ATLAS_V1.md`的任何已冻结研究结论。此次仅录入新环境资格结果与未来候选行动。
