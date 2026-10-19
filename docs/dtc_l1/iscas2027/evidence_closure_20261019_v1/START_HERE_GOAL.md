# Goal: DTC_EVIDENCE_CLOSURE_COORDINATOR_174_V1

角色：新协调Codex窗口，不是AG4窗口。读取本目录README、MASTER_PLAN、PLAN_CONTRACT.json和三个worker Goal。把用户最新授权转为有界、可并行的执行；不要求用户为包装、链接或局部测试脚手架再开一轮。

## 0. 独立工作空间

从本计划实际发布commit创建执行分支 `hrl/iscas2027-dtc-closure-exec-174-v1`，独立worktree和 `/workspace/dtc-evidence-closure-20261019-v1/` raw。不要改计划分支、AG4或其它项目目录。新协调者未取得START收据前不报告正在执行。

## 1. 保护AG4并开展能安全并行的准备

只读核AG4已发布的准确终态；本计划引用的9ece18f6只是预注册快照，不代表当前未启动。没有终态时不重发Goal、不reset、不读活动stdout/maps，不抢它的锁或改observer。

先检查本计划README所述同容器authority兼容风险。AG4可能活动时，只做不会新增未登记执行权的源码审阅、文档/代码准备；不得以改名、搬路径或临时白名单绕开原checker。重CPU测试在明确独立现有环境或AG4终态后进行。若需要等待，先完成GitHub侧三个workpackage准备，不建立自动模拟派发后台。

用已具备且可确认的并行执行能力创建最多三个worker，分别读COV1/SEM1/ROB1；各自分支/工作树/输出隔离。没有可用并行代理时如实发布三个独立入口，不虚报RUNNING。未测试代码只标PREPARED_NOT_TESTED，不将角色名当实际进程状态。

## 2. 作为唯一集成与完整模拟入口

AG4发布完整终态后一次读回LATEST_REPORT、FULL_MATRIX、各点strict、BASE校准、输入/config/runtime身份及退出/锁收据。状态不明不能接管。实际进程实例用当前身份判断，不对历史PID发送信号。

按MASTER_PLAN第3节选择/冻结F，先输出AG4_SCIENTIFIC_REVIEW.md和SELECTION.json。新的P/N/R预算不是补跑AG4的权利。遇AG4未完整、模型正确性/语义需要变化，保留现有结果并对受影响结论作范围裁决，不重复老CPU审计。

读三个worker的不可变交付commit，一次合入必要工具；Core源码修改只允许进入隔离诊断分支，主F保持已选科学配置。source冲突不能机械merge。OFF等价检查可复用原source identity和未变函数证据，只回归受影响路径。

## 3. 将上限计划编成真正预注册

COV1先给八主体输入及N1/N2/N3资格，SEM1提供逐输入支持域，ROB1提供实际实现对照。生成唯一MASTER_MATRIX.tsv，每行含research_question、role、完整input SHA、source/Core/binary、effective options、candidate、BASE来源、family、scope、timeout、UUID、预算来源、strict与统计定义。

预算不超过P16/N6/R6/预备4，总32，按MASTER_PLAN工程替换上限2。旧结果导入只记IMPORTED_VERIFIED，不伪造本计划RUN_START。精确矩阵可分家族发布；每家族首次运行前固定全部成员/分母/输入，不能看本家族收益后删换。

统一runner先有CPU的多root/helper/三个外部CPU角色资格，沿用已验AG4生命周期修复，不另造大型审计框架。首次模拟前核所有文件身份和发布回读。2 workers默认；最多4须事前资源与执行权资格，不能边运行边试上限。所有模拟及替换均由本窗口持有的唯一派发入口计数。

执行优先序：主体F与C+覆盖、服务两点、必要AE/AD公平/机理配对、已准入新输入。各家族独立，已准备好且无依赖的完整点可并行；阻塞输入不拖住整组。全局资源/权属风险停新派发，普通工程错误按有界规则solve-and-continue。负收益照常完成预注册的其余合法点。

## 4. 合并轮次收口

一次产出：总矩阵与缺失项、F/C+逐输入结果、优化增量/公平控制、服务敏感性、三个新增输入情况、SEM1值/顺序证据、全部反证、有效支持域，以及英文v0.17最小科学修改建议。面积/时序明确等用户，不给未经测量的PPA数字。

软件运行身份、模拟完整性、应用值正确、原生等价、硬件可实现性五栏分开。缺一项不伪装全PASS；只保留有限模型结论时明确说明哪些主张未关闭。把关键结果映射到正文问题，不让QA工作取代微架构贡献。

可审材料和小型数据commit/push/fetch-back，原始大日志/trace留原174。报告最终HEAD、tree、关键blob及clean；每个worker发布自己的结果，协调者在CURRENT_STATE.md登记精确commit，不依赖聊天转述。所有实际测试结束后核自身进程与锁退出，无无人值守后续矩阵。

终态可为COMPLETE_WITH_SCOPE、PARTIAL_BLOCKED_INPUT/SOURCE或SCIENTIFIC_STOP，必须给已完成/缺失/原因及最少的下一项决定。不要因格式小问题不停地STOP，也不要因用户强调效率而越过真实数据/语义边界。
