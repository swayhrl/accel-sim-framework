# A26GR1｜Rubble有界压缩包资格修正＋原G1–G4连续原生发现（单Goal草案）

**设计执行者：ChatGPT／AI-ARCH Discovery；拟执行者：既有node109 Codex Lane M。**  
**状态：`SCIENTIFIC_CONTRACT_PROPOSED / USER_FRESH_APPROVAL_REQUIRED / NO_AUTO_RESTART`。**  
**科学目标和资源：严格继承已接受[A26G原合同](AI_ARCH_A26G_GSSCALE_RUBBLE_GATED_NATIVE_109_V1.md)及[A27独立STOP审查](../reviews/AI_ARCH_A27_A26G_G0_STORAGE_GATE_INDEPENDENT_REVIEW_2026-10-14_V1.md)；** 只更正无法凭小元数据证明gzip解压总上界的**存储安全资格顺序**，同时授权有审计的官方COLMAP实际byte转运途径。**没有批准这个R1前，不执行、不开109 GPU或大型下载，不重启旧A26G。**

## 0. 原科学边界与两个必须改变的合同入口

- 原A26G `hrl/aiarch-a26g-gsscale-rubble-gated-native-109-v1`的`e760f332ed41c609d3d19548f87d90b3f11357d8`是**科学合法G0 STOP**（tree `b2165a3fc75ca15c21876a46770e3b03027c8165`）。旧source、21文件与`STORAGE_PREFLIGHT`不可覆盖/静默改写；这次必须**新分支/新worktree/新日志和报告**，起点建议旧STOP SHA，报告目录后缀`A26GR1`。新Goal/独立审查读取本协调固定commit的明确路径，不merge协调branch。
- **准确新授权变更#1**：原G0要求**下载前**已知`tar解压＋缩图＋env/ckpt`准确上界；对没有官方tar index的gzip包不可实现。R1改为：**下载前证明已知压缩体积可安全放盘**，允许一次有界下载该官方`rubble-pixsfm.tgz`；**下载后且解压写盘前**才在只读、限资源的流式tar成员遍历中取得真实展开size。未知展开不再自动判STOP，但仍不允许`tar -xf`在未确认空间与路径安全时盲解压。
- **准确新授权变更#2**：作者Google Drive官方发布的`cameras.bin / images.bin / points3D.bin`已由A26G通过controller只读HEAD证实文件存在，但109直接访问超时。R1若node109仍不能直接下载，允许**仅这三份已定位、确属作者发布的公开COLMAP对象**通过既有受控controller官方HTTP下载再安全转入node109（或经认证流式代理），两端全文件SHA和原始身份一一复核，public Git不记私有代理地址/帐号/凭据；下载/中转与额外缓存纳入原批准的**网络/磁盘预算总账**。安全路径不可用则`OFFICIAL_COLMAP_TRANSFER_NOT_QUALIFIED` STOP，**不得**换无权威来源镜像。
- 不改科学对象：真实Mill-19 Rubble，作者固定源码`SNU-ARC/GS-Scale@6471e958f7e318f4870234d8107e0aa91c2d6932`；强软件`fully optimized GS-Scale`和合法fit才测的`gsplat GPU-only`、naive host仅消融；数值/质量、完整step分母、early/late身份、禁新硬件机制全部不动。

## 1. 总预算仍沿用原用户已批上限，**跨A26G和R1合并记账，不隐形复位**

| 项目 | 总体绝对上限与已消耗证据 |
|---|---|
| 累计官方外网下载 | **≤25GiB**，原A26G已记官方HTTP entity bytes `2,143,328`；R1新数据＋software包＋可能的controller→109必要转运采用保守**合并去重与累计传输字节记录**，宁可高估，不能另立25GiB以规避前项 |
| 新增磁盘（同FS） | **≤60GiB**，原A26G估算新增`<16MiB`仍在，R1压缩原档约**9.10GiB**、COLMAP约**0.55GiB**，raw/extract/resized/newenv/log/ckpt均同账；任时实际FS可用**≥64GiB**，空间突变立刻保护性停止自己任务 |
| CPU准备预算 | A26G记录`974.234433s`；与R1合计**≤4小时**（R1剩余约3h43m46s），CPU全树≤24有效线程、主机RSS≤48GiB；若网络/解压CPU时间超界STOP，无时间到期自动续跑 |
| GPU | 109仅同一RTX4080，`/data/c16/locks/c16_gpu_campaign.lock`**非阻塞独占**先于任何CUDA init，所有GPU子段与先前A26G持锁记录合计≤**2小时**，任务显存≤**14GiB**；G1 CPU下载/scanning绝不借锁跑GPU |
| 数据/训练 | 一个自然Rubble、最多三个**真正连续训练可到达的**已预注册窗口；不做20万步完整训练、不追加任何新模型/多seed/holdout、不得SM quota/NCU/NSYS/NVBit/Accel-Sim/new Cache |

