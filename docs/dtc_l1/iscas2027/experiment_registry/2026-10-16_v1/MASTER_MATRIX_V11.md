# DTC-L1 实验台账 V11：BICG主三臂闭合与有界输入研究授权

日期2026-10-16。本文件是独立科学审查/协调快照；不代替174运行收据或授予其他仿真启动权。V1—V10保留。

## 当前最新证据

- A执行分支 hrl/iscas2027-dtc-service-closure-174-v1，本轮回读实际HEAD e52d3eac6708731e62f689a9cf602fa1c7232784；LATEST_REPORT顶部2026-10-16 14:52Z。
- review_pack/checkpoint_20261016T1451Z/SUMMARY.json机器快照2026-10-16 14:51:10.982898Z：原44行35 PASS_CHECKED_SCOPE、6 RUNNING、3 ADMISSION_HOLD；main Goal ACTIVE，averages NONE。此为已发布GitHub状态，不是直接读取当前运行机器。
- 本次读取BICG_IO_COMPLETE_SCOPE_AND_TRIO_AUDIT.json、aec8c80b-1d77-4301-8314-fb98c5d95058.strict.json、BICG_PRIMARY_TRIO.tsv；原来V10记录的OO ATAX验收仍有效。
- 仍在运行的6个原arm：BICG IO128/WAIT128、ATAX IO256、GESUMMV IO256/OO128/TRAD96；全都已发起，严禁重启。原44的3个旧Hotspot禁发标签不由Hotspot V2独立五臂补入。

## BICG新增完整原输入主三臂

| arm | cycles | active-thread instructions | C+/design | terminal |
|---|---:|---:|---:|---|
| TRAD96 / C+ | 25,353,488 | 145,666,048 | 1.000000 | PASS |
| IO256 | 93,312,525 | 145,666,048 | 0.271705 | PASS |
| OO128 | 47,533,116 | 145,666,048 | 0.533386 | PASS |

IO256 attempt aec8c80b-1d77-4301-8314-fb98c5d95058自然exit0，2 ordered kernels分别74,285,056及71,380,992条活动线程指令。原strict PASS，新增同一输入member/list/指令与资源证明、实际active PIB256/640 lines/cap32768及完整抽样/retirement检查为真；fin Core 6fba0136、binary SHA256 fe2d2737。真正的性能回退保留，无参数修改、无重跑。

BICG完整数值主三臂目前是**资源不同的设计比较**，不能直接说乱序顺序导致IO/OO差距。BICG的IO128同深度控制与WAIT128传统等待深度控制还未完整；必须等待其已有工作自然终止，不能补启动重复条件。按原已声明模型，这也不是等面积、native GPU或全ISA结果。

原12个程序中已有9项主三臂数值闭合（包括BICG）；ATAX和GESUMMV待原行自然完成，旧Hotspot仍不合格。9项不等于9项全部scientific admissible：Btree/2DConvolution/LUD的格式适用性pending始终保留。

## 独立输入与论文边界

- 原Hotspot V2：独立重建输入的5/5 strict/resource PASS，B16-N152914、TC80-N107774、C+82873、IO25685718、OO12884456；不能替代原输入或计算原GM12。
- Btree/2D/LUD：原numeric/terminal PASS不删除；Lane B d46cce269证据指出全部FORMAT_APPLICABILITY_REVIEW_PENDING；LUD全global条件源模型证据与capture未绑定的限制同时保留。
- 当前只有原174 A持有唯一调度权；现代128KiB DTC保持HOLD、109 SpMV/LayerNorm仿真NOT_ADMITTED，其他Lane不会自动重启。
- 面积/关键时序/SRAM宏统一成本尚未闭合；不将旧1.326×/1.592×或旧4.7%当本次有限服务/当前硬件数据，不计算未闭合GM12或无条件等面积主张。

## 本轮用户新批准的有限行动

用户同意先审Btree单PC、full32来源有据的E-list条件派生候选，并审2D整kernel自洽性；LUD后置。现已另写新科学合同及CPU-only Goal：

- btree_format_stability_v1/SCIENTIFIC_DECISION.md：Btree G0-G3 CPU门槛、至多一条派生输入、通过后同输入六arm（B16/C80/C+/IO256/OO128/IO128）的独立注册条件及唯一A调度权；失败STOP。
- btree_format_stability_v1/GOAL_CPU_ONLY_174.md：供原174一个隔离CPU窗口执行；不运行模拟、不碰当前六个A任务。2D仅科学可行性及最小来源缺口，不生成或运行正式候选。
- 本文不是“Btree候选已经PASS”或“新六组已启动”；要等独立CPU证明、未来对应A严格结果再审核。即使两种解释性能方向一致也只能声称这两种模型假设内的有限稳健性，不称原capture已恢复。

## 论文更新提示

英文主稿仍以DTC_ISCAS2027_LATEX_V0_7_STYLE_SOURCE.zip为准；本会话未取得实际ZIP，不假称源码改动。论文必须将BICG IO0.272×/OO0.533×及ATAX OO0.610×等负结果与C+模型的明确成本条件同时呈现。机制主图可以继续讲解Tag lookup可见性与旧物理数据保留的分离，但不能用尚未给出的PPA或尚待来源的Btree/2D优势宣称整体更省面积、更快。可预留输入资格注释和独立Hotspot案例，不移动或混合其原结果。