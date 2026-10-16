# A65：同 batch 编译更新数值诊断与首批存储清理

**科学终态：COMPILED_PATH_NUMERIC_NONALIGNMENT。** 本轮在用户批准首批清理并继续 A65 后执行。

执行分支 `hrl/aiarch-a65-igb-small-compiled-numeric-109-v1`，原固定 Goal 起点 `afe42345c4b0c45b3e09f3cb32ce4e3e0de09989`。初次磁盘 STOP 及发布收据保持在 `history/initial_cpu_disk_stop` 与原提交 `fbb0fe210903872ace1005456b3fd8374d38abee`。没有 merge 协调分支或修改原 A61 STOP。

## 首批清理

仅删除用户批准的两处 pip HTTP cache、五份固定 revision incoming 模型副本，以及 E1 v3 两处闭合硬链接 trace；保留其余模型、控制文件、manifest/ACK、A61/A26GR1、NequIP 和 164 权威归档。

164 当前全量 SHA256 核验 **9172 项**，109 本地 SHA 核验 **9142 项**；模型与 trace 两端都与固定归档清单一致后才删除。E1 的 9,032 个 raw 文件各有两条硬链接，成对解除后只计一次实际空间。

文件系统可用量从 67206217728 bytes 升至 284689309696 bytes（265.138 GiB）。df 净变化含同时发生的外部文件系统活动；逐目标的 allocated/file 数、前后 df 和完整 SHA 记录在 storage_cleanup。

清理工程记录：初次占用检查将不可读 SSH/PAM 基础进程混同未知工作进程，修正后重验；首次归档 SHA 因 SSH 断线中断，改为 174-new 自有 /tmp 持久化逐文件记录、两个受限只读 SHA workers，完成后回读。最终汇总曾把110+9062误写为9182；全部逐文件SHA已通过后，按实际清单集合重新核对为9172并修正计数，复用mtime/size不变的持久化校验结果，未重新读取大payload。所有失败记录保留。没有写164归档或删除未验证payload。

## 输入、环境和独立性

只读复用 A61 已接受的官方 IGB-small：1,000,000×1024 FP32 features、19 类、原 20261015 split、有向 CSC 13,070,502 edges。官方 tar SHA256 `fa237780a84b7d1956c180564a9d080d61b43b32b2bf2810b3960f1ab028a919`，feature/edge/CSC/split/order 全部重新核 SHA。

Torch 2.2.0+cu121 / DGL 2.4.0+cu121 / PyG 2.6.1 / NumPy 1.26.4 / Triton 2.2.0 保持。新 runtime 仅用 symlink 建立同包只读视图，无安装或下载；排除旧 sitecustomize，使用只允许 A65 输出的独立写保护与 cache 路径。未 import 或执行旧 common.py、gpu_supervisor.py、native.py。

原 GraphSAGE、train_step、DataContext 与 validate_mb 按 AST 完全复制审计：3 层 mean、hidden256、fanout10/10/10、B1024、FP32 highest、TF32 关闭，Adam lr.003、weight_decay0、默认 betas/eps1e-8；编译入口仍是 torch.compile(train_step,dynamic=True)。

运行前后核 10,686 项核心运行库 SHA/size/mtime、A61 owned package RECORD、39 份原缓存 wheel；一份 NumPy 自带 pyc 因 pip 重新编译与 wheel RECORD 不同，已经同版本 Python 逐代码对象验证与同 SHA 源码一致。没有重写 bytecode、源码或二进制。CPU 比较器 12 项定向检查通过。

## 实际数值观察

仅一份新自然 B1024 batch，采得 **349419** 个输入节点。PINNED_CACHE_ON feature128MiB、graph1,000,000edges、async/pinned overlap 原路径，未作 cache replay 或再采邻域。实际 subgraph/IDs/labels 保留 NPZ；完整 fetched FP32 features 与只读源逐字节比较后冻结，每路执行前后完整输入 SHA 相同。

从唯一 seed20261015 CPU 初态建立三份独立模型和初始空 Adam state；完整 name/count/order/shape/dtype/逐参数 SHA 和 storage 身份分开记录。三路初态 bitwise 相同，无 parameter 或 optimizer buffer 跨模型共享。

| 路径 | 实际资格更新 | loss |
|---|---:|---:|
| eagerA | 1 | 2.92740559578 |
| eagerB | 1 | 2.92740559578 |
| compiledC | 1 | 2.9274058342 |

每路均为原 train_step 的 forward/crossentropy/backward/Adam 真更新。所有 initial/gradient/updated 张量与逐参数统计保留 raw；没有正式训练窗口或 profiler。更新门严格使用实际 Torch allclose(A,B,atol1e-6,rtol1e-4)，名称门单独判断；loss 门1e-5/1e-4。maxrel 的1e-12诊断分母不改变门限；完整 batch paired gradient 的旧1e-5/1e-3数值仅作描述，未冒充旧16seed FP64 oracle 资格。

