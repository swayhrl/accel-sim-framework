# Node109 大型已归档科研资产一次性冷存回收 — 执行完成

依据用户明确授权的 `NODE109_LARGE_ARCHIVED_ASSET_FAST_RETIREMENT_V1`，从 V4 冻结清单逐组通过四项临删检查后，已在 109 控制目录持久化38文件白名单与INTENT，再按精确路径逐文件非递归 unlink，并逐条 fsync DONE。没有停止/重启科研任务，没有执行GPU实验，也未删除目录或白名单外资产。

| 组别 | 状态 | 文件 | 冻结单硬链接数据块 | 实测可用空间变化 |
| --- | --- | ---: | ---: | ---: |
| R26 `trajectory/` 九份 | **DONE** | 9 | 22.017 GiB | 与R27合并测量 |
| R27 三份历史 `COMMON_POST_BOOTSTRAP.pt` | **DONE** | 3 | 7.339 GiB | R26+R27组共 29.356 GiB |
| Qwen3-30B 精确revision | **DONE** | 26 | 56.889 GiB | 56.889 GiB |

Worker开始前可用 `58063298560` B（54.08 GiB），结束时可用 `150667874304` B（140.32 GiB），**实测增加 `92604575744` B（86.245 GiB）**。随后独立 `df` 复查可用 `150667833344` B（140.32 GiB），根盘使用率降至 85%。文件块期望回收 `92604674048` B；与df差额受控制记录、目录元数据及并发写入影响，未把它强行逐字节归因。

独立复核确认38个源文件全不在，38条 BEFORE_UNLINK 与38条 DONE和冻结白名单完全一致，无异常事件；真164身份及两组全部目标/小型归档回执再次核验 PASS。R26 规范COMMON的原身份不变，R27其它checkpoint与B0、StageA三权重、三处pip缓存均仍在。R26 trajectory目录、Qwen原revision空目录及models父目录保留。

按需恢复：R26九份各从真164 `c16_ai_workload/provenance/awma/r26_tied_weight_production_capacity_boundary_109_v1_20261002/checkpoints/trajectory/` 同名取回；R27三份从真164 R26规范 `checkpoints/COMMON_POST_BOOTSTRAP.pt` 分别恢复到原R27三条绝对路径；Qwen3须从真164 `c16_ai_workload/assets/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/` 取回完整26文件。均应先在109逐文件核对既有SHA与身份、检查配置/索引/运行环境，再启动科研任务；不能假定直接在SSHFS上运行模型。

公开版隐去私有账号/主机，逐文件路径、冻结身份、期望SHA及DONE在 `FROZEN_WHITELIST_AND_DONE.csv`。109持久控制目录及其PLAN/INTENT/EVENTS/FINAL_RECEIPT的SHA在 `EXECUTION_RECEIPT.json`，未上传模型或原始科研数据。完成GitHub提交与远端回读后STOP。
