# EP-L2 唯一 Main 接管与五点准备回执

2026-11-09，EP-L2-8 用户明确指定本 API 窗口接任 174-new EP-L2 唯一 Main，继续 Performance-First 主线；本次授权限于**接管、只读核对和必要准备**，明确不授予五点科学启动。原 Main 的交接边界规定交付后不再开展科学启动；本窗口从本轮起承担后续唯一调度、预算、验收、归档和 Git 集成职责。没有创建常驻 dispatcher、修改科学台账或接管其他 owner 的资源。

## 证据时点与当前判定

| 事项 | 交接快照（有时间边界） | 本轮现场记录 | 判定 |
|---|---|---|---|
| 完整交接 | 本机 `D:/repo/ep_l2_handoff_20261109_v1/`；固定交接 commit `08fc797a44d24906e8e8b08ef8a95cb25a288e64`；`HANDOFF_OWNER_BOUNDARY.json` 记录 outgoing 不再科学启动 | 本机指定六份交接文件 SHA 与 manifest 一致；174-new review 工作树干净，HEAD 仍为 `08fc797a…` | 交接材料可作为接任依据，不授予五点启动 |
| Native/epoch/registry | `2026-11-09T09:33:53Z` 快照：epoch 2，`NATIVE_SCIENCE_ACTIVE`；52 个 EP 请求，五点批准/登记/消费 0 | `2026-11-09T19:25:51+08:00` 只读预检：epoch 2、holder `huangrulin-sshfs-174`，registry 与 epoch SHA 一致；registry SHA `6edffb87df4a25ba4d852dd50907d82fa8e5dc6f4a00122d524269b43da15485`，**与快照相同**；未见五点请求名 | 现场台账未出现交接后五点登记或消费；旧请求余额不能借用 |
| 模型与 owner | 快照无活动模型、无 EP supervisor 候选；若干旧请求的 `RUNNING` 字段属历史元数据 | 只读 `/proc` 预检未见 `accel-sim.out`/strace 模型候选或 EP supervisor 候选；因此本轮无可接续的在跑五点模型/模型 PID owner | 当前无活动模型的观察成立于预检时刻；不把旧 `RUNNING` 行当进程 |
| 版本 | 最新研究基点 `ea480a05fb32eeb6b88dd1d8be1b0b9c89eb8526` | `git ls-remote` 研究分支仍为 `ea480a05…`；review HEAD `08fc797a…`；A Core 工作树干净，HEAD `3d3887bb2e8d5073d13b0792ff9116834e89fe2f` | 文档交接 HEAD 与运行 Framework/ A Core 身份分开 |
| 资源 | 旧快照不构成准入 | 本轮 `/root/data` 可用 `21,368,356,864` B；真 164 挂载 source `admin-wcx@10.208.130.164:/home/shared`、fstype `fuse.sshfs`，可用 `42,226,938,703,872` B；MemAvailable `205,588,032` kB，cgroup memory.current `21,486,968,832` B，memory.max `274,877,906,944` B，cpu.max `38400000 100000` | 仅为只读观察，不是未来启动许可；cap10 仍需逐次对 CPU/RAM/cgroup/SSD/真164和其他 owner 承诺动态准入 |

只读预检使用本机交接包 `read_only_preflight.py` 经 SSH 标准输入执行，未在远端安装脚本。交接 review 目录本身不含该脚本，最初直接按其路径运行失败；改用同一交接脚本的标准输入后成功。该脚本只核元数据、进程候选和资源，不代替启动前科学资格、PID start_ticks/claim 的完整 join 或实时准入。现场检查没有改 Native、registry、Source、预算或进程。

**授权核对：** 在本轮用户消息及已读取的交接文件中，没有交接之后适用于五点的新明确科学启动授权；当前用户消息还明确排除该权限。现场 registry SHA 与快照相同、五点请求未登记，研究远端分支未前进。不能排除尚未提供给本窗口的外部聊天记录，但不能把这种可能性当授权。结论为 **五点待授权，0 个合法登记/消费/运行记录可接续**，不再等待未启动模型的结果。

## 已复用资格与准备锚点

