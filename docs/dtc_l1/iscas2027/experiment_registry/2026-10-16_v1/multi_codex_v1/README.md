# DTC多Codex并行推进 V1

2026-10-16。用户授权规划多个Codex并行处理实验及阻塞项。**本提交准备工作分工，不代表这些辅助窗口已经启动，也不启动、停止或迁移任何服务器任务。** 主Goal保持active，原174账户/容器不是174-new。

## 当前依据与优先级

主执行Framework：`e3dbe3dbf2abb49b923244538d2a3d1828024d4f`，分支`hrl/iscas2027-dtc-service-closure-174-v1`。当前finite Core为`6fba0136f8465b59fe5858a950fa39efb265f654`；构建Framework为`18a68dcccd795f1b6cda75504e9450d00c9cee02`。协调文档所在分支不是运行程序的源码身份。固定44行计划SHA为`281b2d22ace3bbf105711473516f075fc11c495a1d6c214d9f4a3e42414892e1`。

09:43:54 UTC快照：44行中5个terminal/invariant PASS、8个RUNNING、3个ADMISSION_HOLD、28个尚未启动。5个PASS中的Hotspot IO/OO两个**scientific promotion仍HOLD**；其余三个是Btree IO/OO/TRAD96。不得概括成5个无条件科学接受结果。全629成员的指令合计匹配及global-load最多32个128B引用，只支持当前固定输入范围；没有证明所有ISA指令或Hotspot共享地址的语义。

Hotspot需要优先解决，因为它影响既定12负载覆盖和已有对照的适用性。4080固定128KiB和SpMV/SM89是独立的现代扩展阻塞项，时间预算更低，不得拖累11个未遇到该编码问题的原负载。

## 分工：一个执行调度者，三个独立辅助窗口

| 窗口 | 环境 | 负责文件 | 工作与交付 | 权限边界 |
|---|---|---|---|---|
| A 主窗口 | 原174，现有窗口 | GOAL_A_COORDINATOR_CONTINUE.md | 既有44行合法部分、单行验证、复用、调度、结果发布 | 唯一主实验launch及受理权限；不重启Goal |
| B Hotspot | 原174，新窗口 | GOAL_B_HOTSPOT_FORMAT.md | 历史编码溯源、确定解码语义、最小候选修复和影响范围 | 独立worktree/输出；CPU-only；不得放行Hotspot或改主parser |
| C 现代容量 | 原174，新窗口 | GOAL_C_MODERN_CAPACITY.md | 复用已做容量审计，提出最小128KiB存储/端口组织与支持域决策 | 只读源码及CPU布局检查；不实现新协议、不启动现代DTC |
| D SM89准入 | 109，新窗口 | GOAL_D_SPMV_SM89.md | 检查已有Ada支持资产，给出SpMV支持域候选或明确不可行证据 | CPU-only；不重跑native、不改原trace/头部、不复活LayerNorm |

ChatGPT继续论文内容和已发布证据审查。用户硬件报告独立推进；辅助窗口不能由软件结构猜测总面积。

B/C/D建议分支分别为`hrl/iscas2027-dtc-hotspot-format-174-v1`、`hrl/iscas2027-dtc-modern-layout-174-v1`、`hrl/iscas2027-dtc-sm89-admission-109-v1`。先fetch检查分支和活动任务；存在匹配工作就续接，不reset、不开重复任务。每个窗口必须自己建立worktree、构建目录和review_pack。禁止写主执行的LATEST_REPORT、44行注册表、dispatch状态/锁、raw目录、正在运行的binary及cache环境。

## 流水方式

A继续8个现有模拟；已获本arm试点资格的慢行先进入空槽，短控制与验证在其余槽中滚动。B/C/D同时输出独立问题解答，不等待A全部跑完。辅助补丁只作为候选提交；A先核source diff与已有科学合同，需要改变地址、支持域、协议或资源定义的先交审，批准并通过局部验证后才登记新的future attempts。不把新旧binary混写为同一行，不把更正后的Hotspot与旧baseline直接相除。

在当前快照中，GESUMMV IO/OO已经提早启动；不重复提交。现有原协调器仍存活但已无launch authority，scoped协调器是唯一启动者；检查实际ownership token而非按旧PID强制操作。不要因为使用多个Codex再建立一个44行调度器。

## 资源与耗时预算

保留当前8-simulator、最多2个已知heavy的起点。A可按实测RSS/cgroup/CPU/IO将后续启动并发提高到12，再到16；仅在有效模拟吞吐提高、没有持续换页/内存压力时升档。不以CPU有空闲或Codex窗口数推断可安全增加重任务。B/C各用1个CPU扫描/检查进程，确需编译至多-j2；两者不得同时进行全量大编译。D用109 CPU，不占GPU。不给每个Codex各自8个仿真槽。

时间预算是检查点而非完成承诺：B启动后约90分钟提交第一份溯源结论，约4小时到达来源闭合/候选修复/具体未解分歧之一；若有新的可检验来源可继续，但没有新信息不反复全量扫描。C约2小时交可落地的布局方案或必要合同变更，不从零重复629项审计。D约2小时交支持差异，只有已有可信路径时才用额外约2小时做隔离CPU验证；不扩成工具链迁移。

各窗口每次阶段完成push并fetch-back验证。A处理每条terminal时先验证再补位，阶段交付不成为暂停其他合法行的理由。状态采用terminal_validation和scientific_promotion双字段。没有原生值/时序证据的地方不得升级claim；没有新结果不编造ETA或平均值。

本轮不新增负载族、形状或敏感性矩阵，不重开SG3/logical80，不占用其他项目GPU。现代容量和SM89修复若需要长周期新实现，可停在明确边界；Hotspot若无法确定旧地址，只能提出新输入或变更支持集合的方案供用户决定，不能自动删除负载或改称GM12。