**风险预算策略**：对9.77GB已知compressed体积只要原free与原60GiB cap/64GiB reserve以及网络预算同时能满足，便可安全进入archive fetch；这不证明expanded scene一定fit。下载/解压/resize前逐阶段重新计真实free与任务增长，任务超额或无法准确界定就STOP并保留证据，不以“9.77GB不大”欺骗完整训练内存。

## 2. 一个连续Codex Goal的科学可执行门（不要人为开多个Codex窗口）

### R0｜CPU源、依赖、官方目标身份和**已知压缩体**安全预检

1. 原Git起点/旧STOP readback、当前磁盘RAM/网络/下载cap、author git SHA和source差异、官方scene URL HEAD/Range与A26G分段hash，以及三个官方COLMAP fileID/length全部核对。node109 Drive若连接不通，先验证已经批准的受控controller转运**能可靠传一份小合法元数据/前缀并做双端SHA**；否则别下载9GB再遇到科学COLMAP缺失。
2. 只读一次核**完整软件发行闭包**可用性：原作者Python3.10、torch2.2+cu121、torchvision0.17、IPEX2.2、NumPy<2、旧gsplat+依赖，以及CPUAdam/编译ABI/CPU线程限制方案。已有A26G metadata的四个关键发行hash可复用，**缺剩余轮子的确定性闭包可在本阶段补齐**，不是安装前逐叶包STOP。会改变作者数学/算法/质量的依赖替换不得提前许可。
3. 目标FS与新工作目录安全，**仅已知compressed archive需要的空间可计算**。若full tar尺寸未知但已确定压缩字节能完全落盘、允许后续**只读扫描**且不违反总预算，就合法晋升下一门，不再因为未知展开体积预设`STORAGE_BOUND_UNKNOWN_STOP`。

### R1｜受控完整官方tar下载，先扫清实际成员体积再提取

1. 官方tar单份下载到任务自有临时目录，`Range/Content-Range`每chunk合法，累计流量、SHA256、字节总长与HEAD长度完全一致；etag/last-modified有变化时不拼不同版本。不从未知镜像/随机资料代替。中途磁盘/下载/CPU时间预算异常立即STOP；只在自有路径保留可核metadata。
2. 下载完、**不写解压payload**前进行**有界tar list/stream scan**（例如Python3.10 `tarfile` streaming只读、或者GNU tar `--list`，均须真正完成整文件扫描）；记录file size和数量、最大member、完整expanded logical size、prefix与实际路径；gzip checksum/CRC与tar完整性校验单列，不能靠footer `ISIZE`。限制扫描CPU/RSS/成员数与输出日志尺寸；如果发现可用size超本任务剩余空间则`ASSET_EXPANDED_BOUND_EXCEEDS_CAP` STOP。
3. 明确拒绝absolute/parent traversal、duplicate冲突、symlink/hardlink、设备节点、sparse与恶意PAX等无法安全界定的tar entry；明确防解压炸弹。**未经审计不能用`tar -xf`/Python无防护`extractall`**，自写解压只可按已经过安全检查的regular relative files到唯一新root，写入过程中持续核实际FS余量、任务增长与文件checksum。遇到代码需要变更目录结构时不能因此改变科学相机/点云内容。
4. 确认compressed+expanded+COLMAP+4×resize+newenv/build/cache/小ckpt**可合计受控在原60GiB中**，不足则不得以“先解压完再删原压缩”越过任时硬上限；只有自己本次新文件可在自有目录按安全规范清理，原旧数据和author原文件不改。
5. 通过直接可信作者来源取得上述三份COLMAP二进制（必要时获批controller转运），双端完整SHA，检查`cameras/images/points3D`真格式/相机文件映射/数据版本，按作者4×缩图与`test_every=83`冻结scene和camera身份。**只有作者真实科学payload全部有效才给`REAL_SCENE_BYTE_QUALIFIED`**，不以官方HEAD替代。

### R2｜独立旧软件发行及CPUAdam资格（不改变数学）

- 仅新隔离Python3.10/torch2.2+cu121/IPEX2.2/gsplat/CPUAdam环境；遵守精确依赖Hash、编译器/SDK匹配，先CPU only看完整包闭包。普通官方**同版本**wheel/sdist、C++库路径/编译临时目录/Git/manifest允许在剩余时间预算内少量`bounded solve-and-continue`修复并回归，不无限重试/新版本跨越。
- author`omp_set_num_threads(64)`在109 16核24线程上必须通过cgroup/OMP_THREAD_LIMIT/affinity等**实际已安装CPUAdam小canary**证有效同时线程≤24；`OMP_NUM_THREADS=24`字符串并非验收。限定线程方式标软件identity，改变数学/optimizer epsilon/strong kernel算科学STOP。
- env未合格不得启动GPU正式计算，不能偷偷用旧NequIP环境替代作者。

