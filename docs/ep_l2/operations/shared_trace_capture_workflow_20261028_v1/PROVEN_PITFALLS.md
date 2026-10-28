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

详细原因、适用限制、原始路径和完整SHA见[机器可读问题清单](PROVEN_PITFALLS_V2.json)及[证据索引](EVIDENCE_INDEX.json)。
