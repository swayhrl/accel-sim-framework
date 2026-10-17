# Lane1 Goal：立即交付 D2/L25，滚动集成结构与理想参考

先读同目录 [PARALLEL_CONTRACT.md](PARALLEL_CONTRACT.md)。在现有 Lane1 Framework 分支 `hrl/ep-l2-ft20261016-lane1-v1` 续接；先检查自己的最新提交、工作树、在途任务和已有 handoff，不覆盖未提交工作，不重启已登记任务。本 Goal 已获用户授权，包含必要新配置/代码和资源登记，不需逐项再请用户批准。

## 1. 第一件可独立交付的事：原 R19 的 D2 与 L25

读取 Lane5 最新请求；截至快照，精确请求为：

[LANE1_FOLLOWUP_REQUEST.json](https://github.com/swayhrl/accel-sim-framework/blob/73d3e3eedbfd92643db2f674a49e16605d3e2260/docs/ep_l2/review_packs/FT20261017_LANE5_R19_INITIAL8_AND_SELECTION_r1/LANE1_FOLLOWUP_REQUEST.json)

Lane5 已完成原 initial8 及 D4 vector/SAD，总12应用均 accepted；其余已事前选定为 D2/L25，当前依赖 producer，不重做选择。消费共享目录已有准确请求，核实后来是否已交付，去重后直接完成以下两个条件，每就绪一个即发布，不等另一项：

| 条件 | 在已有 Q4/D4 上的精确变化 |
|---|---|
| D2 | Q4 的 queues64/512/256/64、scheduler512、return768、credits1279；DRAM1700MHz，接口100GPUcycles；其他同源参数保持 |
| L25 | D4 的 DRAM3400MHz 和上述 queue/scheduler/return；接口25GPUcycles；其他参数保持 |

使用已冻结的 Core `7b8e6ac70b8fe0f1bd37efca11acb5284938825d`、Framework producer `9bd17f9db3e8cbbc3fdad7283d1e292918546fd5`、binary SHA256 `23094a9d6d6bc5edc4afae4dfc1c5ef0fb3b5d45fbfe56ffb4a33db46c597dee`。这两项是已有真实参数的 overlay，先做配置和受影响路径检查；不为此重编官方 binary，不要求 Lane5 编译。

用真实 effective config 和生产事件核验时钟域、固定延迟、调度/credit、WB lower acceptance/set_done 与退尽。L25 的 fixture 不能把旧100cycles写死后仍宣称覆盖25；D2 应覆盖1700MHz的真实路径。保留正向范围 guard，输出每条件 source/config/binary、B/U overlays、affected-test结果和缺口。按现有 shared request 格式交付给 Lane5，commit/push并远端回读。

R19 deadline仍是2026-10-17 17:09:16UTC（北京时间10月18日01:09:16），cap24/planned20 不变。优先消除这一已有、短路径依赖，不把它排在 Ideal 大模块之后。

## 2. 新并行线采用独立、冻结的 release

Lane2：S64、U_CAP16、P2。Lane3：ROP40、L1_32、ICNT2、WAD256_Q4。Lane4：重基于当前 Core 的 WB/META/read reference 与真正 I_MEM_ALL_DATA，必要时 I_BANK/I_L2_SERVICE。

你负责公共接口和最终 release，模块作者在隔离 worktree 提供窄幅 patch、源映射和真实定向检查。已有 TVD/RO 候选继续保留，但不作为这些任务的共同前置条件。特别注意：

- 从当前 Core7b8出发，保留 A1/atomic 等正式修复；不能把 Lane4 的旧候选整文件覆盖回来。
- 新功能默认OFF；逻辑 profile、真实配置、合法组合、parser、summary和 manifest 一致。不删除 guard 来接纳尚未实现的组合。
- 旧 R19 binary 和结果目录保持冻结；新 binary 在独立 build/output 根，准确绑定 Core/Framework/source tree/binary/config/功能向量。
- 滚动集成已就绪模块；可以合并同时就绪的改动以减少构建，但不等 S64、P2、所有 Ideal 一齐完工才发布首个可跑 release。
- 每个新 release 的 B/U 必须用同一个 binary；为需要的比较提供同 release OFF 锚点，由 Lane5 派生实际运行或复用精确合格既有行。不要跨 binary 拼接比值。
- 受影响生产路径、数据版本/sector/WB/退尽、关闭态和共享路径检查按本次改动验证；复用明确未改动且内容身份一致的检查，不重跑全部历史探索。

## 3. 与作者确认的关键接口

S64必须固定1168项，不能 `1152+64`。角色边界、按bank的容量和所有 getter 一起改变。U_CAP16 token覆盖reserved/live/pending retry，到lower acceptance释放，WAD继续到真实完成；不能只查WB map或WAD size。P2是同一物理GPUcycle的真实2次bank服务，对B/U共同适用。

Ideal旧模式和新 ALL_DATA 各自声明解除/保留的服务。ALL_DATA可采用独立LDST reference，但必须真实提交所有store、保持数据依赖/response snapshot/完成事件，覆盖global/local及声明的其他数据空间。按其真实路径发布独立scope；不得套用旧banked资格，也不得让没有物理WB路径的oracle伪造64slice WB通过。

Lane3的same-binary overlay若已被有效guard允许，可在配置资格后直接交付；若WAD256或其他条件超出现有受测配置范围，采用明确opt-in的受控范围扩展。不要让只改一项参数等待所有源码功能合并。

## 4. 实际工作与交付

所有构建/fixture登记同一共享资源lease；并发上限和存储位置按总合同，不能因加速集成在各worktree启动无登记全量make。完整应用由Lane5唯一调度；你提供可立即消费的producer，不重复跑其任务。

每次交付至少包括：具体已完成profile、runtime身份、有效参数、最小patch及base、受影响检查、OFF行为、scope/非法组合、精确输出路径和hash、Lane5可直接使用的handoff。把已完成与仍未具备资格分开列出；一个后续模式暂未实现不撤回无关已合格release。

原分支commit/push并远端回读。先发布D2/L25短交付，再持续完成本轮已就绪模块集成；在新campaign期限内以滚动release推进，不长时间空等单个Lane，不给用户只交一份计划。
