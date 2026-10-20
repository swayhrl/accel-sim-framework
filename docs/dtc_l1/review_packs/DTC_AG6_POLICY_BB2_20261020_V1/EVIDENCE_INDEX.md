# 最小证据索引

| 文件 | 范围 |
|---|---|
| POLICY_B_CONTRACT.md | 拟议状态机、严格准入/冻结安全条件、缺样闭合、有界I/O替代和生产阻碍 |
| PROGRESS_SIGNAL_FEASIBILITY.md / SOURCE_PROGRESS_PROOF.json | 直接读c809 Core及62323 Framework Git源码；精确blob/SHA/行号；没有读取模型或trace |
| policy_b_offline.py / test_policy_b_offline.py | opt-in纯函数/状态实例；8组DECLARED_SYNTHETIC测试源码；未执行、无CPU PASS |
| cpu_entry.py / CPU_ENTRY_REGISTRATION.json | 单worker源码绑定CPU角色；精确归档准入依赖；不import生产guard/dispatcher，无预算或模拟能力 |
| CPU_QUALIFICATION.json / CPU_ADMISSION_SUMMARY.json | 两次入口的实际范围、0测试、首资源HOLD、仅自身argv不闭合、未重试；最终源码修复未重新执行 |
| replay_closed.py / HISTORICAL_28_ROW_REPLAY.tsv | 28原行逐行旧I/O算术复现；B列明确EXPECTED_ONLY_NOT_EXECUTED_RESOURCE_HOLD，缺失语义/安全适配器不补造 |
| INPUT_PROVENANCE.json | Goal与指定8个BB文件在e831精确blob/SHA256；不复制原大JSONL/映射/raw |
| SCIENCE_AND_BUDGET_BOUNDARY.json | AG6 1/4、BA 0/32、F=null与全部零启动/零生产变更边界 |
| FILES_SHA256.tsv / PUBLICATION_READBACK.json | 小文件manifest；精确GitHub HEAD/tree/所有包blob回读；自引用排除 |

本轮完整读取BB指定报告与小索引，原STOP_RECONSTRUCTION的28行及OWN_PROCESS_COUNTERS表。原2.9MB监控、stdout、maps与trace均不重复读取；旧I/O纯规则只读已固定源码作哈希绑定，用独立算术实现核对28条decision/资格计数。旧规则SHA256=a023f3d3d716088d5f2f596de60b15ac64332b1dc1a3e7a9875bbca53f077bb0；28行输入SHA256=ddf1e46bc733440b6e4bf8e86f33e8f5ec7ecc86d7c28f88f66db281835e67c9。历史性能与接受结果不重新计算。

独立worktree：`/workspace/worktrees/accel-sim-iscas2027-dtc-ag6-bb2-policy-174-v1`；独立输出：`/workspace/dtc-ag6-bb2-policy-174-v1/evidence/`。

局部实际回执（详细全项目OS metadata仅留本地，不发布外项目命令行）：

- 根目录CPU_ENTRY_START/CPU_ENTRY_EXCEPTION：源码提交0c602af0a1d212bf8b67d1cdb7598e25fb11ec2b，归档依赖缺失，OS采样0、测试0。
- cpu_attempt2/CPU_ENTRY_START.json、CPU_FIRST.json、CPU_ADMISSION.json：源码提交3963ee2be（完整SHA在CPU_QUALIFICATION.json），hostIO28.90 首样本HOLD，测试0；全量原始metadata SHA在CPU_ADMISSION_SUMMARY.json。只读authority检查不获取锁、不发信号。
- SOURCE_FREEZE_READBACK.json / SOURCE_REPAIR_READBACK.json：测试前精确fetch源码HEAD/tree与8个source blobs，随后仅2个修复blob；注册source closure均匹配，不重复原49文件审计。
- REPLAY_RESULT.json：旧规则28条匹配；proposal_evaluator_executed=false；新B列为未执行的保守预期。

普通工程修复仅涉及本包：归档依赖完整性、CPU入口绝对argv检查及晚到STOP使completion candidate失效；均未改现行生产模块。新代码只做AST解析/源码审查，**没有以syntax或离线预期冒充实际CPU测试**。资源首失败后没有再次采样、后台监控、未来定时补跑或跨账户执行。

最小下一步是新鲜资源窗口内的精确角色CPU-only语义资格，再单独讨论遥测集成与一次真实端到端资格的科学合同/预算；本包不是可执行AG6注册。