### R3｜真实完整step功能/质量→符合才有限native诊断

- 仅在R0–R2符合且**实际非阻塞持有共享GPU锁**后用完整Rubble camera/点云/GS-Scale强路径跑最小合法full step，核CPU Adam、H2D/D2H、GPU render/backward、梯度/状态及数值有限性。GPU-only只在相同真实条件合法fit时对照；原deferred Adam非逐bit一致，`APPLICATION_QUALITY_MATCH`需由实际数据与预注册标准支持，否则PARTIAL。
- 通过功能/必要质量门才可作原A26G已预授权的**有界**诊断：early真实step100–200，并仅在预算真的足够持续到`refine_stop_iter=15000`附近时才记录late两个阶段。不能用只有`{step,splats.state_dict()}`的checkpoint当完整Adam/RNG/schedule恢复权威，也不能以合成Gaussian模拟后期。
- 未插桩step wall和observer运行分开，按真实主机与CUDA event时间域报告camera ID、Gaussian生灭/稳定ID、CPU Adam线程和实际unhidden time、validID/gradient D2H、H2D、GPU计算和join等待的**重叠并集**；不能相加双计，不允许估计未测物理带宽。**若仅有早期小Gaussian样本，结论必须`EARLY_ONLY / LATE_RESOURCE_HEADROOM_UNKNOWN`**。
- 这轮只能说`SCOPED_EXPOSED_SERVICE_CANDIDATE`或`SOFTWARE_ABSORBED_OR_UNIDENTIFIABLE`，**绝不能根据数据直接启动新Cache/atomic/SM resource机制**。

### R4｜合法停止/完整归档（任何早期STOP都照做）

- 新独立`docs/ai_workload_research/runs/AI_ARCH_A26GR1_GSSCALE_RUBBLE_109_V1/`保存`RUN_IDENTITY`、`BUDGET_CUMULATIVE`、`SOURCE_PROVENANCE`、`HTTP_DOWNLOAD`、`TAR_SCAN_SAFETY`、`ASSET_MANIFEST`、`COLMAP_TRANSFER`、`ENV_LOCK`、`BUILD_AND_THREAD`、`NATIVE_FUNCTIONAL_QUALITY`、`MEASUREMENT_WINDOWS`、`GATES`、`FINAL_REPORT`和`SHA256SUMS`（不适用的写NOT_RUN），附小型原生raw、UTF-8与sha、自有目录大小/资源、耗时和STOP原因。
- 禁止大场景文件/conda wheel/个人凭证入Git、不得把压缩包复制164、不得覆盖原A26G`e760f…`的21份文件。只有可复核的小报告和脚本在**新A26GR1 branch** commit/push/remote fetch-back，并核独立精确commit/tree/blob后STOP，不merge协调。任何运行结果需ChatGPT独立审查后才能成为新性能/机制资格。
- 失败分类必须准确：`OFFICIAL_INPUT_TRANSPORT_BLOCKED`、`NETWORK_OR_BUDGET_STOP`、`ARCHIVE_CORRUPT`、`ASSET_EXPANDED_BOUND_EXCEEDS_CAP`、`COLMAP_IDENTITY_NOT_ESTABLISHED`、`ENV_ABI_STOP`、`CPU_THREAD_LIMIT_STOP`、`GPU_LOCK_DEFERRED`、`NUMERIC_OR_QUALITY_STOP`、`EARLY_ONLY`；**不再因无预发tar size索引这个已知事实反复STOP**。

## 3. 执行申请与结果限制

**本稿只能作为一次性新的用户审批候选**：原用户明确批准A26G一次，且Lane M依照其严格式G0合法STOP，**不能把旧批准擅自迁移为A26GR1新的下载或GPU执行**。需要用户明确批准这个**完整合同及controller文件转运边界**后才创建执行branch、发单条Codex Goal。届时无需再分成下载索引测试/依赖安装/训练三条任务。

若即使按R1仍无法在原预算获取真实source+scene、作者依赖或者足量的后期强baseline，则正常有据STOP并关闭本次Rubble原生复现路线，不继续循环`R2/R3`或为硬件mechanism造弱基线。

**候选终态：`A26GR1_ONE_SHOT_BOUNDED_ARCHIVE_AND_ORIGINAL_NATIVE_DISCOVERY / USER_APPROVAL_PENDING / NO_AUTO_EXECUTION`。**
