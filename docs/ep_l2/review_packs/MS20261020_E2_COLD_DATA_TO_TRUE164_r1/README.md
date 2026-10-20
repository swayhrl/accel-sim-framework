# EP-L2 E2 → S/T：真164冷数据候选 V2

候选 **3303 个文件，allocated bytes 上界 6,420,480,000 B（5.980 GiB）**；实际释放0 B。只完成元数据盘点及 E owner 候选审核，尚无源侧释放许可。

| 原174目录 | 精确COLD子集 allocated bytes | 文件数 |
|---|---:|---:|
| `/workspace/build/ep-l2-potential20261017-lane1-p2-r1` | 1,897,136,128 | 724 |
| `/workspace/build/ep-l2-potential20261017-lane1-structure-r1` | 1,815,011,328 | 712 |
| `/workspace/build/ep-l2-ft20261017-lane1-r0-1-buildfix-r2` | 919,437,312 | 568 |
| `/workspace/build/ep-l2-ft20261017-lane1-r0-1-buildfix-r1` | 919,408,640 | 568 |
| `/workspace/build/ep-l2-potential20261017-lane1-all-data-r1` | 869,486,592 | 731 |

all-data-r1 仅选清单中的731个文件，18个仍被引用的构件保留；microopt整目录WARM。逐文件绝对路径、设备/inode/nlink、逻辑/分配大小、原SHA记录、归属、reader和恢复要求见 `r2/COLD_FILE_CANDIDATES_V1.json`，该历史文件名由r2目录区分版本。

按inode检查111个进程、1209个句柄/进程链接、37167条mmap：无匹配、无权限缺口、无候选变化、全部nlink=1。仅为快照，复制/释放前须再次检查。146个文件有原精确路径SHA记录，3157个没有；未重算大文件SHA或扫描trace正文。

原科研结果、历史raw、失败/撤回日志和旧中间产物均按st_blocks×512排序于 `r2/ALL_INVENTORIED_FILES_ALLOCATED_RANK.csv`。三个正式结果根目录维持HOT计量结构及WARM历史内容，暂不提供源侧释放清单。

S须对精确选择形成不可变传输流清单并核对原SHA；T须证明真164主机/boot及独立落盘设备，完整恢复每个文件并独立哈希、核对目录/模式/属主/链接语义。目标副本或归档存在不足以验收。E随后重新核对科学引用、原始失败/HOLD、台账和每个源文件，才可对精确源集合给出释放验收。

当前df快照可用7,066,738,688 B，小于零其他预留时单路正式运行门槛7,918,845,952 B。overlay分配量不等于删除后真实df增量，不能预先声称恢复空间。未复制、迁出或删除候选数据；未启动CFD/DWT/SAD。

原T0=1792414193、14/40（余26）、32+8、contingency已用8/8和累计6/20GiB政策保持。Conv仍唯一CURRENT_ACCEPTED配对；Vector S COMPLETE_VALID、Vector F RESOURCE_LIMIT；FWT原两端INCOMPLETE不重跑。控制器STOPPED，无活动实验/lease。
