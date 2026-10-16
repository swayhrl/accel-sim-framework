# EP-L2功能实现与理想化实验：公共执行合同

日期：2026-10-16。本文是已获用户同意的本轮执行合同；发布到GitHub不代表节点任务已经启动或实验已经完成。

## 0. 新增用户确认与本轮工程选择

用户确认：独立WBUF数据在原1024 resident＋128 bypass之外；可采用8或16项/slice；允许把其数据存储物理并入统一池。用户同意初期完整epoch RO oracle，以及Tag miss后额外一拍TVD查询并计入服务竞争。用户授权并行推进机制、实验、写作，并补充理想化性能诊断。

本轮固定的实验选择（不是已流片硬件事实）：WBUF16为primary，WBUF8为sensitivity；不看加速结果后再反选主配置。历史shadow WBUF仍然只是观察投影。

| 档位 | Static数据预算/slice | Unified数据项 | 四bank组织 | 全芯片数据量 |
|---|---|---:|---|---|
| Primary C=16 | 1024 resident + 128 bypass + 16 WBUF | 1168 x 128B | 4 x 292 | 9.125MiB |
| Sensitivity C=8 | 1024 resident + 128 bypass + 8 WBUF | 1160 x 128B | 4 x 290 | 9.0625MiB |

其他primary资源不变：64 slices、32 memory channels、128B line/4x32B sectors、1024 resident tags/slice、512 requester descriptors/slice、128 Line-MSHR/slice、每地址32请求上限、128 WAD/slice、L1 BASE、L2->DRAM128/slice、scheduler128/channel、ReturnQ192/channel、DRAM850MHz。理想化诊断可以明确放宽所研究的资源，但不得冒充上述预算内实现。

1168/1160是数据预算；metadata、数据搬运、端口/仲裁和下层数据队列另外逐项核算。payload_id仍需11bit，generation位宽须依据实际生命周期另行说明，不能由C++ unsigned大小推成物理面积。

## 1. 仓库与证据锚点

Framework: swayhrl/accel-sim-framework
- 架构/章程入口：hrl/ep-l2-exp-v0 @ b7dbdecb94054f08aaf2e33bfef48e453747ceb5。
- D512 runtime: aae62b66685f15437cecf0193934f628e6fac6ae。
- M1归档: c0a71e204715289895028d27ac82190041d83b85。
- M0a+M1集成归档: hrl/ep-l2-m0a-m1-int-v0 @ 54fbc7869f4e40b6b48dc936b527fee85dd46406。
- 校准分析: aa44f9e8d685b6f9bbe410b996e07ef185a8de96。
- M0b: 7ad2b240fee32492e778611cb6deb45516c29bcf；M3a: 4f198e307361a2a5e4a38b4db478c5165f89752d。
- Motivation归档: 11cbd5a79127ad2fedf9801969a656be73fead96。
- Streaming归档: cdab5765b65f6e1575d9c185de127a1c1c49dd70；其已记录runtime为db1c90182fad02aacbd282b67ecdc57b8e4cc365，不得以绘图提交替代runtime SHA。

Core: swayhrl/gpgpu-sim
- 原目标基线: 0cde333340792cffed869cbbc7e7dc88667c6b8b。
- D512: 878f80869ce212e779df20b6421e4dc7f987825d。
- M1: 955a50cbb5e8d928b6c7b0c78e1af062b835df44。
- M0a+M1共同集成点: 1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e。
- M0b: 9907b7e617ea0ee6580fb8156e985838720f08fa。
- Motivation: 2a6a31591bc42023e5997cca969e4b672efe0405。
- Streaming: ca3e7bc0b8f61b5d7c052bcda2a91955a1e5c919。

建议以共同集成点建立新工程线，由Lane 1核实Framework匹配及静态回归后发布准确父版本。不要直接把全部历史分支merge；不要因Streaming更新就假设它包含M0b。Lane 4在公共父版本未发布前可以独立审计历史资产、开发诊断与单元测试；历史父版本上的运行只能标HISTORICAL_DIAGNOSTIC，不能填新WBUF16基线的结果空缺。

