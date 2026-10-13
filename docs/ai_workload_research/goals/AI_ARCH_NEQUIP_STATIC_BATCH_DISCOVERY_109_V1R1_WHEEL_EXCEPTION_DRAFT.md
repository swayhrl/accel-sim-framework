# Round A9｜Lane M受控ANTLR打包例外与NequIP观察一次性恢复（候选V1R1）

**方案/科研审查执行者：ChatGPT／AI-ARCH Discovery**  
**拟运行执行者：Codex Lane M／node109的新隔离worktree**  
**状态：DRAFT / EXPLICIT_V1R1_APPROVAL_REQUIRED / NO_AUTOMATIC_GPU_EXECUTION**  
**科学问题：** 与原V1完全相同的32个真实Si静态结构、同一OAM-S模型与FP32数值/边集合，N-C2/N-G2/N-G4/N-G8四条件完整CPU-可用wall时间。

> 这是**只允许一个叶依赖由同版本官方源码构建wheel**的V1R1提案，不能作为自动重启V1的补丁指令。直到用户明确批准本稿中的“ANTLR源码打包例外＋受限恢复109 GPU”两部分，否则不得在109执行任何相关命令。参照[已审V1 STOP](../reviews/AI_ARCH_ROUND_A8_LANE_M_ENV_STOP_INDEPENDENT_REVIEW_2026-10-13_V1.md)，原V1 `ENVIRONMENT_BLOCKED / NOT_EVALUATED`保持不可变。

## 0. 固定来源与允许变化的唯一差异

