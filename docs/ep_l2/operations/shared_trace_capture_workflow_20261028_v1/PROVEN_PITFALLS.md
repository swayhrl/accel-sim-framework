# trace采集与处理的已证实问题

先区分环境、控制入口、采集正文和消费者问题，再按失败阶段修复。原始日志和失败回执保留，已有采集、POST与归档结果直接复用。
| 问题 | 实际表现 | 处理和防再犯 | 证据 |
| --- | --- | --- | --- |
| 空闲状态过期 | 历史空闲回复不能代表当前GPU可用。 | 逐项核实时队列，取同一共享锁后复核；真实FD随所属进程继承，闭合后释放。 | [E001](evidence/E001_ACTUAL_FIRST_JOB_POSITIVE_CAPTURE_HAND_BACK_V15.json) |
| 内部指纹漏更新 | 外层47文件全匹配，内层加载器仍引用旧helper指纹，GPU启动前被拦。 | 同步更新引用并做字面指纹闭合及真实嵌套加载检查。 | [E002](evidence/E002_ACTUAL_DEFERRED_INNER_HELPER_PIN_RESOURCE_HAND_BACK_V16.json) |
| 应用与包装进程退出不同 | 应用采集返回0，包装进程因心跳读取线程退出问题返回1。 | 分别持久化两种返回值；收完ACK和EOF后有界join，保留原失败。 | [E003](evidence/E003_remote.stderr.log) [E004](evidence/E004_LEAF_CAPTURED.json) [E001](evidence/E001_ACTUAL_FIRST_JOB_POSITIVE_CAPTURE_HAND_BACK_V15.json) |
| 服务找不到工具 | nvdisasm在磁盘上，但隔离服务PATH无法找到，应用返回1。 | 固定服务PATH和绝对NVDISASM，并在相同环境做离线依赖检查。 | [E005](evidence/E005_ACTUAL_CFI_A003_POSITIVE_CAPTURE_HAND_BACK_V1.json) |
| 身份采样不能代替执行事实 | 原a001身份快照失败且真实应用返回值未知。 | 保存最早Popen和真实wait；不能由空日志推断没执行或断言发生birth race。 | [E005](evidence/E005_ACTUAL_CFI_A003_POSITIVE_CAPTURE_HAND_BACK_V1.json) |
| 控制与重计算预算混用 | Native重计算未来预算HOLD，轻控制入口可有独立合格资源角色。 | 按实际角色验收，保留完整预算披露；不把控制通过写成重计算通过。 | [E006](evidence/E006_ROOT_CAPTURE_NAS_ONLY_CONTROL_ROLE2_PHYS16_DECISION_V1.json) [E007](evidence/E007_ACTUAL_FRESH_FULL_ADMISSION_V16.json) |
| 跨主机路径不同 | Native绝对路径不是109可执行路径。 | 绑定同字节身份与两端路径，在109重开实际模块和元数据。 | [E008](evidence/E008_ACTUAL109_DATA_STAGE_AND64_METADATA_REOPEN.json) |
| 停止和成功口径混淆 | 启动前defer不等于workload失败；父进程退出也不等于资源已闭合。 | 核同scope、PID与ticks、ACK、cgroup和原锁；排除已采项，仅重试失败阶段。 | [E001](evidence/E001_ACTUAL_FIRST_JOB_POSITIVE_CAPTURE_HAND_BACK_V15.json) [E002](evidence/E002_ACTUAL_DEFERRED_INNER_HELPER_PIN_RESOURCE_HAND_BACK_V16.json) |
| SASS末尾分号 | NOP;被错误当成opcode NOP;，与登记NOP不符。 | 仅规范化无后续token的一个末尾分号，保留原SASS和严格验证。 | [E009](evidence/E009_OP_TOKEN_ONLY.patch) [E010](evidence/E010_ROOT_INDEPENDENT_FULL126_FUNCTIONAL_ACCEPTANCE_V1.json) |
| 读取上限触发预分配 | AS128MiB进程用read128MiB加1读取约1.8MB元数据，提前MemoryError。 | 64KiB分块，保留原总上限；用真实AS边界重放。 | [E011](evidence/E011_ACTUAL_AS128_CHUNK_GATE_REPLAY_V1.json) [E012](evidence/E012_bounded_json_chunk_v1.py) |
| 绑核声明不等于实态 | AllowedCPUs声明未实际收窄进程初始affinity。 | 显式设置后读取sched_getaffinity和cgroup核验。 | [E013](evidence/E013_ROOT_INDEPENDENT_ONELINE_SOURCE_ADMISSION_V5.json) |
| NAS控制锁属性映射 | NAS私有锁呈现的owner和mode与本地期望不同。 | 仅0字节控制锁转109本地0700目录和0600文件；正文与日志继续164。 | [E014](evidence/E014_ROOT_INDEPENDENT_LOCAL_PACER_SINGLE_ADMISSION_V6.json) [E015](evidence/E015_REMOTE_DERIVED_START.json) |
| 心跳瞬时不可见 | SC已完成472项后，一次ENOENT导致退出。 | 仅对短暂读取竞争有界重读，身份和新鲜期限不放宽；采用已闭472而非重算。 | [E016](evidence/E016_REMOTE_DERIVED_TERMINAL.json) [E017](evidence/E017_CURRENT109_BODY_SHA_ADOPTION472_REPLAY.json) |
| 容量文本替换误伤余量 | 2GiB模型容量改动连带将16GiB物理余量变成12GiB。 | 保留真实运行偏差，单独修正并测边界；以后按精确语法表达式修改。 | [E010](evidence/E010_ROOT_INDEPENDENT_FULL126_FUNCTIONAL_ACCEPTANCE_V1.json) |
| 握手JSON提前可见 | 文件已出现但JSON尚未写完，ACK读取失败。 | 关闭并同步临时文件后原子发布；仅短暂不存在或JSON读取竞争有界重读。 | [E018](evidence/E018_SOP_HANDSHAKE_VISIBILITY_ADDITION_V18.json) |
| SSH不保留传入的锁FD | pass_fds参数正确，实际SSH仍关闭FD，远端未结束而锁已空闲。 | 由不exec的Python relay持有真实锁FD，独立核实远端闭合后释放。 | [E019](evidence/E019_ACTUAL_PYTHON_RELAY_4LEASE_REALSSH_PARENTCLOSE_LIFECYCLE_V4.json) |
| CURRENT时间戳触发误拒 | 版本不变，仅时间刷新导致发布CAS失败。 | 仅忽略明确时间字段的值；完整键集、版本、路径、计数及不可变目录SHA仍严格核对。 | [E020](evidence/E020_ROOT_INDEPENDENT_PUBLIC48_PAIR_ACCEPTANCE_V1.json) |
| 心跳线程执行NAS操作 | 旧失败没有精确停止原因；源码显示资源采样会读取NAS自身文件。 | 发送与物理采样分开；缓存已验证源码SHA，保留实际资源超时和失败停止；用真实函数与管道验证。旧失败原因仍标未知。 | [E021](evidence/E021_ROOT_INDEPENDENT_SOURCE_RUNTIME_AND_CONDITIONAL_CONTINUOUS19_ADMISSION_V20R3.json) [E022](evidence/E022_ACTUAL_CACHED_COLLECTOR_AND_HB_DELAY_STOP_CASES_V20R3.json) [E023](evidence/E023_REMOTE_CLOSED_PROPOSAL.json) |