必须阅读：
- docs/ep_l2/ELASTIC_PAYLOAD_L2_ARCHITECTURE_AND_ROADMAP.md
- docs/ep_l2/project_spec/RESEARCH_CHARTER.md
- docs/ep_l2/project_spec/MECHANISM_SEQUENCE_CURRENT.md
- docs/ep_l2/project_spec/PERFORMANCE_HEADROOM_PLAN.md
- docs/ep_l2/chatgpt_handoff/LANE_D_FINAL_CONVERGENCE_CHATGPT_REVIEW.md
并结合对应源码、review_packs、CSV，而非仅看LATEST。

## 2. 执行与协作

这是连续执行Goal，不要止于复述计划。先读取当前节点和工作树状态；若同任务已有活动进程或窗口，登记并复用结果，不重复启动、不停止它。

不得假设具体挂载路径。自动定位两个仓库、已有trace、build和结果目录；不得修改其他项目worktree、权重或trace。每lane使用独立branch/worktree/build/result根。分支建议hrl/ep-l2-ft20261016-lane<N>-v1（N=1..6）。旧分支、旧CSV及旧review pack只读。

Lane 1负责公共生产接口和最终集成；Lane 2/3/4只提交自己模块及最小接入patch，不在同一个工作树并发编辑gpu-cache/l2cache核心文件。Lane 5负责全局实验调度与run-key去重。Lane 6只改论文/PPA记录，不修改实验输入和科学CSV。

每个运行唯一键至少包含Core SHA、Framework SHA、binary SHA256、完整runtime config SHA256、trace内容身份、workload/epoch范围、功能与ideal位向量。同源同binary对照优先；只有完整身份与模式符合时才复用历史行。缺包装文件可从保留来源确定性重建；缺科学payload不得猜补。

Lane 1先发布INTERFACE_CONTRACT和BASELINE_CONTRACT；Lane 2/3可以同时完成独立模块与定向测试，不需要空等。依赖未就绪时继续无依赖子任务，最后发布可接入产物及明确依赖，不用高频轮询或虚假PASS。

并行窗口不等于每窗各开一批长模拟。Lane 5按实际空闲内存、单任务峰值RSS、已有任务和swap制定共享配额；所有lane请求同一配额。不终止其他活跃任务来抢资源。scan单独排队，不能阻塞首批结果。不得重跑全部80行校准仅为换新包装。

所有新功能/ideal开关默认OFF；非法组合拒绝。普通工程问题自行修复并继续；不得为过关删除assert、跳过数值/生命周期检查。仅科学语义、资源预算或不可恢复输入问题需报告阻塞。保留诊断产物，不把FAILED/TIMEOUT/未完成行填零或纳入平均。

产物完成后，在新lane分支commit/push并回读验证；无写权限则保留本地commit和patch，明确说明，不宣称远端已发布。

## 3. 新旧基线与公平比较

OLD_D512_STATIC：历史1152项payload静态模型，不声称有已执行的物理WBUF8/16。
B16_BANKED：新有限WBUF16基线，等预算4x292，静态1024/128/16角色划分，真实容量背压和生命周期；是primary机制对照。
B8_BANKED：同理4x290、1024/128/8，属于敏感性。
LEGACY_SEPARATE_C：分离RAM参考；任何新增WBUF端口模型必须单列为建模选择，不宣称用户确认了端口数。
U_WB_C：等预算统一池首先承担真实WB staging，RO/TVD关闭；允许WB使用可用共享容量，不再保留人为C项数据配额。
U_WB_TVD_C、U_WB_RO_C、FULL_C：逐项启用经过验证的机制。

建立OLD->新功能全关的等价检查；新有限WBUF开启后预期可以改变时序，这属于显式新模型，不是让新基线强行复现旧结果。

Bank-matched static与Unified保持相同bank数及每bank每周期一次line-sized操作。对static resident->WBUF拷贝、WBUF->lower读取与Unified原位读出分别记账。真实避免的拷贝可以成为贡献，但不能赠送免费端口/数据搬运。必要时在一个代表点保留相同copy服务代价，仅切换容量借用以做归因。

若U_WB有效，至少追加一个同总数据预算的静态重划分强对照（如1024 resident+112 bypass+32 WBUF，总1168），不能只比很小WBUF。对确无bypass的计算集，还可用1024 resident+0 bypass+144 WBUF作为明确标注的compute-only竞争参考，禁止把它宣传成保留完整bypass能力的通用基线。只在代表点做，不铺满全矩阵。

