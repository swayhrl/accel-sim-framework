# Round A27｜A26G Rubble G0 STORAGE_BOUND_UNKNOWN_STOP 独立科学审查

**审查执行者：ChatGPT／AI-ARCH Discovery；日期：2026-10-14。**  
**正式裁决：`ACCEPT_SCOPED_A26G_G0_STOP / STORAGE_GATE_METHOD_DESIGN_DEFECT / NOT_ACTUAL_DISK_EXHAUSTION / SCIENTIFIC_PAYLOAD_METADATA_LOCATED / NATIVE_NOT_EVALUATED / NO_AUTO_RETRY`。**  
**证据级别：GitHub固定执行提交完整21文件Git目录与源代码、20条提交文件SHA256自行重算、作者官方数据元数据执行侧receipt、gzip RFC1952和GNU tar原始规范。** 本ChatGPT没有SSH重新访问109，也未再次下载Rubble/Drive原始实体。

## 0. 固定执行身份与接收层级

- 固定执行分支 `hrl/aiarch-a26g-gsscale-rubble-gated-native-109-v1`，最终提交 [`e760f332ed41c609d3d19548f87d90b3f11357d8`](https://github.com/swayhrl/accel-sim-framework/commit/e760f332ed41c609d3d19548f87d90b3f11357d8)，tree `b2165a3fc75ca15c21876a46770e3b03027c8165`；起点 `9fc94371eea82473a3bd29197505b359da2c8d00`；两次commit（第一个完整packet `0e00d87f4aabd3650d2b0732f1497dba05ddd9e0`，后一个closeout），分支HEAD一致、`ahead2/behind0`。
- [执行报告](https://github.com/swayhrl/accel-sim-framework/blob/e760f332ed41c609d3d19548f87d90b3f11357d8/docs/ai_workload_research/runs/AI_ARCH_A26G_GSSCALE_RUBBLE_109_V1/FINAL_REPORT.md)和`STORAGE_PREFLIGHT.json`、`ASSET_MANIFEST.json`、`HTTP_METADATA_RECEIPTS.json`、`GATES.json`、`BUDGET_USAGE.json`、`DEPENDENCY_PREFLIGHT.json`、`ENGINEERING_FIXES.json`及`tools/aiarch_a26g/metadata_probe.py`/`archive_g0.py`直接复核。Git diff只有该独立任务的21份源码与小证据文件，不改旧实验。
- **ChatGPT独立从最终固定Git树获取`SHA256SUMS`所列20份源码/JSON/Markdown文件并以UTF-8字节重算SHA256，20/20与最终清单严格一致**；`SHA256SUMS`本身不自引用，但其文件Git blob`2977ebb0e94c12150a697a6b56dec2a9c51c47e0`由最终tree绑定。首packet的`PUBLICATION_READBACK.json`属于旧首packet验证而非重复验证最终新增closeout，故不能把它单独当后一个commit所有文件的自引用证明。
- **真实性限制**：该审查只在GitHub层证明提交证据内在一致，不表示重新从109发HTTP HEAD或独立下载164/Google Drive全部原始二进制。

## 1. 执行真实进度：数据入口更完整，但没有本机训练

| 项目 | 执行侧原始记录 | 独立科学解释 |
|---|---|---|
| `G0` | `STOP STORAGE_BOUND_UNKNOWN_STOP`，源SHA、CPU/磁盘快照、HTTP Archive HEAD+两段Range、官方COLMAP Root→mill19→rubble→sparse/0的三级子目录及3个二进制HEAD均能核查 | **受合同约束合法STOP**，不能称实验没拿到真实数据源 |
| 官方Rubble | `Content-Length=9,773,995,561 bytes`；HEAD200、Range206、ETag为分段格式、gzip开头含真实jpg entry | 原始compressed size和数据源存在的证据；没完整SHA/输入样本/实际tar成员全集 |
| 合并COLMAP | `cameras.bin=64`、`images.bin=427,380,490`、`points3D.bin=162,597,265` bytes；合计`589,977,819` bytes | 发布者Google Drive元数据由**controller HTTP读到**；node109的Drive直接读超时，**node109能否获取这三个完整科学payload仍未执行**。HEAD不能证明相机/点云字节语义闭合 |
| `G1`–`G3` | **NOT_RUN**：真实场景下载0、env/install/CPUAdam编译0、Torch/CUDA初始化0、训练0步、性能0 | 没有性能负例、数值失败、完整step，也没发现Cache/host硬件剩余 |
| `G4` | 可审核的首packet与最终closeout已push、blob/SHA可读回 | **属于报告归档PASS**，不能当完成模型科学验证 |

**资源**：A26G自行记录的实体HTTP body `2,143,328 bytes`（node109 `561,614`、controller发布元数据 `1,581,714`；Git/TLS另计）、本任务新增总量保守`<16MiB`、node metadata RSS峰值`23,728KiB`、CPU准备约`974s`、GPU runtime持锁0；共享GPU锁**仅非阻塞预检约7.2μs**。没有模型训练、GPU数据采样；旧A16R1/V1R1/A24与C16/AWMA报告按执行侧称未改。该资源receipt只是执行者日志，不是我们重新SSH测得的数据。

## 2. G0的真正设计缺陷：把“安全上限可监控”写成“预下载必须预知展开总尺寸”

官方HTTP `Content-Length`只表示**压缩体大小**。`STORAGE_PREFLIGHT.json`在尾部读取32bytes，得单个gzip footer的`ISIZE=1,213,739,008` bytes；根据[RFC1952 §2.3.1](https://www.rfc-editor.org/rfc/rfc1952.html)，该值仅为**原始数据长度模2^32**，不提供原tar完整展开上界；多member gzip更加不能依据最后footer推全集。首64KiB只看到一个size6,370,242的JPEG entry，非完整tar index。官方同源目录GET及两条假定索引路径为404，只否定这三个路径，并不证明别处没有索引。执行者拒绝猜JPEG压缩率或模回绕数，是正确的。

但原[A26G G0](../goals/AI_ARCH_A26G_GSSCALE_RUBBLE_GATED_NATIVE_109_V1.md)要求**必须在大下载之前**已经知道`raw解压＋4×派生＋env/ckpt`上界，否则强制`STORAGE_BOUND_UNKNOWN_STOP`。由于出版者没有发布小型完整tar成员/尺寸清单，这个门在该数据源上实际很可能无法通过；不是node109不具有解压能力，也不是科学对象Rubble不合法，而是**门被设计成预先证实通常需要全流读取才能知道的信息**。

**实际存储并未不足**：冻结资源`initial_free=144,192,610,304 bytes`（约134.3GiB），用户批准的是所有本任务新增≤`64,424,509,440 bytes`（60GiB）、始终可用≥`68,719,476,736 bytes`（64GiB）。按这个快照，即使任务真占满60GiB，仍可保留约74.3GiB，总量上有约10.3GiB额外余量（并发任务可改变，必须实机持续复核）。压缩包本体占`9,773,995,561 bytes`（9.10GiB）是确定的且**能被单独预算审查**。不必在允许安全下载这个已知体积文件前就证明所有未知后续派生量；但也绝不能因此直接盲`tar -xf`。

## 3. 修正方案：`BOUNDED_DOWNLOAD → READ_ONLY_TAR_SCAN → SAFE_EXTRACT`

这是一项**存储资格验证顺序**修正，不修改真实Rubble模型、相机、优化器、GPU资源/预算、数值目标、强软件baseline：

1. **修正G0a，先核已知压缩体积与可得科学输入**：CPU/source先检查当前单FS的free、旧任务占用、64GiB最小余量及25GiB下载预算，剩余CPU时间/合并COLMAP实际合法取回通道、环境发行闭包；如当前free不能容纳**9.10GiB已知compressed文件并保留64GiB＋额外任务安全余量**，直接STOP；大下载不应到第二个强制阻塞。
2. **有界下载压缩包，只是为了取得精确tar成员资格**：在新的自有目录内下载**这一份官方URL**，Range/ETag长度验证、断点重开核chunk身份、累计实际下载bytes、最终SHA256；下载途中对`df`、本任务磁盘新增与剩余预算进行实际持续监测。不可拉镜像、改目标scene、无限尝试Drive、跨越4h CPU及25GiB累计下载。**该动作须新的审批/修订合同，因为已完成的A26G原G0明确禁止它。**
3. **下载后、实际提取前执行完整只读tar内容扫描**：使用[GNU tar list而非extract](https://www.gnu.org/software/tar/manual/html_section/list.html)，或Python3.10 `tarfile`逐member的`r|gz`流式迭代；只输出限量的member统计/路径摘要/内容尺寸累加与SHA，不写任意展开payload。对entry数量、最大单文件、总uncompressed logical sizes、符号/硬链接、绝对/上级跳转、重复路径、special device、稀疏元数据与字节错误分别fail-closed，扫描CPU/日志/RAM封顶。gzip CRC/完整性需独立验证，不只相信文件名或`ISIZE`。
4. **真正解压门仅在“可明确装入剩余预算”后**：总磁盘占用不仅计compressed+raw tar file sizes，还计COLMAP、缩图输出、isolated env/build/cache/ckpt、文件系统块/metadata安全余量；如这些仍未知，必须以自有目录的真实增量/磁盘64GiB保留余量**实时硬限额控制**，到可能逼近前即安全STOP，不能默默写爆盘。只允许严格校验过的安全相对路径和regular files；不用无防护`extractall`。若member尺寸自身已经挤满额度就写`ASSET_EXPANSION_TOO_LARGE_STOP`，不继续安装/训练，也不把它当GPU负结果。
5. **原科学G1→G3不变**：只有真实COLMAP/image/point对应身份、软件隔离与CPUAdam有效≤24线程、原生数值/质量/强软件正确性PASS后，才能申请共享锁开展有限109 GPU诊断；early-only不能装成后期大Gaussian，不能启动20万步收敛。**任何资源上限都不扩大**，不得自动进入硬件机制。
6. **同一修订Goal一次性连续**：下载/索引/解压/依赖与模型兼容的普通确定性包装小修允许有界解决，不能再为tar index、pip wheel、路径、ABI分别开多轮；如果任一科学门不合格，保留partial与所有真实累计资源收据STOP，不能强行放宽科学条件。

**重要另一个资格缺口**：原node109直接Google Drive metadata超时，而controller能访问官方Drive HEAD。下一次若node109也无法直接获取合法官方COLMAP原件，不能只依据controller HEAD写`BYTE_QUALIFIED`；需在新合同中**明确批准且有审计的官方下载/自有进程中转路径**（下载+中转字节一并计入25GiB、目的端hash必须复核），否则`COLMAP_TRANSFER_NOT_QUALIFIED_STOP`。无许可不得用第三方不明镜像。

## 4. 正式科研决定

- **原A26G：`ACCEPT_SCOPED_G0_STOP`，历史STOP永不改写；独立归档闭合。**
- **G0故障类型：`GOAL_STORAGE_ADMISSION_METHOD_DEFECT`**；既非真实科学payload缺失，也非磁盘预算超额。报告状态保持`NATIVE_NOT_EVALUATED`，而不是“GS-Scale没性能价值”。
- **下一步仅建议一次`A26GR1`整链有界修正**，保留原A26G所有冻结科学对象、预算、数值和共享GPU锁。**目前只准备新Goal草案，不授权另一次下载或109 GPU**；需用户明确批准新合同再由原Lane M单次执行。新许可**不是**G0工具修复后无限重复实验的权利。
- **论文价值门维持**：即使实测早期几百步完整step，未达到动态大Gaussian真实阶段则`EARLY_ONLY`，不具P13大场景硬件因果证据；软件强基线已经含GPU cull/CPU Adam/forwarding，应优先接受无残余/负结果。

**最终：`A27_G0_STOP_ACCEPTED / BOUNDED_TAR_STREAM_AUDIT_PROPOSABLE / NO_AUTO_GPU_OR_HARDWARE_ADMISSION`。**