- V4、V5、UMT1 等既有接受与负结果直接继承；UMT1 4/4 已关闭。工程基点 `ea480a05…` 接受 A Source5 的生产 CPU、Main 独立复放、8 份 283 项 parser/constructor 映射、有限 Source-specific X1 producer/consumer shell 与精确申请。C 是独立 Core/Framework，18/18 生产 CPU 完成而科学点 0；不能与 A 合并，工程 PASS 不等于新完整应用接受。
- 固定 A Source5：Core `3d3887bb2e8d5073d13b0792ff9116834e89fe2f`，Framework `9dd1ee57a83d83b56b7874bc7c716185ab52c8f7`，vendor `f90c430c3a1ce8f08c09942a5a1c3a797bb2295b`，ELF SHA256 `9db48c06ca64e441b5824071f52e0aa0be50374045fbdcef6cdf5d4469182f86`，静态库 SHA256 `7199f3dd5bdba2167186ca6858cd15603997f560660b54e8a1457761f115f48b`。现场 `FINAL_SOURCE5_BUILD_IDENTITY.json` SHA `3f6c62b8bf5555e8864d24cf0ed98e778161cb5fc1226c0793cbc7e17e7893b9` 与 `SOURCE_LINEAGES.json` 对齐；未重 hash 大 ELF/库。
- 五点权威申请：`L/agent_d/FINAL_EXACT_EXPERIMENT_REQUEST.json`，其中 `L=/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1`。现场该申请 SHA `646e6b5c718f68de6c1f12fd5c3fc2f0f73b07761757d009d0c773ac790c7247`，与 `NEXT_FIVE_POINT_REQUEST_INDEX.json` 对齐；固定 Git 发布版见 `ea480a05…/docs/ep_l2/operations/ep_l2_next_cost_aware_architecture_20261107_v1/agent_d/FINAL_EXACT_EXPERIMENT_REQUEST.json`。正式启动时须区分这份本地最终申请、固定 Git 版本及实际 activation Spec，不能只看文件名。
- 精确范围：`A_GEMM_OPTIONAL128_CONTROL3_V1` 的 `NEXT_A_OPTIONAL128_GEMM_WV_EXT0/1/2_V1` 各 1 次；`A_STENCIL_OPTIONAL128_NET2_V1` 的 `NEXT_A_OPTIONAL128_STENCIL_WV_EXT0/2_V1` 各 1 次。前者输入 SHA `140f6ed3a5cdb1d7183cd4d2acc37b086224a054893ef12d990fdb2d5ea3659b`，后者 `bd0309dfeec5745ba97400978c2c5f1413fa9c604376b3dd97e1dd3d5c8cc146`。同 A Source、`WV_ZERO_RO`、G32×8、850MHz/L100、完整 283 项；五点配置 SHA 和 ordered commands 见固定申请及 [接收模板](EP_L2_INTAKE.md)。不使用 Source78 的 EXT0 替身。

## 审批准备与真正缺口

给 EP-L2-8 的**待审范围**已经收敛为两个独立族、合计五个新完整应用启动：GEMM EXT0/1/2 与 Stencil EXT0/2，各点一次；无 S、C、RO、NI、3MM、Transpose、Tag/频率扫描。GEMM 0→1 看付费结构代价、1→2 看同硬件保留增量、0→2 看净效果；Stencil 0→2 只看完整净效果。各点可独立释放，没有跨族完成门。原 Main 工程申请的候选安全 hard wall 为 GEMM 每点 24h、Stencil 每点 48h，须在实际 Spec 中冻结；历史 wall 仅作软背景。

**授权前缺口：** EP-L2-8 对上述精确五点的新明确科学启动授权。现有 handoff、工程 PASS、旧聊天“在执行”与 cap10/旧余额均不能代替。

**授权后、首次消费前的必要 Main 正式绑定：**

1. 复核届时 epoch/registry、旧 owner 退出、模型/claim/PID generation 及其他 owner 资源承诺；按两个族登记新的精确 scoped 预算，各点 once-consumed，不重用旧请求或新建第二 dispatcher。
2. 用已固定 Source5、两输入完整 binding/ordered commands/ordered kernel 身份及五份 283 项配置，形成不可变的逐点 Spec、actual echo 与 Host/Native/consumer 映射；核对 43 字段 Host、22 项 Native 和实际 Host/Trace-child 依赖 pin、boot/mount。Main 完成最小 Source-specific X1 consumer 正式接线与 Base/Ext/global Payload 守恒、精确 Native scoped route。现有 CPU/工程资格直接复用，不重做整轮。
3. 每点单独作当前 CPU/RAM/cgroup/SSD/真164 准入，保留 Native 实际 floor 5GiB 和其他 owner 已承诺增长；cap10 是上限，不要求凑满。随后由唯一 Main 调度。技术失败保留消费和负结果，不自动重试/退款。
4. 正式关闭时核对完整 cycles、命令/kernel/CTA/instructions、协议/drain，真164 full SHA 与两个独立完整 Native target 恢复，再验收、发布、远端 HEAD 回读。小工程包的两次 tar 恢复不能替代应用 Native 恢复。

下一件具体工作：将本回执中的五点精确范围交 EP-L2-8 审定是否授予新的科学启动权限。收到明确授权后，先按上列绑定与实时准入，不凭本次资源快照直接运行。若科学窗口暂不授权，本 Main 可继续独立的小型工程/证据准备，但五点保持未登记、未启动。
