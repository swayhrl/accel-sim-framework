# Round A21｜GS-Scale真实场景训练：强软件与可复现输入的单次CPU源码准入

**拟执行者：Codex Lane T／174-new；实际科研协调/独立审查：ChatGPT／AI-ARCH Discovery**  
**性质：新独立Goal，CPU/source-only，`PREPARED_AWAITING_CODEX_LAUNCH`。没有109 GPU或其它节点操作授权。**  
**唯一科研问题：** 既然ASPLOS2026 GS-Scale已解决大量3DGS训练状态迁移，能否从现有作者代码与公开自然场景资料，形成**一套合法的、消费级16GB设备上可考虑的完整训练输入/强软件/质量/容量/时间合同**？若不能，说明具体缺口和最低修复信息，不靠盲下载和环境升级找正结果。

## 0. 先排除重复工作

- 首先从GitHub协调branch阅读[Round A20原始论文和三家族审查](../literature/AI_ARCH_A20_REAL_AI_WORKLOAD_REDISCOVERY_THREE_FAMILY_AUDIT_2026-10-14_V1.md)与[CURRENT_STATE](../CURRENT_STATE.md)；其中ASPLOS2026 §3–5真实实验组、作者cuda/torch环境、HSTU/MLIP的近邻和新硬件限制**已经完成**。本Goal不要重做三领域大检索，也不要改A20结论。
- 复用原174-new **Lane T** Codex窗口，但新worktree/branch，**不能修改Lane T历史A4/A10 STOP工作区或分支**。本任务不同于原TorchTitan A10。
- 本GoAL的**strong baseline不是朴素Host Offload**，至少必须冻结`gsplat GPU-only`、`GS-Scale fully optimized host`，naive offload只作历史消融；GPU-only若在指定真实场景OOM，只能算容量不可用，不可拿来作为时间比的分母。
- 直接使用已固定的原作者实现：[`SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`](https://github.com/SNU-ARC/GS-Scale/tree/6471e958f7e318f4870234d8107e0aa91c2d6932)；**不是**其当前不停变化的main，也不是与论文精确运行commit已证明相同。

## 1. 唯一工作项：一次性形成一张可审查的完整scene×software×time/quality合同

### A. 源码/软件强基线（最多8个目标源文件）

核对每个source对应Git blob与必要symbol，不全仓clone、不pip安装：

1. `README.md`及`install.sh`：作者明确`Intel CPU only`、CUDA12.x、Python3.10、torch2.2.0+cu121以及Intel Extension for PyTorch 2.2.0；列出该公开代码与2026 ASPLOS论文中`gsplat v1.5.0/CUDA12.4/torch2.2`口径差异，**不要猜109 CPU是Intel或AMD**。
2. `examples/simple_trainer.py` vs `examples/simple_trainer_hybrid_baseline.py` vs `examples/simple_trainer_hybrid_optimized.py`：只定位产生/消费active Gaussian ID、GPU frustum culling、CPU optimizer/forwarding、D2H/H2D、真实同步、相机选样、densification与训练loss/PSNR评估的入口；不要全文复制三份大文件。
3. `examples/simple_trainer_hybrid_optimized_split.py`仅在确定需要极端active-set分裂时审关键分支；否则跳过。不能把image-splitting改变工作/梯度对象的代价当免费。
4. `cpu_adam/src/cpu_adam.cpp`：确认deferred Adam更新/参数计数与CPU线程/平台条件，不把作者“质量近似无损”误写为bitwise identical。
5. `examples/datasets/colmap.py`和`examples/requirements.txt`（如有必要）核public dataset输入与处理依赖，控制总文件数≤8：允许在上述清单内换其中一个不必要的大脚本，而非无限打开额外源码。

### B. 真实场景可追溯输入身份（优先Building或Rubble）

- 只读核对Mill19 **Building** 或 **Rubble** 的作者README下载URL、图像和pixsfm/COLMAP目录结构、训练/验证的merge/test_every规则、原始点云初始化选择、downsample**4倍**、分辨率与scene是否真实；不把`MatrixCity Aerial`合成场景冒充自然输入。
- 若公开资源可提供只读metadata/HTTP HEAD响应，允许**有界HEAD/小JSON**查询，**不下载tgz图像、不拉取HF数据集、不导出几GB场景**。若缺原始scene SHA/manifest/image order，记录`INPUT_IDENTITY_PENDING`和需要用户授权的数据规模，不伪造校验值或版本。
- 收集**最低数据量表**：预估原场景下载/展开范围只能基于有明示的官方meta/HEAD，未披露写UNKNOWN；真实训练数值/画质需要完整scene而非随意挑一帧合成tensor。
- 记录训练camera采样seed、COLMAP初始point cloud、增密/裁剪过程中Gaussian ID变化，不能只用`set_random_seed(42)`推出可回放时间序列。给定同一scene，哪些参数和质量状态必须freeze以获得same-semantics A/B？

### C. 科学headroom准入与真正需要的时间/资源分母

- 从作者source与论文定位完整训练step/epoch wall（GPU+CPU Adam+同步+data prep+PCIe），GPU allocated/reserved peak、host RAM、真实H2D/D2H bytes、被GPU计算覆盖和未被覆盖的host等待、可见集随相机变化及time-to-quality PSNR/SSIM/LPIPS。
- **区分三个可以证伪的不同目标**：同模型同训练规模performance、固定16GB容量可完成性、训练达到给定画质的总时间。不得混合不同Gaussian counts或数值ε近似成相同bitwise。
- 为后续真正物理资源研究设STOP：若已优化GS-Scale对照GPU-only/其它强软件不存在稳定可测的额外wall或host等待，或者只能通过改数学算法/低贡献梯度阈值获得差值，结论`SOFTWARE_ABSORBED`；若CPU厂商不合支持、软件版本必须破坏109环境、真实场景版本无法固定，则`PLATFORM_OR_INPUT_BLOCKED`，不为了产出一篇机制而继续扩。

## 2. 资源隔离和工作方法

- **只有174-new CPU和GitHub公开文本**：不ssh 109/164，不碰GPU锁和运行中的其它项目；不`nvcc`、Python torch import、CUDA context、训练、模型权重下载、GS-Scale安装、3D scene tgz下载、Nsight/Accel-Sim。无需CPU长时间工作，只读取7–8个小范围源文件，输出一份Markdown。
- 不要使用多个subagents/大规模并行扫描，不因公开URL临时失效改目标场景/引入第三方镜像。可以修普通Git ref/Markdown链接、只读HEAD包装小问题。
- 磁盘/下载新增零模型与场景raw；工具自身报告Markdown/Git worktree建议小于20MiB，必要路径由Codex自行合法构建；174曾有root/swap压力，先做轻量read-only预检，不触碰其他任务工作区。
- 如当前软件或原始场景身份无法定量确认，给出`UNKNOWN`并按科学边界STOP，不得降低资格或直接以随机Gaussians跑计算替代。

## 3. 交付及裁决（一次Goal，一份报告）

只新增`docs/ai_workload_research/reviews/AI_ARCH_A21_GSSCALE_REAL_SCENE_SOURCE_ADMISSION_174NEW_V1.md`一份Markdown（≤260行），包括：

1. 原始文件、Git blob与核查到的exact源码symbol；
2. 1个**确实公开的真实场景**的原始input来源/处理/哈希缺口；
3. 3条baseline条件与神经场景训练时间/容量/质量分母；
4. 109环境潜在兼容性（不声称本机CPU厂商、内存/显卡fit已实测）；
5. 最近邻`GSArch`、`GS-Scale`与原gsplat的**已解决能力/不可直接归因的残余**；
6. 一张结论卡：`SOURCE_INPUT_CONTRACT_FEASIBLE_PENDING_ASSETS`、`SOFTWARE_ABSORBED`、`INPUT_IDENTITY_BLOCKED`或`PLATFORM_UNQUALIFIED`，明确下次最小工作及需要的审批范围，**0项自动新GPU/模拟器/机制**。

最后仅在A21独立branch提交/push，远端commit/tree与该文件Git blob/readback核实后STOP，不更新协调分支权威、不merge。ChatGPT依据固定提交独立审查。任何超过CPU源审的资源变化先停止、另审。

**结论导向：** 宁可证明3DGS目前没有可用新硬件headroom，也不要因为论文做出了强软件结果，就以弱基线重复“host offload/Cache”的机制。