| 参数 | A/B 失败元素 | A/C 失败元素 | A/C maxabs | A/C maxabs/tol |
|---|---:|---:|---:|---:|
| layers.0.lin_l.weight | 0 | 0 | 1.6633421e-06 | 0.823264 |
| layers.0.lin_l.bias | 0 | 0 | 7.0780516e-08 | 0.0697567 |
| layers.0.lin_r.weight | 0 | 1 | 2.0314474e-06 | 1.59161 |
| layers.1.lin_l.weight | 0 | 0 | 3.1292439e-07 | 0.0731644 |
| layers.1.lin_l.bias | 0 | 0 | 7.0780516e-08 | 0.0654961 |
| layers.1.lin_r.weight | 0 | 0 | 7.8976154e-07 | 0.716876 |
| layers.2.lin_l.weight | 0 | 0 | 7.4505806e-08 | 0.0697801 |
| layers.2.lin_l.bias | 0 | 0 | 7.0780516e-08 | 0.066405 |
| layers.2.lin_r.weight | 0 | 0 | 1.0430813e-07 | 0.0834989 |

first_failures、对应初值/gradient/更新量、所有参数的 gradient 和 signed update-delta 比较，以及同 gradient 的首步 Adam CPU 解析式核验见 parameter_comparisons.json / failure_element_attribution.json。cold compile wall 和 Dynamo graph breaks 仅为资格 metadata，不是性能样本。

## 数值定位和监督边界

A/B 所有参数在原更新门通过；A/C 只有 layers.0.lin_r.weight[59,378] 一个元素失败。原参数值0.0034851767122745514，eagerA梯度3.1561739888275042e-9、compiledC梯度3.1678837331128307e-9，相差约1.171e-11；更新后分别0.0027654748409986496 / 0.0027634433936327696，差2.0314473658800125e-6，允许量约1.276344339363277e-6。三路均满足各自同梯度的原首步Adam CPU解析式；证据支持先有微小梯度差异、经eps1e-8附近的Adam敏感性放大，不能据此声明不同optimizer语义或Torch bug。

监督器末次轮询保留 EXTERNAL_GPU_TASK_STOP 标志：此时阶段已为 NUMERIC_OBSERVATIONS_COMPLETE_STOP、子进程退出码0，最终NVML列表为空，但触发标志时的PID列表未保存。源码CPU定向复现证明“先读NVML、再读已退出进程组”可能误报自身退出；本次具体PID未捕获，不能将可能性改写为已证明的误报，也不声称完整独占资格PASS。原始flag保持，未改已执行GPU源码，未为此追加GPU重试。见 terminal_supervisor_guard_audit.json。该监督缺口与已实际记录的1元素数值超门分别报告。

## 资源与范围

GPU 共享锁非阻塞，累计 **32.530213s / 180s**；采样树 RSS峰 **9.570GiB**，NVML 进程显存峰 **6982MiB**。原 allocator fraction .70 与提前退出余量保留；采样可能漏瞬时峰，另保留 Torch allocator 峰值。所有自有子进程结束后释放锁。

资格观察完成 3，正式训练 **0**，下载/安装 **0**。新增磁盘按 inode 去重计量，报告、raw、cache、worktree 与本次清理记录纳入保守账；最终 Git 对象增量与 128MiB 门在发布前再次核算。CPU affinity 0,2,4,6，OMP≤4、Torch4、DataLoader0。

原 A61 源码/raw/cache/数据/环境全目录 metadata 前后一致，核心 DLL 与输入 payload SHA 回读不变。旧 A61 已有的失败不被本次新 batch 的结果追溯改写。A65 初次发布 Git pack 最大线程数未测的历史缺口仍保存在 history/initial_cpu_disk_stop/PUBLISH_CPU_OBSERVATION.json；本次后续命令均受四核 affinity 和逐命令 pack/index threads=4 限制。

## 科学解释与停止

本轮仅判断新受控 batch 的数值资格；不证明旧失败根因、Torch bug、正式训练性能、供数瓶颈或硬件收益。无论三路一致还是不一致，都保持原门限并在本轮归档后 STOP。若 eager/eager 自身超门，先接受自然数值波动证据；若仅 compiled 超门，记录编译路径不对齐并逐阶段分析，不自动归罪编译器。后续 GPU 科研须独立审查，本次不会自动启动 A61。

Contains information from Illinois Graph Benchmark (IGB), Khatua et al., KDD2023，按原已接受 ODC Attribution License1.0 的本地数值科研范围使用。原始特征、完整图、环境和编译二进制不入 Git；仅发布本 Goal 授权的小型受控子图/IDs、模型与 gradient 观察、代码和证据。

仅发布本独立分支。commit/tree/全部新增 blob/SHA 远端 fetch-back 与工作区 clean 收据在最终回执及独立私有 final_git_readback.json 保存，避免 commit 自引用。STOP。