## 状态和适用范围

表中的历史运行事实保持原样。部分后续修复仍处于候选或续跑阶段，是否实际部署和完成以对应运行回执为准。特别是心跳有界重读不能凭文档当作已续跑成功。

Gaussian64已有的完整功能回放可以复用。零有效CALL或RET不证明通用CFI支持；历史12GiB资源门的运行也不声称全程符合16GiB要求。新增默认采用轻量准入，归档和公共发布仍须实际完成。

详细原因、适用限制、原始路径和完整SHA见[机器可读问题清单](PROVEN_PITFALLS_V4.json)及[证据索引](EVIDENCE_INDEX.json)。

## 后续实际故障及修复边界

- **远端采集与Native控制预算混用**：旧入口把67GiB预测余量用于只做调度的Native进程。现在按实际2GiB控制角色验收，保留主机16GiB、cgroup8GiB物理余量和独立心跳；这不授予Native重计算资格，也不改其他项目预算。证据：[E024](evidence/E024_ROOT_REMOTE_CAPTURE_CONTROL_ROLE4_PHYS16_CG8_DECISION_V1.json)。
- **普通CPU进程被当作GPU冲突**：scan曾因fwupd约214MiB RSS超过旧128MiB阈值而保留退出。CPU进程现作为观测信息；实际内存、OOM、PSI、GPU/显存和共享锁检查继续严格执行。此次partial仍不算采集成功。证据：[E025](evidence/E025_ROOT_109_BOUNDED_CPU_COACTIVITY_POLICY_V1.json)、[E026](evidence/E026_REMOTE_CLOSED_PROPOSAL.json)。
- **参数契约沿用旧输入**：Gaussian-s256旧尝试仍绑定-s64参数SHA，4.445秒后真实返回-6。修复只改精确参数绑定，并在GPU启动前核对profile、binary、NUL分隔argv、语义映射和cubin五个字段。新尝试171.055秒正常退出，但不因此宣称后处理、模拟器或归档完成。证据：[E027](evidence/E027_application.stderr.log)、[E028](evidence/E028_ROOT_INDEPENDENT18_AND_EXACT_SCOPE_CONTRACT_ADMISSION_V6.json)、[E029](evidence/E029_LEAF_TERMINAL.json)。
- **有界SSHFS客户端线程分配失败**：旧私有挂载报告线程创建和内存分配失败，复制任务无法写终态。AS与线程数限制的独立贡献尚未完全隔离。新挂载固定单线程-s，保留AS128及旧挂载；仅在确认远端任务消失、cgroup空、精确PID身份后回收故障守护。小规模检查通过，长复制仍待COMMIT、全接收SHA和清理回执闭合。证据：[E030](evidence/E030_ACTUAL_FAST_PROVIDER_FAILURE_AND_OWNED_STATE_EVIDENCE_V8.json)、[E031](evidence/E031_ACTUAL_SINGLETHREAD_ALIAS_METADATA_AND_SMALL_SHA_STABILITY_V2.json)、[E032](evidence/E032_ROOT_FAILED_RETAINERS_RETIREMENT_1793174718206039746.json)。

