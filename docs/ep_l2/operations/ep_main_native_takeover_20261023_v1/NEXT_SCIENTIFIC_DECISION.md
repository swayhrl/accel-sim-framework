# EP-MAIN 下一项科学决策与统一待办

状态：DESIGN_ONLY / NOT_AUTHORIZED_TO_RUN。当前 native 新启动预算 0。本文不恢复旧 E2 Goal，也不把旧 r5 的两端余额带到 epoch2。

## 首要问题与预注册判断

在不缩减 Tag way、不扩容 payload、不改输入或 DRAM 时，真实 workload 是否会到达“新 Tag 需求 + 同 set 无可替换 way + 可 detach 的 RO pending 对象”这一必要联合条件？

现有 CFD/DWT 的 r5 已接受点提供触发缺失的负证据，SGEMM 提供正证书但 resident-hit 的上游对照。下一端只优先提名 vectorAdd_4M r5 F：它是历史 r5 未启动条件，精确输入已在真164可用，输入规模和本地 main61 资格耗时已有参考。此选择基于输入可用性与覆盖缺口，不基于新 F 速度；无需为此重跑 CFD/DWT/SGEMM。不能声称一个 Vector 点代表全工作负载。

若 Vector 同样无生产 TagFAIL，则先收紧 T 的应用收益论断，保留 Conv 为下一轮单独决策，不自动扩为四端或继续随机扫描。即使出现 detach，先证明生命周期和正确性，再决定是否值得安排同 binary 的 T-OFF 控制；当前提案不含该额外启动。

## 精确一端候选（尚非启动 spec）

| 字段 | 固定或待完成内容 |
|---|---|
| 新唯一 cohort 候选 | EP_NATIVE_TAGPRESSURE_VECTOR_HOLDOUT_V1；仅名称草案，尚未登记 |
| 新请求预算候选 | 完整应用最多 1 次；0 自动重试/退款。工程资格与实际小型 fixture 的范围亦需在最终授权中列明，本轮不运行 |
| 历史 spec 参照 | E2 精确 HEAD 7c2f830175f40e16651eab4a3cd3a7af73e9927b 的 approved_r5_joint_r1/specs/vectorAdd_4M_F_SPEC.json |
| 运行谱系候选 | Core1093d2629e3d6a9130ba25b9dd119b6f3e16c092、Framework9dd1ee57a83d83b56b7874bc7c716185ab52c8f7、vendorf90c430c3a1ce8f08c09942a5a1c3a797bb2295b |
| binary/archive | e511cce7d8bcd5a3ebbe6255f42ebe153547484a69c6857ab55f7a8835a2dc33 / 7b590d2551ffe094108bef07f1ee467e6890f3eee37aa30e1072c6be3fb7687a；当前未声明 native 可用 |
| profile | F：W/V/T/M 全 1；payload1168/slice、4bank、P1、WBUF16、descriptor512、per-address32、lineMSHR128、WAD128、16 Tag ways；不改变有限设计 |
| 历史 research config composite | c2ab92dfc528d53e91d0af9c62bd2fb1bb3941a8440abce16422b2a8bd7bc450；只固定历史参照，native 绝对路径重绑定需独立记录全部差异及新身份 |
| observer | EPL2_DETACH_DIAG=1、EPL2_TAGPRESSURE_DIAG=1；沿用只读观测与分域，不改变决策顺序 |
| 输入 | 已有 EP_VECTORADD_S；kernelslist.g + kernel-1.traceg；trace composite 138f33b61fffe99c5e9c31a5943a96edcab180e6aaaa5ed4714021249c0d2940 |
| 完整终态 | 56000000 instructions、1 kernel、15625 CTA；真实 exit/wait、64 slice、hardware drain、schema/overflow/global-phase residual/ownership 全闭合 |
| 预计资源包络 | 历史 spec 为 1 CPU、9GiB memory_bytes、单端 result≤384MiB、新增观测≤64MiB；native 总包络须计入进程树、资格/恢复/临时空间及其它项目预留后独立冻结，不是实测峰值保证 |
| 热输出与时间 | 新 UUID 的本地 ext4；历史有效 timeout/start/intake deadline 均为 null，termination_contract 的10800仅保留出处，不是历史运行上限；新 epoch2 停止策略待精确规格授权，原生墙钟未知，不改写旧政策或用中途 cycles 接受性能 |
| 对照 | 复用已接受 CFD/DWT r5 零触发点、SGEMM r4 正证书无事务点作各自身份的机制背景。main61 native Q2 只作入口/完整输入和成本参照，不作跨 binary S/F 比较 |

历史 source spec 与 producer 完整副本、blob SHA、SHA256 记录在证据索引；最终 native spec 必须新建，不能把历史 launch_owner、queue、lease 或绝对路径照搬。

## 结果分类

