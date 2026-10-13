# Round A8｜109静态结构发现性观察：用户批准记录

**协调记录执行者：ChatGPT／AI-ARCH Discovery**  
**用户批准日期：2026-10-13（本AI-ARCH主窗口明确回复“我同意”）**  
**执行状态：EXPLICITLY_APPROVED / NOT_YET_LAUNCHED / NOT_NATIVE_VALIDATED**

## 1. 本次获准的精确科学合同

- 唯一合同：[AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1.md](AI_ARCH_NEQUIP_STATIC_BATCH_DISCOVERY_109_V1.md)。
- 审批前协调分支固定提交：`a6c3389f1699fe93c5033809cae68beadc27eb80`；合同 Git blob：`0101a33c27090ee5ef4f0f29ad5d98b492e6280b`。
- 用户批准的是上一轮已完整披露的 **Round A8**：在node109的独立新worktree/分支按上述V1合同，一次性完成资源/环境/数据资格、模型编译、数值canary、四条件真实时间观察、结果保存与STOP。**不修改V1科学合同**，不扩展新的模型/数据/输入/holdout/硬件机制。
- 运行执行者：一个**node109 Codex新窗口**，为与原174-new的Lane N区分，可称`Lane N-109 / Round A8`。原174-new Lane N源审任务保持STOP；Lane T保持STOP。此Git记录不意味着Codex已由ChatGPT远程启动。
- 科学与独立复审执行者：ChatGPT／AI-ARCH Discovery，待Codex提交固定Git结果再审查。

## 2. 固定对象与必要边界

- 固定模型：Zenodo 18775904的`NequIP-OAM-S-0.1.nequip.zip`、官方MD5 `399a98bf36fc4550bc85d48f35451c6c`；下载后计算独立SHA256和模型元数据并过数值门。不能自动升级模型、不允许MACE/LJ fallback。
- 固定输入：tutorial Si extxyz sha256 `c08d3771a06beb82b0ed4258f78eecc7ce623f73ca6df20be99bd5722163e770`，共110帧×64Si；合同确定的32帧正式集合和0/109两个canary。不能推断连续MD时间顺序。
- 同一编译后的OEQ模型，固定精度FP32且关闭TF32和autocast；四条件：N-C2（CPU matscipy，B2），N-G2/G4/G8（GPU alchemiops，B2/4/8）；四臂必须完成同32帧，包含完整能量、力、应力输出。
- 锁定的数值及边集合门、3 fresh processes×12 paired blocks、全链CPU完成wall计时、统计与raw receipt，全部照V1，不减样本、不调容差、不因中性/负结果加试。

## 3. 用户已同意的资源硬预算

| 项目 | 本次最多 |
|---|---|
| GPU与锁 | **仅node109单RTX4080**；原既有共享锁`/data/c16/locks/c16_gpu_campaign.lock`须非阻塞取得、全CUDA/JIT/编译与正式运行期持有；不能删锁或绕过 |
| 模型+Si文件下载 | 12MiB |
| 隔离依赖下载 | 8GiB；一次受控依赖解析，优先已有缓存 |
| 109新增环境/缓存/产物 | 25GiB；开始前可用至少35GiB，过程中保留至少8GiB |
| CPU/RAM | 最多8 worker、32GiB |
| 显存 | 最多12GiB |
| GPU锁占用时间 | 最多90分钟（上限，不是预期耗时） |
| 纯观察计时阶段 | 最多15分钟（上限，不是预期耗时） |
| 结果小包 | 原raw与日志不超过256MiB |

**明确不批准**：升级驱动/CUDA全局工具链，NSYS/NCU/NVBit、Accel-Sim、训练、MD平台/轨迹、超预算下载、Cache清理、Stage A/C16/AWMA任务恢复、任意模型或精度替换、holdout和新机制。

## 4. 执行、授权与科学STOP区别

- **执行已获用户明确批准**，但当前只完成GitHub协调记账和执行分支准备，**并未通过GitHub工具启动node109 Codex或GPU任务**。启动必须由用户将一次性指令发送至node109的Codex窗口；Codex实际启动后需按本合同自行核实时的资源及科学门。
- 任务共享GPU锁忙、环境版本/依赖不可用、model hash不符、CUDA或编译条件不合格、edge多重集合不匹配、数值重复性失败、任何资源超限，按照合同FAIL-CLOSED保存结果后DEFER/STOP；**不得静默改输入、核心包版本、精度、程序算法和容差“修复”**。
- 普通runner索引、manifest包装/路径错误可在V1允许的有界修复次数内solve-and-continue；科学身份或唯一变量变化STOP并提交审查。
- 一次Goal产生自己的新执行分支与可追溯commit/tree，不合并C16/AWMA实验分支、不自动晋升硬件。ChatGPT独立审查后才从真实数据提科学结论。

## 5. 执行窗口命名勘误与启动报告（2026-10-13追加）

用户随后确认：node109已经向Codex窗口发送Round A8启动指令，并**正式将该窗口命名为`Lane M`**。以前本审批记录中的`Lane N-109`仅为当时提议的临时称呼，现在统一按**`Lane M / node109`**引用。原`Lane N / 174-new`是另一条已完成的非LLM源码审查线，`Lane T / 174-new`是已完成的训练源码审查线；名称不复用。

本条状态仅是`USER_REPORTED_LAUNCHED`：ChatGPT没有重新登录109核验实时Codex进程、GPU锁、实际编译或canary结果，不声称scientific PASS。上文的`NOT_YET_LAUNCHED`是**当时的历史记录**，不是追加记录后的最新状态。新增内容**只更正称呼及记录用户报告启动**，原科学V1合同、GPU预算、禁令和STOP全部不变，不修改正在运行的执行分支。