新协议实际轻量验收：template完整CTA正常退出，17条源记录，544个源lane操作加128个辅助操作，实际退休672个lane操作、5416周期；仅授予SMOKE_NOT_FULL。证据：[E033](evidence/E033_ROOT_INDEPENDENT_ACTUAL_TEMPLATE_SMOKE_ACCEPTANCE_V1.json)。

## 控制通道、资源锁和计数单位

- **心跳不再依赖NAS审计文件**：G6在读取自身频繁替换的心跳时触发同FD元数据检查失败；另一个CPU批次虽物理门通过、STOP为false，仍在NAS诊断间隔47.9秒后触发心跳断言。旧失败没有保存全部比较操作数，不虚构唯一底层FUSE原因。新通道把sender与kernel sampler独立运行，通过SSH stdin给远端读取线程传递严格scope/run/序号/20秒新鲜度/STOP与EOF状态。真实SSH/systemd验证中，审计线程暂停22.022秒，控制消息和新采样继续到达。证据：[E037](evidence/E037_ACTUAL_CPU_A001_FAILURE_PREFIX_AND_POSITIVE_RESOURCE_HAND_BACK_V1.json),[E034](evidence/E034_ROOT_SHARED_STDIN_CONTROL_COMPONENT_ADMISSION_V1.json),[E035](evidence/E035_ssh_stdin_light_control_v1.py),[E036](evidence/E036_ACTUAL_SSH_SYSTEMD_PIPE_E2E_RESULT_V1.json)。
- **精确旧锁不能代表新的CPU角色**：旧SC7规则把合法G6 CPU2所持的EP_MAIN_CPU6锁当成遗弃锁，导致GPU采集中止。新CPU角色使用自有memfd持有生命周期，并按实际硬内存、CPU和并行预算准入；原共享GPU锁和其他项目规则保留。证据：[E038](evidence/E038_ACTUAL_GPU_FALSE_STOP_CPU_SLOT_CONFLICT_DIAGNOSIS_V1.json),[E039](evidence/E039_ROOT_INDEPENDENT_PRIVATE_MEMFD_COMPONENT_ACCEPTANCE_V7.json)。
- **辅助记录数与lane退休量分别统计**：旧POST的aux_uops为记录级操作计数，不能直接当成lane-uops。保留原数据，只更正汇总单位；未保存的全输入辅助lane数标未知。72个实际选中CTA有883220个源lane操作与133394个辅助lane操作，模型实际退休1016614，均为限定SMOKE证据。证据：[E040](evidence/E040_CORRECTED_WHOLE7_POST_UNITS_AND_SELECTED_SMOKE_LANES_V1.json),[E041](evidence/E041_ROOT_INDEPENDENT_ALL7_ACTUAL_SMOKE_ACCEPTANCE_V1.json)。