- 原唯一合同：[`AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1.md`](AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1.md)，approved blob `0101a33c27090ee5ef4f0f29ad5d98b492e6280b`。
- 原已STOP执行：[`06674a961632c107681ac146d735d932dde112d6`](https://github.com/swayhrl/accel-sim-framework/commit/06674a961632c107681ac146d735d932dde112d6)，tree `346c22bb688bc84405510777241c9322b47fd1a9`；执行与数据准备已保存。**不得在`hrl/aiarch-nequip-static-batch-109-v1`上继续提交科学运行**。
- 保持冻结：官方模型`NequIP-OAM-S-0.1.nequip.zip`及MD5 `399a98bf36fc4550bc85d48f35451c6c`/已报告SHA256 `63d4bafd872850a014fd21dedeea416b61173a17750dee0b2b8dd2b126f407aa`；Si数据SHA256 `c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770`；原0/109 canary与32帧索引；Python3.11.17/NequIP/OEQ/ALCHEMI/torch2.10.0+cu126/e3nn0.6.0/warp1.16与原选择的82个发行包**版本不变**。
- **唯一允许的配置变动**：将`antlr4-python3-runtime==4.9.3`这一项从“仅接收PyPI官方wheel”改为“允许由**同一官方sdist**构建一个本地轮子”，而不更换版本、不信任外部第三方wheel、不放开其它包的源码构建。
- 包装例外的原始发布输入：[`antlr4-python3-runtime-4.9.3.tar.gz`](https://pypi.org/project/antlr4-python3-runtime/4.9.3/)大小117,034 bytes，SHA256 `f224469b4168294902bb1efa80a8bf7855f24c99aef99cbefc1bcd3cce77881b`。第三方piwheels存在同版本wheel，但**未取得本合同批准**，不得改用。PyPI无官方4.9.3 wheel是旧V1合法STOP原因。

## 1. 单Goal阶段A：完全不触CUDA的包装资格（一次通过即可续行）

1. 用户明确批准V1R1后才开始。使用109全新worktree/branch：建议`hrl/aiarch-nequip-static-batch-109-v1r1`，从**固定V1 STOP commit `06674a96…`**出发，新建独立目录和manifest，不修改旧STOP物理目录的源文件、文件名或历史哈希。
2. **最小复用**：先只读核过去的`ENVIRONMENT_LOCK.json`、`RESOLVED_REQUIREMENTS.lock`、Git完整包、模型/Si身份与缓存；不重新解析82个版本、不换Python/torch/e3nn/NequIP/OEQ/ALCHEMI、不得删除旧`pip/torch/warp`缓存。不假设旧pip的安装环境已经完整。
3. 从PyPI官方精确URL/现有缓存得到唯一源码包，SHA256匹配才打开。先审tar路径/链接和`setup.py`/build要求，禁用未知自动网络脚本；仅在隔离CPU构建目录、原Python3.11.17及已装`pip26.2.1`/`setuptools84.0.0`/`wheel0.48.0`条件下，**只尝试1次**`pip wheel --no-deps --no-build-isolation --no-index --wheel-dir <new_wheelhouse> <verified-local-sdist>`。若这条命令在已锁环境要求另一种受控调用才可工作，只允许机械CLI包装修正，**不可更换输入sdist/构建软件主版本或重复尝试不同build backend**；记录真实命令。
4. 不因生成轮子即声称通关：检查wheel文件名/完整SHA256、版本metadata、Python兼容tag、安装文件清单/非预期脚本，记录sdist→wheel出处与Python/build环境；在隔离CPU验收环境安装该轮子并测试`import antlr4`、`OmegaConf`、`hydra`以及无GPU`pip check`。`pip check`仅当相关依赖已安装时才作为完整环境通关门；不能把仅有ANTLR的venv提示缺其它包当作ANTLR失败。
5. 原`RESOLVED_REQUIREMENTS.lock`保持只读；另存`V1R1_DERIVED_WHEEL_LOCK`记录**这一个新生成wheel**的SHA256与对应官方sdist SHA256，完整安装仍使用82个原版本及旧缓存，明确新的artifact层而非重新解析所有版本。**不得将新wheel的字节SHA伪装成原sdist SHA**。
6. 在不初始化CUDA前扫描其它所有需wheel安装的已锁发行包：若第二项缺少原合同不允许的官方wheel，记`ADDITIONAL_WHEEL_BLOCKED`后STOP。NequIP/OEQ/ALCHEMI的原V1指定固定源码及其已批准构建路径不受这一“普通叶依赖wheel-only”禁令误伤。
7. 源码构建失败、未匹配官方SHA、版本/tag异常、Import失败且超出原打包范围或出现第二个未批准sdist，都保存诊断并`PACKAGING_STOP`。不得换4.10/4.13、Hydra/OmegaConf版本、换模型或继续GPU。

## 2. 单Goal阶段B：只有阶段A全部通过才触发原V1后续GPU资格

- 重新核node109实际环境/显卡UUID、其它用户状态和**非阻塞**共享锁`/data/c16/locks/c16_gpu_campaign.lock`，在锁空闲且预算满足时才允许任何CUDA/JIT/设备编译。锁忙则`RESOURCE_DEFERRED`，不清锁、不抢占。V1曾有两次非阻塞可用性探针、0秒正式持锁；本轮仍要现场确认。
- 按原V1§2—§10一次连续完成 **完成隔离82包环境→实际模型包加载身份/metadata/单位→官方batch AOT OEQ模型编译→数值/有向周期边集合canary→冻结身份→四条件3×12=144主计时→后数值审计→归档→STOP**。V1R1唯一新增wheel包装账本；**所有物理输入、变量、输出、统计和STOP均保持V1，不重新设计最有利的比较**。
- 现有模型包中记录的历史源版本（NequIP0.15.0、e3nn0.5.6、torch2.7.0+cu128、OEQ0.4.2.dev4）与本次拟运行固定组合不同，**是需验证的兼容风险，不是已证错误**。原生模型加载异常→身份/环境STOP，不能重新打包或修改模型以通过；未通过的点不进入科学性能排名。
- 普通输入路径、文件包装、receipt问题仅在原V1允许范围内做有限solve-and-continue，**不得把数值/科学语义问题当包装修复**。

## 3. 资源账本沿用，不因新branch重置下载额度

| 项目 | 本恢复合同硬约束 |
|---|---|
| 依赖下载 | 原V1保守已计`3,333,112,827` bytes；两轮**累计≤8GiB**。若采用原8GiB上限，尚余约`5,256,821,765` bytes（约4.90GiB），超出即STOP |
| 模型/Si下载 | 已完整并通过官方校验，优先**只读复用**，禁止再下不同模型；保持原模型和输入合计12MiB科学额度 |
| 数据/缓存/产物增量 | 原V1已创建约1.25GB，恢复后同任务全部新增空间累计≤25GiB，开工确认可用≥35GiB，始终保留≥8GiB |
| GPU | node109单RTX4080，同一UUID或说明改变即STOP审，任务峰值≤12GiB |
| GPU锁 | 原V1实际占用0秒；本次取得锁起累计GPU独占≤90分钟，正式观察≤15分钟 |
| CPU/RAM | ≤8 worker、≤32GiB；本次监测包括依赖解析/安装、编译期间峰值；不得把上轮wheel-step的92.6MiB误当完整resolver峰值 |
| raw/log | 总额≤256MiB，保存必要失败receipt但不因完整格式化报告耗费额外GPU时间 |
| 禁止 | 不增加GPU profiling、模拟器、MD、训练、模型权重切换、GPU并发、驱动/系统CUDA升级、AWMA/C16旧工作、额外holdout |

> 依赖剩余额度的十进制计算：8×1024³=8,589,934,592字节，减3,333,112,827字节得5,256,821,765字节。它是对原“保守上界”的记账余量，不是精确网络流量可用余额。

## 4. 结果发布与正式结论分类

- 原V1的[`FINAL_REPORT.md`](https://github.com/swayhrl/accel-sim-framework/blob/06674a961632c107681ac146d735d932dde112d6/docs/ai_workload_research/review_packs/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1/FINAL_REPORT.md)、`FINAL_DECISION.json`、164归档均原样保留。
- 新V1R1结果写入`docs/ai_workload_research/review_packs/AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1R1/`，包含`PACKAGING_EXCEPTION_RECEIPT.json`、`V1R1_DERIVED_WHEEL_LOCK`、完整env/source身份、数值资格/edge检查、未插桩主计时、原始样本、STOP、SHA/164回读及final判断；轻量manifest可合并，原数据永不覆写。
- 两层结果**独立**：`PACKAGING_SOURCE_WHEEL_PASS/FAIL/ADDITIONAL_WHEEL_BLOCKED`，以及GPU科学`NATIVE_QUALIFIED/NUMERIC_STOP/ENVIRONMENT_BLOCKED/NOT_EVALUATED`。数值门PASS才可合法解释时间；不对负/零结果加跑寻正。
- 结束后仅push执行者V1R1新分支和小pack，远端fetch-back，报告exact commit/tree与科学边界，交ChatGPT独立审查。禁止自己更新协调科学权威、合并分支或启动下一GPU任务。

## 5. 明确审批事项（当前全未自动授予）

**审批项A：** 允许一项4.9.3官方sdist受控CPU构建wheel，允许记录新本地wheel SHA并衔接82项原版本环境安装，而非仅官方预编译wheel。其它打包策略不变。

**审批项B：** 仅当A的依赖完整性PASS，才允许Lane M一次恢复109 GPU执行到原V1终点；资源与科学参数照本文件第3节及原V1；无额外模型、数据、方法或新机制。

在用户对A和B**明确同意**前，本文件是`PROPOSAL_ONLY`。不要重发原V1的启动指令或重启旧Lane M终止进程。