1. 无 RO 事务：仅判断该点上游机会缺失；不能推出所有 workload 或全部路径无压力。
2. 有 RO，但 covered 新 Tag 条件没有 all16 RESERVED：支持该点触发缺失；skipped 域为 NA。
3. 原始压力存在但无 eligible：分开报告 attached/reuse_seen/ready/门控原因，不将边际频率相乘成联合概率。
4. eligible 与压力共现但无实际 relieve/detach：检查生产调用域及前置门，暂不归因于 T 失败。
5. detach 发生且 trigger/victim 完整退休：可证明该点生产机制被激活；无 T-OFF 配对时不声称独立性能收益。
6. 身份、终态、数值域、overflow 或 drain 不闭合：HOLD/STOP_UNACCEPTED，保留已收费尝试，不自动补跑。

head-cycle、请求、事务、sector、bytes 和物理周期保持各自分母；不同 slice/阶段等待不能相加为独占 GPU stall。0 分母的比例为 NA。

## 启动前必须完成的具体工程与授权

这些是下一步依赖，不是本轮请求用户批准运行。

- 用精确 COPY_ONLY selector 取得 r5 runtime 或选择新的有身份重建。旧主程序路径为 `/workspace/build/ep-l2-ms20261022-e2-tagpressure-observer-r5/accel-sim.out`（87878744B），archive 为同 build 下 `gpgpu-sim/src/gpgpu-sim/libgpgpusim.a`（82151574B）；绑定上表 SHA，复用已验证真164对象优先。源始终 KEEP；所需 ELF 依赖、native decoder/schema/config/证书与完整 source commit 清单一并由精确 selector 定义。不得泛取整个旧环境。
- 若重编译，记录 compiler/flags/实际新 ELF SHA；即使相同 Core，也不能默认继承 e511 SHA 或旧 native Q。冻结 main61 runtime 不被覆盖。
- 在现有 sole epoch2 frontend 有界接入新 cohort：当前 COHORTS 仅迁移资格，不能直接接受此候选。新增入口代码必须有独立 source/hash、预算/唯一请求/host/mount/input/config/profile/resource/closed prior intent 门，并用不执行模拟器的工程检查验证；不建立第二 controller。
- 完成真正的新 native source/binary/profile/input 资格；仅复用明确等价的已有小型证据，缺少的控制逐项列清，不能用 producer48 fixture 或 C 证书代签。
- 最终提交可审查的新 spec、准确实际启动计费范围、runtime 与 trace hashes、磁盘/RAM/CPU/其它项目预留、输出+恢复+暂存包络和单 receiver 计划，再取得精确用户授权。当前历史 SOURCE_PREFLIGHT 是旧快照，不可把其 other reservations=0 当作实时值。
- 原生输出通过独立科学接受后，按既有 outbox 归档真164、全 SHA、独立 native Target 恢复；源保留。原账本和T0不变，新 epoch2 ledger 单独收费。

## 唯一统一研究待办

| 优先级 | 问题/工作 | 现有基础 | 交付与停止边界 |
|---|---|---|---|
| P0 | 固定接受状态、负结果和论文来源 | 本交接的44结果/25对与原始失败/HOLD | 已完成只读索引；当前母稿未提供，表号映射未知，EN-v22权威不变 |
| P1 | 上述真实 Tag 压力联合问题 | r5 CFD/DWT + r4 SGEMM，Vector r5缺口 | 先完成一端新 native spec/资格/授权；结果决定是否值得后续T控制 |
| P2-W | unified WB 消除copy是否降低实际关键成本 | Conv W-only与copy-free、DWT负/近持平、vector高WB背景 | 先复用已接受同binary控制；copy减少不直接等于端到端改善，不添参数扫描 |
| P2-V | victim 的实际读服务及dirty-forward是否带来净lower流量收益 | B旧FWT观察、后来E049/E050接受配对；Conv稀疏V、SGEMM低W对照 | 明确区分旧未接受快照与新接受完整epoch；若需因果验证再单独申请同背景V-OFF |
| P2-T/M | T detach与M lineMSHR旁路的独立必要性 | Conv F/WV_M、F/WV_T旧控制为同cycles，正向RO证书/诊断另组 | 保留零效应；正向输入若需新控制，用同binary同证书独立规格；不借旧空证书结论覆盖新正向域 |
| P3 | 真实输入可移植性与端到端吞吐 | 原MAIN6/7，SGEMM独立探索，btree地址域HOLD | 先有精确trace/source/capture/numeric身份；NAS吞吐只对已验证输入有效，IO和sim wall与模拟cycles分开 |
| P4 | 面积/时序/成本与稿件声明 | 历史成本与有限资源模型 | 复用准确源码/网表/工具出处；未测字段保留UNKNOWN，不把oracle容量上界叫硬件收益 |

每项均归 EP-MAIN 维护，不重建 A–F 常驻网。T-OPS 只在精确资产/存储/入口任务出现时按需调用；大型已批准实验可设有限临时子 Lane，须有精确任务、隔离分支/工作树、合并回读与关闭。当前不创建子 Lane、后台轮询或长期扫描器。