WB控制状态不等于WB数据配额。复用WAD/已有WB控制条目表示更多待发WB，新增pointer/state逐项计费。不得偷偷赠送无界WB元数据，也不得把原C项数据配额换名为C项控制配额使借用永远不生效。

## 4. WB/TVD生命周期：必须精确

Static：在破坏dirty victim前原子地预留WAD、有限WBUF数据落点和真实需要的下层发行槽位/credit；不满足时无部分提交。数据暂存从真实readout/packet创建开始，到真实L2interface::push下层接收完成。WAD仍保留到真正set_done。

U_WB（TVD OFF）：旧resident payload原位转为WB_STAGED，由control handle保持；新resident获得另一个合法landing。WB数据被下层真实接收且下层有已计账的数据承载之后，释放旧payload；WAD继续跟踪顺序。

U_WB+TVD：在上述边界之后继续保留payload用于dirty-inflight read-forward，是TVD新增retention，不再叫原WBUF staging。其额外占用需统计。依原协议，WB_PENDING/INFLIGHT不可当clean opportunistic项回收；写/atomic等待WB完成。WB完成后可转clean victim或释放。

下层仅收到指针却仍依赖原payload时，不能视作数据已转交而释放。mem_fetch是软件载体，不是额外免费RAM。每段链路声明数据驻留在哪个预算/队列，避免丢失或重复计算物理数据。

TVD read仅在请求sector全部有效时服务；缺sector不得把整条line视作hit。首版缺sector回退须保持单一可写owner与原有ordering。clean write/atomic先promote；dirty inflight read-forward必须可达，不能被旧WAD preview一律挡住。Promotion保留同payload，Tag/目录可见性原子切换。

## 5. 统一池与RO正确性

resident tag i与payload ID不再普遍相等；static模式保持原映射。首版resident分配尽量冻结bank class payload_id%4==tag_index%4；真需要改变时单列placement机制，不暗改。

资源角色按主owner互斥计数：FREE+live payload slots=物理预算；pending-sector/read-reference等作为附属状态，不能把同槽重复计入多种角色。

已接收的lower transaction必须有landing；所有sector返回、所有waiter完成及最后数据读取离开之前不能错误释放。预留策略从等待依赖图与同bank最坏情况推导，覆盖normal fill/bypass/WB退尽；不能把watermark调成制造收益的参数。

RO用完整epoch/line粒度oracle，不能仅按当前load或!is_write()判定。排除写分配伪read、同line store/atomic、别名重叠及无法证明的外部/并发写入。拒绝未获证明请求并走普通路径；oracle成本与覆盖率明确。

RO detach不丢事务；同地址多个RO事务按不同{id,generation}并存。取消现有按地址清理旧owner对detached合法实例的破坏。Attached fill核对Tag generation，detached fill不重新装Tag。全部32B sector/pending mask、512共享descriptor、响应背压及epoch退尽必须覆盖。

## 6. 首批实验与判定

开发集：convolutionSeparable、FWT_7_21、cfd_097k、vectorAdd_4M、sad。
btree、dwt2d作不参与首轮调参的验证集（不是此前未见的负载）。scan独立长任务。先B16/U_WB16；TVD/RO合格后滚动加行，不等FULL，不一开始乘出全部cross-product。

输出cycles、instructions、useful admits/responses、unique requests与attempts分离、blocking/wait、WB staging与WAD lifetime、Payload各角色/borrow/refusal、TVD有效服务与avoided reads/bytes、RO重复读放大/descriptor压力、bank操作/等待、下层压力、终态退尽与身份检查。

边界测试必须驱动生产实现并与小型数据/版本参考模型比较；仅cycles/instructions一致不等于缓存数据正确。

理想化结果单列diagnostic表，与implementation结果分开；它们不需要等FULL完成。旧headroom的机制x系统交互实验仍仅在对应局部效果出现后安排。有限扩大资源必须证明所针对的阻塞已消失；否则只称sensitivity，不称non-binding。

## 7. 不做的事

不扩展AI/graphics trace资产，不无端修改L1/DRAM主配置，不重开大规模机会采样，不依据期望结果选WBUF大小，不把全L2命中诊断称为EP-L2可实现加速，不宣称尚未运行的实验已经启动/完成。
